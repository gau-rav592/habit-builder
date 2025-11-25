import os
from datetime import timedelta
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from dotenv import load_dotenv

from models.user_model import db, User

load_dotenv()
app = Flask(__name__)

# Config from env
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///database.db"   # fallback for quick local dev
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY", "dev-secret")
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# CORS config
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": [FRONTEND_URL],
        "allow_headers": ["Content-Type", "Authorization"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    }
})

# Init extensions
db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# --- FIX FOR FLASK 3.x ---
# Create tables automatically
with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return jsonify({"message": "Backend connected!"})


# Signup Route
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"msg": "Email and password required"}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"msg": "Email already exists"}), 400

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(email=email, password=password_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "Signup successful"})


# Login Route
@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"msg": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    if bcrypt.check_password_hash(user.password, password):
        token = create_access_token(identity=email)
        return jsonify({"token": token})

    return jsonify({"msg": "Invalid password"}), 401


# Auth protected profile route
@app.route("/profile")
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    return jsonify({"msg": "You are authenticated", "user": current_user})


if __name__ == "__main__":
    app.run(debug=True)
