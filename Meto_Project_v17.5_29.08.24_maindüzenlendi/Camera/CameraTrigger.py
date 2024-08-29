import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import gxipy as gx
from log.logger import error_logger

class HardwareTrigger:
    def __init__(self, camera):
        """
        HardwareTrigger, bir kamera nesnesi ile initialize edilir.

        Args:
            camera: Kameranın nesnesi.
        """
        self.camera = camera

    def configure(self):
        """
        Kameranın donanım tetikleme özelliklerini yapılandırır.
        """
        try:
            self.camera.TriggerMode.set(gx.GxSwitchEntry.ON)

            # Desteklenen TriggerSource ayarlarından birini kullanın
            self.camera.TriggerSource.set(gx.GxTriggerSourceEntry.LINE0)  # LINE0 kullanıyoruz

            #self.camera.TriggerActivation.set(gx.GxTriggerActivationEntry.FALLINGEDGE)

            print(f"Kamera tetikleme başarıyla yapılandırıldı: {self.camera}")
        except AttributeError as e:
            error_logger.error(f"Geçersiz bir tetikleme özelliği kullanılıyor: {e}")
            raise
        except Exception as e:
            error_logger.error(f"Kamera tetikleme yapılandırılırken hata oluştu: {e}")
            raise
