"""
Simple in-memory user storage (без MongoDB для простоты)
"""
from flask_login import UserMixin
import bcrypt
from datetime import datetime

# In-memory хранилище пользователей (данные пропадут при перезапуске)
users_storage = {}


class User(UserMixin):
    """User model for authentication"""
    
    def __init__(self, user_data):
        self.id = user_data['id']
        self.email = user_data['email']
        self.username = user_data['username']
        self.created_at = user_data.get('created_at')
        self.role = user_data.get('role', 'user')
    
    @staticmethod
    def create_user(email, username, password):
        """Create new user"""
        # Проверяем, существует ли уже пользователь
        if email.lower() in users_storage:
            return None
            
        user_id = str(len(users_storage) + 1)
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_data = {
            'id': user_id,
            'email': email.lower(),
            'username': username,
            'password_hash': password_hash,
            'created_at': datetime.utcnow(),
            'role': 'user'
        }
        
        users_storage[email.lower()] = user_data
        print(f"✅ Created user: {username} ({email})")
        return User(user_data)
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        user_data = users_storage.get(email.lower())
        return User(user_data) if user_data else None
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        for user_data in users_storage.values():
            if user_data['id'] == user_id:
                return User(user_data)
        return None
    
    @staticmethod
    def verify_password(email, password):
        """Verify user password"""
        user_data = users_storage.get(email.lower())
        if not user_data:
            return None
        
        if bcrypt.checkpw(password.encode('utf-8'), user_data['password_hash']):
            return User(user_data)
        return None


# Создаем дефолтного админа при импорте модуля
def init_default_users():
    """Создаем тестовых пользователей"""
    if not users_storage:
        User.create_user('admin@stellartracker.com', 'Admin', 'admin123')
        User.create_user('demo@stellartracker.com', 'Demo User', 'demo123')
        print("=" * 60)
        print("📝 Тестовые пользователи созданы:")
        print("   Email: admin@stellartracker.com | Password: admin123")
        print("   Email: demo@stellartracker.com  | Password: demo123")
        print("=" * 60)

# Инициализируем при импорте
init_default_users()
