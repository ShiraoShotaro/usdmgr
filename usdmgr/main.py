
def main(resourcePath: str):
    import sys
    from PySide2.QtWidgets import QApplication
    from usdmgr.config import Config
    # from usdmgr.qt.main_window import MainWindow
    from usdmgr.qt.simple_window import SimpleWindow

    if not Config.initialize():
        sys.exit(1)

    app = QApplication()
    app.setApplicationName("usdmgr")
    app.setApplicationDisplayName("USD Manager")
    window = SimpleWindow(resourcePath)
    window.showWindow()
    sys.exit(app.exec_())
