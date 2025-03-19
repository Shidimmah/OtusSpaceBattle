#!/usr/bin/env python3
import os
import re
import glob

def fix_imports(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Получаем имя сервиса из пути
    service_name = file_path.split('/services/')[1].split('/')[0]
    
    # Заменяем относительные импорты на абсолютные
    modified_content = re.sub(
        r'from \.\.(src|)\.(.*?) import',
        f'from otus_space_battle.services.{service_name}.\\1.\\2 import',
        content
    )
    
    # Заменяем импорты без src
    modified_content = re.sub(
        r'from \.\.(.*?) import',
        f'from otus_space_battle.services.{service_name}.\\1 import',
        modified_content
    )
    
    # Проверяем, были ли изменения
    if content != modified_content:
        print(f"Fixing imports in {file_path}")
        with open(file_path, 'w') as f:
            f.write(modified_content)
        return True
    
    return False

def main():
    # Находим все тесты в директориях сервисов
    test_files = glob.glob('otus_space_battle/services/*/tests/*.py')
    
    count = 0
    for test_file in test_files:
        if fix_imports(test_file):
            count += 1
    
    print(f"Fixed imports in {count} files")

if __name__ == "__main__":
    main() 