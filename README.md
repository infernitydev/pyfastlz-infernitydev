FastLZ
======

Python wrapper for [FastLZ], a lightning-fast lossless compression library.


Installation
------------

To install fastlz, simply:

```bash
$ pip install pyfastlz-infernitydev
```

[FastLZ]: https://github.com/ariya/FastLZ


Usage
-----

Compressing is quite simple:
```py
from pyfastlz import compress

compressed, uncompressed_length = compress(uncompressed_bytes)
```

And decompressing uses the length from earlier:
```
from pyfastlz import decompress

decompressed = decompress(compressed, uncompressed_length)
```