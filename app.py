from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from db import db, db_init  # Assuming 'db' and 'db_init' are in a module named 'db'
from models import User  # Import the User model
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, get_jwt
from dotenv import load_dotenv
import os
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Set JWT secret key from environment variables
app.config["JWT_SECRET_KEY"] = os.getenv('KEY')

# Configure SQLAlchemy database URI
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///items.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db_init(app)

# Initialize JWT manager
jwt = JWTManager(app)

# Dictionary to store JTI to access token mapping
token_map = {}

# Home route to test the setup
@app.route('/')
def home():
    return jsonify(message="Hello world"), 200

# Register route to create a new user
@app.route('/register', methods=['POST'])
def register():
    # Get data from the form or JSON request body
    user_email = request.form.get('user_email')
    user_password = request.form.get('user_password')
    user_name = request.form.get('user_name')

    # Check if the email already exists
    test = User.query.filter_by(user_email=user_email).first()
    if test:
        return jsonify(message="Email already exists"), 409  # Conflict status code
    else:
        # Create a new user and add to the database
        new_user = User(user_name=user_name, user_email=user_email, user_password=user_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify(message="User successfully registered"), 200  # Success status code

# Login route to authenticate a user and generate an access token
@app.route('/login', methods=['POST'])
def login():
    user_email = request.form.get('user_email')
    user_password = request.form.get('user_password')
    
    # Query for user by email and password
    user = User.query.filter_by(user_email=user_email, user_password=user_password).first()
    
    if not user:
        return jsonify(message="Invalid user or password"), 401
    else:
        # Create the access token
        access_token = create_access_token(identity=user_email)
        
        # Extract the JTI from the access token
        decoded_token = jwt._decode_jwt_from_config(access_token)
        jti = decoded_token['jti']
        
        # Map JTI to the access token
        token_map[jti] = access_token
        
        return jsonify(access_token=access_token), 200

# Logout route to invalidate the user's token
@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # Get the current JWT identifier (jti)
    jti = get_jwt()['jti']
    print(f"Logging out user with JTI: {jti}")
    
    # Remove the JTI from the token map if it exists
    if jti in token_map:
        del token_map[jti]
        return jsonify(message="Successfully logged out"), 200
    else:
        return jsonify(message="Token not found"), 400

@app.route('/getusers2', methods=['GET'])
@jwt_required()
def get_users2():
    # Retrieve the current logged-in user identity (email)
    current_user = get_jwt_identity()
    
    # Query all users (you can filter or customize based on your logic)
    users = User.query.all()
    
    users_list = [{"id": user.user_id, "name": user.user_name, "email": user.user_email} for user in users]
    
    return jsonify(users=users_list), 200
# Running the Flask app
if __name__ == "__main__":
    app.run(debug=True)
