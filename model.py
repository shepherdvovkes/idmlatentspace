import time

class TransformerVAE:
    def __init__(self, latent_dim: int):
        self.latent_dim = latent_dim
        print(f"Создана модель (симуляция) с латентным пространством: {self.latent_dim}D")

    def train(self, dataset):
        print(f"Начало обучения модели {self.latent_dim}D...")
        time.sleep(3) # Имитация обучения
        print(f"Обучение модели {self.latent_dim}D завершено.")
