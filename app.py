from flask import Flask, render_template, request, redirect, url_for

import pymongo
import os

app = Flask(__name__)
client = pymongo.MongoClient("mongodb://mongodb:27017")

db = client["gamedb"]           #base de datos
games_collection = db["games"]  #tabla

initial_games = [
    {"id": 1, "nombre": "Pocahontas", "cantidad_jugadores": 4, "limite_edades": 10, "pais_origen": "USA", "costo": 50.0},
    {"id": 2, "nombre": "Kiko: The South Zone", "cantidad_jugadores": 2, "limite_edades": 1, "pais_origen": "Canada", "costo": 30.0}
]

# inicializa la base de datos si la coleccion está vacia
if games_collection.count_documents({}) == 0:
    games_collection.insert_many(initial_games)


#------------------------------------------INICIO-----------------------------------------------#

@app.route('/')
def inicio():
    return render_template('inicio.html', title='GameStore')


#-----------------------------------------CATALOGO----------------------------------------------#
@app.route('/catalogo')
def catalogo():
    # obtiene parametro de busqueda
    query = request.args.get("q", "").strip().lower()

    if query:
        games = list(games_collection.find({"nombre": {"$regex": query, "$options": "i"}}))     #busca en la coleccion ignorando mayus y minus
    else:
        games = list(games_collection.find())

    return render_template('catalogo.html', title='Catálogo de Juegos', games=games, query=query)

#----------------------------------------MODIFICAR---------------------------------------------#

@app.route('/modificar/<int:game_id>', methods=['GET'])
def modificar(game_id):

    game=games_collection.find_one({"id":game_id})
    if not game:
        return "Juego no encontrado", 404

    return render_template('modificar.html', title='Modificar Juego', game=game)

@app.route('/modificar/<int:game_id>', methods=['POST'])
def actualizar_juego(game_id):

    # obtiene los datos del formulario
    nombre = request.form['nombre']
    cantidad_jugadores = request.form['cantidad_jugadores']
    limite_edades = request.form['limite_edades']
    pais_origen = request.form['pais_origen']
    costo = float(request.form['costo'])

    # actualiza la base de datos
    games_collection.update_one(
        {"id": game_id},
        {"$set": {
            "nombre": nombre,
            "cantidad_jugadores": cantidad_jugadores,
            "limite_edades": limite_edades,
            "pais_origen": pais_origen,
            "costo": costo
        }}
    )
    return redirect(url_for('catalogo'))

#-----------------------------------------DETALLES---------------------------------------------#

@app.route('/detalles/<int:game_id>')
def detalles(game_id):

    game = games_collection.find_one({"id": game_id})

    if not game:
        return "Juego no encontrado", 404

    return render_template('detalles.html', title='Detalles del Juego', game=game)


#------------------------------------------AÑADIR----------------------------------------------#

@app.route('/añadir', methods=['GET', 'POST'])
def añadir():
    if request.method == 'POST':
        try:
            # obtiene los datos del formulario
            nombre = request.form['nombre']
            cantidad_jugadores = request.form['cantidad_jugadores']
            limite_edades = request.form['limite_edades']
            pais_origen = request.form['pais_origen']
            costo = float(request.form['costo'])

            # obtiene el ID mas alto y le suma 1
            ultimo_juego = games_collection.find_one(sort=[("id", -1)])
            nuevo_id = (ultimo_juego["id"] + 1) if ultimo_juego else 1

            # insertar en la base de datos
            nuevo_juego = {
                "id": nuevo_id,
                "nombre": nombre,
                "cantidad_jugadores": cantidad_jugadores,
                "limite_edades": limite_edades,
                "pais_origen": pais_origen,
                "costo": costo
            }
            games_collection.insert_one(nuevo_juego)

            return redirect(url_for('catalogo'))
        except Exception as e:
            print(f"Error al añadir juego: {e}")
            return "Error al añadir juego", 500

    return render_template('add.html', title='Añadir Juegos')


#----------------------------------------ELIMINAR----------------------------------------------#

@app.route('/eliminar/<int:game_id>', methods=['POST'])
def eliminar_juego(game_id):
    # busca y elimina el juego por su ID
    resultado = games_collection.delete_one({"id": game_id})

    if resultado.deleted_count == 0:
        return "Juego no encontrado", 404

    return redirect(url_for('catalogo'))

if __name__ == '__main__':
    app.run(debug=True)
