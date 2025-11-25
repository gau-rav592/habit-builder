from app import app
from models.user_model import db

with app.app_context():
    db.create_all()
    print("Tables created")