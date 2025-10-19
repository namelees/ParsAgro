#!/usr/bin/env python3
"""
Скрипт для запуска всех примеров
Демонстрирует различные способы использования модуля utils.py
"""

import sys
import os
import subprocess

def run_script(script_name, description):
    """Запускает скрипт и выводит результат"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"📁 Файл: {script_name}")
    print('='*60)
    
    try:
        # Запускаем скрипт
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, 
                              text=True, 
                              cwd=os.path.dirname(__file__))
        
        # Выводим результат
        if result.stdout:
            print("📤 Вывод:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️ Ошибки:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Скрипт выполнен успешно")
        else:
            print(f"❌ Скрипт завершился с кодом {result.returncode}")
            
    except Exception as e:
        print(f"💥 Ошибка при запуске {script_name}: {e}")

def main():
    """Главная функция"""
    print("🎯 Запуск всех примеров использования модуля utils.py")
    print("=" * 60)
    
    # Список примеров для запуска
    examples = [
        ("example_usage.py", "Примеры базового использования функций"),
        ("refactored_example.py", "Примеры рефакторинга с utils"),
        ("test_utils.py", "Тесты для модуля utils"),
        ("integration_example.py", "Примеры интеграции в основной проект")
    ]
    
    # Запускаем каждый пример
    for script_name, description in examples:
        if os.path.exists(script_name):
            run_script(script_name, description)
        else:
            print(f"❌ Файл {script_name} не найден")
    
    print(f"\n{'='*60}")
    print("🎉 Все примеры выполнены!")
    print("📚 Для изучения кода откройте файлы в редакторе")
    print("🔧 Для интеграции в ваш проект используйте примеры из integration_example.py")
    print('='*60)

if __name__ == "__main__":
    main()
