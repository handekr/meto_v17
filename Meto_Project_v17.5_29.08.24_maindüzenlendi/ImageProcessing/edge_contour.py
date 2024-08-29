import os
import cv2
from datetime import datetime
from log.logger import operation_logger
from Directories.directories import DirectoryManager


class ContourStorage:
    def __init__(self):
        self.contours = []

    def save_contours(self, contours):
        self.contours = contours

    def get_contours(self):
        return self.contours

class ContourProcessor:
    def __init__(self, directory_manager, contour_storage):
        self.directory_manager = directory_manager
        self.contour_storage = contour_storage

    def process_crop_and_find_contours(self, crop_image_path):
        try:
            # Kırpılmış gri tonlamalı görüntüyü yükle
            gray_image = cv2.imread(crop_image_path, cv2.IMREAD_GRAYSCALE)
            if gray_image is None:
                raise ValueError(f"Görüntü yüklenemedi: {crop_image_path}")

            # Kenar algılama
            blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            edges = cv2.Canny(thresh, 30, 120)

            # Kontur bulma
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                largest_contour = max(contours, key=cv2.contourArea)

                # Konturları çizmek için gri görüntüyü BGR'ye dönüştür
                contoured_image = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)
                cv2.drawContours(contoured_image, [largest_contour], -1, (0, 0, 255), 2)

                # Çıktı dosya yolunu oluştur
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_image_path = os.path.join(self.directory_manager.get_contoured_output_dir(),
                                                 f"contoured_{timestamp}.jpg")

                # Konturlu görüntüyü kaydet
                cv2.imwrite(output_image_path, contoured_image)
                print(f"Konturlu resim kaydedildi: {output_image_path}")
                operation_logger.info(f"Konturlu resim kaydedildi: {output_image_path}")

                # Kontur verilerini kaydet
                self.contour_storage.save_contours(contours)

            else:
                print("Kontur bulunamadı.")
                operation_logger.info("Kontur bulunamadı.")

            return contours

        except Exception as e:
            print(f"Görüntü işleme sırasında bir hata oluştu: {e}")
            operation_logger.error(f"Görüntü işleme sırasında bir hata oluştu: {e}")
