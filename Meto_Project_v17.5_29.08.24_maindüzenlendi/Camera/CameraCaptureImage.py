import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
import asyncio
from PIL import Image
from datetime import datetime
from utils.helpers import save_image


from log.logger import camera_logger

class CameraManager:
    def __init__(self, camera1, camera2, camera_dirs):
        self.camera1 = camera1
        self.camera2 = camera2
        self.camera_dirs = camera_dirs

    def capture_image(self, camera, index):
        try:
            while True:
                raw_image = camera.data_stream[0].get_image(timeout=1000)
                if raw_image is None:
                    camera_logger.error(f"Kameradan görüntü alınamadı: {index}. Yeniden dene...")
                    time.sleep(1)
                    continue
                return raw_image
        except Exception as e:
            camera_logger.error(f"Kamera {index} ile görüntü yakalama sırasında bir hata oluştu: {e}")
            raise

    async def async_capture_image(self, camera, index):
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.capture_image, camera, index)
        except Exception as e:
            camera_logger.error(f"Asenkron görüntü yakalama sırasında bir hata oluştu: {e}")
            raise

    async def capture_images_parallel(self):
        try:
            raw_image1, raw_image2 = await asyncio.gather(
                self.async_capture_image(self.camera1, 1),
                self.async_capture_image(self.camera2, 2)
            )

            rgb_image1 = raw_image1.convert("RGB")
            rgb_image2 = raw_image2.convert("RGB")

            if rgb_image1 is None or rgb_image2 is None:
                camera_logger.error("Görüntüler RGB formatına dönüştürülemedi.")
                return None

            numpy_image1 = rgb_image1.get_numpy_array()
            pil_image1 = Image.fromarray(numpy_image1)

            numpy_image2 = rgb_image2.get_numpy_array()
            pil_image2 = Image.fromarray(numpy_image2)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename1 = os.path.join(self.camera_dirs[1], f"kamera_1_{timestamp}.jpg")
            filename2 = os.path.join(self.camera_dirs[2], f"kamera_2_{timestamp}.jpg")

            try:
                save_image(pil_image1, filename1)  # save_image fonksiyonunu buradan çağırıyoruz
                save_image(pil_image2, filename2)
            except Exception as e:
                camera_logger.error(f"Görüntüleri kaydetme sırasında bir hata oluştu: {e}")
                raise

            return filename1, filename2

        except Exception as e:
            camera_logger.error(f"Paralel görüntü yakalama sırasında bir hata oluştu: {e}")
            raise
