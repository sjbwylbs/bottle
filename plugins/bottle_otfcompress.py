#!/usr/bin/python
# -*- coding: utf-8 -*-

__autor__   = "Damien Degois"
__version__ = '0.1'
__licence__ = 'MIT'

import bottle
from struct import pack
from zlib import crc32
import zlib
from time import time
from functools import partial

class OtfCompressPlugin(bottle.BasePlugin):
    plugin_name = "otfcompress"

    def wrap(self, callback):
        def wrapper(*args, **kwargs):
            rv = callback(*args, **kwargs)
            # Get and parse accept header or return uncompressed
            enc = bottle.request.headers.get('Accept-Encoding', '')
            enc = [algo.strip() for algo in enc.split(',')]
            if 'gzip' in enc: enc = 'gzip'
            elif 'x-gzip' in enc: enc = 'x-gzip'
            else: return rv
            bottle.response.headers['Content-Encoding'] = enc
            while isinstance(rv, bottle.HTTPResponse):
                rv.apply(bottle.response)
                # Delete content-length header (changes after conpression)
                if 'Content-Length' in bottle.response.headers:
                    del bottle.response.headers['Content-Length']
                rv = rv.output
            if isinstance(rv, (tuple, list)): rv = ''.join(rv)
            if isinstance(rv, unicode): rv = ev.encode(bottle.response.charset)
            if isinstance(rv, str): rv = [rv]
            return iter_compress(rv)
        return wrapper

write32u = partial(pack, "<L")


# From Gzip. This adds gzip specific headers to the deflate data stream
def iter_compress(iterator):
    crc = crc32("") & 0xffffffffL
    compress = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS,
                                   zlib.DEF_MEM_LEVEL, 0)
    size = 0
    # header + method + flag (0) + time + misc headers
    yield '\037\213\010\000'+write32u(long(time()))+'\002\377'
    for part in iterator:
        size += len(part)
        crc = crc32(part, crc) & 0xffffffffL
        yield compress.compress(part)
    # Close
    yield compress.flush()
    yield write32u(crc) + write32u(size & 0xffffffffL)

def test():
    app = bottle.Bottle()
    bottle.debug(True)
    app.install("otfcompress")
    @app.get('/')
    def test():
        return 'Hello World'
    return app

if __name__ == '__main__':
    bottle.run(test())
