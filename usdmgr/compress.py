"""
    ビルド済みパッケージを tar にまとめて zstd 圧縮する.
"""


if __name__ == "__main__":
    import os
    import argparse
    import tarfile
    parser = argparse.ArgumentParser()
    parser.add_argument("dirpath", type=str)
    parser.add_argument("output", type=str)
    args = parser.parse_args()
    if not os.path.exists(args.dirpath) and not os.path.isdir(args.dirpath):
        print(f"Directory {args.dirpath} is not directory.")
        exit(1)
    with tarfile.open(args.output + ".tar", mode="w") as tar:
        for sroot in os.listdir(args.dirpath):
            if sroot in ["src", "share"]:
                continue
            for root, dirs, files in os.walk(os.path.join(args.dirpath, sroot)):
                relroot = os.path.relpath(root, args.dirpath).replace("\\", "/")
                for file in files:
                    tar.add(os.path.join(root, file), os.path.join(relroot, file))

    # Zstd
    with open(args.output + ".tar", mode="rb") as ifst:
        with open(args.output + ".tar.zstd", mode="wb") as ofst:
            import zstd
            ofst.write(zstd.compress(ifst.read(), 8))

    os.remove(args.output + ".tar")
