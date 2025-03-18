import os
import re

def fix_comments(file_path: str) -> None:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Заменяем комментарии через тройные кавычки на комментарии через решётку
    content = re.sub(r'"""(.*?)"""', lambda m: '# ' + m.group(1).strip(), content, flags=re.DOTALL)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def process_directory(directory: str) -> None:
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                print(f"Processing {file_path}")
                fix_comments(file_path)

if __name__ == "__main__":
    # Обрабатываем все Python файлы в директории services
    services_dir = "otus_space_battle/services"
    process_directory(services_dir) 