from models import UserAccount, UserRole, SessionLocal

# Создание сессии
session = SessionLocal()

# Создание пользователя с ролью OWNER
new_user = UserAccount(
    user_name="owner_user",  # Уникальное имя пользователя
    user_role=UserRole.OWNER,  # Назначаем роль OWNER
    password="owner_password"  # Задаем пароль
)

# Добавляем нового пользователя в базу данных
session.add(new_user)
session.commit()

print(f"Создан новый пользователь с именем: {new_user.user_name}, ролью: {new_user.user_role}")
