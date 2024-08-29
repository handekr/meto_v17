import sys
import os
import numpy as np
import asyncio
import nest_asyncio
from datetime import datetime
import cv2
import time
# Eğer logger.py ile main.py aynı dizinde değilse, modülün bulunduğu dizini ekleyin
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'log')))

# Logger ve DirectoryManager modüllerini içe aktar
from logger import parameter_logger, error_logger, operation_logger
from Camera.CameraTrigger import HardwareTrigger
from Camera.CameraCaptureImage import CameraManager
from ImageProcessing.merge_image import ImageMerger
from Camera.CameraParameterSetting import CameraParameters
from Camera.CameraControl import DeviceManager
from ImageProcessing.object_detect import ObjectDetector
from ImageProcessing.crop import CropProcessor
from ImageProcessing.grayscale_image import GrayscaleProcessor
from Directories.directories import DirectoryManager
from ImageProcessing.edge_contour import ContourStorage  # ContourStorage sınıfını tanımladığınız modülün adını kullanın
from ImageProcessing.edge_contour import ContourProcessor  # ContourProcessor sınıfını tanımladığınız modülün adını kullanın
from ImageProcessing.png import convert_to_png  # convert_to_png fonksiyonunu tanımladığınız modül


# Ana dizin yöneticisi ve kontur saklayıcı nesneleri oluşturun
directory_manager = DirectoryManager()
contour_storage = ContourStorage()

async def initialize_cameras(device_manager, camera_params):
    """
    Cihazları başlatır, kameraları açar ve parametreleri uygular.

    Args:
        device_manager (DeviceManager): Cihaz yöneticisi.
        camera_params (CameraParameters): Kameraların parametreleri.

    Returns:
        tuple: İki kamera nesnesi (cam1, cam2).
    """
    cam1, cam2 = None, None
    try:
        cam1 = device_manager.open_device_by_index(2)
        cam2 = device_manager.open_device_by_index(1)

        if cam1 is None or cam2 is None:  # Doğru sözdizimi "or" kullanmak
            return None, None

        # Kamera parametrelerini her iki kameraya uygula
        cameras = [cam1, cam2]
        camera_params.apply_to_multiple_cameras(cameras, error_logger)

        return cam1, cam2

    except Exception as e:
        error_logger.error(f"Kameralarla ilgili bir hata oluştu: {e}")
        return None, None


async def configure_triggers(cam1, cam2):
    """
    Kameraların donanım tetikleme özelliklerini yapılandırır.

    Args:
        cam1: Birinci kamera nesnesi.
        cam2: İkinci kamera nesnesi.
    """
    try:
        trigger_manager1 = HardwareTrigger(cam1)
        trigger_manager2 = HardwareTrigger(cam2)

        trigger_manager1.configure()
        trigger_manager2.configure()

        cam1.stream_on()
        cam2.stream_on()

    except Exception as e:
        error_logger.error(f"Tetikleme yapılandırılırken bir hata oluştu: {e}")
        raise


async def capture_images_and_cleanup(cam1, cam2, directory_manager):
    """
    Kamera görüntülerini yakalar ve ardından kameraların akışını durdurup cihazları kapatır.

    Args:
        cam1: Birinci kamera nesnesi.
        cam2: İkinci kamera nesnesi.
        directory_manager: Dizin yöneticisi.

    Returns:
        tuple: Yakalanan görüntülerin dosya yolları (image1_path, image2_path).
    """
    try:
        # Kamera görüntüleri için CameraManager sınıfını kullan
        camera_manager = CameraManager(cam1, cam2, directory_manager.camera_dirs)
        image1_path, image2_path = await camera_manager.capture_images_parallel()

        return image1_path, image2_path

    except Exception as e:
        error_logger.error(f"Kameralarla ilgili bir hata oluştu: {e}")
        return None, None

    finally:
        if cam1:
            cam1.stream_off()
            cam1.close_device()
        if cam2:
            cam2.stream_off()
            cam2.close_device()


async def process_images(image1_path, image2_path, directory_manager):
    """
    Görüntüleri birleştirir, grayscale dönüştürme yapar, nesne algılama, kırpma ve kontur bulma işlemlerini gerçekleştirir.

    Args:
        image1_path (str): Birinci görüntünün dosya yolu.
        image2_path (str): İkinci görüntünün dosya yolu.
        directory_manager (DirectoryManager): Dizin yöneticisi.

    Returns:
        tuple: Son işlenen PNG görüntünün dosya yolu ve nesne algılama çıktıları.
    """
    try:
        # ---- Süre ölçümünü başlat ----
        start_time = time.time()
        print("proses zaman ölçümü başlatılıyor.......")

        # 1---ImageMerger nesnesini oluşturun ve görüntüleri birleştirin
        image_merger = ImageMerger(directory_manager)
        merged_image_path = image_merger.merge_images(image1_path, image2_path)

        if merged_image_path:
            print(f"Birleştirilmiş resim başarıyla kaydedildi: {merged_image_path}")
        else:
            print("Görüntü birleştirme işlemi başarısız oldu.")


        # 2----grayscale
        grayscale_processor = GrayscaleProcessor(directory_manager)
        grayscale_image_filename = f"grayscale_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        grayscale_image_path = os.path.join(directory_manager.get_grayscale_output_dir(),
                                                grayscale_image_filename)
        grayscale_processor.grayscale_image(merged_image_path, grayscale_image_path)
        operation_logger.info(f"Grayscale resim kaydedildi: {grayscale_image_path}")




        # 3----Nesne algılama işlemi
        object_detector = ObjectDetector(image_path=grayscale_image_path,
                                         output_dir=directory_manager.get_detection_output_dir(),
                                         score_threshold=0.5)
        outputs = object_detector.detect_objects()

        if not outputs:
            operation_logger.error("Nesne algılama sonucu boş, işlem yapılamıyor.")
            print("Nesne algılama sonucu boş, işlem yapılamıyor.")
            return None, None

        operation_logger.info(f"Nesne algılama tamamlandı. Sonuçlar: {outputs}")

       # 4---Görüntü kırpma ve Box kontur bulma işlemleri
        crop_processor = CropProcessor(directory_manager)
        crop_image_path = crop_processor.draw_box(grayscale_image_path, outputs)

        if crop_image_path:

            # 5-Kenar konturlarını bul
            contour_processor = ContourProcessor(directory_manager, contour_storage)
            contours = contour_processor.process_crop_and_find_contours(crop_image_path)

            if contours:

                #6-- PNG formatına çevirmek için convert_to_png fonksiyonunu çağır
                output_dir = directory_manager.get_png_output_dir()
                convert_to_png(crop_image_path, output_dir, contour_storage)
                final_png_path = os.path.join(output_dir, f"cropped_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

                # ---- Süre ölçümünü bitir ve sonucu hesapla ----
                end_time = time.time()
                elapsed_time = end_time - start_time
                operation_logger.info(f"tetiklemeden sonrageçen süre toplamda {elapsed_time:.2f} saniye sürdü.")
                print(f"tetiklemeden sonrageçen süre toplamda {elapsed_time:.2f} saniye sürdü.")

                return final_png_path, outputs
            else:
                operation_logger.error("Kontur bulunamadı.")
                print("Kontur bulunamadı.")
                return None, None
        else:
            operation_logger.error("Kırpılmış görüntü kaydedilemedi, kenar kontur işlemi yapılamıyor.")
            print("Kırpılmış görüntü kaydedilemedi, kenar kontur işlemi yapılamıyor.")
            return None, None

    except Exception as e:
        print(f"Görüntü işleme sırasında bir hata oluştu: {e}")
        error_logger.error(f"Görüntü işleme sırasında bir hata oluştu: {e}")
        return None, None



async def main_async():
    try:
        # DirectoryManager sınıfını başlat
        directory_manager = DirectoryManager()

        # Kamera parametreleri için CameraParameters sınıfını başlatın
        camera_params = CameraParameters(exposure=10000, gain=2.0)
        parameter_logger.info(f"Kameralar için belirlenmiş Exposure Değeri: {camera_params.exposure}")
        parameter_logger.info(f"Kameralar için belirlenmiş Gain Değeri: {camera_params.gain}")

        # Cihazları tanımla ve kontrol et
        device_manager = DeviceManager(error_logger)
        devices_ok, dev_info_list = device_manager.check_devices()

        if not devices_ok:
            return

        # Kameraları başlat ve parametreleri uygula
        cam1, cam2 = await initialize_cameras(device_manager, camera_params)

        if cam1 is None or cam2 is None:
            return  # Eğer kameralar başlatılamazsa, programdan çıkış yap.

        # Donanım tetikleme yapılandırması
        await configure_triggers(cam1, cam2)

        # Kamera görüntülerini yakala ve kamera akışını durdur, cihazları kapat
        image1_path, image2_path = await capture_images_and_cleanup(cam1, cam2, directory_manager)

        if image1_path and image2_path:
            # Tüm görüntü işleme adımlarını içeren process_images fonksiyonunu çağır
            final_png_path, outputs = await process_images(image1_path, image2_path, directory_manager)

            # İşleme sonucunu kontrol et
            if final_png_path and outputs:
                operation_logger.info(f"Görüntü işleme tamamlandı, final PNG: {final_png_path}")
                print(f"Görüntü işleme tamamlandı, final PNG: {final_png_path}")
            else:
                error_logger.error("Görüntü işleme sırasında bir hata oluştu.")
                print("Görüntü işleme sırasında bir hata oluştu.")

    except Exception as e:
        error_logger.error(f"Beklenmeyen bir hata oluştu: {e}")
        print(f"Beklenmeyen bir hata oluştu: {e}")

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main_async())
