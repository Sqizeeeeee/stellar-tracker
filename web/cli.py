"""
Командный интерфейс для управления пользователями StellarTracker
"""

import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Переопределяем MONGO_URI для локального запуска
os.environ['MONGO_URI'] = 'mongodb://admin:stellartracker_mongo_admin_2024@localhost:27017/'

from database import User, objects_collection, observations_collection, history_collection, db, client


def create_user():
    """Создать нового пользователя"""
    email = input("Введите email: ")
    username = input("Введите имя пользователя: ")
    password = input("Введите пароль: ")
    
    user = User.create_user(email, username, password)
    if user:
        print(f"✅ Пользователь создан: {username} ({email})")
    else:
        print("❌ Ошибка при создании пользователя")


def list_users():
    """Список всех пользователей"""
    from database import users_collection
    
    print("\n" + "="*60)
    print("👥 Список пользователей")
    print("="*60 + "\n")
    
    users = users_collection.find()
    for user in users:
        print(f"📧 {user['email']}")
        print(f"   Username: {user['username']}")
        print(f"   Role: {user.get('role', 'user')}")
        print(f"   Created: {user.get('created_at', 'N/A')}")
        print()


def list_objects():
    """Список всех отслеживаемых объектов"""
    print("\n" + "="*60)
    print("🌌 Список отслеживаемых объектов")
    print("="*60 + "\n")
    
    total = objects_collection.count_documents({})
    print(f"Всего объектов: {total}\n")
    
    if total == 0:
        print("❌ База данных пуста! Объекты не были добавлены.\n")
        return
    
    objects = objects_collection.find().sort('created_at', -1)
    
    for obj in objects:
        print(f"🎯 {obj['object_name']}")
        print(f"   Created by: {obj.get('created_by', 'unknown')}")
        print(f"   Created at: {obj.get('created_at', 'N/A')}")
        print(f"   Observations: {obj.get('observations_count', 0)}")
        
        if 'risk' in obj:
            risk = obj['risk']
            print(f"   Risk Level: {risk.get('risk_level', 'unknown')}")
            print(f"   MOID: {risk.get('moid_earth_au', 'N/A')} AU")
        
        if 'orbit' in obj:
            orbit = obj['orbit']
            print(f"   Orbit: a={orbit.get('a_au', 'N/A')} AU, e={orbit.get('e', 'N/A')}")
        
        print()


def list_observations():
    """Список всех наблюдений"""
    print("\n" + "="*60)
    print("📡 Список наблюдений")
    print("="*60 + "\n")
    
    total = observations_collection.count_documents({})
    print(f"Всего наблюдений: {total}\n")
    
    if total == 0:
        print("❌ Наблюдения не найдены!\n")
        return
    
    # Группируем по объектам
    pipeline = [
        {
            '$group': {
                '_id': '$object_name',
                'count': {'$sum': 1},
                'created_by': {'$first': '$created_by'}
            }
        },
        {'$sort': {'count': -1}}
    ]
    
    grouped = list(observations_collection.aggregate(pipeline))
    
    for group in grouped:
        print(f"🎯 {group['_id']}: {group['count']} observations (by {group.get('created_by', 'unknown')})")


def list_history():
    """Список истории обработки"""
    print("\n" + "="*60)
    print("📜 История обработки")
    print("="*60 + "\n")
    
    total = history_collection.count_documents({})
    success = history_collection.count_documents({'status': 'success'})
    error = history_collection.count_documents({'status': 'error'})
    
    print(f"Всего запросов: {total}")
    print(f"Успешных: {success}")
    print(f"Ошибок: {error}\n")
    
    if total == 0:
        print("❌ История пуста!\n")
        return
    
    recent = history_collection.find().sort('created_at', -1).limit(10)
    
    print("Последние 10 запросов:\n")
    for entry in recent:
        status_icon = "✅" if entry['status'] == 'success' else "❌"
        print(f"{status_icon} {entry.get('object_name', 'unknown')}")
        print(f"   Request ID: {entry.get('request_id', 'N/A')}")
        print(f"   Status: {entry['status']}")
        print(f"   Time: {entry.get('processing_time', 0):.2f}s")
        print(f"   Created by: {entry.get('created_by', 'unknown')}")
        if entry.get('error_message'):
            print(f"   Error: {entry['error_message']}")
        print()


def show_db_info():
    """Показать информацию о базе данных"""
    print("\n" + "="*60)
    print("💾 Информация о базе данных")
    print("="*60 + "\n")
    
    # Список всех коллекций
    collections = db.list_collection_names()
    print(f"📊 Коллекции в базе данных '{db.name}':\n")
    
    if not collections:
        print("❌ Нет коллекций!\n")
        return
    
    for coll_name in collections:
        coll = db[coll_name]
        count = coll.count_documents({})
        
        # Получаем размер коллекции
        stats = db.command("collStats", coll_name)
        size_mb = stats.get('size', 0) / (1024 * 1024)
        
        print(f"📁 {coll_name}")
        print(f"   Documents: {count}")
        print(f"   Size: {size_mb:.2f} MB")
        
        # Показываем индексы
        indexes = coll.list_indexes()
        index_names = [idx['name'] for idx in indexes]
        print(f"   Indexes: {', '.join(index_names)}")
        print()
    
    # Общая статистика
    db_stats = db.command("dbStats")
    print("\n📈 Общая статистика:")
    print(f"   Total size: {db_stats.get('dataSize', 0) / (1024 * 1024):.2f} MB")
    print(f"   Collections: {db_stats.get('collections', 0)}")
    print(f"   Objects: {db_stats.get('objects', 0)}\n")


def test_connection():
    """Проверить подключение к MongoDB"""
    print("\n" + "="*60)
    print("🔌 Проверка подключения к MongoDB")
    print("="*60 + "\n")
    
    try:
        # Проверяем подключение
        client.admin.command('ping')
        print("✅ Подключение к MongoDB успешно!\n")
        
        # Информация о сервере
        server_info = client.server_info()
        print(f"MongoDB версия: {server_info.get('version', 'unknown')}")
        print(f"База данных: {db.name}")
        print(f"URI: {os.getenv('MONGO_URI', 'mongodb://mongodb:27017/')}\n")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к MongoDB: {e}\n")
        return False


def clear_users():
    """Очистить всех пользователей"""
    from database import users_collection
    
    print("\n" + "="*60)
    print("⚠️  ВНИМАНИЕ: Удаление ВСЕХ пользователей!")
    print("="*60 + "\n")
    
    confirm = input("Вы уверены? Введите 'YES' для подтверждения: ")
    
    if confirm == 'YES':
        result = users_collection.delete_many({})
        print(f"\n✅ Удалено пользователей: {result.deleted_count}\n")
    else:
        print("\n❌ Отменено\n")


def clear_all_data():
    """Очистить ВСЕ данные (пользователи, объекты, наблюдения, история)"""
    from database import users_collection
    
    print("\n" + "="*60)
    print("⚠️⚠️⚠️  ВНИМАНИЕ: Удаление ВСЕХ данных из БД!")
    print("="*60 + "\n")
    
    confirm = input("Вы уверены? Введите 'DELETE ALL' для подтверждения: ")
    
    if confirm == 'DELETE ALL':
        users_del = users_collection.delete_many({})
        objects_del = objects_collection.delete_many({})
        obs_del = observations_collection.delete_many({})
        hist_del = history_collection.delete_many({})
        
        print("\n✅ Удалено:")
        print(f"   Пользователей: {users_del.deleted_count}")
        print(f"   Объектов: {objects_del.deleted_count}")
        print(f"   Наблюдений: {obs_del.deleted_count}")
        print(f"   История: {hist_del.deleted_count}\n")
    else:
        print("\n❌ Отменено\n")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'create':
            create_user()
        elif command == 'list':
            list_users()
        elif command == 'objects':
            list_objects()
        elif command == 'observations':
            list_observations()
        elif command == 'history':
            list_history()
        elif command == 'db':
            show_db_info()
        elif command == 'test':
            test_connection()
        elif command == 'clear':
            clear_users()
        elif command == 'clear-all':
            clear_all_data()
        else:
            print("Unknown command")
            print("\nUsage:")
            print("  python web/cli.py create        - Create new user")
            print("  python web/cli.py list          - List all users")
            print("  python web/cli.py objects       - List all tracked objects")
            print("  python web/cli.py observations  - List all observations")
            print("  python web/cli.py history       - Show processing history")
            print("  python web/cli.py db            - Show database info")
            print("  python web/cli.py test          - Test MongoDB connection")
            print("  python web/cli.py clear         - Clear all users")
            print("  python web/cli.py clear-all     - Clear ALL data (dangerous!)")
    else:
        print("Usage:")
        print("  python web/cli.py create        - Create new user")
        print("  python web/cli.py list          - List all users")
        print("  python web/cli.py objects       - List all tracked objects")
        print("  python web/cli.py observations  - List all observations")
        print("  python web/cli.py history       - Show processing history")
        print("  python web/cli.py db            - Show database info")
        print("  python web/cli.py test          - Test MongoDB connection")
        print("  python web/cli.py clear         - Clear all users")
        print("  python web/cli.py clear-all     - Clear ALL data (dangerous!)")