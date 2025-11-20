from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models.user_model import create_users_table, add_user, find_user_by_email

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Secret key for JWT (move to env in production)
app.config['JWT_SECRET_KEY'] = "super-secret-key"
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
    current_user = get_jwt_identity()
    return jsonify({"msg": "You are authenticated!", "user": current_user})

if __name__ == "__main__":
    app.run(debug=True)
