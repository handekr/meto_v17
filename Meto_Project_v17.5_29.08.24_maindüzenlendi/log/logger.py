from pathlib import Path
import logging

class LoggerManager:
    def __init__(self, log_directory="logs"):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)

        self.camera_logger = self._create_logger('camera_settings', 'camera_settings.log', logging.INFO)
        self.error_logger = self._create_logger('errors', 'errors.log', logging.ERROR)
        self.operation_logger = self._create_logger('operations', 'operations.log', logging.INFO)
        self.parameter_logger = self._create_logger('parameters', 'parameters.log', logging.INFO)

    def _create_logger(self, name, log_file, level):
        logger = logging.getLogger(name)
        logger.setLevel(level)
        file_handler = logging.FileHandler(self.log_directory / log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
        return logger

# LoggerManager'ı başlat
logger_manager = LoggerManager()

# Logger nesnelerini dışa aktar
camera_logger = logger_manager.camera_logger
error_logger = logger_manager.error_logger
operation_logger = logger_manager.operation_logger
parameter_logger = logger_manager.parameter_logger
