from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout
app = QApplication([])
window = QWidget()
layout = QHBoxLayout()
layout.addWidget(QPushButton('Top'))
layout.addWidget(QPushButton('Bottom'))
window.setLayout(layout)
window.show()
app.exec()