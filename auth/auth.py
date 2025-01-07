from flask import Blueprint, request, jsonify
from functools import wraps
from models import UserAccount, UserRole, session
import jwt
import datetime
from config import Config
from flask_cors import CORS  # Import CORS

# Create Blueprint for auth
auth_bp = Blueprint('auth', __name__)

# Enable CORS only for the login route
CORS(auth_bp, resources={r"/login": {"origins": "http://localhost:3000"}})

# Token verification decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]  # Extract token after Bearer
        else:
            return jsonify({"message": "Token is missing!"}), 403

        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            current_user = session.query(UserAccount).filter_by(id=data['user_id']).first()
        except Exception as e:
            return jsonify({"message": f"Token is invalid! {str(e)}"}), 403
        return f(current_user, *args, **kwargs)
    return decorated

# Role checking decorator
def role_required(*roles):  # Accept multiple roles as arguments
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            if current_user.user_role not in roles:  # Check if the user role is in the allowed roles
                return jsonify({"message": "Permission denied!"}), 403
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator

# Login route
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Retrieve the user by username
    user = session.query(UserAccount).filter_by(user_login=data.get('login')).first()

    # Check if user exists and if the provided password matches the stored password
    if user and user.password_hash == data.get('password'):
        # Generate JWT token
        token = jwt.encode(
            {
                'user_id': user.id,
                'login': user.user_login,  # Include username in the JWT token payload
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            },
            Config.SECRET_KEY,
            algorithm="HS256"
        )
        
        # Return token and username in response
        return jsonify({"token": token, "login": user.user_login, "user_role" : user.user_role})
    
    return jsonify({"message": "Invalid credentials!"}), 401

