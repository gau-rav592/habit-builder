from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models.user_model import create_users_table, add_user, find_user_by_email
from datetime import timedelta
import os
from flask_cors import CORS

app = Flask(__name__)

FRONTEND_URL = os.ENVIRON.GET("FRONTEND_URL", "http://localhost:3000")

CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": [FRONTEND_URL],
        "allow_headers": ["Content-Type", "Authorization"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    }
})
bcrypt = Bcrypt(app)

# Secret key for JWT (move to env in production)
app.config['JWT_SECRET_KEY'] = "super-secret-key"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
jwt = JWTManager(app)

# Create users table on startup
create_users_table()

@app.route("/")
def home():
    return jsonify({"message": "Backend connected!"})

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"msg": "Email and password required"}), 400

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    try:
        add_user(email, password_hash)
        return jsonify({"msg": "Signup successful"})
    except Exception as e:
        # more specific handling is possible
        return jsonify({"msg": "Email already exists"}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"msg": "Email and password required"}), 400

    user = find_user_by_email(email)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    stored_hash = user[2]  # password column

    if bcrypt.check_password_hash(stored_hash, password):
        token = create_access_token(identity=email)
        return jsonify({"token": token})
    else:
        return jsonify({"msg": "Invalid password"}), 401

@app.route("/profile")
@jwt_required()
def profile():
    current_user = get_jwt_identity() #email stored as identity
    return jsonify({"msg": "You are authenticated!", "user": current_user})

if __name__ == "__main__":
    app.run(debug=True)
