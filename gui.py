import sys
import yaml
from queue import Queue
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QProgressBar, QFrame,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QComboBox, QTextEdit)
from PySide6.QtCore import QThread, Signal, Slot
from PySide6.QtGui import QFont
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from pipeline import AnalysisWorker
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Анализатор Латентных Пространств v2.0 (PySide6)")
        self.setGeometry(100, 100, 1400, 900)

        # Загрузка конфигурации
        with open("config.yaml", "r") as f:
            self.config = yaml.safe_load(f)

        self.worker_thread = None
        self.queue = Queue()

        self.init_ui()
        self.populate_midi_selector()

    def init_ui(self):
        # --- Основной макет ---
        main_layout = QHBoxLayout()
        
        # --- Левая панель ---
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.StyledPanel)
        left_panel.setFixedWidth(300)
        left_layout = QVBoxLayout(left_panel)

        title_label = QLabel("Управление")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        left_layout.addWidget(title_label)

        self.start_button = QPushButton("Начать анализ")
        self.start_button.setFixedHeight(40)
        self.start_button.clicked.connect(self.start_analysis)
        left_layout.addWidget(self.start_button)

        self.status_label = QLabel("Готов к работе.")
        self.status_label.setWordWrap(True)
        left_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        left_layout.addWidget(self.progress_bar)
        
        left_layout.addSpacing(20)
        
        midi_selector_label = QLabel("Анализ файла:")
        left_layout.addWidget(midi_selector_label)
        self.midi_selector = QComboBox()
        self.midi_selector.currentTextChanged.connect(self.on_midi_select)
        left_layout.addWidget(self.midi_selector)
        
        left_layout.addSpacing(20)
        
        log_label = QLabel("Лог выполнения:")
        left_layout.addWidget(log_label)
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        left_layout.addWidget(self.log_console)

        # --- Правая панель ---
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.StyledPanel)
        right_layout = QVBoxLayout(right_panel)

        self.table = QTableWidget()
        self.init_table()
        right_layout.addWidget(self.table, 1)

        self.pca_canvas = FigureCanvas()
        self.cc_canvas = FigureCanvas()
        
        plot_layout = QHBoxLayout()
        plot_layout.addWidget(self.pca_canvas, 1)
        plot_layout.addWidget(self.cc_canvas, 1)
        right_layout.addLayout(plot_layout, 2)

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def init_table(self):
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Latent Dim.", "CC-ME ↓", "MR-STFT Loss ↓", "Final DKL", "Note Accuracy ↑"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

    def populate_midi_selector(self):
        path = self.config['data_source']['midi_path']
        if os.path.exists(path):
            midi_files = [f for f in os.listdir(path) if f.endswith('.mid')]
            self.midi_selector.addItems(midi_files)

    @Slot()
    def start_analysis(self):
        self.start_button.setEnabled(False)
        self.log_console.clear()
        self.table.setRowCount(0)
        self.log_message("Запуск анализа...")

        self.worker_thread = QThread()
        self.analysis_worker = AnalysisWorker(self.config, self.queue)
        self.analysis_worker.moveToThread(self.worker_thread)

        self.analysis_worker.progress.connect(self.update_progress)
        self.analysis_worker.finished.connect(self.on_analysis_finished)
        
        self.worker_thread.started.connect(self.analysis_worker.run)
        self.worker_thread.start()

    @Slot(int, str)
    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
        if "Лог:" in message:
            self.log_message(message.replace("Лог: ", ""))

    @Slot(dict)
    def on_analysis_finished(self, results):
        self.results = results
        self.log_message("Анализ завершен!")
        self.status_label.setText("Готов к работе.")
        self.progress_bar.setValue(100)
        
        self.worker_thread.quit()
        self.worker_thread.wait()
        self.start_button.setEnabled(True)
        
        self.populate_results_table()
        self.on_midi_select(self.midi_selector.currentText())


    def populate_results_table(self):
        self.table.setRowCount(len(self.results))
        for i, (dim, data) in enumerate(self.results.items()):
            metrics = data['metrics']
            self.table.setItem(i, 0, QTableWidgetItem(str(dim)))
            self.table.setItem(i, 1, QTableWidgetItem(f"{metrics['CC-ME']:.4f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{metrics['MR-STFT']:.4f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{metrics['DKL']:.4f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{metrics['Note Accuracy']:.2%}"))

    @Slot(str)
    def on_midi_select(self, filename):
        if not hasattr(self, 'results') or not self.results:
            return
            
        # Просто берем результаты первой модели для отображения графиков
        first_dim = next(iter(self.results))
        data = self.results[first_dim]

        self.update_plot(self.pca_canvas, data['plots']['pca'])
        
        # Обновляем CC график для выбранного файла
        cc_plot_fig = data['plots']['cc_comparison'].get(filename)
        if cc_plot_fig:
            self.update_plot(self.cc_canvas, cc_plot_fig)

    def update_plot(self, canvas, fig):
        canvas.figure.clf()
        if fig:
            fig.set_canvas(canvas)
            ax = fig.gca()
            canvas.figure.add_axes(ax)
            canvas.draw()
            
    def log_message(self, message):
        self.log_console.append(message)
