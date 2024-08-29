import os
import cv2
from datetime import datetime
from log.logger import operation_logger
from ImageProcessing.edge_contour import ContourStorage
import numpy as np

def convert_to_png(contoured_image_path, output_dir, contour_storage):
    """
    Konturlu resmi keser ve PNG formatına çevirir.

    Args:
        contoured_image_path (str): Konturlanmış resmin dosya yolu.
        output_dir (str): PNG dosyasının kaydedileceği dizin.
        contour_storage (ContourStorage): Kontur verilerini saklayan nesne.
    """
    try:
        # Konturlanmış resmi yükle
        contoured_image = cv2.imread(contoured_image_path)
        if contoured_image is None:
            raise ValueError(f"Resim yüklenemedi: {contoured_image_path}")
        print("Konturlanmış görüntü başarıyla yüklendi.")

        # Kontur bilgilerini al
        contours = contour_storage.get_contours()
        if not contours:
            raise ValueError("Kontur verisi bulunamadı.")

        # Maske oluştur (aynı boyutta siyah bir resim)
        mask = np.zeros_like(contoured_image)

        # Kontur alanını beyaz yap (maske üzerinde)
        cv2.drawContours(mask, contours, -1, (255, 255, 255), thickness=cv2.FILLED)

        # Maske ile orijinal görüntüyü birleştir
        cropped_image = cv2.bitwise_and(contoured_image, mask)

        # PNG formatına çevirmek için alpha kanalını ekleyin
        gray_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
        _, alpha = cv2.threshold(gray_image, 1, 255, cv2.THRESH_BINARY)
        b, g, r = cv2.split(cropped_image)
        rgba = cv2.merge([b, g, r, alpha])

        # Dosya adını oluştur ve kaydet
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        png_filename = os.path.join(output_dir, f"png_{timestamp}.png")
        cv2.imwrite(png_filename, rgba)

        print(f"PNG formatında kaydedildi: {png_filename}")
        operation_logger.info(f"PNG formatında kaydedildi: {png_filename}")

    except Exception as e:
        print(f"Görüntüyü PNG formatına çevirme sırasında bir hata oluştu: {e}")
        operation_logger.error(f"Görüntüyü PNG formatına çevirme sırasında bir hata oluştu: {e}")
