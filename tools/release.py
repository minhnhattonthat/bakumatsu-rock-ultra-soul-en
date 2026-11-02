"""release.py: build -> checks -> xdelta3 patch -> re-apply and compare -> zip. Stops at the first failure.

    python -X utf8 tools/release.py [--version 1.0] [--force] [--skip-tests]

Steps: build (isodiff + read-back inside) -> tests (tools/check.py) -> smoke (cold boot to the main menu) -> jp_left over
every text record of the build (tools/textscan.py) -> qa_gate.py check on every work/qa/**/manifest.tsv -> no unticked
line in docs/polish.md -> debug tool off -> xdelta3 patch -> re-apply to the clean original, compare SHA-1 -> zip
(patch + README.txt, ZIP_STORED) in release/. The playable image stays in build/. Never publishes (D9)."""
import argparse, glob, hashlib, os, subprocess, sys, zipfile, zlib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skill import SKILL  # noqa: E402

GAME = 'Bakumatsu_Rock_Ultra_Soul_EN'
REL = os.path.join(ROOT, 'release')


def step(msg):
    print(f'== {msg}', flush=True)


def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode:
        raise SystemExit(f'failed ({r.returncode}): {" ".join(cmd)}')


def hashes(path):
    h = {'md5': hashlib.md5(), 'sha1': hashlib.sha1()}
    crc = 0
    with open(path, 'rb') as f:
        while b := f.read(1 << 22):
            crc = zlib.crc32(b, crc)
            for x in h.values(): x.update(b)
    return dict(size=os.path.getsize(path), crc32=f'{crc:08x}', md5=h['md5'].hexdigest(), sha1=h['sha1'].hexdigest())


README = """Bakumatsu Rock: Ultra Soul - English translation patch v{version}
================================================================

Unofficial fan translation of Bakumatsu Rock: Ultra Soul (PSP, Marvelous, 2014). No game data is included and no
pre-patched images are provided: you need your own dump of the Japanese UMD.

Base image (Redump: "{rom_name}", http://redump.org/discs/quicksearch/Bakumatsu%20Rock/)
  size   {base[size]} bytes
  CRC32  {base[crc32]}
  MD5    {base[md5]}
  SHA-1  {base[sha1]}
Patched image
  CRC32  {out[crc32]}
  SHA-1  {out[sha1]}

How to patch
  xdelta3 -d -s "{rom_name}.iso" {patch} "Bakumatsu Rock - Ultra Soul (English).iso"
  (or any xdelta3 GUI such as Delta Patcher / xdelta UI). The patch only applies to the exact image above.

Tested in PPSSPP (v1.20.4 and its headless build). On a fresh memory stick the game shows an autosave notice, then
"Failed to load system data. Try loading again?": answer No and a new system file is made.
Start the patched game from a cold boot: emulator savestates made with the Japanese image keep its old code and
text.
Real hardware: the patch ships a decrypted EBOOT (the dialogue layout needs a small code change), which custom
firmware runs; an unmodified PSP will not.

Translation status
  Story dialogue, choices, narration, skits, profiles, menus, system messages, save data, credits: English.
  Menu, title-card, notice, sound-effect and button graphics: English.
  Left in Japanese: lyrics on the rhythm-game notes and in the song videos (the songs are sung in Japanese); shop
  signs, banners and crests painted into backgrounds; the game's logo.

Known issues
  - Two profile names are shortened to fit their slot: "S. Takasugi", "T. Hijikata" (and three voice actors).
  - Option > Data install copies the original Japanese data: leave install off.

Report bugs: https://github.com/minhnhattonthat/bakumatsu-rock-ultra-soul-en/issues (a savestate helps).

Credits: translation and tools by minhnhattonthat, with AI assistance (Claude) for translation drafts, review and
tooling. Fonts: PT Serif, Anton, Bangers, Archivo Black (SIL Open Font License). Bakumatsu Rock is (c) Marvelous;
this project is not affiliated with them.
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--version', default='1.0')
    ap.add_argument('--force', action='store_true', help="overwrite this version's files")
    ap.add_argument('--skip-tests', action='store_true', help='skip tools/check.py (already run by the commit hook)')
    a = ap.parse_args()
    patch = f'{GAME}_v{a.version}.xdelta'
    zpath = os.path.join(REL, f'{GAME}_v{a.version}.zip')
    if os.path.exists(zpath) and not a.force:
        raise SystemExit(f'{zpath} exists; --force to rebuild this version')

    import build, check_rom
    step('build')
    sha = build.build()
    if not a.skip_tests:
        step('tests')
        run([sys.executable, '-X', 'utf8', 'tools/check.py'])
    step('smoke')
    run([sys.executable, '-X', 'utf8', os.path.join(SKILL, 'scripts', 'emu.py'), build.OUT, '--out', 'work/qa/smoke',
         '--route', 'tools/routes/boot.txt', '--smoke'])
    step('jp_left')
    run([sys.executable, '-X', 'utf8', 'tools/textscan.py', build.OUT])
    out = subprocess.run([sys.executable, '-X', 'utf8', os.path.join(SKILL, 'scripts', 'jp_left.py'), 'work/qa/text.bin',
                          '--sjis', '--halfwidth', '--kanji-runs', '--min', '1'], cwd=ROOT, capture_output=True, text=True)
    print(out.stdout.strip().splitlines()[-1] if out.stdout.strip() else out.stderr)
    if out.returncode or not out.stdout.strip().endswith('0 Japanese runs, 0 bytes'):
        raise SystemExit('jp_left: Japanese left in the build (lyrics excluded, D13)')
    step('visual / story QA gates')
    mans = sorted(glob.glob(os.path.join(ROOT, 'work', 'qa', '**', 'manifest.tsv'), recursive=True))
    if not mans: raise SystemExit('no QA manifest under work/qa')
    for m in mans:
        run([sys.executable, '-X', 'utf8', os.path.join(SKILL, 'scripts', 'qa_gate.py'), 'check', m,
             os.path.join(os.path.dirname(m), 'verdicts')])
    step('polish')
    left = [l for l in open(os.path.join(ROOT, 'docs', 'polish.md'), encoding='utf-8') if l.startswith('- [ ]')]
    if left: raise SystemExit(f'docs/polish.md: {len(left)} unticked lines')
    step('debug tool off')   # warp.py works by emulator RAM pokes; nothing of tools/debug may reach the build
    if any(m in sys.modules for m in ('warp', 'pspdbg', 'textprobe')):
        raise SystemExit('a debug module was imported while building')
    step('patch')
    os.makedirs(REL, exist_ok=True)
    ppath = os.path.join(REL, patch)
    # -B: source window = the whole ISO; the rebuilt CPKs move data further than the 64 MB default (994 MB patch -> 8 MB).
    # A plain `xdelta3 -d` decodes it (the re-apply below runs that).
    run(['xdelta3', '-e', '-f', '-9', '-S', 'djw', '-B', '1879048192', '-s', build.ROM, build.OUT, ppath])
    step('re-apply to the clean original')
    check_rom.check()
    again = os.path.join(ROOT, 'build', 'reapplied.iso')
    run(['xdelta3', '-d', '-f', '-s', build.ROM, ppath, again])
    got = hashes(again)
    os.remove(again)
    if got['sha1'] != sha: raise SystemExit(f're-applied image {got["sha1"]} != build {sha}')
    step('zip')
    text = README.format(version=a.version, rom_name=os.path.splitext(os.path.basename(build.ROM))[0], patch=patch,
                         base=hashes(build.ROM), out=got)
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_STORED) as z:
        z.write(ppath, patch)
        z.writestr('README.txt', text)
    with open(os.path.join(REL, f'{GAME}_v{a.version}_README.txt'), 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'{zpath}\npatch sha1 {hashes(ppath)["sha1"]}; patched image sha1 {sha} ({build.OUT})')


if __name__ == '__main__':
    main()
