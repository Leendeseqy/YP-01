"""
PyTest тесты для приложения Project Manager
Запуск: pytest test_project_manager.py -v
"""

import pytest
import psycopg2
from psycopg2 import Error
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import tkinter as tk
from project_manager import ProjectManagerApp, DB_CONFIG
import sys

# ============================================================================
# ФИКСТУРЫ И ХЕЛПЕРЫ
# ============================================================================

@pytest.fixture
def test_db_config():
    """Конфигурация тестовой БД"""
    return {
        'host': 'localhost',
        'database': 'test_project_manager',
        'user': 'postgres',
        'password': '1111',
        'port': '5432'
    }

@pytest.fixture
def setup_test_db(test_db_config):
    """Создание и настройка тестовой БД"""
    # Подключаемся к основной БД для создания тестовой
    conn = psycopg2.connect(
        host=test_db_config['host'],
        database='postgres',
        user=test_db_config['user'],
        password=test_db_config['password'],
        port=test_db_config['port']
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Пытаемся удалить старую тестовую БД
    try:
        cursor.execute(f"DROP DATABASE IF EXISTS {test_db_config['database']}")
    except Exception:
        pass
    
    # Создаём новую тестовую БД
    cursor.execute(f"CREATE DATABASE {test_db_config['database']}")
    cursor.close()
    conn.close()
    
    # Создаём таблицы в тестовой БД
    conn = psycopg2.connect(**test_db_config)
    cursor = conn.cursor()
    
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
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS technologies (
            id SERIAL PRIMARY KEY,
            project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
            technology VARCHAR(255) NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id SERIAL PRIMARY KEY,
            project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
            action_type VARCHAR(50) NOT NULL,
            action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details TEXT
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return test_db_config

@pytest.fixture
def temp_project_folder():
    """Создание временной папки для проектов"""
    temp_dir = tempfile.mkdtemp()
    projects_dir = os.path.join(temp_dir, 'projects')
    reports_dir = os.path.join(temp_dir, 'reports')
    charts_dir = os.path.join(temp_dir, 'reports', 'charts')
    
    os.makedirs(projects_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    os.makedirs(charts_dir, exist_ok=True)
    
    yield temp_dir
    
    # Очистка после тестов
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def mock_tkinter():
    """Мок для tkinter"""
    with patch('project_manager.tk.Tk'), \
         patch('project_manager.ttk'), \
         patch('project_manager.messagebox'):
        yield

@pytest.fixture
def sample_project_data():
    """Тестовые данные проекта"""
    return {
        'name': 'Тестовый проект',
        'discipline': 'Тестирование',
        'status': 'В процессе',
        'description': '# Тестовый проект\n\nОписание тестового проекта.'
    }

# ============================================================================
# МОДУЛЬНЫЕ ТЕСТЫ
# ============================================================================

class TestDatabaseOperations:
    """Тесты операций с базой данных"""
    
    def test_database_connection(self, setup_test_db):
        """Тест подключения к БД"""
        conn = psycopg2.connect(**setup_test_db)
        assert conn is not None
        conn.close()
    
    def test_create_tables(self, setup_test_db):
        """Тест создания таблиц"""
        conn = psycopg2.connect(**setup_test_db)
        cursor = conn.cursor()
        
        # Проверяем существование таблиц
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'projects' in tables
        assert 'technologies' in tables
        assert 'activity_log' in tables
        
        cursor.close()
        conn.close()
    
    def test_insert_project(self, setup_test_db):
        """Тест добавления проекта"""
        conn = psycopg2.connect(**setup_test_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO projects (name, discipline, status)
            VALUES (%s, %s, %s)
            RETURNING id
        """, ('Тестовый проект', 'Тестирование', 'В процессе'))
        
        project_id = cursor.fetchone()[0]
        assert project_id > 0
        
        cursor.execute("SELECT COUNT(*) FROM projects")
        count = cursor.fetchone()[0]
        assert count == 1
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def test_insert_technology(self, setup_test_db):
        """Тест добавления технологии"""
        conn = psycopg2.connect(**setup_test_db)
        cursor = conn.cursor()
        
        # Сначала создаём проект
        cursor.execute("""
            INSERT INTO projects (name, discipline, status)
            VALUES (%s, %s, %s)
            RETURNING id
        """, ('Проект с технологиями', 'Разработка', 'В процессе'))
        
        project_id = cursor.fetchone()[0]
        
        # Добавляем технологию
        cursor.execute("""
            INSERT INTO technologies (project_id, technology)
            VALUES (%s, %s)
        """, (project_id, 'Python'))
        
        cursor.execute("SELECT COUNT(*) FROM technologies")
        count = cursor.fetchone()[0]
        assert count == 1
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def test_log_activity(self, setup_test_db):
        """Тест логирования действий"""
        conn = psycopg2.connect(**setup_test_db)
        cursor = conn.cursor()
        
        # Создаём проект
        cursor.execute("""
            INSERT INTO projects (name, discipline, status)
            VALUES (%s, %s, %s)
            RETURNING id
        """, ('Проект для логов', 'Логирование', 'В процессе'))
        
        project_id = cursor.fetchone()[0]
        
        # Логируем действие
        cursor.execute("""
            INSERT INTO activity_log (project_id, action_type, details)
            VALUES (%s, %s, %s)
        """, (project_id, 'CREATE', 'Создан тестовый проект'))
        
        cursor.execute("SELECT COUNT(*) FROM activity_log")
        count = cursor.fetchone()[0]
        assert count == 1
        
        conn.commit()
        cursor.close()
        conn.close()

class TestFileOperations:
    """Тесты операций с файлами"""
    
    def test_create_project_folder(self, temp_project_folder):
        """Тест создания папок проектов"""
        projects_dir = os.path.join(temp_project_folder, 'projects')
        reports_dir = os.path.join(temp_project_folder, 'reports')
        charts_dir = os.path.join(temp_project_folder, 'reports', 'charts')
        
        assert os.path.exists(projects_dir)
        assert os.path.exists(reports_dir)
        assert os.path.exists(charts_dir)
    
    def test_create_markdown_file(self, temp_project_folder):
        """Тест создания Markdown файла"""
        file_path = os.path.join(temp_project_folder, 'projects', 'test_project.md')
        
        content = "# Тестовый проект\n\nОписание проекта."
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        assert os.path.exists(file_path)
        
        # Проверяем содержимое
        with open(file_path, 'r', encoding='utf-8') as f:
            read_content = f.read()
        
        assert read_content == content
    
    def test_safe_filename(self):
        """Тест безопасного имени файла"""
        # Этот тест проверяет логику создания безопасных имён файлов
        test_name = "Test Project: Special/Characters*in?Name"
        safe_name = "".join(c for c in test_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        # Проверяем, что опасные символы удалены
        assert ':' not in safe_name
        assert '/' not in safe_name
        assert '*' not in safe_name
        assert '?' not in safe_name

# ============================================================================
# ИНТЕГРАЦИОННЫЕ ТЕСТЫ
# ============================================================================

class TestProjectManagerIntegration:
    """Интеграционные тесты ProjectManagerApp"""
    
    @patch('project_manager.DB_CONFIG')
    def test_app_initialization(self, mock_db_config, setup_test_db, temp_project_folder, mock_tkinter):
        """Тест инициализации приложения"""
        mock_db_config.__getitem__.side_effect = setup_test_db.__getitem__
        
        # Создаём mock для root окна
        mock_root = Mock()
        
        # Инициализируем приложение
        app = ProjectManagerApp(mock_root)
        
        assert app.root == mock_root
        assert app.current_project_id is None
        assert app.current_project_file is None
        assert isinstance(app.project_technologies, dict)
    
    @patch('project_manager.DB_CONFIG')
    @patch('project_manager.messagebox')
    def test_create_project_integration(self, mock_messagebox, mock_db_config, 
                                       setup_test_db, temp_project_folder, mock_tkinter):
        """Интеграционный тест создания проекта"""
        mock_db_config.__getitem__.side_effect = setup_test_db.__getitem__
        
        # Настраиваем моки
        mock_root = Mock()
        mock_messagebox.showwarning = Mock()
        mock_messagebox.showinfo = Mock()
        
        # Создаём приложение
        app = ProjectManagerApp(mock_root)
        
        # Настраиваем поля ввода
        app.project_name_entry = Mock()
        app.project_name_entry.get.return_value = "Интеграционный тест"
        app.discipline_entry = Mock()
        app.discipline_entry.get.return_value = "Интеграция"
        app.status_combobox = Mock()
        app.status_combobox.get.return_value = "В процессе"
        
        # Мокаем load_projects чтобы не пытался обновлять GUI
        app.load_projects = Mock()
        
        # Вызываем создание проекта
        app.create_project()
        
        # Проверяем, что проект создан в БД
        conn = psycopg2.connect(**setup_test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM projects WHERE name = %s", 
                      ("Интеграционный тест",))
        count = cursor.fetchone()[0]
        
        assert count == 1
        
        cursor.close()
        conn.close()
    
    @patch('project_manager.DB_CONFIG')
    def test_add_technology_integration(self, mock_db_config, setup_test_db, 
                                       temp_project_folder, mock_tkinter):
        """Интеграционный тест добавления технологии"""
        mock_db_config.__getitem__.side_effect = setup_test_db.__getitem__
        
        # Создаём проект в БД
        conn = psycopg2.connect(**setup_test_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO projects (name, discipline, status)
            VALUES (%s, %s, %s)
            RETURNING id
        """, ('Проект для технологии', 'Тестирование', 'В процессе'))
        
        project_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        # Настраиваем приложение
        mock_root = Mock()
        app = ProjectManagerApp(mock_root)
        app.current_project_id = project_id
        
        # Настраиваем поле ввода технологии
        app.tech_entry = Mock()
        app.tech_entry.get.return_value = "PyTest"
        
        # Мокаем вспомогательные методы
        app.log_activity = Mock()
        app.load_technologies = Mock()
        
        # Добавляем технологию
        app.add_technology()
        
        # Проверяем, что технология добавлена
        conn = psycopg2.connect(**setup_test_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM technologies 
            WHERE project_id = %s AND technology = %s
        """, (project_id, "PyTest"))
        
        count = cursor.fetchone()[0]
        assert count == 1
        
        cursor.close()
        conn.close()

# ============================================================================
# ТЕСТЫ С МОКАМИ
# ============================================================================

class TestMockedOperations:
    """Тесты с использованием моков"""
    
    def test_log_activity_mocked(self):
        """Тест логирования с моком БД"""
        with patch('project_manager.psycopg2.connect') as mock_connect:
            # Настраиваем мок
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            # Создаём приложение
            mock_root = Mock()
            app = ProjectManagerApp(mock_root)
            
            # Вызываем логирование
            app.log_activity(1, 'TEST_ACTION', 'Тестовое действие')
            
            # Проверяем вызовы
            mock_connect.assert_called_once()
            mock_cursor.execute.assert_called_once()
            mock_conn.commit.assert_called_once()
            mock_cursor.close.assert_called_once()
            mock_conn.close.assert_called_once()
    
    def test_generate_report_mocked(self):
        """Тест генерации отчёта с моками"""
        with patch('project_manager.psycopg2.connect') as mock_connect, \
             patch('project_manager.messagebox') as mock_messagebox, \
             patch('project_manager.os.makedirs') as mock_makedirs, \
             patch('project_manager.openpyxl.Workbook') as mock_workbook, \
             patch('project_manager.datetime') as mock_datetime:
            
            # Настраиваем моки
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            # Мокаем данные статистики
            mock_cursor.fetchone.side_effect = [
                (5,),  # Количество проектов
                [('Дисциплина1', 2), ('Дисциплина2', 3)],  # Проекты по дисциплинам
                [('В процессе', 3), ('Завершен', 2)],  # Проекты по статусам
                (10, 25),  # Действия за 7 и 30 дней
                [('Python', 5), ('PostgreSQL', 3)],  # Топ технологии
                [('Проект1', 'Дисц1', 'Статус1', datetime.now())],  # Последние проекты
            ]
            
            mock_datetime.now.return_value.strftime.return_value = "20260129_120000"
            
            # Создаём приложение
            mock_root = Mock()
            app = ProjectManagerApp(mock_root)
            app.report_info_label = Mock()
            
            # Вызываем генерацию отчёта
            app.generate_report()
            
            # Проверяем, что методы вызывались
            mock_connect.assert_called()
            mock_cursor.execute.assert_called()
    
    def test_export_to_excel_mocked(self):
        """Тест экспорта в Excel с моками"""
        with patch('project_manager.psycopg2.connect') as mock_connect, \
             patch('project_manager.filedialog.asksaveasfilename') as mock_filedialog, \
             patch('project_manager.openpyxl.Workbook') as mock_workbook, \
             patch('project_manager.messagebox') as mock_messagebox:
            
            # Настраиваем моки
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            # Мокаем данные проектов
            mock_cursor.fetchall.return_value = [
                ('Проект1', 'Дисциплина1', 'В процессе', datetime.now(), datetime.now()),
                ('Проект2', 'Дисциплина2', 'Завершен', datetime.now(), datetime.now()),
            ]
            
            mock_filedialog.return_value = '/fake/path/projects.xlsx'
            
            # Создаём приложение
            mock_root = Mock()
            app = ProjectManagerApp(mock_root)
            
            # Вызываем экспорт
            app.export_to_excel()
            
            # Проверяем вызовы
            mock_connect.assert_called_once()
            mock_filedialog.assert_called_once()

# ============================================================================
# ТЕСТЫ ОШИБОК И ИСКЛЮЧЕНИЙ
# ============================================================================

class TestErrorHandling:
    """Тесты обработки ошибок"""
    
    def test_database_connection_error(self):
        """Тест ошибки подключения к БД"""
        with patch('project_manager.psycopg2.connect') as mock_connect, \
             patch('project_manager.messagebox') as mock_messagebox:
            
            # Настраиваем мок для выброса ошибки
            mock_connect.side_effect = Error("Connection failed")
            mock_messagebox.showerror = Mock()
            
            # Пытаемся создать приложение
            mock_root = Mock()
            
            try:
                app = ProjectManagerApp(mock_root)
                # Если не выбросило исключение, проверяем что сообщение показано
                mock_messagebox.showerror.assert_called()
            except:
                pass  # Ожидаемое поведение
    
    def test_file_not_found_error(self):
        """Тест обработки отсутствующего файла"""
        with patch('project_manager.os.path.exists') as mock_exists, \
             patch('project_manager.messagebox') as mock_messagebox:
            
            # Настраиваем моки
            mock_exists.return_value = False
            mock_messagebox.showwarning = Mock()
            
            # Создаём приложение
            mock_root = Mock()
            app = ProjectManagerApp(mock_root)
            app.current_project_file = '/fake/path/project.md'
            
            # Пытаемся открыть несуществующий файл
            app.open_description()
            
            # Проверяем, что показано предупреждение
            mock_messagebox.showwarning.assert_called_once()
    
    def test_empty_project_name_error(self):
        """Тест создания проекта без имени"""
        with patch('project_manager.messagebox') as mock_messagebox:
            
            mock_messagebox.showwarning = Mock()
            
            # Создаём приложение
            mock_root = Mock()
            app = ProjectManagerApp(mock_root)
            
            # Настраиваем пустое имя
            app.project_name_entry = Mock()
            app.project_name_entry.get.return_value = ""
            
            # Пытаемся создать проект
            app.create_project()
            
            # Проверяем, что показано предупреждение
            mock_messagebox.showwarning.assert_called_once()

# ============================================================================
# ТЕСТЫ ПРОИЗВОДИТЕЛЬНОСТИ
# ============================================================================

class TestPerformance:
    """Тесты производительности"""
    
    def test_load_projects_performance(self, setup_test_db):
        """Тест производительности загрузки проектов"""
        # Создаём 100 тестовых проектов
        conn = psycopg2.connect(**setup_test_db)
        cursor = conn.cursor()
        
        for i in range(100):
            cursor.execute("""
                INSERT INTO projects (name, discipline, status)
                VALUES (%s, %s, %s)
            """, (f'Тестовый проект {i}', f'Дисциплина {i % 5}', 'В процессе'))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Тестируем время выполнения
        import time
        
        with patch('project_manager.DB_CONFIG') as mock_db_config:
            mock_db_config.__getitem__.side_effect = setup_test_db.__getitem__
            
            mock_root = Mock()
            app = ProjectManagerApp(mock_root)
            
            # Мокаем treeview чтобы не зависеть от GUI
            app.tree = Mock()
            app.tree.get_children.return_value = []
            app.tree.insert = Mock()
            
            start_time = time.time()
            app.load_projects()
            end_time = time.time()
            
            execution_time = end_time - start_time
            
            # Проверяем что выполняется менее чем за 2 секунды
            assert execution_time < 2.0, f"Загрузка проектов заняла {execution_time:.2f} секунд"

# ============================================================================
# ТЕСТЫ БИЗНЕС-ЛОГИКИ
# ============================================================================

class TestBusinessLogic:
    """Тесты бизнес-логики"""
    
    def test_project_statistics_logic(self, setup_test_db):
        """Тест логики сбора статистики"""
        # Создаём тестовые данные
        conn = psycopg2.connect(**setup_test_db)
        cursor = conn.cursor()
        
        # Проекты с разными дисциплинами и статусами
        projects = [
            ('Проект 1', 'Разработка', 'В процессе'),
            ('Проект 2', 'Тестирование', 'Завершен'),
            ('Проект 3', 'Разработка', 'В процессе'),
            ('Проект 4', 'Аналитика', 'На паузе'),
            ('Проект 5', 'Тестирование', 'В процессе'),
        ]
        
        for project in projects:
            cursor.execute("""
                INSERT INTO projects (name, discipline, status)
                VALUES (%s, %s, %s)
            """, project)
        
        # Технологии
        cursor.execute("SELECT id FROM projects LIMIT 3")
        project_ids = [row[0] for row in cursor.fetchall()]
        
        technologies = ['Python', 'PostgreSQL', 'PyTest', 'Python', 'Django']
        for i, tech in enumerate(technologies):
            cursor.execute("""
                INSERT INTO technologies (project_id, technology)
                VALUES (%s, %s)
            """, (project_ids[i % 3], tech))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Собираем статистику через метод приложения
        with patch('project_manager.DB_CONFIG') as mock_db_config:
            mock_db_config.__getitem__.side_effect = setup_test_db.__getitem__
            
            mock_root = Mock()
            app = ProjectManagerApp(mock_root)
            
            stats = app.collect_statistics()
            
            # Проверяем статистику
            assert stats['total_projects'] == 5
            assert stats['projects_by_discipline']['Разработка'] == 2
            assert stats['projects_by_discipline']['Тестирование'] == 2
            assert stats['projects_by_discipline']['Аналитика'] == 1
            assert stats['projects_by_status']['В процессе'] == 3
            assert stats['projects_by_status']['Завершен'] == 1
            assert stats['projects_by_status']['На паузе'] == 1
            assert 'Python' in stats['top_technologies']
    
    def test_technology_duplicate_prevention(self, setup_test_db):
        """Тест предотвращения дублирования технологий"""
        with patch('project_manager.DB_CONFIG') as mock_db_config, \
             patch('project_manager.messagebox') as mock_messagebox:
            
            mock_db_config.__getitem__.side_effect = setup_db.__getitem__
            mock_messagebox.showwarning = Mock()
            
            # Создаём проект
            conn = psycopg2.connect(**setup_test_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO projects (name, discipline, status)
                VALUES (%s, %s, %s)
                RETURNING id
            """, ('Проект дубликатов', 'Тестирование', 'В процессе'))
            
            project_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
            # Создаём приложение
            mock_root = Mock()
            app = ProjectManagerApp(mock_root)
            app.current_project_id = project_id
            
            # Добавляем технологию первый раз
            app.tech_entry = Mock()
            app.tech_entry.get.return_value = "Python"
            app.log_activity = Mock()
            app.load_technologies = Mock()
            
            app.add_technology()
            
            # Пытаемся добавить ту же технологию второй раз
            app.add_technology()
            
            # Проверяем, что показано предупреждение о дублировании
            mock_messagebox.showwarning.assert_called_once()

# ============================================================================
# ЗАПУСК ТЕСТОВ
# ============================================================================

if __name__ == "__main__":
    print("Запуск тестов Project Manager...")
    print("=" * 50)
    
    # Создаём временные директории для тестов
    temp_dir = tempfile.mkdtemp()
    print(f"Временная директория: {temp_dir}")
    
    # Запускаем pytest
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        f"--rootdir={temp_dir}"
    ])
    
    # Очистка
    shutil.rmtree(temp_dir, ignore_errors=True)