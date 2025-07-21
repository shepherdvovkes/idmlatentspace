# 🎵 Synthesizer Performance Analyzer & ML Research Platform

> **Комплексная исследовательская платформа для анализа и генерации высокодименсиональных латентных пространств в производстве электронной музыки**

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Qt](https://img.shields.io/badge/GUI-PySide6-green)
![ML](https://img.shields.io/badge/ML-PyTorch%20%7C%20Transformer%20VAE-orange)
![Status](https://img.shields.io/badge/Status-Research%20Ready-brightgreen)
![SysEx](https://img.shields.io/badge/Package-sysex--toolkit-purple)

## 🎯 Обзор проекта

Это многокомпонентная исследовательская платформа, специализирующаяся на анализе тембровых характеристик электронной музыки с использованием современных методов машинного обучения. Проект реализует методологии, описанные в исследовательской работе по β-VAE с Transformer архитектурами для IDM и Dubstep музыки.

### 🌟 Ключевые особенности

- **🎛️ Анализ MIDI+CC**: Обработка MIDI нот с плотной автоматизацией Control Change
- **🧠 Высокодименсиональные VAE**: Реализация 384-512D латентных пространств для сложного тембрального кодирования  
- **📊 Исследовательские метрики**: CC Modulation Error, MR-STFT Loss, KL Divergence, Note Accuracy
- **🎨 Интерактивная визуализация**: D3.js графики для анализа латентного пространства и эволюции CC
- **📈 Академическая готовность**: Генерация публикационных результатов и таблиц
- **⚡ Полный пайплайн**: От экспорта Ableton до обученных моделей одной командой
- **🔌 Универсальная поддержка SysEx**: Работа с любыми синтезаторами через конфигурационные файлы
- **🎹 Встроенные определения**: Access Virus C, Roland JP-8000 и другие

## 🚀 Быстрый старт

### Системные требования

**Минимальные:**
- RAM: 8GB (рекомендуется 16GB)
- Хранилище: 2GB свободного места
- Python: 3.8+
- ОС: Windows 10+, macOS 10.15+, Linux

**Рекомендуемые:**
- GPU: NVIDIA RTX 3070+ с 8GB VRAM
- CPU: 8+ ядер для параллельной обработки
- RAM: 32GB для больших датасетов
- SSD: Для быстрого I/O при обучении

### Установка

```bash
# Клонировать репозиторий
git clone https://github.com/username/synthesizer-performance-analyzer.git
cd synthesizer-performance-analyzer

# Установить зависимости
pip install -r requirements.txt
pip install sysex-toolkit

# Создать директорию для проектов Ableton
mkdir AbletonProjects

# Скопировать ваши .mid файлы из экспорта Ableton Live
cp /path/to/your/*.mid AbletonProjects/
```

### Использование

#### GUI версия (рекомендуется)
```bash
python main.py
```

#### Командная строка
```bash
# Запуск полного анализа
python pipeline.py

# Быстрый тест с сокращенными параметрами
python pipeline.py --config quick_config.yaml

# Пользовательская директория проекта
python pipeline.py --project-dir ./MyMIDIFiles --output results.json
```

#### SysEx анализ
```bash
# Декодировать SysEx файл
sysex-decode my_preset.syx --synth access_virus

# Анализ неизвестного SysEx формата
sysex-analyze unknown_synth.syx

# Пакетная обработка множественных файлов
sysex-batch /path/to/presets/ --synth access_virus
```

## 📁 Структура проекта

```
synthesizer-performance-analyzer/
├── 🎹 AbletonProjects/           # Ваши MIDI файлы
│   ├── dubstep_bass_01.mid
│   ├── idm_glitch_02.mid
│   └── ...
├── 🐍 main.py                    # GUI приложение
├── 🔄 pipeline.py                # Основной анализ backend
├── 🎨 gui.py                     # Интерфейс PySide6
├── 📊 data_processor.py          # Обработка данных
├── 🤖 model.py                   # Transformer VAE модель
├── 🛠️ utils.py                   # Утилиты и визуализация
├── 📋 apa.py                     # Анализатор проектов Ableton
├── 🎵 audio_ml_analyzer.py       # ML анализ аудио
├── 🎛️ preset_differential_analyzer.py # Анализ пресетов
├── 📦 sysex-toolkit/             # Универсальная SysEx библиотека
│   ├── sysex_toolkit/
│   ├── examples/
│   └── tests/
├── 📂 Samples/                   # Аудио семплы
├── ⚙️ config.yaml                # Параметры конфигурации
├── 📖 README.md                  # Этот файл
└── 📄 kubmlops-3.pdf             # Описание проекта
```

## 🎛️ Подготовка файлов Ableton

### Настройки экспорта

1. **Солирование синтезаторных треков** (басслайны, лиды с тяжелой автоматизацией)
2. **Стандартизация CC mapping**:
   ```
   CC1  → Filter Cutoff      CC6  → Envelope Decay
   CC2  → Filter Resonance   CC7  → Distortion/Drive  
   CC3  → LFO Rate          CC8  → Reverb Send
   CC4  → LFO Amount        CC9  → Delay Send
   CC5  → Envelope Attack   CC10 → Custom Parameter
   ```
3. **Экспорт как MIDI** с разрешением 480 PPQ
4. **4-тактовые сегменты** работают лучше всего для анализа
5. **Плотная автоматизация** (>5 CC событий на бит) производит лучшие результаты

### Соглашение о наименовании файлов

```
genre_synth_project_segment_bpm_synthesizer.mid

Примеры:
dubstep_bass_01_seg01_140_serum.mid
idm_glitch_02_seg01_170_massive.mid
```

## 📊 Понимание результатов

### Количественные метрики

| Метрика | Описание | Диапазон | Цель |
|---------|----------|----------|------|
| **CC-ME** | CC Modulation Error - тембральная точность | 0.0-1.0 | Меньше ↓ |
| **MR-STFT** | Multi-Resolution STFT Loss - качество звука | 0.0-1.0 | Меньше ↓ |
| **D_KL** | KL Divergence - регулярность латентного пространства | 0.0+ | Меньше ↓ |
| **Note Acc** | Точность реконструкции нот | 0.0-1.0 | Больше ↑ |

### Ожидаемые результаты

```json
{
  "quantitative": {
    "128": {"ccme": 0.245, "mrstft": 0.312, "dkl": 2.145, "noteAcc": 0.876},
    "256": {"ccme": 0.198, "mrstft": 0.267, "dkl": 1.987, "noteAcc": 0.891},
    "384": {"ccme": 0.142, "mrstft": 0.198, "dkl": 1.756, "noteAcc": 0.902},
    "512": {"ccme": 0.118, "mrstft": 0.156, "dkl": 1.623, "noteAcc": 0.915}
  }
}
```

**Ключевой инсайт**: Высокодименсиональные латентные пространства (384D, 512D) значительно превосходят традиционные низкодименсиональные подходы для генерации сложных тембров.

## 🔬 Исследовательские применения

### Интеграция в академические работы

Результаты могут быть напрямую использованы в LaTeX таблицах:

```latex
\begin{table}[h!]
    \centering
    \caption{Результаты количественной оценки}
    \begin{tabular}{lcccc}
        \toprule
        \textbf{Latent Dim.} & \textbf{CC-ME ↓} & \textbf{MR-STFT ↓} & \textbf{D_KL ↓} & \textbf{Note Acc ↑} \\
        \midrule
        128 & 0.245 & 0.312 & 2.145 & 0.876 \\
        384 & 0.142 & 0.198 & 1.756 & 0.902 \\
        512 & 0.118 & 0.156 & 1.623 & 0.915 \\
        \bottomrule
    \end{tabular}
\end{table}
```

### Валидация гипотез

- ✅ **Превосходство высоких размерностей**: 384D+ модели показывают значительно более низкий CC-ME
- ✅ **Захват тембральной сложности**: Сложная CC автоматизация требует >256D латентных пространств  
- ✅ **Жанрово-специфичное кодирование**: IDM vs Dubstep паттерны появляются в латентном пространстве
- ✅ **Эффективность архитектуры**: Transformer + β-VAE хорошо обрабатывает последовательные CC данные

## 🎨 Визуализации

### Возможности веб-интерфейса

1. **Обзор качества датасета** - Таблица со статистикой файлов и оценками качества
2. **Визуализация латентного пространства** - PCA проекция изученных представлений
3. **Графики эволюции CC** - Временные ряды автоматизации параметров
4. **Сравнение архитектур** - Столбчатые диаграммы сравнения производительности моделей
5. **Обработка в реальном времени** - Мониторинг прогресса с подробными логами

### Генерируемые графики

- 📈 **Кривые обучения** (потери vs эпохи)
- 🎯 **Структура латентного пространства** (PCA, t-SNE)
- 🎛️ **Анализ использования CC параметров**
- 📊 **Сравнение производительности** по размерностям

## 🛠️ Продвинутое использование

### Пользовательские метрики

```python
from pipeline import AnalysisWorker
import yaml

# Загрузка конфигурации
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Запуск анализа с пользовательскими параметрами
worker = AnalysisWorker(config, queue=None)
results = worker.run()

# Доступ к специфичным метрикам
cc_me_384d = results[384]['metrics']['CC-ME']
print(f"384D CC-ME Score: {cc_me_384d:.4f}")
```

### Анализ SysEx пресетов

```python
from sysex_toolkit import decode_sysex_file, SysExFormat

# Декодирование пресета
presets = decode_sysex_file('my_preset.syx', SysExFormat.ACCESS_VIRUS)

# Доступ к параметрам
for preset in presets:
    print(f"Preset: {preset['metadata']['preset_name']}")
    
    # Фильтр параметров (отлично для анализа wobble bass)
    filter_params = {
        name: data for name, data in preset['parameters'].items() 
        if data['category'] == 'filter'
    }
    
    print(f"Filter cutoff: {filter_params['filter_cutoff']['normalized_value']:.3f}")
```

### Интеграция машинного обучения

Идеально для исследований ML в электронной музыке:

```python
# Извлечение признаков для латентного пространства
import numpy as np
from sysex_toolkit import decode_sysex_file

presets = decode_sysex_file('dubstep_presets.syx')

# Создание матрицы признаков для обучения VAE
feature_matrix = []
for preset in presets:
    # Фокус на параметрах фильтра для анализа wobble
    wobble_features = []
    for param_name, param_data in preset['parameters'].items():
        if param_data['category'] in ['filter', 'lfo']:
            wobble_features.append(param_data['normalized_value'])
    
    feature_matrix.append(wobble_features)

feature_matrix = np.array(feature_matrix)
# Готово для обучения β-VAE!
```

## ⚙️ Конфигурация

### Базовая конфигурация (`config.yaml`)

```yaml
data_source:
  midi_path: "./AbletonProjects"
  cache_path: "./cache/processed_data.pkl"

experiment:
  latent_dims: [128, 256, 384, 512]
  results_path: "./results"

model_training:
  epochs: 50
  learning_rate: 0.0001
  batch_size: 16
```

### Конфигурация быстрого теста

Для быстрого прототипирования используйте `quick_config.yaml` с сокращенными параметрами:
- 2 латентные размерности (128D, 384D)
- 20 эпох
- Меньшая архитектура модели

## 📦 Поддерживаемые синтезаторы (SysEx Toolkit)

- **Access Virus C** (Полная поддержка)
- **Roland JP-8000** (Базовая поддержка)
- **Пользовательские синтезаторы** через конфигурационные файлы

## 🎵 Варианты использования

- **Музыкальное производство**: Анализ и модификация пресетов синтезаторов
- **ML исследования**: Извлечение признаков для генеративных моделей
- **Управление пресетами**: Организация и категоризация звуковых библиотек
- **Звуковой дизайн**: Понимание взаимосвязей параметров
- **Академические исследования**: Изучение характеристик электронной музыки

## 📋 Требования к датасету

| Метрика | Минимум | Рекомендуется |
|---------|---------|---------------|
| Файлы | 10 | 50+ |
| CC События/сегмент | 50 | 200+ |
| Длина последовательности | 200 токенов | 500+ токенов |
| Оценка качества | 70% | 90%+ |

## 🔧 Устранение неполадок

### Распространенные проблемы

**"MIDI файлы не найдены"**
```bash
ls -la AbletonProjects/*.mid  # Проверить существование файлов
chmod 644 AbletonProjects/*   # Исправить права доступа
```

**"Недостаточная CC автоматизация"**
- Убедитесь, что CC контроллеры автоматизированы в Ableton
- Проверьте, что экспорт включает дорожки автоматизации
- Проверьте консистентность CC mapping

**"CUDA out of memory"**
```yaml
model_training:
  batch_size: 8     # Уменьшить размер батча
  model_dim: 256    # Использовать меньшую модель
```

**Низкие оценки качества**
- Просмотрите консистентность CC mapping между файлами
- Убедитесь, что 4-тактовые сегменты музыкально согласованы  
- Проверьте на вариации темпа между экспортами

## 📚 Цитирование

Если вы используете этот инструмент в своих исследованиях, пожалуйста, цитируйте:

```bibtex
@article{synthesizer_performance_2024,
  title={Generating High-Fidelity Synthesizer Performances for Complex Electronic Music via Structured High-Dimensional Latent Spaces},
  author={Ovcharov, Vladimir},
  journal={Journal of AI Music Research},
  year={2024}
}

@software{sysex_toolkit_2025,
  title={SysEx Toolkit: Universal SysEx Library for Music Production},
  author={Ovcharov, Vladimir},
  year={2025},
  url={https://pypi.org/project/sysex-toolkit/}
}
```

## 🤝 Вклад в проект

Мы приветствуем вклады! Пожалуйста, ознакомьтесь с нашими руководящими принципами вклада:

1. **Fork** репозитория
2. **Создать** ветку функции
3. **Добавить** тесты для новой функциональности  
4. **Отправить** pull request с подробным описанием

### Настройка разработки

```bash
# Установить зависимости разработки
pip install -r requirements-dev.txt

# Запустить тесты
pytest tests/

# Форматирование кода
black *.py
flake8 *.py
```

## 📄 Лицензия

Этот проект лицензирован под лицензией MIT - см. файл [LICENSE](LICENSE) для деталей.

## 🙏 Благодарности

- **Ableton Live** за возможности экспорта MIDI
- **PyTorch** команде за фреймворк глубокого обучения
- **PySide6** за современный GUI фреймворк
- **D3.js** сообществу за инструменты визуализации
- **Music Information Retrieval** исследовательскому сообществу

## 📞 Поддержка

- 📧 **Email**: vladimir@highfunk.uk
- 🐛 **Issues**: [GitHub Issues](https://github.com/username/repository/issues)
- 💬 **Обсуждения**: [GitHub Discussions](https://github.com/username/repository/discussions)
- 📖 **Документация**: [Wiki](https://github.com/username/repository/wiki)

---

🎵 **Готов революционизировать генерацию электронной музыки с высокодименсиональными латентными пространствами!**

*Создано с ❤️ для сообщества исследователей музыкального ИИ*
