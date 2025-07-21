import time
import os
import datetime
import pickle
from PySide6.QtCore import QObject, Signal, Slot
from data_processor import DataProcessor
from model import TransformerVAE
from utils import calculate_metrics, generate_pca_plot, generate_cc_plot

class AnalysisWorker(QObject):
    progress = Signal(int, str)
    finished = Signal(dict)

    def __init__(self, config, queue):
        super().__init__()
        self.config = config
        self.queue = queue

    @Slot()
    def run(self):
        results = {}
        config = self.config
        
        # Создание папки для результатов этого запуска
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        run_results_path = os.path.join(config['experiment']['results_path'], timestamp)
        os.makedirs(run_results_path, exist_ok=True)
        self.progress.emit(0, f"Лог: Результаты будут сохранены в {run_results_path}")

        latent_dims = config['experiment']['latent_dims']
        total_steps = len(latent_dims) * 2 + 1  # 1 data, 2 per model

        # 1. Обработка данных
        self.progress.emit(int(1/total_steps*100), "Шаг 1: Обработка данных...")
        processor = DataProcessor(config['data_source'])
        processed_data = processor.load_and_process_data()
        
        if not processed_data:
            self.progress.emit(100, "Ошибка: MIDI файлы не найдены.")
            self.finished.emit({})
            return

        # 2. Обучение и оценка
        for i, dim in enumerate(latent_dims):
            step_base = i * 2 + 2
            
            # Обучение
            self.progress.emit(int(step_base/total_steps*100), f"Шаг {step_base}: Обучение модели {dim}D...")
            model = TransformerVAE(dim)
            model.train(processed_data['data'])
            
            # Оценка и визуализация
            self.progress.emit(int((step_base + 1)/total_steps*100), f"Шаг {step_base + 1}: Оценка и визуализация {dim}D...")
            metrics = calculate_metrics(model)
            
            # Генерация и сохранение графиков
            pca_fig = generate_pca_plot(dim)
            pca_fig.savefig(os.path.join(run_results_path, f"pca_plot_{dim}D.png"))
            
            cc_plots = {}
            for filename in processed_data['filenames']:
                cc_fig = generate_cc_plot(filename)
                cc_plots[filename] = cc_fig
                cc_fig.savefig(os.path.join(run_results_path, f"cc_plot_{dim}D_{filename}.png"))

            results[dim] = {
                "metrics": metrics,
                "plots": {
                    "pca": pca_fig,
                    "cc_comparison": cc_plots
                }
            }
            self.progress.emit(int((step_base + 1)/total_steps*100), f"Лог: Модель {dim}D оценена.")
            time.sleep(1)

        self.finished.emit(results)
