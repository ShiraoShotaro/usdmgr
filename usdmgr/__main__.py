
if __name__ == "__main__":
    from PySide2.QtWidgets import QApplication
    from usdmgr.config import Config
    from usdmgr.qt.main_window import MainWindow

    if not Config.initialize():
        exit(1)

    app = QApplication()
    window = MainWindow()
    window.showWindow()
    exit(app.exec_())
