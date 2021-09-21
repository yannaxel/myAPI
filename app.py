#importer Flask

from re import UNICODE
from flask import Flask, json, jsonify, abort, request
from flask.helpers import make_response, url_for

# from flaskext.mysql import MySQL
from flask_mysqldb import MySQL

app = Flask(__name__)

# APPEL DE MYSQL POUR L'utiliser
mysql = MySQL(app)

# configuration a la connection de mysql
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'sakila' #pour faire le lien avec notre base BEER

# route pour acceder et tester ma connection a la bdd
@app.route('/bdd',methods=['GET'])
def indexBdd():
    prenom = 'Micheline'
    nom = 'Jean-Jacques'
    #ouvrir la connection a ma bdd
    cur = mysql.connection.cursor()
    # quoi faire avec ma bdd
    cur.execute("INSERT INTO actor(first_name,last_name,last_update) VALUES (%s,%s,now())",(prenom,nom))
    # envoie de la requete
    mysql.connection.commit()
    # fermer ma connection
    cur.close()
    return "200"

# ****************************************************************************************************** 
# *********************************************** CREATE *********************************************** 
# ******************************************************************************************************

# route pour ajouter un actor dans la BDD
@app.route('/actors',methods=['POST'])
def create_actor():

    if not request.json and not "actor_id" in request.json:
        abort(400)
    try:
        # creer champ de ma nouvelle tache
        prenom = request.json['first_name']
        nom = request.json['last_name']
        print(prenom,nom)
        #creer ma connection et envoyer à ma bdd
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO actor (first_name,last_name,last_update) VALUES(%s,%s,now())",(prenom,nom))
        mysql.connection.commit()
        cur.close()
        return jsonify({'is':True})

    except Exception as e:
        print(e)
        return jsonify({'is':False})

# PAS FINIE !
# # route pour ajouter un film dans la BDD
# @app.route('/films',methods=['POST'])
# def create_film():

#     if not request.json and not "film_id" in request.json:
#         abort(400)
#     try:
#         # creer champ de ma nouvelle tache
#         titre = request.json['title']
#         description = request.json['description']
#         annee = request.json['release_year']
#         #creer ma connection et envoyer à ma bdd
#         cur = mysql.connection.cursor()
#         cur.execute("INSERT INTO film (title,description,release_year,language_id,original_language_id,rental_duration,rental_rate,length,replacement_cost,rating,special_features,last_update) VALUES(%s,%s,%s,NULL,NULL,NULL,NULL,NULL,NULL,NULL,now())",(titre,description,annee))
#         mysql.connection.commit()
#         cur.close()
#         return jsonify({'is':True})

#     except Exception as e:
#         print(e)
#         return jsonify({'is':False})

# ****************************************************************************************************** 
# ************************************************ READ ************************************************ 
# ****************************************************************************************************** 

# .............................................. actors ................................................

# route pour recuperer un acteur precis depuis la BDD
@app.route('/actors/<int:id_actor>', methods=['GET'])
def get_actor_by_id(id_actor):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM actor WHERE actor_id=%s"%(str(id_actor))) # cast en string pour pouvoir communiquer avec la BDD
        reponse = cur.fetchone()
        cur.close()
        return jsonify(make_public_actor(make_actor(reponse)))
    except Exception as e:
        print(e)
        abort(404)

# route pour recuperer la liste des acteurs de la BDD
@app.route('/actors', methods=['GET'])
def get_actors():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM actor")
        reponse = cur.fetchall() #return des tuples puisque ca vient de la BDD
        cur.close()
        actors=[]
        for elem in reponse:
            made_elem = make_actor(elem) # ==> convert tuple to list
            actors.append(made_elem)
        return jsonify([make_public_actor(x) for x in actors])
    except Exception as e:
        print(e)
        abort(404)

# ............................................... film .................................................

# route pour recuperer un film precis depuis la BDD
@app.route('/films/<int:id_film>', methods=['GET'])
def get_film_by_id(id_film):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM film WHERE film_id=%s"%(str(id_film))) # cast en string pour pouvoir communiquer avec la BDD
        reponse = cur.fetchone()
        cur.close()
        return jsonify(make_public_film(make_film(reponse)))
    except Exception as e:
        print(e)
        abort(404)

# route pour recuperer la liste des films de la BDD
@app.route('/films', methods=['GET'])
def get_films():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM film")
        reponse = cur.fetchall() #return des tuples puisque ca vient de la BDD
        cur.close()
        films=[]
        for elem in reponse:
            made_elem = make_film(elem) # ==> convert tuple to list
            films.append(made_elem)
        return jsonify([make_public_film(x) for x in films])
    except Exception as e:
        print(e)
        abort(404)

# ****************************************************************************************************** 
# *********************************************** UPDATE *********************************************** 
# ****************************************************************************************************** 

# route pour modifier un acteur particulier de ma liste dans la BDD
@app.route('/actors/<int:id_actor>',methods=['PUT'])
def update_actor(id_actor):
    actor = get_actor_by_id(id_actor)

    # verif
    if not request.json:
        abort(400)
    if not "first_name" in request.json and type(request.json['first_name']) is not str:
        abort(400)
    if not "last_name" in request.json and type(request.json['last_name']) is not str: 
        abort(400)
    try:
        prenom = request.json.get('first_name', actor.json['first_name'])
        nom = request.json.get('last_name', actor.json['last_name'])
        # connecter la base 
        cur = mysql.connection.cursor()
        cur.execute("UPDATE actor SET first_name=%s, last_name=%s, last_update=now() WHERE actor_id=%s",
                    (prenom, nom, str(id_actor)))

        # on ferme la connexion
        mysql.connection.commit()
        cur.close()
        return get_actor_by_id(id_actor)

    except Exception as e:
        print(e)
        return jsonify({'is':False}), 400

# ****************************************************************************************************** 
# *********************************************** DELETE *********************************************** 
# ****************************************************************************************************** 

# .............................................. actors ................................................

# route pour supprimer un acteur de ma BDD
@app.route('/actors/<int:id_actor>',methods=['DELETE'])
def delete_actor(id_actor):
    actor_a_supprimer = get_actor_by_id(id_actor)
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM actor WHERE actor_id=%s", (str(id_actor),))
        mysql.connection.commit()
        cur.close()
        return actor_a_supprimer
    except Exception as e:
        print(e)
        return jsonify({'is': False})

# ............................................... film .................................................

# route pour supprimer un film de ma BDD
@app.route('/films/<int:id_film>',methods=['DELETE'])
def delete_film(id_film):
    film_a_supprimer = get_film_by_id(id_film)
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM film WHERE film_id=%s", (str(id_film),))
        mysql.connection.commit()
        cur.close()
        return film_a_supprimer
    except Exception as e:
        print(e)
        return jsonify({'is': False})

# ****************************************************************************************************** 

# annotations app.route('URL')
@app.route('/')
def index():
    return "Welcome to Sakila"

# ****************************************************************************************************** 

# .............................................. actors ................................................

# fonction pour creer une url de façon dynamique à partir d'un acteur
def make_public_actor(actor):
    public_actor = {}
    for argument in actor:
        if argument == "actor_id":
            public_actor['url'] = url_for("get_actor_by_id",id_actor=actor['actor_id'], _external=True)
        else:
            public_actor[argument] = actor[argument]
    return public_actor

# fonction pour generer un acteur a partir d'un acteur de la BDD
def make_actor(actor_bdd):
    # ordre des columns de la BDD
    list_actor = list(actor_bdd)
    
    # stockage dans un dictionnaire reprenant les clefs de la table comme dans la BDD
    new_actor = {}
    new_actor['actor_id'] = int(list_actor[0])
    new_actor['first_name'] = str(list_actor[1])
    new_actor['last_name'] = str(list_actor[2])
    new_actor['last_update'] = str(list_actor[3])

    return new_actor

# ............................................... film .................................................

# fonction pour creer une url de façon dynamique à partir d'un film
def make_public_film(film):
    public_film = {}
    for argument in film:
        if argument == "actor_id":
            public_film['url'] = url_for("get_film_by_id",id_actor=film['film_id'], _external=True)
        else:
            public_film[argument] = film[argument]
    return public_film

# fonction pour generer un film a partir d'un film de la BDD
def make_film(film_bdd):
    # ordre des columns de la BDD
    list_film = list(film_bdd)
    
    # stockage dans un dictionnaire reprenant les clefs de la table comme dans la BDD
    new_film = {}
    new_film['film_id'] = int(list_film[0])
    new_film['title'] = str(list_film[1])
    new_film['description'] = str(list_film[2])
    new_film['release_year'] = str(list_film[3])

    return new_film

# lancer mon application
if __name__ == 'main':
    app.run(debug=True)
