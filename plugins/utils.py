from typing import Optional, List
import venv
import os
import subprocess


def pullGitRepo(repoPath: str, branch: str = "master"):
    import git
    repo = git.Repo(repoPath)
    targetHead = None
    for head in repo.heads:
        if head.name == branch:
            targetHead = head
            break
    else:
        raise RuntimeError(f"Failed to find branch name. {branch}")

    targetHead.checkout()
    repo.remote("origin").pull()


def createBuildDirectory(buildDirectory: str):
    import shutil
    if os.path.exists(buildDirectory):
        shutil.rmtree(buildDirectory)
    os.makedirs(buildDirectory)


class PythonEnv(venv.EnvBuilder):
    def __init__(self):
        super().__init__(with_pip=True)
        self._context = None

    def post_setup(self, context):
        self._context = context
        super().post_setup(context)

    def executePython(self, *args, env=None, cwd=None):
        cmd = [self._context.env_exec_cmd] + list(args)
        print("venv:executePython", cmd)
        subprocess.check_output(cmd, env=env, cwd=cwd)

    def executeShell(self, *args, cwd=None):
        cmd = ["call", os.path.join(self._context.bin_path, "activate"), "&"] + list(args)
        print("venv:executeShell", cmd)
        subprocess.check_call(cmd, shell=True, cwd=cwd)


def createPythonEnv(buildDirectory: str):
    env = PythonEnv()
    env.create(f"{buildDirectory}/.env")
    return env


def installConanV1(sourceDirectory: str, buildDirectory: str, env: PythonEnv, *conanInstallArgs):
    env.executePython("-m", "pip", "install", "conan==1.64.1")
    env.executeShell("conan", "install", sourceDirectory, *conanInstallArgs, cwd=buildDirectory)


def buildConanV1(sourceDirectory: str, buildDirectory: str, env: PythonEnv, *conanBuildArgs):
    env.executePython("-m", "pip", "install", "conan==1.64.1")
    env.executeShell("conan", "build", sourceDirectory, "-bf", buildDirectory, *conanBuildArgs, cwd=buildDirectory)


def cmakeBuild(buildDirectory: str, env: PythonEnv, *cmakeBuildArgs):
    env.executePython("-m", "pip", "install", "cmake")
    env.executeShell("cmake", "build", buildDirectory, *cmakeBuildArgs, cwd=buildDirectory)


def cmakeConfigure(sourceDirectory: str, buildDirectory: str, *cmakeConfigureArgs):
    subprocess.check_call(
        ["cmake", "configure", "-S", sourceDirectory, "-B", buildDirectory] + list(cmakeConfigureArgs),
        cwd=buildDirectory)
