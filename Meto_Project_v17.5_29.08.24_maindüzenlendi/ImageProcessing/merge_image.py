import cv2
import numpy as np
from PIL import Image
from log.logger import logger_manager
import os
from datetime import datetime
from logger import parameter_logger, error_logger, operation_logger

class ImageMerger:
    def __init__(self, directory_manager, parameter_logger=None):
        self.directory_manager = directory_manager
        self.parameter_logger = parameter_logger

    def merge_images(self, image1_path, image2_path):
        try:
            # Birleştirilmiş görüntünün dosya yolunu oluştur
            merged_image_path = os.path.join(self.directory_manager.get_merged_output_dir(),
                                             f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")

            # İlk ve ikinci görüntüyü oku ve döndür
            image1 = Image.open(image1_path).rotate(270, expand=True)
            image2 = Image.open(image2_path).rotate(-90, expand=True)

            # Görüntülerin genişlik ve yüksekliklerini al
            width1, height1 = image1.size
            width2, height2 = image2.size

            # Görüntülerin aynı boyutta olduğundan emin olun
            new_height = max(height1, height2)
            image1 = image1.resize((width1, new_height))
            image2 = image2.resize((width2, new_height))

            # Yeni görüntü genişliği ve yüksekliği
            total_width = width1 + width2
            max_height = new_height

            # Yeni görüntüyü oluştur
            merge_image = Image.new('RGB', (total_width, max_height))
            merge_image.paste(image1, (0, 0))
            merge_image.paste(image2, (width1, 0))

            # PIL Image nesnesini NumPy array'e dönüştür
            merge_image_cv = np.array(merge_image)

            # Renk sırasını RGB'den BGR'ye çevir (OpenCV BGR kullanır)
            merge_image_cv = cv2.cvtColor(merge_image_cv, cv2.COLOR_RGB2BGR)

            # OpenCV ile görüntüyü kaydet
            if cv2.imwrite(merged_image_path, merge_image_cv):
                print(f"Birleştirilmiş resim başarıyla kaydedildi: {merged_image_path}")
                operation_logger.info(f"Birleştirilmiş resim kaydedildi: {merged_image_path}")
                return merged_image_path  # Başarıyla kaydedilen görüntünün yolunu döndür
            else:
                print(f"Birleştirilmiş resim kaydedilemedi: {merged_image_path}")
                operation_logger.error(f"Birleştirilmiş resim kaydedilemedi: {merged_image_path}")
                return None

        except Exception as e:
            print(f"Görüntü birleştirme sırasında bir hata oluştu: {e}")
            operation_logger.error(f"Görüntü birleştirme sırasında bir hata oluştu: {e}")
            return None

