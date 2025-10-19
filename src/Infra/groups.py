import os
import json
import logging

logger = logging.getLogger(__name__)

# Глобальная переменная для хранения данных групп
groups_database = {}

def load_groups_data():
    """Загружает данные групп из файла"""
    global groups_database
    possible_paths = [
        'src/groups_data.json',
        './src/groups_data.json', 
        f'{os.getcwd()}/src/groups_data.json',
        'groups_data.json',
        os.path.join(os.path.dirname(__file__), 'groups_data.json'),
    ]
    
    for file_path in possible_paths:
        try:
            if os.path.exists(file_path):
                
                print("file_path: ", file_path)

                with open(file_path, 'r', encoding='utf-8') as f:
                    groups_database = json.load(f)
                logger.info(f"✅ Загружено {len(groups_database)} групп из {file_path}")
                return
        except Exception as e:
            logger.warning(f"⚠️ Не удалось загрузить из {file_path}: {e}")
            continue
    
    logger.error("❌ Файл groups_data.json не найден ни по одному пути!")
    groups_database = {}

def find_group(query):
    """Умный поиск группы по названию или номеру"""
    query = query.strip()
    
    # 1. Точное совпадение (с учетом регистра)
    if query in groups_database:
        return [(query, groups_database[query])]
    
    # 2. Поиск по номеру группы в URL
    if query.isdigit():
        matches = []
        for group_name, group_url in groups_database.items():
            if query in group_url:
                matches.append((group_name, group_url))
        if matches:
            return matches
    
    # 3. Поиск по частичному совпадению
    matches = []
    for group_name, group_url in groups_database.items():
        if query in group_name:
            matches.append((group_name, group_url))
        elif query.lower() in group_name.lower():
            matches.append((group_name, group_url))
    
    return matches

def get_groups_database():
    """Возвращает текущую базу данных групп"""
    return groups_database
