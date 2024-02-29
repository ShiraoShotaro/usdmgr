# usd manager

ショートカット的なツールです。

# Simple Version

## 起動方法

起動方法は以下の通りです.

### 共通準備

pip-requirements.txt に記述されるパッケージを揃えた環境を用意します.

```
python -m venv .env
call .env\Script\activate
pip install -r pip-requirements.txt
```

### 1. python で直接起動する方法

```python
python -m usdmgr
```

### 2. pyinstaller で固める方法 (windows)

```
packaging/package.cmd
... (wait for packaging...)
dist/startup.exe
```

exe になって嬉しいことは, タスクバーに登録できるようになります.
python の起動コマンドをまとめた bat に対するショートカットを登録することもできますが, そうするとショートカットとウィンドウが別のタスクバーアイコンになってしまいます.

## 使用方法

### 環境を追加する
Settings メニューから Open Environment Json を押します.
開いた json ファイルを編集してください.
エンコードは UTF-8 で保存してください.

```json
{
    "environments": [
        {
            "label": "ラベル文字列, python に依存している場合",
            "usdRoot": {
                "release": "（省略可能） Release 版 USD のインストール先ディレクトリ",
                "debug": "（省略可能） Debug 版 USD のインストール先ディレクトリ"
            },
            "usdVersion": "YYXXv",
            "python": {
                "version": [
                    3,
                    9
                ],
                "venv": "virtual env へのパス"
            }
        },
        {
            "label": "ラベル文字列, python に依存していない場合",
            "usdRoot": {
                "release": "（省略可能） Release 版 USD のインストール先ディレクトリ",
                "debug": "（省略可能） Debug 版 USD のインストール先ディレクトリ"
            },
            "usdVersion": "YYXXv"
        },
    ],
    "plugins": {
        "searchPaths": [
            "プラグインの検索パス (詳細は後述)"
        ]
    }
}
```

#### usdRoot

release, debug のいずれか, もしくは両方を指定します.
これらは config 以外, 混乱を避けるため, 同じオプションでビルドされたものをお勧めします.
オプション違いの場合は, それぞれに環境を複製することをお勧めします.

#### usdVersion

YYMM, YYMMv のような文字列で指定します. 例えば 23.11 は 2311, 24.03 は 2403 のように記述します.

v はバリアント識別文字です. 基本的には使用しません.

この usdVersion で指定した文字列は, 後述するプラグインの検索にて使用されます.
同じ USD バージョンであっても, ビルドをカスタマイズした場合など, プラグインバイナリに互換性が無い場合に, 任意の文字列を指定することができます. 例えば 2311conan など.

#### python

Python ON でビルドされた USD を利用するときには, この python データを指定します.

version には長さ2の配列で `[majorVersion, minorVersion]` を数値で指定します.
省略可能で, 省略された場合, 必要になったタイミングで, ツールが `python --version` を呼び出して調べます.

venv は usd をビルドした virtual env を指定します.
（今のところ venv は省略できませんが）省略可能で, その場合このツールを駆動している python と, その pythonpath を継承して利用します.

#### plugins.searchPaths

プラグインの検索パスの配列.

ルールに従ってプラグインバイナリを配置すると,  Tools タブからツールを起動するときに適切なバージョンのプラグインへのパスを通します.

ルールは後述します.

### ツールを追加する

Settings メニューから Open Tools Json を押します.
開いた json ファイルを編集してください.
エンコードは UTF-8 で保存してください.

```json
{
    "tools": [
        {
            "label": "ツール名ラベル",
            "hidden": false,
            "debug": true,
            "requirePython": false,
            "iconPath": "path/to/icon.png",
            "cmdline": "notepad",
            "workingDir": ".",
            "envvars": {
                "PATH": "path/to/additional/path;${PATH}"
            },
            "subEntries": [
                {
                    "label": "Sub entry label 1",
                    "cmdline": "notepad.txt /v",
                    "workingDir": ".",
                    "envvars": {}
                },
                {
                    "label": "Sub entry label 2",
                    "cmdline": "notepad.txt /v",
                    "workingDir": ".",
                    "envvars": {}
                }
            ]
        }
    ]
}
```

#### hidden
`True` の場合, ツールを非表示にします. 省略可能で, デフォルトだと `False` (表示) です.

#### debug
`True` の場合, USD のデバッグ版を利用します.

#### requirePython
`True` の場合, python 環境でのみ起動します.

#### iconPath
アイコンへの画像パスを指定します. 省略可能で, 省略された場合や, 指定されたパスに画像が見つからなかった場合, デフォルトの画像が使用されます.

#### cmdline
コマンドラインを文字列, もしくは配列の文字列で指定します.
配列で指定する場合, 1区切りを1要素として指定します.

```
["hoge.exe", "arg1", "arg2", "arg3"]
```

#### workingDir
実行時のカレントディレクトリを指定します.
デフォルトではこの json が保存されているディレクトリが使用されます.

#### envvars
実行時の追加の環境変数を指定します.
指定しない場合は現在の環境変数を引き継ぎます.

現在の環境変数は, `${PATH}` のように記述できます.

#### subEntries
ツールアイコンを右クリックしたときに出てくるメニューから起動できる, 追加の起動コマンドを指定できます.

### 環境を選ぶ
USD Environment ラベルの右側のコンボボックスにて, 使用する環境を切り替えられます.

### Tools タブ
前述した tools.json に記述したツールが一覧になって表示されます.

### USDView タブ
**未実装、次ここから**

USDView を起動したり, 履歴を記憶して起動したり, などなど…

# プラグインの検索

プラグインを配置する場合に, 以下のルールに従って配置することで, 自動的に適切なプラグインを選択してパスを通します.

1. 1階層目に USD バージョン: `YYMM` or `YYMMv`
1. 2階層目に python バージョン: `_` or `py<Major><Minor>`
1. 3階層目に config: `release` or `debug`
1. 4階層目に
    - plugin
        - plugInfo.json (必須)
    - python (pythonが必要な時)
        - python packages
    - bin (省略可能)
        - exe など
    - usdview (省略可能)
        - USDView のプラグイン

`YYMMv`/`YYMM` の場所については, 検索パスのディレクトリ以下を再帰的に探します.

## 例

以下のようなディレクトリ構造で

- S drive
    - [D] hoge
        - [D] huga
            - [D] **sproot**
                - [D] myplugin_dist
                    - [D] 2311
                        - [D] py39
                            - [D] release
                                - [D] plugin
                                    - [F] plugInfo.json
                        - [D] _
                            - [D] release
                                - [D] plugin
                                    - [F] plugInfo.json
                - [D] external_plugin_dist
                    - [D] 2403
                        - [D] py311
                            - [D] debug
                                - [D] plugin
                                    - [F] plugInfo.json

`sproot` ディレクトリを searchPath に指定していたとします.

以下, ツールを起動したときにセットアップされる環境変数の中身です. ただし, ディレクトリ `bin`, `python`, `usdview` は存在するときのみ追加されます.

|環境 | 環境変数 `PATH` | 環境変数 `PXR_PLUGINPATH_NAME` | 環境変数 `PYTHONPATH` |
|--|--|--|--
|23.11 / python3.9 / release | `myplugin/2311/py39/release/plugin` `myplugin/2311/py39/release/bin` | `myplugin/2311/py39/release/plugin` `myplugin/2311/py39/release/usdview` | `myplugin/2311/py39/release/python` |
|23.11 / No python / release | `myplugin/2311/_/release/plugin` `myplugin/2311/_/release/bin` | `myplugin/2311/_/release/plugin` `myplugin/2311/_/release/usdview` | `myplugin/2311/_/release/python` |
|24.03 / python3.11 / debug | `myplugin/2403/py311/debug/plugin` `myplugin/2403/py311/debug/bin` | `myplugin/2403/py311/debug/plugin` `myplugin/2403/py311/debug/usdview` | `myplugin/2403/py311/debug/python` |

# Lisence

This project is licensed under the MIT License, see the [license.txt](license.txt) file for details.
