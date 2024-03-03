
def main(resourcePath: str):
    import sys
    from PySide2.QtWidgets import QApplication
    from usdmgr.config import Config
    # from usdmgr.qt.main_window import MainWindow
    from usdmgr.qt.simple_window import SimpleWindow

    app = QApplication()
    app.setApplicationName("usdmgr")
    app.setApplicationDisplayName("USD Manager")

    if not Config.initialize():
        sys.exit(1)

    restart = True
    while restart:
        window = SimpleWindow(resourcePath)
        window.showWindow()
        ret = app.exec_()
        Config.getInstance().save()
        if not (ret == 0 and window.restart):
            break
    sys.exit(ret)
