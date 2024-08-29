import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from log.logger import camera_logger

def save_image(image, filename):
    """
    Görüntüyü belirtilen dosya adıyla kaydeder.
    """
    image.save(filename)
    print(f"Resim kaydedildi: {filename}")
    camera_logger.info(f"Resim kaydedildi: {filename}")

def get_next_index(camera_dir):
    """
    Belirtilen dizindeki JPG dosyalarının sayısını alır ve bir sonraki dosya için indeks döndürür.
    """
    files = [f for f in os.listdir(camera_dir) if f.endswith('.jpg')]
    return len(files) + 1
