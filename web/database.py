"""
MongoDB database configuration and User model
"""
from pymongo import MongoClient
from flask_login import UserMixin
import bcrypt
from datetime import datetime

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['stellartracker']
users_collection = db['users']

# Create indexes
users_collection.create_index('email', unique=True)
users_collection.create_index('username', unique=True)


class User(UserMixin):
    """User model for authentication"""
    
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.email = user_data['email']
        self.username = user_data['username']
        self.created_at = user_data.get('created_at')
        self.role = user_data.get('role', 'user')
    
    @staticmethod
    def create_user(email, username, password):
        """Create new user in database"""
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_data = {
            'email': email.lower(),
            'username': username,
            'password_hash': password_hash,
            'created_at': datetime.utcnow(),
            'role': 'user'
        }
        
        try:
            result = users_collection.insert_one(user_data)
            user_data['_id'] = result.inserted_id
            return User(user_data)
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        user_data = users_collection.find_one({'email': email.lower()})
        return User(user_data) if user_data else None
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        from bson.objectid import ObjectId
        user_data = users_collection.find_one({'_id': ObjectId(user_id)})
        return User(user_data) if user_data else None
    
    @staticmethod
    def verify_password(email, password):
        """Verify user password"""
        user_data = users_collection.find_one({'email': email.lower()})
        if not user_data:
            return None
        
        if bcrypt.checkpw(password.encode('utf-8'), user_data['password_hash']):
            return User(user_data)
        return None
