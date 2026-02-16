import os
import sys
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QMessageBox,
    QMenuBar, QMenu, QStatusBar, QSpinBox, QDoubleSpinBox,
    QLineEdit, QGroupBox, QGridLayout, QTabWidget, QFrame, QAction
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QKeySequence

from .styles import MAIN_STYLE, STATUS_RECORDING, STATUS_PLAYING, STATUS_IDLE
from recorder import Recorder
from player import Player
from config_manager import AppConfig


class MainWindow(QMainWindow):
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    playback_started = pyqtSignal()
    playback_stopped = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoGhostPY")
        self.setGeometry(100, 100, 500, 400)
        self.setStyleSheet(MAIN_STYLE)
        
        self.recorder = Recorder()
        self.player = Player()
        self.config = AppConfig.load()
        self.current_file: str = ""
        
        self.recorder.set_on_stop_callback(self._on_recording_stopped)
        self.player.set_on_finish_callback(self._on_playback_finished)
        self.player.set_on_stop_callback(self._on_playback_stopped)
        
        self.recording_started.connect(self._update_ui_recording)
        self.recording_stopped.connect(self._update_ui_idle)
        self.playback_started.connect(self._update_ui_playing)
        self.playback_stopped.connect(self._update_ui_idle)
        
        self._setup_ui()
        self._setup_menu()
        self._setup_shortcuts()
        self._update_ui_idle()
        
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(100)
        
    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.tabs = QTabWidget()
        
        self.file_tab = self._create_file_tab()
        self.tabs.addTab(self.file_tab, "Arquivo")
        
        self.config_tab = self._create_config_tab()
        self.tabs.addTab(self.config_tab, "Config")
        
        self.help_tab = self._create_help_tab()
        self.tabs.addTab(self.help_tab, "Ajuda")
        
        layout.addWidget(self.tabs)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #45475a;")
        layout.addWidget(line)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        self.play_btn = QPushButton("PLAY")
        self.play_btn.setObjectName("playButton")
        self.play_btn.setMinimumHeight(50)
        self.play_btn.clicked.connect(self._on_play)
        
        self.stop_btn = QPushButton("STOP")
        self.stop_btn.setObjectName("stopButton")
        self.stop_btn.setMinimumHeight(50)
        self.stop_btn.clicked.connect(self._on_stop)
        
        self.record_btn = QPushButton("REC")
        self.record_btn.setObjectName("recordButton")
        self.record_btn.setMinimumHeight(50)
        self.record_btn.clicked.connect(self._on_record)
        
        buttons_layout.addWidget(self.play_btn)
        buttons_layout.addWidget(self.stop_btn)
        buttons_layout.addWidget(self.record_btn)
        
        layout.addLayout(buttons_layout)
        
        self.status_label = QLabel("Pronto")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(STATUS_IDLE)
        layout.addWidget(self.status_label)
        
        self.statusBar().showMessage("AutoGhostPY v1.0")
        
    def _create_file_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        file_group = QGroupBox("Arquivo de Automação")
        file_layout = QGridLayout()
        
        self.file_label = QLabel("Nenhum arquivo selecionado")
        self.file_label.setWordWrap(True)
        file_layout.addWidget(QLabel("Arquivo:"), 0, 0)
        file_layout.addWidget(self.file_label, 0, 1)
        
        btn_layout = QHBoxLayout()
        select_btn = QPushButton("Selecionar")
        select_btn.clicked.connect(self._select_file)
        new_btn = QPushButton("Novo")
        new_btn.clicked.connect(self._new_file)
        
        btn_layout.addWidget(select_btn)
        btn_layout.addWidget(new_btn)
        file_layout.addLayout(btn_layout, 1, 0, 1, 2)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        info_group = QGroupBox("Info")
        info_layout = QVBoxLayout()
        self.info_label = QLabel("Selecione um arquivo")
        info_layout.addWidget(self.info_label)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        return widget
    
    def _create_config_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        speed_group = QGroupBox("Velocidade")
        speed_layout = QGridLayout()
        
        speed_layout.addWidget(QLabel("Velocidade:"), 0, 0)
        self.speed_spin = QDoubleSpinBox()
        self.speed_spin.setRange(0.1, 5.0)
        self.speed_spin.setSingleStep(0.1)
        self.speed_spin.setValue(self.config.playback_speed)
        self.speed_spin.valueChanged.connect(self._save_config)
        speed_layout.addWidget(self.speed_spin, 0, 1)
        
        speed_group.setLayout(speed_layout)
        layout.addWidget(speed_group)
        
        repeat_group = QGroupBox("Repetição")
        repeat_layout = QGridLayout()
        
        repeat_layout.addWidget(QLabel("Repetições:"), 0, 0)
        self.repeat_spin = QSpinBox()
        self.repeat_spin.setRange(1, 999)
        self.repeat_spin.setValue(self.config.repeat_count)
        self.repeat_spin.valueChanged.connect(self._save_config)
        repeat_layout.addWidget(self.repeat_spin, 0, 1)
        
        repeat_group.setLayout(repeat_layout)
        layout.addWidget(repeat_group)
        
        hotkey_group = QGroupBox("Atalhos")
        hotkey_layout = QGridLayout()
        
        hotkey_layout.addWidget(QLabel("Force Stop (Ctrl+):"), 0, 0)
        self.stop_key_input = QLineEdit(self.config.force_stop_key)
        self.stop_key_input.setMaxLength(1)
        self.stop_key_input.textChanged.connect(self._save_config)
        hotkey_layout.addWidget(self.stop_key_input, 0, 1)
        
        hotkey_layout.addWidget(QLabel("Rec Start:"), 1, 0)
        self.record_start_input = QLineEdit(self.config.record_start_key)
        self.record_start_input.textChanged.connect(self._save_config)
        hotkey_layout.addWidget(self.record_start_input, 1, 1)
        
        hotkey_layout.addWidget(QLabel("Rec Stop:"), 2, 0)
        self.record_stop_input = QLineEdit(self.config.record_stop_key)
        self.record_stop_input.textChanged.connect(self._save_config)
        hotkey_layout.addWidget(self.record_stop_input, 2, 1)
        
        hotkey_group.setLayout(hotkey_layout)
        layout.addWidget(hotkey_group)
        
        layout.addStretch()
        return widget
    
    def _create_help_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        help_text = """
        <h2>AutoGhostPY</h2>
        <p><b>Como usar:</b></p>
        <ol>
            <li>Clique REC para gravar</li>
            <li>Clique STOP para parar</li>
            <li>Clique PLAY para executar</li>
        </ol>
        <p><b>Atalhos:</b> F9=Iniciar | F10=Parar | Ctrl+Q=Force Stop</p>
        """
        
        label = QLabel(help_text)
        label.setWordWrap(True)
        label.setTextFormat(Qt.RichText)
        layout.addWidget(label)
        layout.addStretch()
        
        return widget
    
    def _setup_menu(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("Arquivo")
        
        open_action = QAction("Abrir...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._select_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Salvar...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_as)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
    def _setup_shortcuts(self):
        from PyQt5.QtWidgets import QShortcut
        
        self.record_start_shortcut = QShortcut(
            QKeySequence(self.config.record_start_key), self
        )
        self.record_start_shortcut.activated.connect(self._on_record)
        
        self.record_stop_shortcut = QShortcut(
            QKeySequence(self.config.record_stop_key), self
        )
        self.record_stop_shortcut.activated.connect(self._on_stop)
        
        self.force_stop_shortcut = QShortcut(
            QKeySequence(f"Ctrl+{self.config.force_stop_key.upper()}"), self
        )
        self.force_stop_shortcut.activated.connect(self._force_stop)
    
    def _update_shortcuts(self):
        self.record_start_shortcut.setKey(QKeySequence(self.config.record_start_key))
        self.record_stop_shortcut.setKey(QKeySequence(self.config.record_stop_key))
        self.force_stop_shortcut.setKey(QKeySequence(f"Ctrl+{self.config.force_stop_key.upper()}"))
    
    def _select_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Selecionar", "", "JSON (*.json)"
        )
        if filepath:
            self._load_file(filepath)
    
    def _load_file(self, filepath: str):
        try:
            self.player.load_from_file(filepath)
            self.current_file = filepath
            self.file_label.setText(os.path.basename(filepath))
            self.info_label.setText(f"Eventos: {len(self.player.events)}")
            self.statusBar().showMessage(f"Carregado: {filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))
    
    def _new_file(self):
        self.current_file = ""
        self.file_label.setText("Novo arquivo")
        self.info_label.setText("Clique REC para gravar")
        self.player.events = []
    
    def _save_as(self):
        if not self.recorder.events and not self.player.events:
            QMessageBox.warning(self, "Aviso", "Nada para salvar!")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Salvar", "", "JSON (*.json)"
        )
        if filepath:
            if not filepath.endswith('.json'):
                filepath += '.json'
            self.recorder.save_to_file(filepath)
            self.current_file = filepath
            self.file_label.setText(os.path.basename(filepath))
    
    def _on_record(self):
        if self.recorder.recording or self.player.playing:
            return
        
        # Limpa eventos antigos para gravar por cima
        self.player.events = []
        self.recorder.events = []
        
        # Se tiver arquivo selecionado, mantém o path mas limpa o conteúdo
        if self.current_file:
            self.info_label.setText(f"Regravando: {os.path.basename(self.current_file)}")
        
        self.recorder.start()
        self.recording_started.emit()

    
    def _on_stop(self):
        if self.recorder.recording:
            self.recorder.stop()
        elif self.player.playing:
            self.player.stop()
    
    def _force_stop(self):
        if self.player.playing:
            self.player.stop()
    
    def _on_play(self):
        if self.recorder.recording:
            return
        if not self.player.events:
            if not self.current_file:
                QMessageBox.warning(self, "Aviso", "Selecione um arquivo!")
                return
            self.player.load_from_file(self.current_file)
        
        self.player.speed = self.speed_spin.value()
        self.player.repeat_count = self.repeat_spin.value()
        self.player.play()
        self.playback_started.emit()
    
    def _on_recording_stopped(self):
        self.recording_stopped.emit()
        
        # Salva no arquivo atual ou cria novo
        if self.current_file:
            self.recorder.save_to_file(self.current_file)
            self.info_label.setText(f"Regravado: {os.path.basename(self.current_file)} | Eventos: {len(self.recorder.events)}")
        else:
            default_name = f"auto_{os.getpid()}.json"
            self.recorder.save_to_file(default_name)
            self.current_file = default_name
            self.file_label.setText(default_name)

    
    def _on_playback_finished(self):
        self.playback_stopped.emit()
    
    def _on_playback_stopped(self):
        self.playback_stopped.emit()
    
    def _update_ui_recording(self):
        self.record_btn.setEnabled(False)
        self.play_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("GRAVANDO...")
        self.status_label.setStyleSheet(STATUS_RECORDING)
    
    def _update_ui_playing(self):
        self.record_btn.setEnabled(False)
        self.play_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("EXECUTANDO...")
        self.status_label.setStyleSheet(STATUS_PLAYING)
    
    def _update_ui_idle(self):
        self.record_btn.setEnabled(True)
        self.play_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("Pronto")
        self.status_label.setStyleSheet(STATUS_IDLE)
    
    def _update_status(self):
        pass
    
    def _save_config(self):
        self.config.playback_speed = self.speed_spin.value()
        self.config.repeat_count = self.repeat_spin.value()
        self.config.force_stop_key = self.stop_key_input.text() or "q"
        self.config.record_start_key = self.record_start_input.text() or "f9"
        self.config.record_stop_key = self.record_stop_input.text() or "f10"
        self.config.save()
        self._update_shortcuts()
    
    def closeEvent(self, event):
        if self.recorder.recording:
            self.recorder.stop()
        if self.player.playing:
            self.player.stop()
        event.accept()