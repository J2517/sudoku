# Este servidor utiliza flask
# Este es el segundo servidor y se encarga de verificar que el dato recibido no se encuentre en el cuadrante correspondiente
# Para ello se necesitan 4 valores:
# 1. la estructura JSON sudoku.json
# 2. El valor a ubicar en el tablero
# 3. La fila en la que se va a ubicar el valor (entre 0 y 9)
# 4. La columnaaumnaa en la que se va a ubicar el valor (entr 0 y 9)


from azure.communication.email import EmailClient
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import json


load_dotenv()

app = Flask(__name__)


def cargarTablero():
    with open("sudoku.json") as file:
        return json.load(file)


def guardarTablero(sudoku):
    with open("sudoku.json", "w") as file:
        json.dump(sudoku, file)


sudoku = cargarTablero()


# Verificar cuadrante
def cuadrante(valor, fila, columna):
    # Calcula la sección, fila y columna de la submatriz
    seccion = (
        fila // 3
    )  # el resultado de la división entera indica "fila": en el archivo json
    filaSeccion = (
        fila % 3
    )  # el residuo de la división entera indica "subfila": en el archivo json
    subfila = columna // 3  #
    subcolumna = columna % 3

    for i in range(3):
        for j in range(3):
            if sudoku[seccion]["columnas"][filaSeccion][i][j] == valor:
                return False
            if sudoku[seccion]["columnas"][j][subfila][subcolumna] == valor:
                return False
            if sudoku[seccion]["columnas"][i][j][subcolumna] == valor:
                return False
            if sudoku[seccion]["columnas"][i][subfila][j] == valor:
                return False
    return True


# Esta función envía un correo con el json de sudoku
def enviarCorreo(sudoku):
    try:
        connection_string = os.environ.get("CONNECTION_STRING")
        client = EmailClient.from_connection_string(connection_string)

        message = {
            "senderAddress": os.environ.get("SENDER_ADDRESS"),
            "recipients": {
                "to": [{"address": "jackria345@gmail.com"}],
            },
            "content": {
                "subject": "Correo electrónico de prueba",
                "plainText": json.dumps(sudoku),
                # "html": f"<table id=\"sudokuTable\"></table>\n<script>\nfetch('sudoku.json')\n.then(response => response.json()\n.then(data => {{\nconst sudokuTable = document.getElementById('sudokuTable');\ndata.forEach(row => {{\nconst newRow = document.createElement('tr');\nrow.columnas.forEach(subgrid => {{\nconst subgridCell = document.createElement('td');\nconst subgridTable = document.createElement('table');\nsubgrid.forEach(subrow => {{\nconst subrowElement = document.createElement('tr');\nsubrow.forEach(cell => {{\nconst cellElement = document.createElement('td');\ncellElement.textContent = cell;\nsubrowElement.appendChild(cellElement);\n}});\nsubgridTable.appendChild(subrowElement);\n}});\nsubgridCell.appendChild(subgridTable);\nnewRow.appendChild(subgridCell);\n}});\nsudokuTable.appendChild(newRow);\n}});\n}})\n</script><table></table>",
            },
        }
        poller = client.begin_send(message)
        result = poller.result()
        return jsonify({"message": "Correo enviado correctamente"}), 200
    except Exception as ex:
        return jsonify({"message": str(ex)})


@app.route("/sudoku", methods=["GET"])
def mostrarSudoku():
    return jsonify(sudoku)


@app.route("/sudoku", methods=["POST"])
def ingresarValor():
    try:
        data = request.json
        valor = data["valor"]
        fila = data["fila"] - 1
        columna = data["columna"] - 1

        seccion = fila // 3
        filaSeccion = fila % 3
        subfila = columna // 3
        subcolumna = columna % 3

        if not (0 <= fila <= 8 and 0 <= columna <= 8):
            return jsonify({"message": "Fila y columna deben estar entre 1 y 9"}), 400

        if cuadrante(valor, fila, columna):
            sudoku[seccion]["columnas"][filaSeccion][subfila][subcolumna] = valor
            guardarTablero(sudoku)
            enviarCorreo(sudoku)
            return jsonify({"message": f"Dato ubicado correctamente"}), 200
        else:
            return (
                jsonify(
                    {"message": f"El dato no puede ser ubicado, cambie de posición"}
                ),
                400,
            )
    except Exception as ex:
        # return jsonify({"message": str(ex)})
        return jsonify({"message": "Ocurrió un error al procesar la solicitud"}), 500


if __name__ == "__main__":
    app.run(debug=True)
