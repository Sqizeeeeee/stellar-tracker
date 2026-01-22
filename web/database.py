"""
MongoDB database models for StellarTracker
"""
from pymongo import MongoClient, ASCENDING, DESCENDING
from flask_login import UserMixin
import bcrypt
from datetime import datetime
import os
from prometheus_client import Counter, Histogram


# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongodb:27017/')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'stellartracker')

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

# Collections
users_collection = db.users
objects_collection = db.objects
observations_collection = db.observations
history_collection = db.processing_history


# Business метрики
OBJECTS_CREATED = Counter('objects_created_total', 'Total objects created')
OBSERVATIONS_SAVED = Counter('observations_saved_total', 'Total observations saved', ['object_name'])
DB_OPERATIONS = Counter('mongodb_operations_total', 'MongoDB operations', ['collection', 'operation'])
DB_OPERATION_DURATION = Histogram('mongodb_operation_duration_seconds', 'MongoDB operation duration', ['collection', 'operation'])


def init_db():
    """Initialize database with indexes"""
    # Users indexes
    users_collection.create_index([('email', ASCENDING)], unique=True)
    
    # Objects indexes
    objects_collection.create_index([('object_name', ASCENDING)], unique=True)
    objects_collection.create_index([('created_at', DESCENDING)])
    objects_collection.create_index([('risk.risk_level', ASCENDING)])
    
    # Observations indexes
    observations_collection.create_index([('object_name', ASCENDING)])
    observations_collection.create_index([('created_at', DESCENDING)])
    
    # History indexes
    history_collection.create_index([('created_at', DESCENDING)])
    history_collection.create_index([('object_name', ASCENDING)])
    
    print("✅ Database indexes created")


def serialize_mongo_object(obj):
    """Конвертировать MongoDB объект в JSON-совместимый формат"""
    if obj is None:
        return None
    
    if isinstance(obj, list):
        return [serialize_mongo_object(item) for item in obj]
    
    if isinstance(obj, dict):
        serialized = {}
        for key, value in obj.items():
            if key == '_id':
                serialized['id'] = str(value)
            elif isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, dict):
                serialized[key] = serialize_mongo_object(value)
            elif isinstance(value, list):
                serialized[key] = [serialize_mongo_object(item) for item in value]
            else:
                serialized[key] = value
        return serialized
    
    return obj


class User(UserMixin):
    """User model for authentication"""
    
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.email = user_data['email']
        self.username = user_data['username']
        self.created_at = user_data.get('created_at')
        self.last_login = user_data.get('last_login')
        self.role = user_data.get('role', 'user')
    
    @staticmethod
    def create_user(email, username, password):
        """Create new user"""
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_data = {
            'email': email.lower(),
            'username': username,
            'password_hash': password_hash,
            'created_at': datetime.utcnow(),
            'last_login': None,
            'role': 'user'
        }
        
        try:
            result = users_collection.insert_one(user_data)
            user_data['_id'] = result.inserted_id
            print(f"✅ Created user: {username} ({email})")
            return User(user_data)
        except Exception as e:
            print(f"❌ Error creating user: {e}")
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
        try:
            user_data = users_collection.find_one({'_id': ObjectId(user_id)})
            return User(user_data) if user_data else None
        except:
            return None
    
    @staticmethod
    def verify_password(email, password):
        """Verify user password"""
        user_data = users_collection.find_one({'email': email.lower()})
        if not user_data:
            return None
        
        if bcrypt.checkpw(password.encode('utf-8'), user_data['password_hash']):
            # Update last login
            users_collection.update_one(
                {'_id': user_data['_id']},
                {'$set': {'last_login': datetime.utcnow()}}
            )
            return User(user_data)
        return None


class AstroObject:
    """Модель астероида/объекта"""
    
    @staticmethod
    def create(object_name, orbit_data, risk_data, created_by_email):
        """Создать или обновить объект"""
        import time
        start_time = time.time()
        
        obj_data = {
            'object_name': object_name,
            'updated_at': datetime.utcnow(),
            'created_by': created_by_email,
            'orbit': orbit_data,
            'risk': risk_data
        }
        
        try:
            # Upsert - создать или обновить
            result = objects_collection.update_one(
                {'object_name': object_name},
                {
                    '$set': obj_data,
                    '$setOnInsert': {
                        'created_at': datetime.utcnow(),
                        'observations_count': 0
                    }
                },
                upsert=True
            )
            
            # ДОБАВЛЕНО: метрики
            duration = time.time() - start_time
            DB_OPERATIONS.labels(collection='objects', operation='upsert').inc()
            DB_OPERATION_DURATION.labels(collection='objects', operation='upsert').observe(duration)
            
            if result.upserted_id:
                OBJECTS_CREATED.inc()
            
            print(f"✅ Object saved: {object_name} (matched={result.matched_count}, modified={result.modified_count}, upserted={result.upserted_id is not None})")
            return obj_data
        except Exception as e:
            print(f"❌ Error saving object: {e}")
            return None
    
    @staticmethod
    def find_by_name(object_name):
        """Найти объект по имени"""
        return objects_collection.find_one({'object_name': object_name})
    
    @staticmethod
    def find_all(limit=100, risk_level=None):
        """Получить все объекты с фильтрацией"""
        query = {}
        if risk_level:
            query['risk.risk_level'] = risk_level
        
        return list(objects_collection.find(query).sort('created_at', DESCENDING).limit(limit))
    
    @staticmethod
    def increment_observations(object_name):
        """Увеличить счетчик наблюдений"""
        objects_collection.update_one(
            {'object_name': object_name},
            {'$inc': {'observations_count': 1}}
        )
    
    @staticmethod
    def get_stats():
        """Получить статистику по объектам"""
        pipeline = [
            {
                '$group': {
                    '_id': '$risk.risk_level',
                    'count': {'$sum': 1}
                }
            }
        ]
        risk_stats = list(objects_collection.aggregate(pipeline))
        
        # Преобразуем в удобный формат
        stats = {'low': 0, 'moderate': 0, 'high': 0, 'unknown': 0}
        for stat in risk_stats:
            level = stat['_id'] or 'unknown'
            stats[level] = stat['count']
        
        stats['total'] = objects_collection.count_documents({})
        return stats
    
    @staticmethod
    def get_high_risk(limit=10):
        """Получить объекты с высоким риском"""
        objects = list(objects_collection.find(
            {'risk.risk_level': 'high'}
        ).sort([('risk.moid_earth_au', ASCENDING)]).limit(limit))
        return [serialize_mongo_object(obj) for obj in objects]
    
    @staticmethod
    def get_recent(limit=10):
        """Получить последние объекты"""
        return list(objects_collection.find().sort('created_at', DESCENDING).limit(limit))
    
    @staticmethod
    def get_by_user(user_email, limit=10):
        """Получить объекты пользователя"""
        objects = list(objects_collection.find(
            {'created_by': user_email}
        ).sort('created_at', DESCENDING).limit(limit))
        return [serialize_mongo_object(obj) for obj in objects]
    
    @staticmethod
    def get_popular(limit=10):
        """Получить популярные объекты (по количеству наблюдений)"""
        objects = list(objects_collection.find().sort([
            ('observations_count', DESCENDING),
            ('created_at', DESCENDING)
        ]).limit(limit))
        return [serialize_mongo_object(obj) for obj in objects]


class Observation:
    """Модель наблюдения"""
    
    @staticmethod
    def create(object_name, obs_time, ra_deg, dec_deg, station, catalog, created_by_email):
        """Создать наблюдение"""
        import time
        start_time = time.time()
        
        obs_data = {
            'object_name': object_name,
            'obs_time': obs_time,
            'ra_deg': ra_deg,
            'dec_deg': dec_deg,
            'station': station,
            'catalog': catalog,
            'created_at': datetime.utcnow(),
            'created_by': created_by_email
        }
        
        try:
            result = observations_collection.insert_one(obs_data)
            AstroObject.increment_observations(object_name)
            
            
            duration = time.time() - start_time
            DB_OPERATIONS.labels(collection='observations', operation='insert').inc()
            DB_OPERATION_DURATION.labels(collection='observations', operation='insert').observe(duration)
            OBSERVATIONS_SAVED.labels(object_name=object_name).inc()
            
            print(f"✅ Observation saved for {object_name}")
            return obs_data
        except Exception as e:
            print(f"❌ Error saving observation: {e}")
            return None


class ProcessingHistory:
    """Модель истории обработки"""
    
    @staticmethod
    def create(request_id, object_name, status, error_message=None, processing_time=0, created_by_email=None):
        """Создать запись истории"""
        history_data = {
            'request_id': request_id,
            'object_name': object_name,
            'status': status,
            'error_message': error_message,
            'processing_time': processing_time,
            'created_at': datetime.utcnow(),
            'created_by': created_by_email
        }
        
        try:
            result = history_collection.insert_one(history_data)
            return history_data
        except Exception as e:
            print(f"❌ Error saving history: {e}")
            return None
    
    @staticmethod
    def find_recent(limit=50):
        """Получить последнюю историю"""
        return list(history_collection.find().sort('created_at', DESCENDING).limit(limit))
    
    @staticmethod
    def find_by_user(user_email, limit=50):
        """Получить историю пользователя"""
        return list(history_collection.find(
            {'created_by': user_email}
        ).sort('created_at', DESCENDING).limit(limit))
    
    @staticmethod
    def get_stats():
        """Получить статистику обработки"""
        total = history_collection.count_documents({})
        success = history_collection.count_documents({'status': 'success'})
        error = history_collection.count_documents({'status': 'error'})
        
        # Средняя скорость обработки
        pipeline = [
            {'$match': {'status': 'success'}},
            {'$group': {
                '_id': None,
                'avg_time': {'$avg': '$processing_time'}
            }}
        ]
        avg_result = list(history_collection.aggregate(pipeline))
        avg_time = avg_result[0]['avg_time'] if avg_result else 0
        
        return {
            'total': total,
            'success': success,
            'error': error,
            'success_rate': round(success / total * 100, 1) if total > 0 else 0,
            'avg_processing_time': round(avg_time, 2)
        }


# Initialize database on import
try:
    init_db()
except Exception as e:
    print(f"⚠️  Database initialization: {e}")
