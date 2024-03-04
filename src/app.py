"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Users, Characters, Planets, CharacterFavorites, PlanetFavorites


# Instancias de Flask
app = Flask(__name__)
app.url_map.strict_slashes = False
# Configuración de DB
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET', 'POST'])
def handle_users():
    response_body = {}
    # Metodo GET
    if request.method == 'GET':
        users = db.session.execute(db.select(Users)).scalars()
        response_body['results'] = [row.serialize() for row in users]
        response_body['message'] = 'Data retrieved successfully!'
        return response_body, 200
    # Metodo POST
    if request.method == 'POST':
        data = request.json
        user = Users(email=data['email'],
                     password=data['password'],
                     is_active=True)
        db.session.add(user)
        db.session.commit()
        response_body['message'] = 'User created successfully!'
        return response_body, 200
    else:
        return 'Method not found', 405


@app.route('/users/<int:id_user>', methods=['GET', 'PUT', 'DELETE'])
def handle_user(id_user):
    response_body = {}
    # Metodo GET
    if request.method == 'GET':
        user = db.session.execute(db.select(Users).where(Users.id == id_user)).scalar()
        response_body['results'] = user.serialize()
        response_body['message'] = 'Successful!'
        return response_body, 200
    # Metodo PUT
    if request.method == 'PUT':
        data = request.json
        user = Users(email=data['email'],
                     password=data['password'],
                     is_active=data['is_active'])
        db.session.add(user)
        db.session.commit()
        response_body['message'] = 'Successful!'
        return response_body, 200
    # Metodo DELETE
    if request.method == 'DELETE':
        user = db.session.execute(db.select(Users).where(Users.id == id_user)).scalar()
        db.session.delete(user)
        db.session.commit()
        response_body['message'] = 'Successful!'
        return response_body, 200
    else:
        return 'Method not found', 405


@app.route('/characters', methods=['GET'])
def handle_character():
    response_body = {}
    character = db.session.execute(db.select(Characters)).scalars()
    response_body['results'] = [row.serialize() for row in character]
    response_body['message'] = 'Data retrieved successfully!'
    return response_body, 200


@app.route('/characters/<int:id_character>', methods=['GET'])
def handle_character_id(id_character):
    response_body = {}
    character = db.session.execute(db.select(Characters).where(Characters.id == id_character)).scalar()
    response_body['results'] = character.serialize()
    response_body['message'] = 'Successful!'
    return response_body, 200


@app.route('/planets', methods=['GET'])
def handle_planets():
    response_body = {}
    planet = db.session.execute(db.select(Planets)).scalars()
    response_body['results'] = [row.serialize() for row in planet]
    response_body['message'] = 'Data retrieved successfully!'
    return response_body, 200


@app.route('/planets/<int:id_planet>', methods=['GET'])
def handle_planet_id(id_planet):
    response_body = {}
    planet = db.session.execute(db.select(Planets).where(Planets.id == id_planet)).scalar()
    response_body['results'] = planet.serialize()
    response_body['message'] = 'Successful!'
    return response_body, 200


@app.route('/users/<int:id_user>/favorites', methods=['GET'])
def handle_favorites(id_user):
    response_body = {}
    results = {}
    favorite_planets = db.session.execute(db.select(PlanetFavorites)).scalars()
    favorite_characters = db.session.execute(db.select(CharacterFavorites)).scalars()
    results['favorite_planets'] = [row.serialize() for row in favorite_planets]
    results['favorite_characters'] = [row.serialize() for row in favorite_characters]
    response_body['results'] = results
    response_body['message'] = 'Data retrieved successfully!'
    return response_body, 200


@app.route('/favorites/<int:id_user>/planet', methods=['POST'])
def handle_favorite_planet(id_user):
    response_body = {}
    data = request.json
    favorite = PlanetFavorites(user_id=id_user,
                               planet_id=data["planet_id"])
    db.session.add(favorite)
    db.session.commit()
    response_body['message'] = f'Planet {data["planet_id"]} added to favorites of {id_user}'
    return response_body, 200


@app.route('/favorites/<int:id_user>/character', methods=['POST'])
def handle_favorite_character(id_user):
    response_body = {}
    data = request.json
    favorite = CharacterFavorites(user_id=id_user,
                                  character_id=data["character_id"])
    db.session.add(favorite)
    db.session.commit()
    response_body['message'] = f'Character {data["character_id"]} added to favorites of {id_user}'
    return response_body, 200


@app.route('/favorites/<int:id_user>/planet/<int:id_planet>', methods=['DELETE'])
def handle_remove_favorite_planet(id_user, id_planet):
    response_body = {}
    planet = db.session.execute(db.select(PlanetFavorites).where(PlanetFavorites.user_id == id_user)).scalar()
    db.session.delete(planet)
    db.session.commit()
    response_body['message'] = f'Planet {id_planet} deleted from favorites of {id_user}'
    return response_body, 200


@app.route('/favorites/<int:id_user>/character/<int:id_character>', methods=['DELETE'])
def handle_remove_favorite_character(id_user, id_character):
    response_body = {}
    character = db.session.execute(db.select(CharacterFavorites).where(CharacterFavorites.user_id == id_user)).scalar()
    db.session.delete(character)
    db.session.commit()
    response_body['message'] = f'character {id_character} deleted from favorites of {id_user}'
    return response_body, 200


# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
