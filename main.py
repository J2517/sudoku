# Este servidor utiliza flask
# Este es el segundo servidor y se encarga de verificar que el dato recibido no se encuentre en el cuadrante correspondiente
# Para ello se necesitan 4 valores:
# 1. la estructura JSON sudoku.json
# 2. El valor a ubicar en el sudoku
# 3. La fila en la que se va a ubicar el valor (entre 0 y 9)
# 4. La columnaaumnaa en la que se va a ubicar el valor (entr 0 y 9)


from azure.communication.email import EmailClient
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import json


load_dotenv()

app = Flask(__name__)


def ObtenerFilasyColumnas(sudoku):
    filas = []
    for bloque in sudoku:
        for fila_index, fila in enumerate(bloque["columnas"]):
            fila_completa = [
                valor for subfila in fila for valor in subfila
            ]  # Aplana la fila
            filas.append(fila_completa)

    # Generar columnas a partir de las filas
    columnas = [
        [] for _ in range(9)
    ]  # Inicializa una lista de 9 listas vacías para las columnas
    for fila in filas:
        for i in range(9):
            columnas[i].append(fila[i])

    return filas, columnas


def validarNuevoValor(sudoku, nuevo_valor, fila, columna):
    # Obtener filas y columnas del sudoku
    filas, columnas = ObtenerFilasyColumnas(sudoku)

    # Validar fila
    if nuevo_valor in filas[fila]:
        return False

    # Validar columna
    if nuevo_valor in columnas[columna]:
        return False

    return True


def generarTabla(tablero):
    html = "<html><body>"
    for bloque in tablero:
        html += "-------------------------<br>"
        for fila in bloque["columnas"]:
            html += "| {} {} {} | {} {} {} | {} {} {} |<br>".format(
                *fila[0], *fila[1], *fila[2]
            )
        html += "-------------------------<br>"
    html += "</body></html>"
    return html


def enviarCorreo(sudoku):
    try:
        connection_string = os.environ.get("CONNECTION_STRING")
        if connection_string is None:
            return {
                "message": "La variable de entorno CONNECTION_STRING no está definida"
            }, 500

        client = EmailClient.from_connection_string(connection_string)

        message = {
            "senderAddress": os.environ.get("SENDER_ADDRESS"),
            "recipients": {
                "to": [
                    {"address": "jackria345@gmail.com"},
                    {"address": "juan.carmona29296@ucaldas.edu.co"},
                ],
            },
            "content": {
                "subject": "Tablero de Sudoku",
                "html": generarTabla(sudoku),
            },
        }

        poller = client.begin_send(message)
        result = poller.result()

        return {"message": "Correo enviado correctamente"}, 200
    except Exception as ex:
        return {"message": str(ex)}, 500

    if es_valido:
        enviarCorreo(data["tablero"])
        response = {"message": "Dato ubicado correctamente"}
        status_code = 200
    else:
        response = {"message": "El dato no puede ser ubicado, cambie de posición"}
        status_code = 400

    return jsonify(response), status_code


@app.route("/sudoku", methods=["POST"])
def ingresarValor():
    try:
        data = request.json
        tablero = data["tablero"]  # Obtener el tablero de la solicitud POST
        valor = data["valor"]
        fila = data["fila"] - 1
        columna = data["columna"] - 1

        seccion = fila // 3
        filaSeccion = fila % 3
        subfila = columna // 3
        subcolumna = columna % 3

        if not (0 <= fila <= 8 and 0 <= columna <= 8):
            return jsonify({"message": "Fila y columna deben estar entre 1 y 9"}), 400

        # Validar el nuevo valor en el sudoku
        es_valido = validarNuevoValor(tablero, valor, fila, columna)
        if es_valido:
            for i in range(3):
                for j in range(3):
                    if tablero[seccion]["columnas"][filaSeccion][i][j] == valor:
                        return False
                    if tablero[seccion]["columnas"][j][subfila][subcolumna] == valor:
                        return False
                    if tablero[seccion]["columnas"][i][j][subcolumna] == valor:
                        return False
                    if tablero[seccion]["columnas"][i][subfila][j] == valor:
                        return False

            tablero[seccion]["columnas"][filaSeccion][subfila][subcolumna] = valor
            enviarCorreo(tablero)
            return jsonify({"message": f"Dato ubicado correctamente"}), 200
        else:
            return (
                jsonify(
                    {"message": f"El dato no puede ser ubicado, cambie de posición"}
                ),
                400,
            )
    except Exception as ex:
        return jsonify({"message": str(ex)}), 500


if __name__ == "__main__":
    app.run(debug=True)
