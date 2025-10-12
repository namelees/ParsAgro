import re

def getGroupId(url):
    """
    Извлекает ID группы из ссылки вида https://lk2.stgau.ru/WebApp/#/Rasp/Group/22296
    
    Args:
        url (str): URL ссылка, из которой нужно извлечь ID группы
        
    Returns:
        str: ID группы или None, если ID не найден
        
    Example:
        >>> getGroupId("https://lk2.stgau.ru/WebApp/#/Rasp/Group/22296")
        "22296"
    """
    # Паттерн для поиска ID группы в URL
    pattern = r'/Rasp/Group/(\d+)'
    
    # Ищем совпадение в URL
    match = re.search(pattern, url)
    
    if match:
        return match.group(1)
    else:
        return None


# Пример использования
if __name__ == "__main__":
    # Тестовые случаи
    test_url = "https://lk2.stgau.ru/WebApp/#/Rasp/Group/22296"
    group_id = getGroupId(test_url)
    print(f"URL: {test_url}")
    print(f"Group ID: {group_id}")
    
    # Дополнительные тесты
    test_cases = [
        "https://lk2.stgau.ru/WebApp/#/Rasp/Group/12345",
        "https://lk2.stgau.ru/WebApp/#/Rasp/Group/999",
        "https://example.com/other/path",  # Неправильный URL
        "https://lk2.stgau.ru/WebApp/#/Rasp/Group/",  # URL без ID
    ]
    
    print("\nДополнительные тесты:")
    for url in test_cases:
        result = getGroupId(url)
        print(f"URL: {url} -> Group ID: {result}")
