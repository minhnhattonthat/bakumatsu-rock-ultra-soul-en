"""Unpack CPK files from the extracted ISO into work/cpk/<CPK>/<dir>/<name>, CRILAYLA-decompressed.
usage: unpack.py [--glob PATTERN] [CPK ...]   (default: both CPKs, every file; skips files already unpacked)
Needs work/iso/ (python tools/iso9660.py x ROM work/iso)."""
import argparse, fnmatch, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from cpk import open_cpk
from crilayla import is_crilayla, decompress

ROOT = os.path.join(os.path.dirname(__file__), '..')
USR = os.path.join(ROOT, 'work', 'iso', 'PSP_GAME', 'USRDIR')


def read_entry(cpk_path, e):
    with open(cpk_path, 'rb') as f:
        f.seek(e.off); b = f.read(e.csize)
    return decompress(b) if is_crilayla(b) else b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cpks', nargs='*', default=['INST', 'NOINST'])
    ap.add_argument('--glob', default='*')
    a = ap.parse_args()
    for c in a.cpks:
        path = os.path.join(USR, c + '.CPK')
        _, ents = open_cpk(path)
        for e in ents:
            name = f'{e.dir}/{e.name}'
            if not fnmatch.fnmatch(name, a.glob): continue
            out = os.path.join(ROOT, 'work', 'cpk', c, e.dir, e.name)
            if os.path.exists(out): continue
            os.makedirs(os.path.dirname(out), exist_ok=True)
            data = read_entry(path, e)
            assert len(data) == e.size, (name, len(data), e.size)
            open(out, 'wb').write(data)


if __name__ == '__main__':
    main()
