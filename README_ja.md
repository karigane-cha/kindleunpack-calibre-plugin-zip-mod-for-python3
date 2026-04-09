# KindleUnpack the calibre Plugin + ZIP mod for Python 3  

[English](Readme.md) | 日本語  

## 概要  
[KindleUnpack the Calibre Plugin + ZIP mod](https://github.com/junk2ool/kindleunpack-calibre-plugin-zip-mod) は、 Python 3 には対応していないコードが含まれていました。そのため、Python 3 が用いられた新しいバージョンの Calibre では動作しませんでした。そこで、以前の機能を維持しつつ、最新の Calibre でも動作するようにプラグインを改修しました。  


## 対応バージョン  
- Calibre 5.0.0 以上  


## [オリジナル版](https://github.com/junk2ool/kindleunpack-calibre-plugin-zip-mod)からの変更点  
### kindleunpack  
- v0.72.1 から v0.83.8 に更新。  

### kindleunpack/DumpAZW6_v01.py  
- Python 3 対応版に変更。  
- Python 3.13 以降で imghdr が廃止されたため、マジックバイトを用いた検出に変更。  

### kindleunpack/unpack_structure.py  
- Python 3.12 以降で distutils が廃止されたため、shutil を用いる実装に変更。  


## 使用方法  
1. [リリースページ](https://github.com/karigane-cha/KindleUnpack_Calibre_Plugin_zip_mod_for_Python3/releases)から最新のプラグインをインストールします。
2. Calibre を起動して、`環境設定 > プラグイン > ファイルからプラグインを読み込む`でプラグインをインストールします。  
2. インストールして再起動したら、ツールバーに KindleUnpack のアイコンが出現します。そこから各種設定が可能です。  
3. zip や epub ファイルを生成する際に `.azw.res` ファイルを取り込みたい場合は、忘れずに Kindle Content ディレクトリを指定してください。  


## 参照  
- [KindleUnpack the calibre Plugin + ZIP mod](https://github.com/junk2ool/kindleunpack-calibre-plugin-zip-mod): v.0.3  
- [KindleUnpack the calibre Plugin](https://github.com/dougmassay/kindleunpack-calibre-plugin): v0.83.8  
- [DumpAZW6_py3.py](https://gist.github.com/fireattack/99b7d9f6b2896cfa33944555d9e2a158)  
- https://rio2016.5ch.io/test/read.cgi/ebooks/1526467330/  
の [>>395](http://rio2016.5ch.io/test/read.cgi/ebooks/1526467330/395) さんの修正も取り込んでいます。  


## ライセンス  
### KindleUnpack the Calibre Plugin + ZIP mod for Python 3  

    Licensed under the GPLv3.

### KindleUnpack the Calibre Plugin + ZIP mod (https://github.com/junk2ool/kindleunpack-calibre-plugin-zip-mod)  

    Licensed under the GPLv3.

### KindleUnpack the Calibre Plugin (https://github.com/dougmassay/kindleunpack-calibre-plugin)  

    Licensed under the GPLv3.

### KindleUnpack (https://github.com/kevinhendricks/KindleUnpack)  

    Based on initial mobipocket version Copyright © 2009 Charles M. Hannum <root@ihack.net>
    Extensive Extensions and Improvements Copyright © 2009-2014 
    By P. Durrant, K. Hendricks, S. Siebert, fandrieu, DiapDealer, nickredding, tkeo.
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 3.

### python-patch (https://github.com/techtonik/python-patch)  

    Copyright © 2008-2015 anatoly techtonik
    Available under the terms of the MIT license (http://opensource.org/licenses/mit-license.php)

    Copyright (c) 2008-2015 anatoly techtonik

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights    
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.


## クレジット  
- [KindleUnpack the calibre Plugin + ZIP mod](https://github.com/junk2ool/kindleunpack-calibre-plugin-zip-mod)  
- [KindleUnpack the calibre Plugin](https://github.com/dougmassay/kindleunpack-calibre-plugin)  
- [DumpAZW6_py3.py](https://gist.github.com/fireattack/99b7d9f6b2896cfa33944555d9e2a158)  