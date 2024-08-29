# import cv2
# import os
# import numpy as np
# from log.logger import logger_manager
#
#
# parameter_logger = logger_manager.parameter_logger
#
#
# class GrayscaleProcessor:
#     def __init__(self, directory_manager):
#         self.directory_manager = directory_manager
#
#     def grayscale_image(self, image_path, grayscale_filename):
#         try:
#             # OpenCV ile görüntüyü oku
#             image = cv2.imread(image_path)
#             if image is None:
#                 raise ValueError(f"Görüntü yüklenemedi: {image_path}")
#
#             # Grayscale dönüşümü
#             grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#
#             # Çıktı dizinini ve dosya yolunu ayarla
#             output_dir = self.directory_manager.get_grayscale_output_dir()
#
#             # Burada sadece dosya adını birleştiriyoruz
#             grayscale_output_path = os.path.join(output_dir, os.path.basename(grayscale_filename))
#
#             # Grayscale görüntüyü kaydet
#             cv2.imwrite(grayscale_output_path, grayscale_image)
#             print(f"Grayscale görüntü kaydedildi: {grayscale_output_path}")
#
#             # Ortalama grayscale değeri hesapla ve logla
#             mean_grayscale_value = np.mean(grayscale_image)
#             print(f"Ortalama grayscale değeri: {mean_grayscale_value}")
#             parameter_logger.info(f"Ortalama grayscale değeri: {mean_grayscale_value}")
#
#             return mean_grayscale_value
#
#         except Exception as e:
#             print(f"Grayscale işlemi sırasında bir hata oluştu: {e}")
#             parameter_logger.error(f"Grayscale işlemi sırasında bir hata oluştu: {e}")
#             return None
import cv2
import os
import numpy as np
from log.logger import logger_manager


parameter_logger = logger_manager.parameter_logger


class GrayscaleProcessor:
    def __init__(self, directory_manager):
        self.directory_manager = directory_manager

    def grayscale_image(self, image_path, grayscale_filename):
        try:
            # OpenCV ile görüntüyü oku
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Görüntü yüklenemedi: {image_path}")

            # Grayscale dönüşümü
            grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Çıktı dizinini ve dosya yolunu ayarla
            output_dir = self.directory_manager.get_grayscale_output_dir()

            # Burada sadece dosya adını birleştiriyoruz
            grayscale_output_path = os.path.join(output_dir, os.path.basename(grayscale_filename))

            # Grayscale görüntüyü kaydet
            cv2.imwrite(grayscale_output_path, grayscale_image)
            print(f"Grayscale görüntü kaydedildi: {grayscale_output_path}")

            # 1. Tüm görüntünün ortalama grayscale değeri hesapla ve logla
            mean_grayscale_value = np.mean(grayscale_image)
            print(f"Ortalama grayscale değeri: {mean_grayscale_value}")
            parameter_logger.info(f"Ortalama grayscale değeri: {mean_grayscale_value}")

            # 2. Merkezde 10x10 kare oluştur ve ortalama grayscale değeri hesapla
            height, width = grayscale_image.shape
            center_x, center_y = width // 2, height // 2

            # 10x10 alanın sınırlarını belirle
            start_x = max(center_x - 100, 0)
            start_y = max(center_y - 100, 0)
            end_x = min(center_x + 100, width)
            end_y = min(center_y +100, height)

            # Merkezdeki 100*100piksel alanını al
            center_region = grayscale_image[start_y:end_y, start_x:end_x]

            # Merkez alanının ortalama grayscale değeri
            mean_center_grayscale_value = np.mean(center_region)
            print(f"Merkezin 10x10 grayscale değeri: {mean_center_grayscale_value}")
            parameter_logger.info(f"Merkezin 10x10 grayscale değeri: {mean_center_grayscale_value}")
            # 3. Merkezdeki 10x10 karenin sınırlarını görüntüye çiz (kırmızı renkte)
            image_with_rectangle = cv2.cvtColor(grayscale_image, cv2.COLOR_GRAY2BGR)
            cv2.rectangle(image_with_rectangle, (start_x, start_y), (end_x, end_y), (0, 0, 255), 2)

            # Çizilmiş kareyi aynı dosya yoluna kaydet
            cv2.imwrite(grayscale_output_path, image_with_rectangle)
            print(f"Kare çizilmiş görüntü kaydedildi: {grayscale_output_path}")
            return mean_grayscale_value, mean_center_grayscale_value



        except Exception as e:
            print(f"Grayscale işlemi sırasında bir hata oluştu: {e}")
            parameter_logger.error(f"Grayscale işlemi sırasında bir hata oluştu: {e}")
            return None
