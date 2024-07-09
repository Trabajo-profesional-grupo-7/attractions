import os
from typing import List

import boto3
import nltk
import numpy as np
import pandas as pd
from deep_translator import GoogleTranslator
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from app.db import crud
from app.db.database import get_db_session
from app.services.constants import (
    FILLNA_VALUE,
    MINIMUM_NUMBER_OF_RATINGS,
    N_RECOMMENDATIONS,
)
from app.services.logger import Logger

from ..db import models

nltk.download("vader_lexicon")


# Devuelve las posiciones de los n números más grandes dado un arreglo de números
# Ej: [8, 3, 2, 9, 7] con n=3 devuelve [3, 0, 4]
def n_greatest_positions(numbers, n):
    sorted_indices = sorted(range(len(numbers)), key=lambda i: numbers[i], reverse=True)
    return sorted_indices[:n]


def get_sentiment_metric(text):
    sia = SentimentIntensityAnalyzer()
    translator = GoogleTranslator(source="auto", target="en")
    text = translator.translate(text)

    Logger().debug(msg=f"Done translating")
    sentiment = sia.polarity_scores(text)
    positive, negative = (
        sentiment["pos"],
        sentiment["neg"],
    )

    if positive > negative:
        return positive
    elif positive < negative:
        return -negative
    else:
        return 0


def create_rating_score(rating: int):
    if rating == 1:
        return -1
    elif rating == 2:
        return -0.5
    elif rating == 3:
        return 0.1
    elif rating == 4:
        return 0.5
    elif rating == 5:
        return 1
    else:
        return 0


def get_merged_df(db: Session):
    Logger().debug(msg=f"Start loading ratings")
    df_ratings = pd.DataFrame(
        db.query(
            models.Ratings.user_id, models.Ratings.attraction_id, models.Ratings.rating
        ).all(),
        columns=["user_id", "attraction_id", "rating"],
    )

    Logger().debug(msg=f"Start loading likes")
    df_likes = pd.DataFrame(
        db.query(models.Likes.user_id, models.Likes.attraction_id).all(),
        columns=["user_id", "attraction_id"],
    )
    df_likes["is_liked"] = 1

    Logger().debug(msg=f"Start loading saved")
    df_saved = pd.DataFrame(
        db.query(models.Saved.user_id, models.Saved.attraction_id).all(),
        columns=["user_id", "attraction_id"],
    )
    df_saved["is_saved"] = 1

    Logger().debug(msg=f"Start loading done")
    df_done = pd.DataFrame(
        db.query(models.Done.user_id, models.Done.attraction_id).all(),
        columns=["user_id", "attraction_id"],
    )
    df_done["is_done"] = 1

    Logger().debug(msg=f"Start loading comments")
    df_comments = pd.DataFrame(
        (
            db.query(
                models.Comments.user_id,
                models.Comments.attraction_id,
                models.Comments.comment,
                models.Comments.sentiment_metric,
            ).all()
        ),
        columns=["user_id", "attraction_id", "comment", "sentiment_metric"],
    )

    db.close()

    Logger().debug(msg=f"Agrupa los comentarios por usuario")
    df_comments = df_comments.groupby(["user_id", "attraction_id"]).agg(
        {"sentiment_metric": "mean"}
    )

    Logger().debug(msg=f"Start merging dfs")

    df = (
        pd.merge(df_ratings, df_likes, on=["user_id", "attraction_id"], how="outer")
        .merge(df_saved, on=["user_id", "attraction_id"], how="outer")
        .merge(df_done, on=["user_id", "attraction_id"], how="outer")
        .merge(df_comments, on=["user_id", "attraction_id"], how="outer")
    )

    df.fillna(0, inplace=True)

    df["score"] = (
        100 * df["is_liked"]
        + 50 * df["is_saved"]
        + 20 * df["is_done"]
        + df["rating"].apply(create_rating_score) * 200
        + df["sentiment_metric"] * 50
    )
    return df


def run_recommendation_system(db: Session):
    df = get_merged_df(db=db)

    # Matriz usuarios-atracciones
    matrix = df.pivot(index="user_id", columns="attraction_id", values="score")

    # Se rellenan los nulos
    matrix = matrix.fillna(FILLNA_VALUE)

    Logger().info(msg=f"Start calculating the cosine similarity matrix")

    # Se calcula la similitud coseno de todos los usuarios con todos
    user_similarity = cosine_similarity(matrix)
    user_similarity_df = pd.DataFrame(
        user_similarity, index=matrix.index, columns=matrix.index
    )

    db = get_db_session()

    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    dynamodb = session.resource("dynamodb", region_name="us-east-2")

    table_name = "recommendations"
    table = dynamodb.Table(table_name)

    for user_id in matrix.index:
        Logger().info(msg=f"Processing user {user_id}")

        if (
            crud.number_of_interactions_of_user(db=db, user_id=user_id)
            >= MINIMUM_NUMBER_OF_RATINGS
        ):

            # Se obtienen los ratings hechos por el usuario actual
            user_ratings = matrix.loc[user_id]

            # Se buscan usuarios similares utilizando a los que tengan mayor similitud coseno
            similar_users = user_similarity_df[user_id].sort_values(ascending=False)

            if similar_users[similar_users != 0].count() > 1:

                # Se genera un vector de ceros donde se almacenarán los scores predichos
                scores = np.zeros(matrix.shape[1])

                # Se recorren todos los usuarios eliminando el primero por ser el propio usuario con similitud=1
                for similar_user in similar_users.index[1:]:
                    similarity_score = user_similarity_df[user_id][similar_user]
                    similar_user_ratings = matrix.loc[similar_user]
                    scores += similarity_score * similar_user_ratings

                scores = pd.Series(scores, index=matrix.columns)

                # Se eliminan las atracciones con las cuales el usuario ya interactuó
                scores = scores[user_ratings == 0]

                # Se toman las N_RECOMMENDATIONS con mayor score
                recommendations = (
                    scores.sort_values(ascending=False)
                    .head(N_RECOMMENDATIONS)
                    .index.tolist()
                )

                # Se actualiza el registro en DynamoDB
                item_data = {
                    "user_id": user_id,
                    "attraction_ids": recommendations,
                }

                table.put_item(Item=item_data)


def update_recommendations(user_id: int, attractions_ids: List[str]):
    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    dynamodb = session.resource("dynamodb", region_name="us-east-2")

    table_name = "recommendations"
    table = dynamodb.Table(table_name)

    item_data = {
        "user_id": user_id,
        "attraction_ids": attractions_ids,
    }

    table.put_item(Item=item_data)


def get_recommendations_for_user_in_city(db: Session, user_id: int, city: str):
    df = get_merged_df(db=db)

    df_attractions = pd.DataFrame(
        (
            db.query(models.Attractions.attraction_id, models.Attractions.city)
            .filter(
                models.Attractions.city == city,
            )
            .all()
        ),
        columns=["attraction_id", "city"],
    )

    df_attractions["attraction_id"] = df_attractions["attraction_id"].astype(str)
    df["attraction_id"] = df["attraction_id"].astype(str)

    df = pd.merge(
        df.reset_index(drop=True),
        df_attractions.reset_index(drop=True),
        on="attraction_id",
        how="inner",
    )

    # Matriz usuarios-atracciones
    matrix = df.pivot(index="user_id", columns="attraction_id", values="rating")

    # Se rellenan los nulos
    matrix = matrix.fillna(FILLNA_VALUE)

    Logger().debug(msg=f"Start computing cosine similarity")
    user_similarity = cosine_similarity([matrix.loc[user_id]], matrix)

    # Se obtienen las posiciones de los usuarios más cercanos
    # Se agrega 1 al n porque se debe tener en cuenta que una siempre va a ser la propia atracción por tener similitud=1
    positions = n_greatest_positions(user_similarity, N_RECOMMENDATIONS + 1)

    # se filtra a la matriz dejando solamente a los usuarios cercanos
    filtered_matrix = matrix.iloc[positions]
    if user_id in filtered_matrix.index:
        filtered_matrix = filtered_matrix.drop(user_id, axis=0)

    recommendations = filtered_matrix.mean().nlargest(N_RECOMMENDATIONS).index.tolist()

    return recommendations
