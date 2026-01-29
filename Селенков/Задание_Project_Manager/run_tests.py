"""
Скрипт для запуска всех тестов
"""

import pytest
import os
import sys

def run_all_tests():
    """Запуск всех тестов"""
    print("=" * 60)
    print("ЗАПУСК ТЕСТОВ PROJECT MANAGER")
    print("=" * 60)
    
    # Аргументы для pytest
    args = [
        "test_project_manager.py",
        "-v",  # Подробный вывод
        "--tb=short",  # Короткий traceback
        "--color=yes",  # Цветной вывод
        f"--rootdir={os.path.dirname(os.path.abspath(__file__))}",
    ]
    
    # Добавляем покрытие кода если установлен pytest-cov
    try:
        import pytest_cov
        args.extend([
            "--cov=project_manager",
            "--cov-report=term-missing",
            "--cov-report=html",
        ])
    except ImportError:
        print("pytest-cov не установлен, пропускаем анализ покрытия")
        print("Установите: pip install pytest-cov")
    
    # Запускаем тесты
    exit_code = pytest.main(args)
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)
    
    return exit_code

if __name__ == "__main__":
    # Проверяем что файлы существуют
    if not os.path.exists("project_manager.py"):
        print("ОШИБКА: Файл project_manager.py не найден!")
        sys.exit(1)
    
    if not os.path.exists("test_project_manager.py"):
        print("ОШИБКА: Файл test_project_manager.py не найден!")
        sys.exit(1)
    
    # Запускаем тесты
    sys.exit(run_all_tests())