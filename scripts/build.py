#!/usr/bin/env python3
"""Build KEMET from the checked-in source and stamp a static update manifest."""
import argparse
import base64
from pathlib import Path
from versioning import stamp

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'src'
def data_uri(name):
    return 'data:image/png;base64,'+base64.b64encode((ROOT/'assets'/name).read_bytes()).decode()

def build(export=None):
    html=(SRC/'shell.html').read_text()
    parts={
        '/*__CSS__*/':'\n'.join((SRC/name).read_text() for name in ['style.css','readability.css','comfort.css','updater.css']),
        '/*__DATA__*/':(SRC/'data.js').read_text(),
        '/*__DIAGRAMS__*/':(SRC/'diagrams.js').read_text(),
        '/*__APP__*/':(SRC/'app.js').read_text(),
        '/*__UPDATER__*/':(SRC/'updater.js').read_text(),
        '<!--__QR__-->':(ROOT/'qr.svg').read_text(),
        '__APP_ICON_DATA__':data_uri('kemet-mark-v2.png'),
    }
    for placeholder,value in parts.items():
        assert placeholder in html,placeholder
        html=html.replace(placeholder,value)
    html=stamp(html,'kemet',ROOT)
    (ROOT/'index.html').write_text(html)
    offline=html.replace('<link rel="manifest" href="site.webmanifest?v=2">','')
    for name in ['favicon-32-v2.png','kemet-icon-192-v2.png','apple-touch-icon-v2.png']:
        offline=offline.replace('href="assets/'+name+'"','href="'+data_uri(name)+'"')
    (ROOT/'KEMET.html').write_text(offline)
    (ROOT/'.nojekyll').touch()
    if export:
        export.mkdir(parents=True,exist_ok=True)
        (export/'KEMET.html').write_text(offline)
    print(f'Built {len(html.encode()):,} bytes; 6 monuments.')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--export',type=Path)
    build(parser.parse_args().export)
