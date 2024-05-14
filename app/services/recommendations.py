import os
from typing import List

import boto3
import pandas as pd
from pysentimiento import create_analyzer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from app.db import crud
from app.services.constants import MINIMUM_NUMBER_OF_RATINGS

from ..db import models

# Cantidad de atracciones que se quieren recomendar
N_RECOMMENDATIONS = 20

# Valor para rellenar a los nulos
# Un nulo sucede cuando un usuario no calificó una atracción
FILLNA_VALUE = 0


# Devuelve las posiciones de los n números más grandes dado un arreglo de números
# Ej: [8, 3, 2, 9, 7] con n=3 devuelve [3, 0, 4]
def n_greatest_positions(numbers, n):
    sorted_indices = sorted(range(len(numbers)), key=lambda i: numbers[i], reverse=True)
    return sorted_indices[:n]


def get_sentiment(text):
    analyzer = create_analyzer(task="sentiment", lang="es")
    return analyzer.predict(text).probas["POS"]


def get_merged_df(db: Session):
    df_ratings = pd.DataFrame(
        [row.__dict__ for row in (db.query(models.Ratings).all())],
        columns=["user_id", "attraction_id", "rating", "rated_at"],
    )

    df_likes = pd.DataFrame(
        [row.__dict__ for row in (db.query(models.Likes).all())],
        columns=["user_id", "attraction_id", "liked_at"],
    )
    df_likes["is_liked"] = 1

    df_saved = pd.DataFrame(
        [row.__dict__ for row in (db.query(models.Saved).all())],
        columns=["user_id", "attraction_id", "saved_at"],
    )
    df_saved["is_saved"] = 1

    df_done = pd.DataFrame(
        [row.__dict__ for row in (db.query(models.Done).all())],
        columns=["user_id", "attraction_id", "done_at"],
    )
    df_done["is_done"] = 1

    df_comments = pd.DataFrame(
        (
            db.query(
                models.Comments.user_id,
                models.Comments.attraction_id,
                models.Comments.comment,
            ).all()
        ),
        columns=["user_id", "attraction_id", "comment"],
    )

    df_comments = (
        df_comments.groupby(["user_id", "attraction_id"])["comment"]
        .agg(lambda x: " ".join(x))
        .reset_index()
    )

    df_comments["sentiment"] = df_comments["comment"].apply(get_sentiment)

    print("df_comments:")
    print(df_comments)

    df = (
        pd.merge(df_ratings, df_likes, on=["user_id", "attraction_id"], how="outer")
        .merge(df_saved, on=["user_id", "attraction_id"], how="outer")
        .merge(df_done, on=["user_id", "attraction_id"], how="outer")
        .merge(df_comments, on=["user_id", "attraction_id"], how="outer")
    )

    df.fillna(0, inplace=True)

    df["score"] = (
        0.2 * df["is_liked"]
        + 0.1 * df["is_saved"]
        + 0.1 * df["is_done"]
        + 0.4 * df["rating"] / 5
        + 0.2 * df["sentiment"]
    )
    return df


def run_recommendation_system(db: Session):
    df = get_merged_df(db=db)
    print("df:")
    print(df)

    # Matriz usuarios-atracciones
    matrix = df.pivot(index="user_id", columns="attraction_id", values="score")

    # Se rellenan los nulos
    matrix = matrix.fillna(FILLNA_VALUE)
    print("\nMatriz:")
    print(matrix)

    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    dynamodb = session.resource("dynamodb", region_name="us-east-2")

    table_name = "recommendations"
    table = dynamodb.Table(table_name)

    user_similarity = cosine_similarity(matrix)

    print(user_similarity)

    for i, user_id in enumerate(matrix.index):

        if (
            crud.number_of_interactions_of_user(db=db, user_id=user_id)
            >= MINIMUM_NUMBER_OF_RATINGS
        ):

            print(f"Se calcula para {user_id}")

            # Se obtienen las posiciones de los usuarios más cercanos
            # Se agrega 1 al n porque se debe tener en cuenta que una siempre va a ser la propia atracción por tener similitud=1
            positions = n_greatest_positions(user_similarity[i], N_RECOMMENDATIONS + 1)
            print("\nPositions:")
            print(positions)

            # se filtra a la matriz dejando solamente a los usuarios cercanos
            filtered_matrix = matrix.iloc[positions]
            if user_id in filtered_matrix.index:
                filtered_matrix = filtered_matrix.drop(user_id, axis=0)

            print("\nMatriz filtrada:")
            print(filtered_matrix)

            recommendations = (
                filtered_matrix.mean().nlargest(N_RECOMMENDATIONS).index.tolist()
            )
            print("\nRecomendaciones:")
            print(recommendations)

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

    print("df:")
    print(df)

    # Matriz usuarios-atracciones
    matrix = df.pivot(index="user_id", columns="attraction_id", values="rating")

    # Se rellenan los nulos
    matrix = matrix.fillna(FILLNA_VALUE)
    print("\nMatriz:")
    print(matrix)

    user_similarity = cosine_similarity([matrix.loc[user_id]], matrix)

    print(user_similarity)

    # Se obtienen las posiciones de los usuarios más cercanos
    # Se agrega 1 al n porque se debe tener en cuenta que una siempre va a ser la propia atracción por tener similitud=1
    positions = n_greatest_positions(user_similarity, N_RECOMMENDATIONS + 1)
    print("\nPositions:")
    print(positions)

    # se filtra a la matriz dejando solamente a los usuarios cercanos
    filtered_matrix = matrix.iloc[positions]
    if user_id in filtered_matrix.index:
        filtered_matrix = filtered_matrix.drop(user_id, axis=0)

    print("\nMatriz filtrada:")
    print(filtered_matrix)

    recommendations = filtered_matrix.mean().nlargest(N_RECOMMENDATIONS).index.tolist()
    print("\nRecomendaciones:")
    print(recommendations)

    return recommendations
