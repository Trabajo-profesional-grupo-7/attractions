import os

import boto3
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from . import models

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


def run_recommendation_system(db: Session):
    df = pd.DataFrame(
        [row.__dict__ for row in (db.query(models.Ratings).all())],
        columns=["user_id", "attraction_id", "rating", "rated_at"],
    )
    print("df:")
    print(df)

    # Matriz usuarios-atracciones
    matrix = df.pivot(index="user_id", columns="attraction_id", values="rating")

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

        recomendations = (
            filtered_matrix.mean().nlargest(N_RECOMMENDATIONS).index.tolist()
        )
        print("\nRecomendaciones:")
        print(recomendations)

        item_data = {
            "user_id": user_id,
            "attraction_ids": recomendations,
        }

        table.put_item(Item=item_data)
