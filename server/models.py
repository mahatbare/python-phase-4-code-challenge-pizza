from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    restaurant_pizzas = db.relationship(
        'RestaurantPizza',
        backref='restaurant',
        cascade='all, delete-orphan',
        lazy=True
    )

    def to_dict(self, include_relationships=False, only=None, exclude=None):
        data = {
            "id": self.id,
            "name": self.name,
            "address": self.address
        }
        if include_relationships:
            data["restaurant_pizzas"] = [
                rp.to_dict(include_relationships=True) for rp in self.restaurant_pizzas
            ]
        return data

class Pizza(db.Model):
    __tablename__ = 'pizzas'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)
    restaurant_pizzas = db.relationship(
        'RestaurantPizza',
        backref='pizza',
        cascade='all, delete-orphan',
        lazy=True
    )

    def to_dict(self, include_relationships=False, only=None, exclude=None):
        data = {
            "id": self.id,
            "name": self.name,
            "ingredients": self.ingredients
        }
        if include_relationships:
            data["restaurant_pizzas"] = [
                rp.to_dict(include_relationships=True) for rp in self.restaurant_pizzas
            ]
        return data

class RestaurantPizza(db.Model):
    __tablename__ = 'restaurant_pizzas'
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    def __init__(self, price, pizza_id, restaurant_id):
        if not isinstance(price, int):
            raise ValueError("Price must be an integer.")
        if not (1 <= price <= 30):
            raise ValueError("Price must be between 1 and 30.")
        self.price = price
        self.pizza_id = pizza_id
        self.restaurant_id = restaurant_id

    def to_dict(self, include_relationships=False, only=None, exclude=None):
        data = {
            "id": self.id,
            "price": self.price,
            "pizza_id": self.pizza_id,
            "restaurant_id": self.restaurant_id
        }
        if include_relationships:
            data["pizza"] = self.pizza.to_dict(only=('id', 'name', 'ingredients'))
            data["restaurant"] = self.restaurant.to_dict(only=('id', 'name', 'address'))
        return data

