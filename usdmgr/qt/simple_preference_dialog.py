import os
from PySide2.QtCore import Qt, QStandardPaths, QSignalBlocker, QSize
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QAction,
    QComboBox,
    QDockWidget,
    QToolButton,
    QLineEdit,
    QFileDialog,
    QListWidget,
    QListWidgetItem,
    QDialog,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSlider,
)
from usdmgr.config import Config


class SimplePreferenceDialog:
    def __init__(self, parent, resourcePath):
        from PySide2.QtUiTools import QUiLoader
        self._resourcePath = resourcePath
        self._restart = False
        self.ui: QDialog = QUiLoader().load(os.path.join(self._resourcePath, "simple_preference_dialog.ui"), parent)
        self.ui.setWindowTitle("Preference...")

        dirp = os.path.abspath(Config.getInstance().getValue(
            "se.configDirectory", QStandardPaths.writableLocation(
                QStandardPaths.AppConfigLocation)))

        self.leConfigDirectory: QLineEdit = self.ui.leConfigDirectory
        self.leConfigDirectory.setText(dirp)

        self.tbConfigDirectory: QToolButton = self.ui.tbConfigDirectory

        self.tbConfigDirectory.clicked.connect(
            lambda *, w=self.leConfigDirectory: self._openDialogBrowserAndSet(w))
        self.leConfigDirectory.textChanged.connect(self._e_onConfigDirectoryChanged)

    def _openDialogBrowserAndSet(self, widget):
        ret = QFileDialog.getExistingDirectory(self.ui, "Choose Directory", widget.text())
        if ret:
            self.leConfigDirectory.setText(ret)

    def _e_onConfigDirectoryChanged(self):
        confdir = self.leConfigDirectory.text()
        if confdir and os.path.isdir(confdir):
            Config.getInstance().setValue("se.configDirectory", confdir)
            self.leConfigDirectory.setStyleSheet("font-family: arial;")
        else:
            self.leConfigDirectory.setStyleSheet("font-family: arial; background: #FFCCCC;")

    @classmethod
    def showDialog(cls, parent, resourcePath):
        dialog = cls(parent, resourcePath)
        dialog.ui.exec_()
