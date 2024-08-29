import os
import torch
from PIL import Image
from torchvision import transforms, models
from torchvision.models.detection import FasterRCNN_ResNet50_FPN_Weights
import logging
import time  # Zaman ölçümü için gerekli modül
import numpy as np
# Logger ayarı
operation_logger = logging.getLogger(__name__)

class ObjectDetector:
    def __init__(self, image_path, output_dir, score_threshold=0.01):
        """
        ObjectDetector sınıfı, derin öğrenme modeli kullanarak nesne algılama yapar.

        Args:
            image_path (str): Nesne algılaması yapılacak görüntünün dosya yolu.
            output_dir (str): Algılama sonuçlarının kaydedileceği dizin.
            score_threshold (float): Nesne algılama için skor eşiği.
        """
        self.image_path = image_path
        self.output_dir = output_dir
        self.score_threshold = score_threshold
        self.weights = FasterRCNN_ResNet50_FPN_Weights.COCO_V1
        self.model = models.detection.fasterrcnn_resnet50_fpn(weights=self.weights)
        self.model.eval()

        operation_logger.info(f"ObjectDetector initialized with image: {image_path}, "
                              f"output_dir: {output_dir}, score_threshold: {score_threshold}")

    def detect_objects(self):
        """
        Bir görüntü üzerinde nesne algılama yapar ve belirli bir skorun üzerindeki sonuçları döndürür.

        Returns:
            list: Algılanan nesnelerin kutuları, etiketleri ve skorlarını içeren liste.
        """
        try:
            # Nesne tespiti işlemi başlatıldı mesajı
            print("Nesne tespiti işlemi başlatıldı... Nesne aranıyor...")
            operation_logger.info("Nesne tespiti işlemi başlatıldı... Nesne aranıyor...")

            # Süre ölçümüne başla
            start_time = time.time()

            # Görüntüyü yükle ve tensöre dönüştür
            image = Image.open(self.image_path)
            operation_logger.info(f"Görüntü yüklendi: {self.image_path}")

            transform = transforms.Compose([transforms.ToTensor()])
            image_tensor = transform(image).unsqueeze(0)
            operation_logger.info("Görüntü tensöre dönüştürüldü.")

            # Model ile nesne algılama
            with torch.no_grad():
                outputs = self.model(image_tensor)
            operation_logger.info("Model ile nesne algılama işlemi başarıyla tamamlandı.")

            # Süreyi hesapla
            end_time = time.time()
            duration = end_time - start_time
            operation_logger.info(f"Nesne algılama tamamlandı. Süre: {duration:.2f} saniye.")

            # Yalnızca belirli bir skorun üzerindeki algılamaları döndür
            filtered_outputs = []
            for output in outputs:
                high_score_indices = [i for i, score in enumerate(output['scores']) if score > self.score_threshold]
                filtered_output = {
                    'boxes': output['boxes'][high_score_indices],
                    'labels': output['labels'][high_score_indices],
                    'scores': output['scores'][high_score_indices]
                }
                filtered_outputs.append(filtered_output)

            # Algılanan nesneleri ve skorlarını yazdır ve kaydet
            results = []

            for i, output in enumerate(outputs):
                operation_logger.info(f"Output {i}:")
                for j in range(len(output['boxes'])):
                    box = output['boxes'][j].numpy()
                    score = output['scores'][j].item()
                    label = output['labels'][j].item()
                    print(f"  Box: {box}, Label: {label}, Score: {score}")
                    operation_logger.info(f"  Box: {box}, Label: {label}, Score: {score}")

                    results.append((box, label, score))
                    # En yüksek skorlu nesneyi bul ve yazdır
            if results:
                max_score_index = np.argmax([result[2] for result in results])
                max_box, max_label, max_score = results[max_score_index]
                print(
                    f"Tanımlanan en yüksek skorlu nesne: Box: {max_box}, Label: {max_label}, Score: {max_score:.4f}")
                operation_logger.info(
                    f"Tanımlanan en yüksek skorlu nesne: Box: {max_box}, Label: {max_label}, Score: {max_score:.4f}")

            print(f"Nesne algılama tamamlandı. Süre: {duration:.2f} saniye.")  # Süreyi konsola yazdır
            # Sonuçları output_dir içine kaydet
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
                operation_logger.info(f"{self.output_dir} dizini oluşturuldu.")

            output_file_path = os.path.join(self.output_dir, f"results_{os.path.basename(self.image_path)}.txt")
            with open(output_file_path, 'w') as f:
                for result in results:
                    box, label, score = result
                    f.write(f"Box: {box}, Label: {label}, Score: {score}\n")

            return filtered_outputs

        except Exception as e:
            operation_logger.error(f"Nesne algılama sırasında bir hata oluştu: {e}")
            raise e  # Hatayı yeniden fırlatmak, üst seviyede de ele alınmasını sağlar.



