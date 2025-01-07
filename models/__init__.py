from .models import Base, UserAccount, Event, Schedule, EventType, UserRole,Organization, FaceEncoding, Subscription  # Импорт моделей
from .models import engine, SessionLocal  # Импорт движка и сессии

# Создаем сессию для работы с БД
session = SessionLocal()