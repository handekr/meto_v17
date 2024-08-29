import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import numpy as np
from datetime import datetime
from log.logger import operation_logger

class CropProcessor:
    def __init__(self, directory_manager):
        self.directory_manager = directory_manager

    def draw_box(self, image_path, outputs, expansion=100):
        try:
            # Görüntüyü yükle
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Görüntü yüklenemedi: {image_path}")

            processed_boxes = set()

            for output in outputs:
                if len(output['scores']) == 0:
                    continue

                max_score_index = np.argmax(output['scores'])
                max_score = output['scores'][max_score_index]
                box = output['boxes'][max_score_index]

                # Mevcut koordinatları genişlet
                x1, y1, x2, y2 = map(int, box)
                x1 = max(0, x1 - expansion)
                y1 = max(0, y1 - expansion)
                x2 = min(image.shape[1], x2 + expansion)
                y2 = min(image.shape[0], y2 + expansion)

                # Kırpma işlemi
                cropped_image = image[y1:y2, x1:x2]

                # Dosya yolunu oluştur
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                crop_image_path = os.path.join(self.directory_manager.get_cropped_output_dir(),
                                               f"crop_{timestamp}.jpg")

                # Kırpılmış görüntüyü kaydet
                cv2.imwrite(crop_image_path, cropped_image)

                print(f"Kırpılmış resim kaydedildi: {crop_image_path}")
                operation_logger.info(f"Kırpılmış resim kaydedildi: {crop_image_path}")

                # İşlenmiş kutuyu kaydet
                processed_boxes.add(tuple(box))

                return crop_image_path  # Kırpılmış görüntünün dosya yolunu döndürün

        except Exception as e:
            operation_logger.error(f"Box işlem sırasında bir hata oluştu: {e}")
            print(f"Box işlem sırasında bir hata oluştu: {e}")
            return None  # Hata durumunda None döndürün