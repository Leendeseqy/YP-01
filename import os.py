import os

def is_text_file(file_path):
    """Проверяет, является ли файл текстовым (не бинарным)."""
    text_extensions = {'.py', 'txt','.md', '.json', '.html', '.css', '.js', '.sh', '.c', '.cpp', '.h', '.cs'}
    return any(file_path.lower().endswith(ext) for ext in text_extensions)

def extract_contents(root_path, output_file):
    """Рекурсивно извлекает пути и содержимое файлов в TXT."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Содержимое проекта: {root_path}\n")
        f.write("=" * 80 + "\n\n")
        
        for dirpath, _, filenames in os.walk(root_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(file_path, root_path)
                
                f.write(f"Путь: {rel_path}\n")
                f.write("-" * 50 + "\n")
                
                try:
                    if is_text_file(file_path) and os.path.getsize(file_path) < 10**6:  # <1MB
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                            content = file.read()
                            f.write(content)
                    else:
                        f.write("(Файл пропущен: бинарный или слишком большой)\n")
                except Exception as e:
                    f.write(f"(Ошибка чтения: {e})\n")
                
                f.write("\n" + "=" * 80 + "\n\n")

if __name__ == "__main__":
    root_path = input("Введите путь к папке проекта: ").strip()
    if os.path.isdir(root_path):
        output_file = "project_contents.txt"
        extract_contents(root_path, output_file)
        print(f"Готово! Результат в {output_file}")
    else:
        print("Папка не найдена!")

