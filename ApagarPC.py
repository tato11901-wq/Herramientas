import sys
import subprocess
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                               QLabel, QPushButton, QSpinBox, QMessageBox, QGridLayout, QGroupBox)
from PySide6.QtCore import QTimer, Qt

class ApagarPCApp(QWidget):
    def __init__(self):
        super().__init__()
        self.segundos_restantes = 0
        self.segundos_inicial = 0
        self.activo = False
        self.alerta_mostrada = False
        self.shutdown_programado_windows = False
        
        self.init_ui()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_contador)
        
    def init_ui(self):
        self.setWindowTitle("Temporizador de Apagado")
        self.resize(380, 480)
        
        # Estilo oscuro moderno (basado en Catppuccin)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                font-size: 14px;
            }
            QGroupBox {
                border: 1px solid #45475a;
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 15px;
                font-weight: bold;
                font-size: 13px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: #89b4fa;
            }
            QPushButton {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45475a;
            }
            QPushButton#btnProgramar {
                background-color: #89b4fa;
                color: #1e1e2e;
                font-size: 14px;
                margin-top: 10px;
            }
            QPushButton#btnProgramar:hover {
                background-color: #b4befe;
            }
            QPushButton#btnCancelar {
                background-color: #f38ba8;
                color: #1e1e2e;
                font-size: 14px;
                margin-top: 10px;
            }
            QPushButton#btnCancelar:hover {
                background-color: #eba0ac;
            }
            QSpinBox {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 6px;
                font-size: 16px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 25px;
            }
            QLabel#lblContador {
                font-size: 52px;
                font-weight: bold;
                color: #a6e3a1;
            }
            QLabel#lblEstado {
                color: #a6adc8;
                font-style: italic;
                font-size: 16px;
            }
        """)
        
        layout_principal = QVBoxLayout()
        layout_principal.setSpacing(15)
        layout_principal.setContentsMargins(25, 25, 25, 25)
        
        # --- Grupo: Tiempo Personalizado ---
        grupo_personalizado = QGroupBox("Tiempo Personalizado")
        layout_personalizado = QGridLayout()
        layout_personalizado.setSpacing(10)
        
        self.spin_horas = QSpinBox()
        self.spin_horas.setRange(0, 23)
        self.spin_horas.setAlignment(Qt.AlignCenter)
        
        self.spin_minutos = QSpinBox()
        self.spin_minutos.setRange(0, 59)
        self.spin_minutos.setAlignment(Qt.AlignCenter)
        
        layout_personalizado.addWidget(QLabel("Horas:"), 0, 0, Qt.AlignRight)
        layout_personalizado.addWidget(self.spin_horas, 0, 1)
        layout_personalizado.addWidget(QLabel("Minutos:"), 0, 2, Qt.AlignRight)
        layout_personalizado.addWidget(self.spin_minutos, 0, 3)
        
        btn_programar = QPushButton("Programar Apagado")
        btn_programar.setObjectName("btnProgramar")
        btn_programar.clicked.connect(self.iniciar_manual)
        layout_personalizado.addWidget(btn_programar, 1, 0, 1, 4)
        
        grupo_personalizado.setLayout(layout_personalizado)
        layout_principal.addWidget(grupo_personalizado)
        
        # --- Grupo: Accesos Rápidos ---
        grupo_rapido = QGroupBox("Accesos Rápidos")
        layout_rapido = QGridLayout()
        layout_rapido.setSpacing(10)
        
        btn_30m = QPushButton("30 min")
        btn_30m.clicked.connect(lambda: self.rapido(30))
        btn_1h = QPushButton("1 hora")
        btn_1h.clicked.connect(lambda: self.rapido(60))
        btn_2h = QPushButton("2 horas")
        btn_2h.clicked.connect(lambda: self.rapido(120))
        btn_4h = QPushButton("4 horas")
        btn_4h.clicked.connect(lambda: self.rapido(240))
        
        layout_rapido.addWidget(btn_30m, 0, 0)
        layout_rapido.addWidget(btn_1h, 0, 1)
        layout_rapido.addWidget(btn_2h, 1, 0)
        layout_rapido.addWidget(btn_4h, 1, 1)
        
        grupo_rapido.setLayout(layout_rapido)
        layout_principal.addWidget(grupo_rapido)
        
        # --- Botón Cancelar ---
        btn_cancelar = QPushButton("Cancelar Apagado")
        btn_cancelar.setObjectName("btnCancelar")
        btn_cancelar.clicked.connect(self.cancelar_apagado)
        layout_principal.addWidget(btn_cancelar)
        
        layout_principal.addSpacing(10)
        
        # --- Estado y Contador ---
        self.label_estado = QLabel("Sin temporizador activo")
        self.label_estado.setObjectName("lblEstado")
        self.label_estado.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(self.label_estado)
        
        self.label_contador = QLabel("--:--:--")
        self.label_contador.setObjectName("lblContador")
        self.label_contador.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(self.label_contador)
        
        layout_principal.addStretch()
        
        self.setLayout(layout_principal)
        
    def formatear_tiempo(self, segundos):
        h = segundos // 3600
        m = (segundos % 3600) // 60
        s = segundos % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
        
    def actualizar_contador(self):
        if self.activo and self.segundos_restantes > 0:
            self.segundos_restantes -= 1
            self.label_contador.setText(self.formatear_tiempo(self.segundos_restantes))
            
            # Alerta a 1 minuto y programar el apagado en Windows
            if self.segundos_inicial > 60 and self.segundos_restantes == 60 and not self.alerta_mostrada:
                self.alerta_mostrada = True
                
                # Ahora sí lo mandamos a Windows
                self.ejecutar_comando(["shutdown", "/s", "/t", "60"])
                self.shutdown_programado_windows = True
                
                # Intentar traer la ventana al frente
                self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
                self.activateWindow()
                self.raise_()
                
                respuesta = QMessageBox.question(
                    self, 
                    "Apagado inminente", 
                    "El PC se apagará en 1 minuto.\\n¿Deseas cancelar?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if respuesta == QMessageBox.Yes:
                    self.cancelar_apagado()
                    
        elif self.activo and self.segundos_restantes <= 0:
            self.label_contador.setText("Apagando...")
            self.activo = False
            self.timer.stop()

    def ejecutar_comando(self, comando):
        # CREATE_NO_WINDOW (0x08000000) evita que se abra la consola negra en Windows al ejecutar el comando
        subprocess.run(comando, creationflags=0x08000000)

    def programar_apagado(self, segundos):
        if segundos <= 0:
            QMessageBox.warning(self, "Tiempo inválido", "Selecciona un tiempo mayor a 0.")
            return

        if segundos <= 60:
            self.ejecutar_comando(["shutdown", "/s", "/t", str(segundos)])
            self.shutdown_programado_windows = True
        else:
            self.shutdown_programado_windows = False
        
        self.segundos_restantes = segundos
        self.segundos_inicial = segundos
        self.alerta_mostrada = False
        self.activo = True
        
        self.label_estado.setText("Apagado programado")
        self.label_contador.setText(self.formatear_tiempo(self.segundos_restantes))
        self.label_contador.setStyleSheet("color: #f9e2af;") # Color amarillo para indicar que está activo
        
        if not self.timer.isActive():
            self.timer.start(1000)

    def iniciar_manual(self):
        horas = self.spin_horas.value()
        minutos = self.spin_minutos.value()
        total = horas * 3600 + minutos * 60
        self.programar_apagado(total)

    def rapido(self, minutos):
        self.programar_apagado(minutos * 60)

    def cancelar_apagado(self):
        if self.activo:
            if getattr(self, 'shutdown_programado_windows', True):
                self.ejecutar_comando(["shutdown", "/a"])
                self.shutdown_programado_windows = False
            self.activo = False
            self.timer.stop()
            self.label_estado.setText("Apagado cancelado")
            self.label_contador.setText("--:--:--")
            self.label_contador.setStyleSheet("color: #a6e3a1;") # Vuelve al verde
            QMessageBox.information(self, "Cancelado", "El apagado ha sido cancelado.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = ApagarPCApp()
    ventana.show()
    sys.exit(app.exec())
