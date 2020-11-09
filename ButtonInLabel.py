from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

class ButtonInLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create ToolButton.
        self.iconButton = QToolButton(self)
        self.iconButton.setCursor(Qt.PointingHandCursor)
        self.iconButton.setFocusPolicy(Qt.NoFocus)
        self.iconButton.setIcon(QIcon('folder.png'))
        self.iconButton.setStyleSheet("background: transparent; border: none;")
        self.iconButton.setToolTip('Open folder...')

        # Create layout.
        layout = QHBoxLayout(self)
        layout.addWidget(self.iconButton, 0, Qt.AlignRight)
        ## Set layout.
        # layout.setSpacing(0)
        layout.setMargin(0)
