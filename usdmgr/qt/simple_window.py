import os
from PySide2.QtCore import Qt, QStandardPaths, QSignalBlocker
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QAction,
    QComboBox,
    QDockWidget,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
)


class SignalBlocker:
    def __init__(self, widget):
        self._widget = widget

    def __enter__(self):
        self._blocker = QSignalBlocker(self._widget)

    def __exit__(self, *_):
        self._blocker.unblock()


class SimpleWindow:
    def __init__(self, resourcePath):
        from PySide2.QtUiTools import QUiLoader
        self._resourcePath = resourcePath
        self.ui: QMainWindow = QUiLoader().load(os.path.join(self._resourcePath, "simple_window.ui"), None)
        self.ui.setWindowTitle("USD Manager - Simple")

        # fetch
        self.actionOpenEnvironmentJson: QAction = self.ui.actionOpenEnvironmentJson
        self.actionOpenToolsJson: QAction = self.ui.actionOpenToolsJson
        self.actionReloadSettingsJson: QAction = self.ui.actionReloadSettingsJson
        self.actionExit: QAction = self.ui.actionExit
        self.menuWindow: QMenu = self.ui.menuWindow
        self.cbUSDEnvironment: QComboBox = self.ui.cbUSDEnvironment
        self.lwTools: QListWidget = self.ui.lwTools
        self.pbOpenUsdView: QPushButton = self.ui.pbOpenUsdView
        self.lwUsdViewHistory: QListWidget = self.ui.lwUsdViewHistory
        self.pteEnvironment: QPlainTextEdit = self.ui.pteEnvironment
        self.dwLog: QDockWidget = self.ui.dwLog
        self.pteLog: QPlainTextEdit = self.ui.pteLog

        self.menuWindow.addAction(self.dwLog.toggleViewAction())
        self.lwTools.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lwTools.customContextMenuRequested.connect(self._e_onToolsCustomContextMenuRequested)

        # load jsons
        self._configDirpath = QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)
        if not self._configDirpath:
            raise RuntimeError("No directory path to save tool config file.")
        self._environmentFilepath = os.path.join(self._configDirpath, "env.json")
        self._toolsFilepath = os.path.join(self._configDirpath, "tools.json")
        self._environment = None
        self._tools = None
        self._icons = dict()

        # load config
        self._loadEnvironmentJson()
        self._loadToolsJson()

        # connect
        self.actionOpenToolsJson.triggered.connect(self._openToolsJson)
        self.actionOpenEnvironmentJson.triggered.connect(self._openEnvironmentsJson)
        self.actionReloadSettingsJson.triggered.connect(self._reloadConfigAndWidgets)
        self.cbUSDEnvironment.currentIndexChanged.connect(self._onCurrentEnvironmentChanged)
        self.lwTools.itemClicked.connect(self._e_onToolClicked)

        # initialize widget
        self._initializeWidget()

    def _getIcon(self, filepath: str) -> QIcon:
        if filepath not in self._icons:
            if os.path.isabs(filepath) and os.path.exists(filepath):
                icon = QIcon(filepath)
            else:
                if os.path.exists(os.path.join(self._configDirpath, filepath)):
                    icon = QIcon(os.path.join(self._configDirpath, filepath))
                elif os.path.exists(os.path.join(self._resourcePath, "icons", filepath)):
                    icon = QIcon(os.path.join(self._resourcePath, "icons", filepath))
                else:
                    icon = QIcon(os.path.join(self._resourcePath, "icons", "default_tool_icon.png"))
            self._icons[filepath] = icon
        return self._icons[filepath]

    def _initializeWidget(self):
        self.cbUSDEnvironment
        envs = self._environment.get("environments", list())
        self.cbUSDEnvironment.clear()
        for env in envs:
            self.cbUSDEnvironment.addItem(env.get("label", ""), env)

    def _loadEnvironmentJson(self):
        import json
        os.makedirs(os.path.dirname(self._environmentFilepath), exist_ok=True)
        if not os.path.exists(self._environmentFilepath):
            initialData = dict()
            envs = list()
            envs.append(
                dict(
                    label="Template - Label",
                    usdRoot=dict(
                        release="path/to/release/root",
                        debug="path/to/debug/root"),
                    usdVersion="YYMM",
                    python=dict(
                        version=[3, 9],
                        venv="path/to/venv")))
            initialData["environments"] = envs
            with open(self._environmentFilepath, mode="w", encoding="utf-8") as fp:
                json.dump(initialData, fp, indent=4)
        with open(self._environmentFilepath, mode="r", encoding="utf-8") as fp:
            self._environment = json.load(fp)

    def _loadToolsJson(self):
        import json
        os.makedirs(os.path.dirname(self._toolsFilepath), exist_ok=True)
        if not os.path.exists(self._toolsFilepath):
            initialData = dict()
            envs = list()
            envs.append(
                dict(
                    label="ToolName",
                    release=True,
                    debug=True,
                    requirePython=False,
                    iconPath="path/to/icon.png",
                    cmdline="notepad.txt",
                    workingDir=".",
                    envvars=dict(
                        PATH="path/to/additional/path;${PATH}"),
                    subEntries=list(
                        [
                            dict(
                                label="Sub entry label 1",
                                cmdline="notepad.txt /v",
                                workingDir=".",
                                envvars=dict()),
                            dict(
                                label="Sub entry label 2",
                                cmdline="notepad.txt /v",
                                workingDir=".",
                                envvars=dict()),
                        ])))
            initialData["tools"] = envs
            with open(self._toolsFilepath, mode="w", encoding="utf-8") as fp:
                json.dump(initialData, fp, indent=4)
        with open(self._toolsFilepath, mode="r", encoding="utf-8") as fp:
            self._tools = json.load(fp)

    def _openToolsJson(self):
        os.startfile(self._toolsFilepath)

    def _openEnvironmentsJson(self):
        os.startfile(self._environmentFilepath)

    def _reloadConfigAndWidgets(self):
        self._loadToolsJson()
        self._loadEnvironmentJson()
        self._initializeWidget()

    def _onCurrentEnvironmentChanged(self, index):
        if index == -1:
            self.lwTools.clear()
        elif index < self.cbUSDEnvironment.count():
            self._initializeTools()

    def _initializeTools(self):
        self.lwTools.clear()
        currentEnv = self.cbUSDEnvironment.currentData()
        withPython = (currentEnv.get("python", None) is not None)
        for tool in self._tools.get("tools", list()):
            if tool.get("hidden", False) is True:
                continue
            requirePython = tool.get("requirePython", False)
            if requirePython is True and not withPython:
                # python が必須だが, python がこの env にない.
                continue

            iconFilepath = tool.get("iconPath", None)
            icon = self._getIcon(iconFilepath) if iconFilepath else None
            if icon:
                item = QListWidgetItem(icon, tool.get("label", ""))
            else:
                item = QListWidgetItem(tool.get("label", ""))
            item.setData(Qt.UserRole, tool)
            item.setToolTip(tool.get("label", ""))

            self.lwTools.addItem(item)

    def _e_onToolClicked(self, item: QListWidgetItem):
        if item:
            toolData = item.data(Qt.UserRole)
            self.startupTool(toolData)

    def startupTool(
            self,
            toolData: dict,
            *,
            debug: bool = False,
            overrideCmdLine=None,
            overrideCwd=None,
            overrideEnv=None):
        import subprocess
        if not toolData:
            return
        cmdline = toolData.get("cmdline", None)
        if not cmdline:
            QMessageBox.critical(self, "Error", "Failed to startup tool. \"cmdline\" is empty.")
            return

        toolLabel = toolData.get("label", "<No Titled Tool>")
        self.pteLog.clear()
        self.pteLog.appendPlainText("Execute tool: {}".format(toolLabel))

        usdenv = self.cbUSDEnvironment.currentData(Qt.UserRole)
        withPython = (usdenv.get("python", None) is not None)
        requirePython = toolData.get("requirePython", False)
        if requirePython is True and not withPython:
            # python が必須だが, python がこの env にない.
            QMessageBox.critical(self, "Error", "Required python, but this envrionment has no python.")
            return

        env = dict(os.environ)
        for key, value in toolData.get("envvars", dict()).items():
            expanded = os.path.expandvars(value)
            env[key] = expanded

        def _toUpperKey(key: str):
            if key.lower() in env:
                env[key.upper()] = env[key.lower()]
                del env[key.lower()]
        _toUpperKey("PATH")
        _toUpperKey("PXR_PLUGINPATH_NAME")
        _toUpperKey("PYTHONPATH")

        cwd = self._configDirpath
        if "workingDir" in toolData:
            cwd = os.path.expandvars(toolData["workingDir"])

        cmdline = os.path.expandvars(cmdline)

        # path, pythonpath, pluginpath を錬成する
        usdRoot = ""
        if debug and "debug" in usdenv.get("usdRoot", dict()):
            usdRoot = usdenv["usdRoot"]["debug"]
        elif not debug and "release" in usdenv.get("usdRoot", dict()):
            usdRoot = usdenv["usdRoot"]["release"]

        venv = ""
        if requirePython is True:
            venv = usdenv.get("python", dict()).get("venv", None)
            if venv:
                env["PATH"] = "{}/Scripts;{}".format(venv, env["PATH"])
                env["PYTHONPATH"] = "{}/Lib/site-packages;{}".format(venv, env["PYTHONPATH"])

        env["PATH"] = "{0}/bin;{0}/lib;{1}".format(usdRoot, env["PATH"])
        if requirePython:
            env["PYTHONPATH"] = "{}/lib/python;{}".format(usdRoot, env["PYTHONPATH"])

        # Plugin を探す.
        pluginSearchPaths = self._environment.get("plugins", dict()).get("searchPaths", list())

        usdVersion = usdenv.get("usdVersion", "_")
        pythonVersion = "_"
        configVariant = "debug" if debug else "release"
        if requirePython:
            version = usdenv.get("version", None)
            if version is not None:
                pythonMajor, pythonMinor = version
            else:
                ret = subprocess.run(["python", "--version"],
                                     env=dict(PATH=f"{venv}/Scripts"),
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     encoding="utf-8")
                if ret.returncode != 0:
                    QMessageBox.critical("Error", "Failed to get python version.")
                    return
                pythonMajor, pythonMinor = (int(v) for v in ret.stdout[len("Python "):].split(".")[0:2])
                usdenv["version"] = [pythonMajor, pythonMinor]
            pythonVersion = f"py{pythonMajor}{pythonMinor}"

        self.pteLog.appendPlainText(f"- USD Version = {usdVersion}")
        self.pteLog.appendPlainText(f"- python Version = {pythonVersion}")
        self.pteLog.appendPlainText(f"- Config = {configVariant}")

        env["PROMPT"] = f"({usdVersion}/{pythonVersion}/{configVariant}) $P$G"

        import glob
        for path in pluginSearchPaths:
            if not os.path.isdir(path):
                self.pteLog.appendPlainText(f"- Plugin search path '{path}' is not directory.")
                continue
            for pluginfoPath in glob.glob(
                    f"{path}/**/{usdVersion}/{pythonVersion}/{configVariant}/plugin/plugInfo.json",
                    recursive=True):
                self.pteLog.appendPlainText(f"- plugInfo found: {pluginfoPath}")
                pluginRootPath = os.path.dirname(os.path.dirname(pluginfoPath))
                env["PATH"] = "{}/plugin;{}".format(pluginRootPath, env["PATH"])
                env["PXR_PLUGINPATH_NAME"] = "{}/plugin;{}".format(pluginRootPath, env["PXR_PLUGINPATH_NAME"])
                if os.path.isdir(f"{pluginRootPath}/bin"):
                    env["PATH"] = "{}/bin;{}".format(pluginRootPath, env["PATH"])
                if requirePython and os.path.isdir(f"{pluginRootPath}/python"):
                    env["PYTHONPATH"] = "{}/python;{}".format(pluginRootPath, env["PYTHONPATH"])
                if requirePython and os.path.isdir(f"{pluginRootPath}/usdview"):
                    env["PXR_PLUGINPATH_NAME"] = "{}/usdview;{}".format(pluginRootPath, env["PXR_PLUGINPATH_NAME"])
                    env["PYTHONPATH"] = "{}/usdview;{}".format(pluginRootPath, env["PYTHONPATH"])

        self.pteLog.appendPlainText("- PATH = {}".format(env.get("PATH", "<NONE>")))
        self.pteLog.appendPlainText("- PYTHONPATH = {}".format(env.get("PYTHONPATH", "<NONE>")))
        self.pteLog.appendPlainText("- PXR_PLUGINPATH_NAME = {}".format(env.get("PXR_PLUGINPATH_NAME", "<NONE>")))
        self.pteLog.appendPlainText("- Working Directory = {}".format(cwd))
        self.pteLog.appendPlainText("- Command Line = {}".format(cmdline))

        try:
            subprocess.Popen(cmdline, env=env, shell=True, cwd=cwd)
            self.ui.statusBar().showMessage(f"Execute! {toolLabel}", 5000)
        except subprocess.SubprocessError as e:
            self.pteLog.appendPlainText(f"Failed to execute subprocess. {e}")

    def _e_onToolsCustomContextMenuRequested(self, p):
        index = self.lwTools.itemAt(p)
        if not index:
            return
        menu = QMenu()
        debugMenu = None
        gp = self.lwTools.mapToGlobal(p)
        toolData = index.data(Qt.UserRole)
        isDebug = toolData.get("debug", False)
        actions = list()
        if isDebug is True:
            debugMenu = QMenu()
            debugMenu.setTitle("Debug...")
            menu.addMenu(debugMenu)
            actionDebug = QAction("Run in debug")
            actionDebug.triggered.connect(
                lambda *, t=toolData: self.startupTool(t, debug=True))
            debugMenu.addAction(actionDebug)
            debugMenu.addSeparator()
            actions.append(actionDebug)

        for subentry in toolData.get("subEntries", list()):
            if "cmdline" not in subentry:
                continue
            actionSubEntryRelease = QAction(subentry.get("label", "<Subentry>"))
            actionSubEntryRelease.triggered.connect(lambda *, t=toolData, s=subentry:
                                                    self.startupTool(
                                                        t,
                                                        overrideCmdLine=s["cmdline"],
                                                        overrideCwd=s.get("workingDir", None),
                                                        overrideEnv=s.get("envvars", None)))
            menu.addAction(actionSubEntryRelease)
            actions.append(actionSubEntryRelease)

            if isDebug:
                actionSubEntryDebug = QAction("[DEBUG] " + subentry.get("label", "<Subentry>"))
                actionSubEntryDebug.triggered.connect(lambda *, t=toolData, s=subentry:
                                                      self.startupTool(
                                                          t,
                                                          debug=True,
                                                          overrideCmdLine=s["cmdline"],
                                                          overrideCwd=s.get("workingDir", None),
                                                          overrideEnv=s.get("envvars", None)))
                actions.append(actionSubEntryDebug)
                debugMenu.addAction(actionSubEntryDebug)

        menu.exec_(gp)

    def showWindow(self):
        self.ui.show()
