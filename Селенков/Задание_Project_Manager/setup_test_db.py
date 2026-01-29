import psycopg2
from psycopg2 import Error

def setup_test_database():
    """Создание тестовой базы данных"""
    
    # Конфигурация подключения к основной БД
    config = {
        'host': 'localhost',
        'database': 'postgres',  # Подключаемся к основной БД
        'user': 'postgres',
        'password': '1111',  # Ваш пароль
        'port': '5432'
    }
    
    try:
        # Подключаемся к PostgreSQL
        conn = psycopg2.connect(**config)
        conn.autocommit = True  # Для создания БД нужен autocommit
        cursor = conn.cursor()
        
        print("Подключение к PostgreSQL успешно установлено")
        
        # Проверяем существование БД
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'test_project_manager'")
        exists = cursor.fetchone()
        
        if exists:
            print("Тестовая база данных уже существует")
            choice = input("Удалить и пересоздать? (y/n): ")
            if choice.lower() == 'y':
                # Завершаем все подключения к БД
                cursor.execute("""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = 'test_project_manager'
                    AND pid <> pg_backend_pid();
                """)
                
                # Удаляем БД
                cursor.execute("DROP DATABASE test_project_manager")
                print("Старая тестовая БД удалена")
            else:
                print("Используем существующую БД")
                cursor.close()
                conn.close()
                return
        
        # Создаём новую БД
        cursor.execute("CREATE DATABASE test_project_manager")
        print("Тестовая база данных 'test_project_manager' создана")
        
        # Подключаемся к новой БД для создания таблиц
        cursor.close()
        conn.close()
        
        # Теперь подключаемся к тестовой БД
        config['database'] = 'test_project_manager'
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Создаём таблицы
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                discipline VARCHAR(255),
                status VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_path TEXT
            )
        """)
        print("Таблица 'projects' создана")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS technologies (
                id SERIAL PRIMARY KEY,
                project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
                technology VARCHAR(255) NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Таблица 'technologies' создана")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id SERIAL PRIMARY KEY,
                project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
                action_type VARCHAR(50) NOT NULL,
                action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        """)
        print("Таблица 'activity_log' создана")
        
        conn.commit()
        
        # Добавляем тестовые данные
        print("\nДобавляем тестовые данные...")
        
        # Проекты
        test_projects = [
            ('Тестовый проект 1', 'Разработка', 'В процессе'),
            ('Тестовый проект 2', 'Тестирование', 'Завершен'),
            ('Тестовый проект 3', 'Аналитика', 'На паузе'),
            ('Тестовый проект 4', 'Дизайн', 'Планируется'),
            ('Тестовый проект 5', 'Разработка', 'В процессе'),
        ]
        
        for project in test_projects:
            cursor.execute("""
                INSERT INTO projects (name, discipline, status)
                VALUES (%s, %s, %s)
                RETURNING id
            """, project)
            project_id = cursor.fetchone()[0]
            
            # Технологии для проекта
            if 'Разработка' in project:
                technologies = ['Python', 'PostgreSQL', 'Django']
            elif 'Тестирование' in project:
                technologies = ['PyTest', 'Selenium', 'Postman']
            else:
                technologies = ['Git', 'Docker']
            
            for tech in technologies:
                cursor.execute("""
                    INSERT INTO technologies (project_id, technology)
                    VALUES (%s, %s)
                """, (project_id, tech))
        
        # Логи действий
        cursor.execute("""
            INSERT INTO activity_log (project_id, action_type, details)
            VALUES 
            (1, 'CREATE', 'Создан тестовый проект 1'),
            (2, 'UPDATE', 'Обновлён тестовый проект 2'),
            (3, 'ADD_TECH', 'Добавлена технология Docker')
        """)
        
        conn.commit()
        
        print("\nТестовые данные добавлены:")
        cursor.execute("SELECT COUNT(*) FROM projects")
        print(f"- Проектов: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM technologies")
        print(f"- Технологий: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM activity_log")
        print(f"- Логов действий: {cursor.fetchone()[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 50)
        print("ТЕСТОВАЯ БАЗА ДАННЫХ УСПЕШНО СОЗДАНА!")
        print("=" * 50)
        
    except Error as e:
        print(f"Ошибка при создании БД: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")

if __name__ == "__main__":
    setup_test_database()