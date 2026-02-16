# Estilos CSS para a interface
MAIN_STYLE = """
QMainWindow {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
}

QMenuBar {
    background-color: #313244;
    color: #cdd6f4;
    border-bottom: 1px solid #45475a;
}

QMenuBar::item:selected {
    background-color: #585b70;
}

QMenu {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
}

QMenu::item:selected {
    background-color: #585b70;
}

QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 13px;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #b4befe;
}

QPushButton:pressed {
    background-color: #74c7ec;
}

QPushButton:disabled {
    background-color: #45475a;
    color: #6c7086;
}

QPushButton#recordButton {
    background-color: #f38ba8;
}

QPushButton#recordButton:hover {
    background-color: #fab387;
}

QPushButton#stopButton {
    background-color: #f38ba8;
}

QPushButton#stopButton:hover {
    background-color: #eba0ac;
}

QPushButton#playButton {
    background-color: #a6e3a1;
}

QPushButton#playButton:hover {
    background-color: #b9f2bc;
}

QLabel {
    color: #cdd6f4;
    padding: 5px;
}

QLineEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    padding: 5px;
    border-radius: 4px;
}

QSpinBox, QDoubleSpinBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    padding: 5px;
    border-radius: 4px;
}

QGroupBox {
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    margin-top: 10px;
    font-weight: bold;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}

QStatusBar {
    background-color: #313244;
    color: #cdd6f4;
}

QTabWidget::pane {
    border: 1px solid #45475a;
    background-color: #1e1e2e;
}

QTabBar::tab {
    background-color: #313244;
    color: #cdd6f4;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #585b70;
}

QTabBar::tab:hover:!selected {
    background-color: #45475a;
}
"""

STATUS_RECORDING = "color: #f38ba8; font-weight: bold;"
STATUS_PLAYING = "color: #a6e3a1; font-weight: bold;"
STATUS_IDLE = "color: #cdd6f4;"