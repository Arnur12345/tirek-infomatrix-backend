from models import Base  # Добавляем ваши модели

def run_migrations_online():
    ...
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=Base.metadata  # Указываем метаданные моделей
        )
