import os
import subprocess
from . import utils
from .context import Context


REPO_PATH = os.path.join(os.path.dirname(__file__), "repos", "usdRemoteViewer")


def main(ctx: Context):
    # git pull
    utils.pullGitRepo(REPO_PATH, "main")

    # create build directory
    utils.createBuildDirectory(ctx.buildDirectory)

    # create python venv
    env = utils.createPythonEnv(ctx.buildDirectory)

    # pip install
    env.executePython("-m", "pip", "install", "grpcio==1.54.3", "grpcio-tools==1.54.3")

    # conan setup
    utils.installConanV1(
        REPO_PATH,
        ctx.buildDirectory,
        env,
        f"--output-folder={ctx.buildDirectory}",
        "--build", "missing",
        "-o", "USD=")

    # conan build
    # 最初は失敗する.
    try:
        utils.buildConanV1(REPO_PATH, ctx.buildDirectory, env,
                           "-c")
    except subprocess.CalledProcessError:
        pass

    # configure
    openusdDir = "S:/dist/pxr/openusd/2408/_/release"
    installTarget = "T:/test_install"
    utils.cmakeConfigure(REPO_PATH, ctx.buildDirectory,
                         f"-Dpxr_DIR={openusdDir}",
                         "--install-prefix", installTarget)

    # build
    utils.buildConanV1(REPO_PATH, ctx.buildDirectory, env, "-b")
