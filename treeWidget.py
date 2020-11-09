import os
import sys
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
# from PySide2 import QtCore
from ButtonInLabel import ButtonInLabel
# QtCore.QCoreApplication.addLibraryPath(os.path.join(os.path.dirname(QtCore.__file__), "plugins"))  # 掃plugin套件(windows必備)

class TreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 建立QTreeWidget，但如果預設自己就是QTreeWidget則不要再定義
        # self = QTreeWidget()  

        # Set column count.
        self.setColumnCount(2)

        # Set label.
        self.setHeaderLabels(['key', 'Value'])

        # Create root item.(父節點)
        root01 = QTreeWidgetItem(self)
        root01.setText(0, 'Adam')
        root02 = QTreeWidgetItem(self)
        root02.setText(0, 'Input')
        root03 = QTreeWidgetItem(self)
        root03.setText(0, 'Data')

        # Create child node.
        ############### root01 ###############
        ### Row 1 or root01
        self.child01_01 = QTreeWidgetItem()
        self.child01_01.setText(0, 'id')
        self.child01_01.setText(1, 'CHP10')
        root01.addChild(self.child01_01)

        ### Row 2 or root01
        self.child01_02 = QTreeWidgetItem()
        self.child01_02.setText(0, 'ip')
        self.child01_02.setText(1, '192.168.0.140')
        root01.addChild(self.child01_02)

        ############### root02 ###############
        ### Row 1 or root02
        self.child02_01 = QTreeWidgetItem()
        self.child02_01.setText(0, 'Input data path')
        root02.addChild(self.child02_01)
        # Create label with toolbutton.
        self.labelBtn = ButtonInLabel('File path')
        self.setItemWidget(self.child02_01, 1, self.labelBtn)
        
        ### Row 2 or root02
        self.child02_02 = QTreeWidgetItem()
        self.child02_02.setText(0, 'Folder name')
        self.child02_02.setText(1, 'test')
        root02.addChild(self.child02_02)

        ############### root01 ###############
        ### Row 1 or root03
        self.child03_01 = QTreeWidgetItem()
        self.child03_01.setText(0, 'Freq')
        self.child03_01.setText(1, '100')
        root03.addChild(self.child03_01)

        ### Row 2 or root03
        self.child03_02 = QTreeWidgetItem()
        self.child03_02.setText(0, 'Size of train set')
        self.child03_02.setText(1, '30')
        root03.addChild(self.child03_02)

        ### Row 3 or root03
        self.child03_03 = QTreeWidgetItem()
        self.child03_03.setText(0, 'Current truncate start')
        self.child03_03.setText(1, '30')
        root03.addChild(self.child03_03)

        ### Row 4 or root03
        self.child03_04 = QTreeWidgetItem()
        self.child03_04.setText(0, 'Cut length')
        self.child03_04.setText(1, '500')
        root03.addChild(self.child03_04)

        ### Row 5 or root03
        self.child03_05 = QTreeWidgetItem()
        self.child03_05.setText(0, 'Boundary of cum-EV')
        self.child03_05.setText(1, '0.95')
        root03.addChild(self.child03_05)

        # Set column editable.
        self.openPersistentEditor(self.child01_01, 1)
        self.openPersistentEditor(self.child01_02, 1)
        self.openPersistentEditor(self.child02_02, 1)
        self.openPersistentEditor(self.child03_01, 1)
        self.openPersistentEditor(self.child03_02, 1)
        self.openPersistentEditor(self.child03_03, 1)
        self.openPersistentEditor(self.child03_04, 1)
        self.openPersistentEditor(self.child03_05, 1)

        # Connect event.
        ## Connect event that item is edited.
        self.itemDoubleClicked.connect(self.slot_treeWidget)
        ## Connect event when clicked icon.
        self.labelBtn.connect(
            self.labelBtn.iconButton, 
            SIGNAL('clicked()'), 
            self.slot_file_dialog
        )

        # Add top item.
        self.addTopLevelItem(root01)

        # Expand all tree.
        self.expandAll()

        # self.setCentralWidget(self)

    def slot_treeWidget(self, item, column_count):
        if item == self.child02_01:
            self.slot_file_dialog()
        else:
            print(item.text(column_count))

    def slot_file_dialog(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Open file', '', '*.txt')
        self.labelBtn.setText(file)
        self.labelBtn.setToolTip(file)
        # self.labelBtn.setWordWrap(True)
        width = self.labelBtn.fontMetrics().boundingRect(self.labelBtn.text()).width()
        self.setColumnWidth(1, width + 25)


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     tree = TreeWidget()
#     tree.show()
#     sys.exit(app.exec_())
