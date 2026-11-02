"""isodiff.py: the build changed only what insert.plan() asked for (the PSP form of romdiff.py; build.py runs it).

    python -X utf8 tools/isodiff.py [BUILT_ISO] [--texts script]

Fails (exit 1) on any of:
  - an ISO sector outside the edited files' old extents, their directory records, the PVD and the appended tail;
  - a CPK entry that differs from the original but is not an edit, or an edit whose stored bytes are not the plan's;
  - an edited UI table byte outside its string slots; an EBOOT byte outside the save-title slots and ADV_CODE words
    (against the plain work/eboot/EBOOT.ELF); a PARAM.SFO byte outside the title slot.
"""
import argparse, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cpk, insert, iso9660, uitable
from crilayla import decompress, is_crilayla

SEC = 2048
CHUNK = 4096 * SEC


class Sub:
    """A file view starting at BASE (a CPK inside the ISO) for cpk.parse."""
    def __init__(self, f, base):
        self.f, self.base = f, base

    def seek(self, off):
        self.f.seek(self.base + off)

    def read(self, n):
        return self.f.read(n)


def bad_sectors(a, b, allowed, size):
    """Sectors < SIZE/2048 where file objects A and B differ and that are not in ALLOWED (a set of sector numbers)."""
    bad = []
    a.seek(0); b.seek(0)
    for base in range(0, size, CHUNK):
        x, y = a.read(CHUNK), b.read(CHUNK)
        if x == y:
            continue
        for s in range(0, len(x), SEC):
            if x[s:s + SEC] != y[s:s + SEC] and (base + s) // SEC not in allowed:
                bad.append((base + s) // SEC)
    return bad


def spans_diff(old, new, spans):
    """Byte offsets where OLD and NEW differ outside SPANS [(off, len)] (same length expected)."""
    if len(old) != len(new):
        return [f'size {len(old)} -> {len(new)}']
    ok = bytearray(len(old))
    for o, n in spans:
        ok[o:o + n] = b'\1' * n
    return [f'{i:#x}' for i in range(len(old)) if old[i] != new[i] and not ok[i]][:5]


def check(built, ed):
    """-> list of problems (empty = the build matches the plan ED and nothing else changed)."""
    import build
    probs = []
    with open(build.ROM, 'rb') as fo, open(built, 'rb') as fn:
        old = {p: (lba, ln, pos) for p, lba, ln, pos in iso9660.listing(fo)}
        new = {p: (lba, ln, pos) for p, lba, ln, pos in iso9660.listing(fn)}
        size = fo.seek(0, 2)
        edited = ['/PSP_GAME/USRDIR/%s.CPK' % c for c in build.CPKS if ed[c]] + list(ed['iso'])
        allowed = {16}
        for p in edited:
            lba, ln, pos = old[p]
            allowed |= set(range(lba, lba + -(-ln // SEC))) | {pos // SEC}
        probs += [f'ISO sector {s} changed outside the edited files' for s in bad_sectors(fo, fn, allowed, size)][:5]
        if set(old) != set(new):
            probs.append('ISO file list changed')
        for c in build.CPKS:
            p = '/PSP_GAME/USRDIR/%s.CPK' % c
            _, _, ents_o = cpk.parse(_head(fo, old[p][0]), Sub(fo, old[p][0] * SEC))
            _, _, ents_n = cpk.parse(_head(fn, new[p][0]), Sub(fn, new[p][0] * SEC))
            seen = set()
            for a, b in zip(ents_o, ents_n):
                key = f'{a.dir}/{a.name}' if a.dir else a.name
                ra, rb = _raw(fo, old[p][0], a), _raw(fn, new[p][0], b)
                if key in ed[c]:
                    seen.add(key)
                    if rb != ed[c][key]:
                        probs.append(f'{c} {key}: stored bytes are not the planned edit')
                    elif key.startswith('systemdata/'):
                        name = key.split('/')[1]
                        ra = decompress(ra) if is_crilayla(ra) else ra
                        d = spans_diff(ra, rb, [(s.off, s.capacity) for s in uitable.slots(ra, name)])
                        probs += [f'{c} {key}: byte {x} changed outside the string slots' for x in d]
                elif (a.dir, a.name, a.size, a.csize) != (b.dir, b.name, b.size, b.csize) or ra != rb:
                    probs.append(f'{c} {key}: changed but not an edit')
            if len(ents_o) != len(ents_n) or seen != set(ed[c]):
                probs.append(f'{c}: entry list or edit set differs ({sorted(set(ed[c]) - seen)[:3]})')
        for p, data in ed['iso'].items():
            fn.seek(new[p][0] * SEC)
            if fn.read(new[p][1]) != data:
                probs.append(f'{p}: ISO file is not the planned edit')
    if '/PSP_GAME/SYSDIR/EBOOT.BIN' in ed['iso']:
        with open(insert.EBOOT, 'rb') as f:
            elf = f.read()
        spans = [(s.off, s.capacity) for s in uitable.eboot_slots(elf)]
        spans += [(va - insert.ELF_BASE, 4) for va, _, _ in insert.ADV_CODE + insert.CHAPTER_CODE + insert.TEXT_CODE]
        probs += [f'EBOOT byte {x} changed outside the slots and code patches'
                  for x in spans_diff(elf, ed['iso']['/PSP_GAME/SYSDIR/EBOOT.BIN'], spans)]
    if '/PSP_GAME/PARAM.SFO' in ed['iso']:
        with open(insert.SFO, 'rb') as f:
            probs += [f'PARAM.SFO byte {x} changed outside the title'
                      for x in spans_diff(f.read(), ed['iso']['/PSP_GAME/PARAM.SFO'], [uitable.SFO_TITLE])]
    return probs


def readback(ed, directory=insert.SCRIPT):
    """Re-parse every planned file: each text slot holds its `en` (or the original text where none) -> problems.
    Catches an insert step that skips entries (a table, a name, a field) that the byte diff would accept."""
    import mzscript
    texts, names = insert.load_texts(directory)
    probs = []
    for rel, t in sorted(texts.items()):
        stem = rel.split('/')[-1][:-len('.json')]
        if rel.startswith(('scene/', 'play/')):
            kind = rel.split('/')[0]
            d = insert.SCENE_DIR if kind == 'scene' else insert.PLAY_DIR
            with open(os.path.join(insert.CPK, *d, stem + '.bin'), 'rb') as f:
                old = mzscript.parse(f.read(), kind)
            new = mzscript.parse(ed['INST']['/'.join(d[1:] + (stem + '.bin',))], kind)
            # text slots only: a remapped jump word can look like an empty string header (0x0000fb03) to the parser
            if len(old.text_slots) != len(new.text_slots):
                probs.append(f'{rel}: {len(old.text_slots)} text slots -> {len(new.text_slots)}'); continue
            for so, sn in zip(old.text_slots, new.text_slots):
                if so in old.table_slots:   # op-0x19 speaker table: per-file name, else the shared one
                    i = old.table_slots.index(so)
                    want = names.get((stem, i)) or names.get(i) or so.text
                else:
                    want = t.get(so.off, so.text)
                if sn.text != want:
                    probs.append(f'{rel} 0x{so.off:x}: reads {sn.text[:30]!r}, want {want[:30]!r}')
        elif rel.startswith('ui/'):
            path = insert._ui_path(stem)   # slots in place: read each back as a C string at its original slot
            with open(path, 'rb') as f:
                slots = {s.off: s for s in uitable.slots(f.read(), os.path.basename(path))}
            new = ed['NOINST']['systemdata/' + os.path.basename(path)]
            for o, en in t.items():
                s = slots[o]
                got = new[o:o + s.capacity].split(b'\0')[0].decode(s.enc, 'replace')
                if got != en:
                    probs.append(f'{rel} 0x{o:x}: reads {got[:30]!r}, want {en[:30]!r}')
        elif rel == 'eboot.json':
            got = {s.off: s.text for s in uitable.eboot_slots(ed['iso']['/PSP_GAME/SYSDIR/EBOOT.BIN'])}
            probs += [f'{rel} 0x{o:x}: reads {got.get(o)!r}' for o, en in t.items() if got.get(o) != en]
        elif rel == 'param_sfo.json':
            got = uitable.sfo_title(ed['iso']['/PSP_GAME/PARAM.SFO']).text
            probs += [f'{rel}: reads {got!r}' for en in t.values() if got != en]
    return probs[:20]


def _head(f, lba):
    f.seek(lba * SEC)
    return f.read(0x800)


def _raw(f, lba, e):
    f.seek(lba * SEC + e.off)
    return f.read(e.csize)


def main():
    import build
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('built', nargs='?', default=build.OUT)
    ap.add_argument('--texts', default=None)
    a = ap.parse_args()
    probs = check(a.built, build.edits(a.texts))
    print('\n'.join(probs) if probs else 'isodiff: OK (only the planned edits changed)')
    sys.exit(1 if probs else 0)


if __name__ == '__main__':
    main()
