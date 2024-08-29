class CameraParameters:
    def __init__(self, exposure=10000, gain=2.0):
        self.exposure = exposure
        self.gain = gain

    def apply_parameters(self, camera):
        try:
            camera.ExposureTime.set(self.exposure)
            camera.Gain.set(self.gain)
            return True
        except Exception as e:
            print(f"Kamera parametreleri uygulanırken hata oluştu: {e}")
            return False

    def apply_to_multiple_cameras(self, cameras, error_logger=None):
        results = {}
        for i, camera in enumerate(cameras, start=1):
            success = self.apply_parameters(camera)
            results[f"camera_{i}"] = success
            if not success and error_logger:
                error_logger.error(f"Kamera {i} parametreleri uygulanamadı")
        return results