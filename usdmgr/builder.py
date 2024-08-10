import subprocess
import urllib.request
import glob
import sys
import os
import tempfile
import venv
import shutil


# Python は各自 install してください
python3 = {
    "v9": "C:/Users/shirao/AppData/Local/Programs/Python/Python39",
    "v10": "C:/Users/shirao/AppData/Local/Programs/Python/Python310",
    "v11": "C:/Users/shirao/AppData/Local/Programs/Python/Python311",
}


# msvc17 / 16 の BuildTool を install してください
msvc = "C:/Program Files (x86)/Microsoft Visual Studio"


msvcVersions = {
    17: 2022,
    16: 2019,
}


vfxReference = {
    "CY2025": {
        "msvc": [17, 4, None],
        "python": [3, 12, None],
        "pyside": [6, 5, None],
        "numpy": [1, 26, None],
    },
    "CY2024": {
        "msvc": [17, 4, None],
        "python": [3, 11, None],
        "pyside": [6, 5, None],
        "numpy": [1, 24, None],
    },
    "CY2023": {
        "msvc": [17, 4, None],
        "python": [3, 10, None],
        "pyside": [5, 15, None],
        "numpy": [1, 23, None],
    },
}


usdVersions = {
    "v24.08": {
        "url": "https://github.com/PixarAnimationStudios/OpenUSD/archive/refs/tags/v24.08.zip",
        "major": 24,
        "minor": 8,
    },
    "v24.05": {
        "url": "https://github.com/PixarAnimationStudios/OpenUSD/archive/refs/tags/v24.05.zip",
        "major": 24,
        "minor": 5,
    },
    "v24.03": {
        "url": "https://github.com/PixarAnimationStudios/OpenUSD/archive/refs/tags/v24.03.zip",
        "major": 24,
        "minor": 3,
    },
    "v23.11": {
        "url": "https://github.com/PixarAnimationStudios/OpenUSD/archive/refs/tags/v23.11.zip",
        "major": 23,
        "minor": 11,
    },
    "v23.05": {
        "url": "https://github.com/PixarAnimationStudios/OpenUSD/archive/refs/tags/v23.05.zip",
        "major": 23,
        "minor": 5,
    },
    "v23.02": {
        "url": "https://github.com/PixarAnimationStudios/OpenUSD/archive/refs/tags/v23.02.zip",
        "major": 23,
        "minor": 2,
    }
}


class BuildEnv:
    @classmethod
    def getPython(cls, minor: int, debug: bool = False, *, check: bool = True):
        try:
            path = python3[f"v{minor}"]
            path = os.path.join(path, "python.exe" if debug is False else "python_d.exe")
            if check:
                if not os.path.exists(path):
                    return None
            return path

        except KeyError:
            return None

    @classmethod
    def getMSVCBatfile(cls, version: int, *, check: bool = True):
        year = msvcVersions[version]
        path = os.path.join(msvc, str(year), "BuildTools", "VC", "Auxiliary", "Build", "vcvars64.bat")
        if check:
            if not os.path.exists(path):
                return None
        return path


class PythonVenvBuilder(venv.EnvBuilder):
    def __init__(self, pythonExecutable, pysideVersion, numpyVersion):
        super().__init__(with_pip=True)
        self._pysideVersion = pysideVersion
        self._numpyVersion = numpyVersion
        self._pythonExecutable = pythonExecutable
        self._context = None

    def ensure_directories(self, env_dir):
        context = super().ensure_directories(env_dir)
        context.executable = self._pythonExecutable
        dirname, exename = os.path.split(os.path.abspath(self._pythonExecutable))
        context.python_dir = dirname
        context.python_exe = exename
        context.env_exe = os.path.join(context.bin_path, exename)
        context.env_exec_cmd = context.env_exe
        if sys.platform == 'win32':
            # bpo-45337: Fix up env_exec_cmd to account for file system redirections.
            # Some redirects only apply to CreateFile and not CreateProcess
            real_env_exe = os.path.realpath(context.env_exe)
            if os.path.normcase(real_env_exe) != os.path.normcase(context.env_exe):
                context.env_exec_cmd = real_env_exe
        self._context = context
        return context

    def post_setup(self, context):
        deps = list()
        if self._pysideVersion is not None:
            deps.append(
                "PySide{}{}{}{}".format(
                    6 if self._pysideVersion[0] >= 6 else 2,
                    f"=={self._pysideVersion[0]}" if self._pysideVersion[0] is not None else "",
                    f".{self._pysideVersion[1]}" if self._pysideVersion[1] is not None else ".*",
                    f".{self._pysideVersion[2]}" if self._pysideVersion[2] is not None else ".*"))
            deps.append("PyOpenGL")
        if self._numpyVersion is not None:
            deps.append(
                "numpy{}{}{}".format(
                    f"=={self._numpyVersion[0]}" if self._numpyVersion[0] is not None else "",
                    f".{self._numpyVersion[1]}" if self._numpyVersion[1] is not None else ".*",
                    f".{self._numpyVersion[2]}" if self._numpyVersion[2] is not None else ".*"))

        if deps:
            deps.append("jinja2")
            subprocess.check_call([self._context.env_exec_cmd, "-u", "-m", "pip", "install"] + deps)
        super().post_setup(context)

    def executeScript(self, args: list, cwd: str, *, batfile=None):
        subprocess.check_call(
            ["call", batfile, "&", os.path.join(self._context.bin_path, "python.exe")] + args,
            shell=True, cwd=cwd)


class USDBuilder:
    def __init__(self, usdVersion: str, cyVersion: str, destination: str):
        self._usdVersion = usdVersions[usdVersion]
        self._cyVersion = vfxReference[cyVersion]
        self._destination = destination

    def build(self, *, debug: bool = False, python: bool = False):
        import time
        with tempfile.TemporaryDirectory() as tmpdir:
            print(tmpdir)
            usdroot = self._downloadUSD(tmpdir)
            venvBuilder = self._createPythonEnv(tmpdir, python, debug)
            self._executeBuildScript(usdroot, tmpdir, venvBuilder, python, debug)
            self._install(usdroot, tmpdir, self._destination, python, debug)
            time.sleep(1)

    def _downloadUSD(self, dest: str):
        print("Downloading...", self._usdVersion["url"])
        package_filepath = os.path.join(dest, "usd_package.zip")
        usd_dirpath = os.path.join(dest, "usd")
        urllib.request.urlretrieve(self._usdVersion["url"], package_filepath)
        shutil.unpack_archive(package_filepath, usd_dirpath)
        return os.path.dirname(glob.glob(os.path.join(dest, "usd", "*", "README.md"))[0])

    def _createPythonEnv(self, dest: str, withPython: bool, debug: bool):
        envpath = os.path.join(dest, "build_env")
        pythonExecutable = sys.executable
        if withPython:
            pythonVersion = self._cyVersion["python"]
            pythonExecutable = BuildEnv.getPython(pythonVersion[1], debug)
        if pythonExecutable is None:
            raise RuntimeError(f"No python executable. Required version: {pythonVersion}")

        envbuilder = PythonVenvBuilder(pythonExecutable, self._cyVersion["pyside"], self._cyVersion["numpy"])
        envbuilder.create(envpath)

        return envbuilder

    def _executeBuildScript(
            self,
            usdroot: str,
            dest: str,
            venvBuilder: PythonVenvBuilder,
            withPython: bool,
            debug: bool):
        buildPath = os.path.join(dest, "_build")
        installPath = os.path.join(dest, "_install")
        os.makedirs(buildPath)
        batfile = BuildEnv.getMSVCBatfile(self._cyVersion["msvc"][0])
        args = [
            "-u", "-X", "utf8", os.path.join(usdroot, "build_scripts", "build_usd.py"),
            "--build", buildPath,
            "--build-variant", "debug" if debug else "release",
            "--build-shared",
            "--tools",
            "--no-tests", "--no-examples", "--no-tutorials", "--no-docs",
            "--usd-imaging",
            "--no-openimageio", "--no-opencolorio",
            "--no-ptex", "--no-openvdb", "--no-embree", "--no-prman", "--no-alembic",
            "--no-hdf5", "--no-draco", "--no-materialx",
        ]
        if withPython is True:
            args.append("--python")
            if debug is True:
                args.append("--debug-python")
            else:
                args.append("--no-debug-python")
            args.append("--usdview")
        else:
            args.append("--no-python")
            args.append("--no-usdview")
            args.append("--no-debug-python")
        args.append(installPath)
        print(args)
        venvBuilder.executeScript(
            args,
            cwd=os.path.dirname(batfile),
            batfile=batfile)
        srcPath = os.path.join(installPath, "src")

        # src directory は消す.
        if os.path.exists(srcPath):
            shutil.rmtree(srcPath)

    def _install(self, usdroot, tmpdir: str, installDest: str, withPython: bool, debug: bool):
        installDest = os.path.join(
            installDest,
            f"{self._usdVersion['major']:02d}{self._usdVersion['minor']:02d}",
            f"py{self._cyVersion['python'][0]}{self._cyVersion['python'][1]}" if withPython is True else "_",
            "debug" if debug is True else "release")
        if os.path.exists(installDest):
            shutil.rmtree(installDest)
        os.makedirs(installDest, exist_ok=False)
        shutil.copytree(os.path.join(tmpdir, "_install"), installDest, dirs_exist_ok=True)

        if withPython:
            srcEnvpath = os.path.join(tmpdir, "build_env")
            dstEnvpath = os.path.join(installDest, "pyenv")
            shutil.copytree(srcEnvpath, dstEnvpath)
            venv.create(dstEnvpath)  # パスの更新


if __name__ == "__main__":
    buildSets = [  # usdversion, cyversion, with python?, is debug?
        # ("v24.08", "CY2024", False, False),
        # ("v24.08", "CY2024", False, True),
        # ("v24.08", "CY2024", True, False),
        # ("v24.08", "CY2024", True, True),
        # ("v24.05", "CY2024", False, False),
        # ("v24.05", "CY2024", False, True),
        # ("v24.05", "CY2024", True, False),
        # ("v24.05", "CY2024", True, True),
        # ("v24.03", "CY2024", False, False),
        # ("v24.03", "CY2024", False, True),
        ("v24.03", "CY2024", True, False),
        ("v24.03", "CY2024", True, True),
        # ("v23.11", "CY2023", False, False),
        # ("v23.11", "CY2023", False, True),
        ("v23.11", "CY2023", True, False),
        ("v23.11", "CY2023", True, True),
        # ("v23.05", "CY2023", False, False),
        # ("v23.05", "CY2023", False, True),
        ("v23.05", "CY2023", True, False),
        ("v23.05", "CY2023", True, True),
        # ("v23.02", "CY2023", False, False),
        ("v23.02", "CY2023", False, True),
        ("v23.02", "CY2023", True, False),
        ("v23.02", "CY2023", True, True),
    ]

    installDest = "S:/dist/pxr/openusd"

    for usdV, cyV, python, debug in buildSets:
        builder = USDBuilder(usdV, cyV, installDest)
        try:
            print("--------- BUILD ---------")
            print(f"-- USD Version: {usdV}")
            print(f"--  CY Version: {cyV}")
            print(f"--       debug: {debug}")
            print(f"--      python: {python}")
            builder.build(debug=debug, python=python)
        except Exception as e:
            print("!!ERROR:", e)
