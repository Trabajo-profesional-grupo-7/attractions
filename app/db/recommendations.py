import os

import boto3
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from . import models

# Cantidad de atracciones que se quieren recomendar
N_RECOMMENDATIONS = 2

# Valor para rellenar a los nulos
# Un nulo sucede cuando un usuario no calificó una atracción
FILLNA_VALUE = 0


# Devuelve las posiciones de los n números más grandes dado un arreglo de números
# Ej: [8, 3, 2, 9, 7] con n=3 devuelve [3, 0, 4]
def n_greatest_positions(numbers, n):
    sorted_indices = sorted(range(len(numbers)), key=lambda i: numbers[i], reverse=True)
    return sorted_indices[:n]


def run_recommendation_system(db: Session):
    df = pd.DataFrame(
        [row.__dict__ for row in (db.query(models.Ratings).all())],
        columns=["user_id", "attraction_id", "rating", "rated_at"],
    )
    print("df:")
    print(df)

    # Matriz atracciones-usuarios
    matrix = df.pivot(index="attraction_id", columns="user_id", values="rating")

    # Se rellenan los nulos
    matrix = matrix.fillna(FILLNA_VALUE)
    print("\nMatriz:")
    print(matrix)

    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    dynamodb = session.resource("dynamodb", region_name="us-east-2")

    table_name = "attractions"
    table = dynamodb.Table(table_name)

    # Se realiza el cálculo para cada atracción
    for attraction_id in df["attraction_id"].unique():

        print(f"Se calcula para {attraction_id}")

        # Se calcula la similaridad coseno de la atracción con todas las otras atracciones
        # Se obtiene un vector con las similitudes cosenos
        user_similarity = cosine_similarity([matrix.loc[attraction_id]], matrix)[0]
        print("\nUser similarity:")
        print(user_similarity)

        # Se obtienen las posiciones de las atracciones más cercanas
        # Se agrega 1 al n porque se debe tener en cuenta que una siempre va a ser la propia atracción por tener similitud=1
        positions = n_greatest_positions(user_similarity, N_RECOMMENDATIONS + 1)
        print("\nPositions:")
        print(positions)

        # Se filtra a la matriz dejando solamente a los usuarios cercanos
        filtered_matrix = matrix.iloc[positions]
        if attraction_id in filtered_matrix.index:
            filtered_matrix = filtered_matrix.drop(attraction_id, axis=0)
        recomendations = filtered_matrix.index.tolist()
        print("\nRecomendaciones:")
        print(recomendations)

        item_data = {
            "attraction_id": attraction_id,
            "similar_attractions": recomendations,
        }

        table.put_item(Item=item_data)
