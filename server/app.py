#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify
from flask_restful import Api
import os

# Initialize Flask App
app = Flask(__name__)

# Configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False  # Makes JSON responses pretty

# Initialize Extensions
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

# Index Route
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# ------------------- CRUD for Restaurant -------------------

# GET /restaurants
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants])

# GET /restaurants/<int:id>
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant:
        return jsonify(restaurant.to_dict(include_relationships=True))
    else:
        return jsonify({"error": "Restaurant not found"}), 404

# POST /restaurants
@app.route('/restaurants', methods=['POST'])
def create_restaurant():
    data = request.get_json()
    try:
        name = data['name']
        address = data['address']
        if not name or not address:
            return jsonify({"errors": ["Name and address are required."]}), 400
        new_restaurant = Restaurant(name=name, address=address)
        db.session.add(new_restaurant)
        db.session.commit()
        return jsonify(new_restaurant.to_dict(only=('id', 'name', 'address'))), 201
    except KeyError as e:
        return jsonify({"errors": [f"Missing field: {e.args[0]}"]}), 400
    except Exception as e:
        return jsonify({"errors": ["Failed to create restaurant.", str(e)]}), 400

# PUT /restaurants/<int:id>
@app.route('/restaurants/<int:id>', methods=['PUT'])
def update_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant:
        data = request.get_json()
        try:
            name = data.get('name', restaurant.name)
            address = data.get('address', restaurant.address)
            if not name or not address:
                return jsonify({"errors": ["Name and address cannot be empty."]}), 400
            restaurant.name = name
            restaurant.address = address
            db.session.commit()
            return jsonify(restaurant.to_dict(only=('id', 'name', 'address')))
        except Exception as e:
            return jsonify({"errors": ["Failed to update restaurant.", str(e)]}), 400
    else:
        return jsonify({"error": "Restaurant not found"}), 404

# DELETE /restaurants/<int:id>
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant:
        try:
            db.session.delete(restaurant)
            db.session.commit()
            return '', 204
        except Exception as e:
            return jsonify({"errors": ["Failed to delete restaurant.", str(e)]}), 400
    else:
        return jsonify({"error": "Restaurant not found"}), 404

# ------------------- CRUD for Pizza -------------------

# GET /pizzas
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in pizzas])

# GET /pizzas/<int:id>
@app.route('/pizzas/<int:id>', methods=['GET'])
def get_pizza(id):
    pizza = db.session.get(Pizza, id)
    if pizza:
        return jsonify(pizza.to_dict(only=('id', 'name', 'ingredients')))
    else:
        return jsonify({"error": "Pizza not found"}), 404

# POST /pizzas
@app.route('/pizzas', methods=['POST'])
def create_pizza():
    data = request.get_json()
    try:
        name = data['name']
        ingredients = data['ingredients']
        if not name or not ingredients:
            return jsonify({"errors": ["Name and ingredients are required."]}), 400
        new_pizza = Pizza(name=name, ingredients=ingredients)
        db.session.add(new_pizza)
        db.session.commit()
        return jsonify(new_pizza.to_dict(only=('id', 'name', 'ingredients'))), 201
    except KeyError as e:
        return jsonify({"errors": [f"Missing field: {e.args[0]}"]}), 400
    except Exception as e:
        return jsonify({"errors": ["Failed to create pizza.", str(e)]}), 400

# PUT /pizzas/<int:id>
@app.route('/pizzas/<int:id>', methods=['PUT'])
def update_pizza(id):
    pizza = db.session.get(Pizza, id)
    if pizza:
        data = request.get_json()
        try:
            name = data.get('name', pizza.name)
            ingredients = data.get('ingredients', pizza.ingredients)
            if not name or not ingredients:
                return jsonify({"errors": ["Name and ingredients cannot be empty."]}), 400
            pizza.name = name
            pizza.ingredients = ingredients
            db.session.commit()
            return jsonify(pizza.to_dict(only=('id', 'name', 'ingredients')))
        except Exception as e:
            return jsonify({"errors": ["Failed to update pizza.", str(e)]}), 400
    else:
        return jsonify({"error": "Pizza not found"}), 404

# DELETE /pizzas/<int:id>
@app.route('/pizzas/<int:id>', methods=['DELETE'])
def delete_pizza(id):
    pizza = db.session.get(Pizza, id)
    if pizza:
        try:
            db.session.delete(pizza)
            db.session.commit()
            return '', 204
        except Exception as e:
            return jsonify({"errors": ["Failed to delete pizza.", str(e)]}), 400
    else:
        return jsonify({"error": "Pizza not found"}), 404

# ------------------- Create a RestaurantPizza -------------------

# POST /restaurant_pizzas
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    errors = []

    # Validate required fields
    required_fields = ['price', 'pizza_id', 'restaurant_id']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        errors.extend([f"Missing field: {field}" for field in missing_fields])
        return jsonify({"errors": errors}), 400

    # Extract fields
    price = data.get('price')
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')

    # Validate price
    if not isinstance(price, int):
        errors.append("Price must be an integer.")
    elif not (1 <= price <= 30):
        errors.append("Price must be between 1 and 30.")

    # Validate pizza_id
    pizza = db.session.get(Pizza, pizza_id)
    if not pizza:
        errors.append("Pizza not found.")

    # Validate restaurant_id
    restaurant = db.session.get(Restaurant, restaurant_id)
    if not restaurant:
        errors.append("Restaurant not found.")

    # If any validation errors, return them
    if errors:
       return jsonify({"errors": ["validation errors"]}), 400

    # Check if RestaurantPizza already exists for this pizza and restaurant
    existing_rp = RestaurantPizza.query.filter_by(pizza_id=pizza_id, restaurant_id=restaurant_id).first()
    if existing_rp:
        return jsonify({"errors": ["RestaurantPizza already exists for this pizza and restaurant."]}), 400

    # Create RestaurantPizza
    try:
        new_restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        return jsonify(new_restaurant_pizza.to_dict(include_relationships=True)), 201
    except ValueError as ve:
        return jsonify({"errors": [str(ve)]}), 400
    except Exception as e:
        return jsonify({"errors": ["Failed to create restaurant pizza.", str(e)]}), 400

if __name__ == "__main__":
    app.run(port=5555, debug=True)
