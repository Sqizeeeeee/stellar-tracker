"""
Командный интерфейс для управления пользователями StellarTracker
"""
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Переопределяем MONGO_URI для локального запуска
os.environ['MONGO_URI'] = 'mongodb://admin:stellartracker_mongo_admin_2024@localhost:27017/'

from web.database import User


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
    from web.database import users_collection
    
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


def clear_users():
    """Очистить всех пользователей"""
    from web.database import users_collection
    
    print("\n" + "="*60)
    print("⚠️  ВНИМАНИЕ: Удаление ВСЕХ пользователей!")
    print("="*60 + "\n")
    
    confirm = input("Вы уверены? Введите 'YES' для подтверждения: ")
    
    if confirm == 'YES':
        result = users_collection.delete_many({})
        print(f"\n✅ Удалено пользователей: {result.deleted_count}\n")
    else:
        print("\n❌ Отменено\n")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'create':
            create_user()
        elif command == 'list':
            list_users()
        elif command == 'clear':
            clear_users()
        else:
            print("Unknown command. Use: create, list or clear")
    else:
        print("Usage:")
        print("  python web/cli.py create   - Create new user")
        print("  python web/cli.py list     - List all users")
        print("  python web/cli.py clear    - Clear all users")