

if __name__ == "__main__":
    import os
    import argparse
    import importlib
    from plugins.context import Context
    parser = argparse.ArgumentParser()
    parser.add_argument("appName", type=str)
    parser.add_argument(
        "--build",
        type=str, default=None,
        help="Build directory path. (Default: %TEMP%/<AppName>/build)")
    args = parser.parse_args()

    ctx = Context(
        os.path.expandvars(f"%TEMP%/{args.appName}/build") if args.build is None else args.build
    )
    print(f"Build Directory: {ctx.buildDirectory}")

    module = importlib.import_module(f"plugins.{args.appName}")
    module.main(ctx)
