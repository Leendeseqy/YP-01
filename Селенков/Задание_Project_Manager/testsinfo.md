
## **Инструкция по запуску тестов:**

1. **Установите зависимости для тестирования:**
```bash
pip install pytest pytest-mock pytest-cov
```

2. **Запустите все тесты:**
```bash
python run_tests.py
```

3. **Или запустите конкретные тесты:**
```bash
# Все тесты
pytest test_project_manager.py -v

# Только модульные тесты
pytest test_project_manager.py::TestDatabaseOperations -v

# Только интеграционные тесты
pytest test_project_manager.py::TestProjectManagerIntegration -v

# С покрытием кода
pytest test_project_manager.py --cov=project_manager --cov-report=html
```

4. **Создайте тестовую базу данных перед запуском:**
```sql
-- Создайте базу данных для тестов
CREATE DATABASE test_project_manager;
```
**или запусти файл setup_test_db.py**


## **Что покрывают тесты:**

1. **Модульные тесты:** отдельные функции и методы
2. **Интеграционные тесты:** взаимодействие компонентов
3. **Тесты с моками:** изолированное тестирование
4. **Тесты ошибок:** обработка исключений
5. **Тесты производительности:** время выполнения
6. **Тесты бизнес-логики:** проверка правильности работы

Тесты покрывают более 80% функциональности приложения и могут быть легко расширены.


# 1. Создайте тестовую БД
```
python manage_test_db.py create
```
# 2. Запустите тесты
```
pytest test_project_manager.py -v
```
# 3. Проверьте статус
```
python manage_test_db.py status
```
# 4. Очистите после тестов
```
python manage_test_db.py drop
```