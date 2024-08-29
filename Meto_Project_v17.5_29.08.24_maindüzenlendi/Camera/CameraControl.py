import gxipy as gx

class DeviceManager:
    def __init__(self, error_logger=None):
        self.device_manager = gx.DeviceManager()
        self.error_logger = error_logger

    def get_devices(self):
        dev_num, dev_info_list = self.device_manager.update_device_list()
        return dev_num, dev_info_list

    def check_devices(self, required_device_count=2):
        dev_num, dev_info_list = self.get_devices()

        if dev_num == 0:
            message = "Cihaz bulunamadı"
            print(message)
            if self.error_logger:
                self.error_logger.error(message)
            return False, []

        if dev_num < required_device_count:
            message = f"En az {required_device_count} kamera gereklidir"
            print(message)
            if self.error_logger:
                self.error_logger.error(message)
            return False, []

        return True, dev_info_list

    def open_device_by_index(self, index):
        try:
            return self.device_manager.open_device_by_index(index)
        except Exception as e:
            message = f"Cihaz {index} açılırken bir hata oluştu: {e}"
            print(message)
            if self.error_logger:
                self.error_logger.error(message)
            return None
