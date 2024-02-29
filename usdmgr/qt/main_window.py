import os
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QComboBox, QListWidget, QLabel, QTabWidget, QCheckBox, QTreeWidget, QTreeWidgetItem, QPushButton, QStackedWidget, QLineEdit, QToolButton, QAction
from usdmgr.config import Config


class MainWindow:
    def __init__(self):
        from PySide2.QtUiTools import QUiLoader
        self.ui = QUiLoader().load(os.path.join(os.path.dirname(__file__), "main_window.ui"), None)
        self.ui.setWindowTitle("USD Manager")

        # fetch
        self.pbConfig: QPushButton = self.ui.pbConfig
        self.cbUsdVersions: QComboBox = self.ui.cbUsdVersions
        self.cbPython: QComboBox = self.ui.cbPython
        self.cbOpenVBD: QCheckBox = self.ui.cbOpenVBD
        self.cbOIIO: QCheckBox = self.ui.cbOIIO
        self.cbOCIO: QCheckBox = self.ui.cbOCIO
        self.cbPtex: QCheckBox = self.ui.cbPtex
        self.lbHeader: QLabel = self.ui.lbHeader
        self.pbDownload: QPushButton = self.ui.pbDownload
        self.swSubPage: QStackedWidget = self.ui.swSubPage
        self.twTools: QTabWidget = self.ui.twTools
        self.pbAddNew: QPushButton = self.ui.pbAddNew
        self.twEnvSets: QTreeWidget = self.ui.twEnvSets
        self.swPage: QStackedWidget = self.ui.swPage
        self.lwTools: QListWidget = self.ui.lwTools
        self.lwUsdView: QListWidget = self.ui.lwUsdView
        self.leInstallRootDirectory: QLineEdit = self.ui.leInstallRootDirectory
        self.tbInstallRootDirectory: QToolButton = self.ui.tbInstallRootDirectory
        self.leDownloadTempDirectory: QLineEdit = self.ui.leDownloadTempDirectory
        self.tbDownloadTempDirectory: QToolButton = self.ui.tbDownloadTempDirectory
        self.twToolchains: QTreeWidget = self.ui.twToolchains
        self.actionOpenGithub: QAction = self.ui.actionOpenGithub
        self.actionExit: QAction = self.ui.actionExit

        # variables

        # initialize
        self.twEnvSets.clear()
        self.swPage.setCurrentIndex(0)

        self._buildEnvSetTree()

    def _buildEnvSetTree(self):
        """ EnvSetTree のアイテムを初期化する. """
        self.twEnvSets.clear()

        cfg = Config.getInstance()
        envRoots: list = cfg.getValue("envRoots", list())

        rootItems = list()

    def showWindow(self):
        self.ui.show()
