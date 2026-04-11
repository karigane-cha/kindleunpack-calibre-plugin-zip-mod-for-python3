# KindleUnpack the calibre Plugin + ZIP mod for Python 3

English | [日本語](README_ja.md)  

## About  
[KindleUnpack the calibre Plugin + ZIP mod](https://github.com/junk2ool/kindleunpack-calibre-plugin-zip-mod) contained code that was not compatible with Python 3. Therefore, it did not work with newer versions of calibre that use Python 3. To address this, the plugin has been modified to work with the latest calibre while maintaining its previous functionality.  


## Supported Versions  
- calibre 5.0.0 or later  


## Changes from the [Original Version](https://github.com/junk2ool/kindleunpack-calibre-plugin-zip-mod)  
### kindleunpack  
- Updated from v0.72.1 to v0.83.8  

### kindleunpack/DumpAZW6_v01.py  
- Modified to support Python 3.  
- Since imghdr was deprecated in Python 3.13 and later, detection has been changed to use magic bytes.  

### kindleunpack/unpack_structure.py  
- Since distutils was deprecated in Python 3.12 and later, the implementation has been changed to use shutil.  


## How to Use  
1. Install the latest plugin from the [release page](https://github.com/karigane-cha/kindleunpack-calibre-plugin-zip-mod-for-python3/releases).  
2. Launch calibre and install the plugin via `Preferences > Plugins > Load plugin from file`.  
3. After installation and restart, KindleUnpack icon will appear in the toolbar. You can configure various settings from there.  
4. If you want to include the `.azw.res` file when generating zip or epub files, be sure to specify the Kindle Content directory.  


## References  
- [KindleUnpack the calibre Plugin + ZIP mod](https://github.com/junk2ool/kindleunpack-calibre-plugin-zip-mod): v.0.3  
- [KindleUnpack the calibre Plugin](https://github.com/dougmassay/kindleunpack-calibre-plugin): v0.83.8  
- [DumpAZW6_py3.py](https://gist.github.com/fireattack/99b7d9f6b2896cfa33944555d9e2a158)  
- https://rio2016.5ch.io/test/read.cgi/ebooks/1526467330/  
The corrections in [>>395](https://rio2016.5ch.io/test/read.cgi/ebooks/1526467330/395) have also been reflected.


## License  
### KindleUnpack the calibre Plugin + ZIP mod for Python 3  

    Licensed under the GPLv3.

### KindleUnpack the calibre Plugin + ZIP mod (https://github.com/junk2ool/kindleunpack-calibre-plugin-zip-mod)  

    Licensed under the GPLv3.

### KindleUnpack the calibre Plugin (https://github.com/dougmassay/kindleunpack-calibre-plugin)  

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


## Credits  
- [KindleUnpack the calibre Plugin + ZIP mod](https://github.com/junk2ool/kindleunpack-calibre-plugin-zip-mod)  
- [KindleUnpack the calibre Plugin](https://github.com/dougmassay/kindleunpack-calibre-plugin)  
- [DumpAZW6_py3.py](https://gist.github.com/fireattack/99b7d9f6b2896cfa33944555d9e2a158)  