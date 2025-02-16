import base64
from PIL import Image
import io

def image_to_base64(image_path):
    """
    Преобразует изображение в кодировку base64.
    
    Аргументы:
        image_path (str): Путь к файлу изображения.
        
    Возвращается:
        str: Строка изображения в кодировке base64.
    """
    with Image.open(image_path) as image:
        buffered = io.BytesIO()
        image.save(buffered, format=image.format)
        image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return image_base64

# Пример использования
image_path = 'path_to_your_image.jpg'  # Замените на свой путь к изображению
base64_string = image_to_base64(image_path)
print(base64_string)
