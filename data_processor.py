import os
import time
import pickle

class DataProcessor:
    def __init__(self, config):
        self.midi_path = config['midi_path']
        self.cache_path = config['cache_path']
        print("Инициализирован процессор данных.")

    def load_and_process_data(self):
        # Проверка кеша
        if os.path.exists(self.cache_path):
            print(f"Найден кеш: {self.cache_path}. Загрузка...")
            with open(self.cache_path, 'rb') as f:
                return pickle.load(f)
        
        print("Кеш не найден. Запуск полной обработки...")
        midi_files = [f for f in os.listdir(self.midi_path) if f.endswith('.mid')]
        if not midi_files:
            return None
        
        event_streams = []
        for f in midi_files:
            print(f"Обработка (симуляция): {f}")
            time.sleep(0.2)
            event_streams.append([f"event_{i}" for i in range(150)])
            
        processed_data = {
            'data': event_streams,
            'filenames': midi_files
        }
        
        # Сохранение в кеш
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, 'wb') as f:
            pickle.dump(processed_data, f)
        print(f"Данные обработаны и сохранены в кеш: {self.cache_path}")
        
        return processed_data
