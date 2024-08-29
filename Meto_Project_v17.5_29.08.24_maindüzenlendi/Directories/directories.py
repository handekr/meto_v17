import os
from log.logger import camera_logger

class DirectoryManager:
    def __init__(self, output_dir='C:Fotograflar'):
        """
        DirectoryManager sınıfı, verilen ana dizin altında gerekli alt dizinleri oluşturur ve yönetir.

        Args:
            output_dir (str): Ana dizin yolu.
        """
        self.output_dir = output_dir
        self.camera_dirs = {}
        self.merged_output_dir = None
        self.cropped_output_dir = None
        self.contoured_output_dir = None
        self.png_output_dir = None
        self.area_output_dir = None
        self.detection_output_dir = None  # detection_output_dir niteliğini ekliyoruz

        self.create_directories()

    def create_directories(self):
        """
        Gerekli alt dizinleri oluşturur ve dizin yollarını initialize eder.
        """
        # Ana dizini oluştur
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Kamera dizinlerini oluştur
        self.camera_dirs = {1: os.path.join(self.output_dir, 'kamera1'), 2: os.path.join(self.output_dir, 'kamera2')}
        for camera_dir in self.camera_dirs.values():
            if not os.path.exists(camera_dir):
                os.makedirs(camera_dir)

        # Diğer alt dizinleri oluştur
        self.merged_output_dir = os.path.join(self.output_dir, 'merged')
        if not os.path.exists(self.merged_output_dir):
            os.makedirs(self.merged_output_dir)

        self.grayscale_output_dir = os.path.join(self.output_dir, 'grayscale')
        if not os.path.exists(self.grayscale_output_dir):
            os.makedirs(self.grayscale_output_dir)

        self.cropped_output_dir = os.path.join(self.output_dir, 'cropped')
        if not os.path.exists(self.cropped_output_dir):
            os.makedirs(self.cropped_output_dir)

        self.contoured_output_dir = os.path.join(self.output_dir, 'contoured')
        if not os.path.exists(self.contoured_output_dir):
            os.makedirs(self.contoured_output_dir)

        self.png_output_dir = os.path.join(self.output_dir, 'png')
        if not os.path.exists(self.png_output_dir):
            os.makedirs(self.png_output_dir)

        self.area_output_dir = os.path.join(self.output_dir, 'area')
        if not os.path.exists(self.area_output_dir):
            os.makedirs(self.area_output_dir)

        # Detection dizinini oluştur
        self.detection_output_dir = os.path.join(self.output_dir, 'detection')
        if not os.path.exists(self.detection_output_dir):
            os.makedirs(self.detection_output_dir)

    def get_camera_dir(self, camera_index):
        """
        Belirtilen kamera için dizin yolunu döndürür.

        Args:
            camera_index (int): Kameranın indeksi (1 veya 2).

        Returns:
            str: Kameraya ait dizin yolu.
        """
        return self.camera_dirs.get(camera_index, None)

    def get_merged_output_dir(self):
        """
        Birleştirilmiş görsellerin kaydedileceği dizin yolunu döndürür.

        Returns:
            str: Birleştirilmiş görseller dizini.
        """
        return self.merged_output_dir
    def get_grayscale_output_dir(self):
        """
        Birleştirilmiş görsellerin grayscale halinin dizin yolunu döndürür.

        Returns:
            str: Birleştirilmiş görseller dizini.
        """
        return self.grayscale_output_dir

    def get_detection_output_dir(self):
        """
        Nesne algılama sonuçlarının kaydedileceği dizin yolunu döndürür.

        Returns:
            str: Nesne algılama sonuçları dizini.
        """
        return self.detection_output_dir

    def get_cropped_output_dir(self):
        """
        Kesilmiş nesnelerin kaydedileceği dizin yolunu döndürür.

        Returns:
            str: Kesilmiş nesneler dizini.
        """
        return self.cropped_output_dir

    def get_contoured_output_dir(self):
        """
        Konturlu görüntülerin kaydedileceği dizin yolunu döndürür.

        Returns:
            str: Konturlu görüntüler dizini.
        """
        return self.contoured_output_dir

    def get_png_output_dir(self):
        """
        PNG dosyalarının kaydedileceği dizin yolunu döndürür.

        Returns:
            str: PNG dosyaları dizini.
        """
        return self.png_output_dir

    def get_area_output_dir(self):
        """
        Alan hesaplaması yapılan dosyaların kaydedileceği dizin yolunu döndürür.

        Returns:
            str: Alan hesaplamaları dizini.
        """
        return self.area_output_dir

    def get_next_index(self, camera_index):
        """
        Belirtilen kamera dizininde bulunan JPEG dosyalarının sayısını döndürür.

        Args:
            camera_index (int): Kameranın indeksi (1 veya 2).

        Returns:
            int: Sonraki görüntü indexi.
        """
        camera_dir = self.get_camera_dir(camera_index)
        if camera_dir and os.path.exists(camera_dir):
            files = [f for f in os.listdir(camera_dir) if f.endswith('.jpg')]
            return len(files) + 1
        else:
            return 1  # Eğer dizin yoksa, index 1'den başlar

    def save_image(self, image, filename):
        """
        Görüntüyü belirtilen dosya adına kaydeder ve loglar.

        Args:
            image: Kaydedilecek görüntü.
            filename (str): Görüntünün kaydedileceği dosya adı.
        """
        image.save(filename)
        print(f"Resim kaydedildi: {filename}")
        camera_logger.info(f"Resim kaydedildi: {filename}")
