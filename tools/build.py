"""build.py: original ISO -> build/bakumatsu_rock_us_en.iso.

    python -X utf8 tools/build.py [--out ISO]

Checks the dump (rom.sha1), rebuilds both CPKs with the edited files from edits() and patches them into a copy of the ISO.
With no edits the output is byte-identical to the original (tests/test_identity.py). Needs work/iso (extracted on first run)."""
import argparse, hashlib, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import check_rom, cpk, iso9660

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ROM = os.path.join(ROOT, 'rom', 'Bakumatsu Rock - Ultra Soul (Japan).iso')
WORK_ISO = os.path.join(ROOT, 'work', 'iso')
OUT = os.path.join(ROOT, 'build', 'bakumatsu_rock_us_en.iso')
CPKS = ('INST', 'NOINST')


def edits():
    """-> {CPK name: {'dir/name': bytes}} for files inside the CPKs, plus {'/ISO/PATH': bytes} under key 'iso'.
    Text, font and graphics insertion plug in here (phase 4+)."""
    return {'INST': {}, 'NOINST': {}, 'iso': {}}


def extract_iso():
    if os.path.exists(os.path.join(WORK_ISO, 'PSP_GAME', 'USRDIR', 'NOINST.CPK')): return
    with open(ROM, 'rb') as f:
        for p, lba, ln, _ in iso9660.listing(f):
            d = WORK_ISO + p; os.makedirs(os.path.dirname(d), exist_ok=True); f.seek(lba * 2048)
            with open(d, 'wb') as o: o.write(f.read(ln))


def build(out=OUT, ed=None):
    """ed: edits() by default; the identity test passes no edits."""
    check_rom.check()
    extract_iso()
    ed = edits() if ed is None else ed
    os.makedirs(os.path.dirname(out), exist_ok=True)
    src = ROM
    for name in CPKS:   # one CPK in memory at a time (~0.5 GB each)
        data = cpk.rebuild(os.path.join(WORK_ISO, 'PSP_GAME', 'USRDIR', name + '.CPK'), ed[name])
        iso9660.patch(src, out, {f'/PSP_GAME/USRDIR/{name}.CPK': data}); src = out
    # shortcut: INST.DNS is the PGD-encrypted INST.CPK (install data); it stays original until PGD re-encryption exists
    if ed['iso']: iso9660.patch(out, out, ed['iso'])
    with open(out, 'rb') as f: return hashlib.file_digest(f, 'sha1').hexdigest()


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default=OUT); a = ap.parse_args()
    sha = build(a.out)
    orig = next(l for l in open(os.path.join(ROOT, 'rom.sha1'), encoding='utf-8') if l.strip() and l[0] != '#').split()[0]
    print(f'{a.out}  sha1 {sha}' + ('  (identical to the original)' if sha == orig else ''))
