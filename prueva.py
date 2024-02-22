from azure.communication.email import EmailClient
import os
from dotenv import load_dotenv
import json

load_dotenv()

def generar_tabla_html(tablero):
    html = "<html><body>"
    for bloque in tablero:
        html += "-------------------------<br>"
        for fila in bloque["columnas"]:
            html += "| {} {} {} | {} {} {} | {} {} {} |<br>".format(*fila[0], *fila[1], *fila[2])
        html += "-------------------------<br>"
    html += "</body></html>"
    return html

def enviarCorreo(sudoku):
    try:
        connection_string = os.environ.get("CONNECTION_STRING")
        if connection_string is None:
            return {"message": "La variable de entorno CONNECTION_STRING no está definida"}, 500

        client = EmailClient.from_connection_string(connection_string)

        message = {
            "senderAddress": os.environ.get("SENDER_ADDRESS"),
            "recipients": {
                "to": [{"address": "juan.carmona29296@ucaldas.edu.co"}],
            },
            "content": {
                "subject": "Tablero de Sudoku",
                "html": generar_tabla_html(sudoku["tablero"]),
            },
        }

        poller = client.begin_send(message)
        result = poller.result()

        return {"message": "Correo enviado correctamente"}, 200
    except Exception as ex:
        return {"message": str(ex)}, 500

# Datos de ejemplo
sudoku_ejemplo = {
    "tablero": [
        {
            "fila": 0,
            "columnas": [
                [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
            ]
        },
        {
            "fila": 1,
            "columnas": [
                [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
            ]
        },
        {
            "fila": 2,
            "columnas": [
                [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
            ]
        }
    ],
    "fila": 0,
    "columna": 0,
    "nuevo_valor": 1
}

# Prueba de la función enviarCorreo con datos de ejemplo
resultado, status_code = enviarCorreo(sudoku_ejemplo)
print(resultado, status_code)


