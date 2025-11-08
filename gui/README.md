
## publish
pyinstaller 打包 py
```shell
pyinstaller `
    --onefile `
    --noconsole `
    --clean `
    --strip `
    --upx-dir "D:/Go/bin" `
    --exclude-module test `
    --exclude-module unittest `
    --exclude-module distutils `
    --exclude-module setuptools `
    --exclude-module pip `
    --exclude-module numpy `
    --exclude-module scipy `
    --exclude-module xml `
    --exclude-module http `
    --exclude-module email `
    --exclude-module html `
    --exclude-module asyncio `
    --name tile_optimized `
    tile.py
```

nuitka 将 Python 编译成 C，再编译成二进制
```shell
pip install nuitka zstandard

nuitka --standalone tile.py `
--onefile `
--windows-console-mode=disable `
--enable-plugin=tk-inter `
--output-dir=build `
--lto=yes `
--remove-output
```