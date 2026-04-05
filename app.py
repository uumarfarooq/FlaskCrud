from flask import Flask, request, jsonify
from models import db, User
from config import config
from routes import register_routes
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)
mail = Mail(app)

with app.app_context():
    db.create_all()

register_routes(app, mail)

if __name__ == '__main__': 
    app.run(debug=True)