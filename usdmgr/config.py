

class Config:
    _instance = None

    def __init__(self, filepath: str):
        self._filepath = filepath
        self._config = dict()

    @classmethod
    def initialize(cls) -> bool:
        """ 設定ファイルを読み込む. """
        import os
        from PySide2.QtCore import QStandardPaths
        if cls._instance is not None:
            return True
        dirpath = QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)
        if not dirpath:
            print("No directory path to save tool config file.")
            return False
        os.makedirs(dirpath, exist_ok=True)
        filepath = os.path.join(dirpath, "config.json")
        cls._instance = cls(filepath)
        if os.path.exists(filepath):
            import json
            try:
                with open(filepath, mode="r", encoding="utf-8") as fp:
                    cls._instance._config = json.load(fp)
            except BaseException as e:
                print(f"Failed to load config file. {filepath}, {e}")
        return True

    @classmethod
    def getInstance(cls):
        return cls._instance

    def save(self) -> bool:
        import json
        try:
            with open(self._filepath, mode="w", encoding="utf-8") as fp:
                json.dump(self._config, fp, ensure_ascii=True, indent=4)
            return True
        except BaseException as e:
            print(f"Failed to save config. {self._filepath}, {e}")
            return False

    def getValue(self, key: str, defaultValue=None):
        return self._config.get(key, defaultValue)

    def setValue(self, key: str, value, *, with_save=False):
        """ 値を設定する. value に None を指定すると, 指定のキーを削除する. """
        if value is not None:
            self._config[key] = value
        elif key in self._config:
            del self._config[key]
        if with_save:
            self.save()
