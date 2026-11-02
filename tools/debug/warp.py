"""Debug warp: cold-boot the game and land on any scene in tools/debug/scenes.tsv, with a shot (and optionally a
savestate) to prove it. No user save, no playthrough.

    python -X utf8 tools/debug/warp.py SCENE [SCENE..] [--iso ISO] [--shot-every N] [--frames N] [--state]
    python -X utf8 tools/debug/warp.py --all [--iso ISO] [--jobs 3]     # every scene; states -> work/states/warp/
    python -X utf8 tools/debug/warp.py --list

How (docs/re/debug.md):
- Boot: tools/routes/menu.txt (cold boot, fresh memstick, to the top MENU), cached once per ISO as
  work/states/warp/_menu_<iso>.ppst (rebuilt when the ISO is newer).
- UNLOCK (every scene): write the system-data unlock flags and the skit/event order arrays (UNLOCK below, offsets
  from obj = *0x08AA8480): all chapters, songs, gallery events, movies, skits, profiles.
- kind=script: STORY -> ROCKstory, with an exec breakpoint on the script setter's strcpy return (0x08888DAC, s0 =
  script manager): the name the menu just set is overwritten with ARG, so the ADV engine boots that script the way
  the menu would (chapter card, intro and all). Any file in scene/script works, by name.
  ARG may carry a route after the file name (FILE.bin;6 start;60 -), played once the script runs.
- kind=menu: ARG is a route played from the MENU.
- kind=boot: ARG is a route from power-on (fresh memstick, no unlock): boot notices, title.
- Every run logs sequence changes (0x08892948, a1 = name) and asserts: kind=script -> the loaded script name equals
  ARG; SEQ column (if not '-') -> that sequence was entered during the run. Exit 1 when any scene fails.
Output: work/qa/warp/<scene>/ (fNNNNNN.png shots, final.png, seq.txt); --state also writes work/states/warp/<scene>.ppst."""
import argparse, concurrent.futures as cf, os, shutil, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pspdbg as D  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SCENES = os.path.join(HERE, 'scenes.tsv')
MENU_ROUTE = os.path.join(D.ROOT, 'tools', 'routes', 'menu.txt')
STATES = os.path.join(D.ROOT, 'work', 'states', 'warp')
QA = os.path.join(D.ROOT, 'work', 'qa', 'warp')

MGR_PTR = 0x08AA8480          # -> script/system manager object
SCRIPT_NAME = 0x26AC          # obj + this: current script file name (64 bytes)
# System data lives at obj + 0x3B30 (0x1548 bytes, the SYSTEM01 save). Unlock state inside it (docs/re/debug.md):
UNLOCK = [
    (0x4F4C, b'\xff' * 0xB0),                    # flag bits 0..0x57F (chapters, songs, profiles 0x1F2+, event NEW 0x29F+)
    (0x4FFC, bytes(range(70))), (0x5042, b'\x46'),   # skit order array (-1 = locked) + its counter
    (0x5044, bytes(range(1, 27))), (0x506C, b'\x1a'),  # event gallery order array (-1 = locked) + its counter
]
BP_SCRIPT_SET = 0x08888DAC    # in setter 0x08888D8C, right after strcpy(obj+0x26AC, name); s0 = obj
BP_SEQ = 0x08892948           # sequence change (a0 manager, a1 sequence name)
STORY_ROCK = '6 circle;300 -'  # MENU -> STORY submenu (ROCKstory highlighted)


def load_scenes():
    rows = {}
    for ln in open(SCENES, encoding='utf-8'):
        if not ln.strip() or ln.startswith('#') or ln.startswith('name\t'): continue
        name, kind, arg, seq, frames, note = (ln.rstrip('\n').split('\t') + [''] * 6)[:6]
        assert kind in ('script', 'menu', 'boot'), (name, kind)
        assert name not in rows, f'duplicate scene {name}'
        rows[name] = dict(name=name, kind=kind, arg=arg, seq=seq, frames=int(frames or 600), note=note)
    return rows


def menu_state(iso):
    """Cold boot to the MENU once per ISO; reused by every scene of this run."""
    os.makedirs(STATES, exist_ok=True)
    st = os.path.join(STATES, f'_menu_{os.path.splitext(os.path.basename(iso))[0].replace(" ", "_")}.ppst')
    if os.path.exists(st) and os.path.getmtime(st) > max(os.path.getmtime(iso), os.path.getmtime(MENU_ROUTE)): return st
    run = D.start(iso, os.path.join(QA, '_menu'))
    try:
        D.play(run, open(MENU_ROUTE).read())
        run.save_state(st)
        run.shot('menu.png')
    finally:
        run.close()
    return st


def warp(scene, iso, shot_every=120, frames=None, state=False, log=print):
    out = os.path.join(QA, scene['name'])
    shutil.rmtree(out, ignore_errors=True)
    boot = scene['kind'] == 'boot'
    run = D.start(iso, out, None if boot else menu_state(iso))
    seqs = []
    try:
        obj = D.u32(run, MGR_PTR)
        if not boot:
            for off, data in UNLOCK: D.write(run, obj + off, data)

        def on_seq(r):
            seqs.append((r.frame(), D.cstr(r, D.reg(r, 'a1'))))

        hooks = {BP_SEQ: on_seq}
        n = frames or scene['frames']
        script, _, rest = scene['arg'].partition(';')   # script ARG: FILE.bin[;route played after the warp press]
        if scene['kind'] == 'script':
            name = script.encode('ascii') + b'\0'
            assert len(name) <= 64

            def on_set(r):
                D.write(r, D.reg(r, 's0') + SCRIPT_NAME, name)
                return True
            D.play(run, STORY_ROCK, hooks=dict(hooks))
            route = f'6 circle;{rest + ";" if rest else ""}{n} -'
            hooks[BP_SCRIPT_SET] = on_set
        else:
            route = f'{scene["arg"]};{n} -'
        total = sum(k for k, _ in D.psp.parse_route(route))
        D.play(run, route, shots=range(shot_every, total + 1, shot_every) if shot_every else (), hooks=hooks)
        run.shot('final.png')
        errs = []
        obj = D.u32(run, MGR_PTR)   # 0 until the game creates it (boot scenes)
        got = D.cstr(run, obj + SCRIPT_NAME) if obj else ''
        if scene['kind'] == 'script' and got != script: errs.append(f'script is {got!r}, want {script!r}')
        if scene['seq'] not in ('', '-'):
            if scene['seq'] not in [s for _, s in seqs]: errs.append(f'sequence {scene["seq"]!r} never entered')
        if D.psp.blank(os.path.join(out, 'final.png')): errs.append('final frame is blank')
        open(os.path.join(out, 'seq.txt'), 'w').write(''.join(f'{f}\t{s}\n' for f, s in seqs))
        if state and not errs: run.save_state(os.path.join(STATES, scene['name'] + '.ppst'))
    finally:
        run.close()
    log(f'{scene["name"]:24} {"FAIL " + "; ".join(errs) if errs else "ok"}  script {got or "-"}  seq {[s for _, s in seqs]}',
        flush=True)
    return not errs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('scenes', nargs='*'); ap.add_argument('--all', action='store_true'); ap.add_argument('--list', action='store_true')
    ap.add_argument('--iso', default=D.ISO); ap.add_argument('--shot-every', type=int, default=120)
    ap.add_argument('--frames', type=int); ap.add_argument('--state', action='store_true')
    ap.add_argument('--jobs', type=int, default=3); ap.add_argument('--sheet', action='store_true', help='contact sheet per scene')
    a = ap.parse_args()
    rows = load_scenes()
    if a.list:
        for r in rows.values(): print(f'{r["name"]:24} {r["kind"]:6} {r["arg"][:50]:50} {r["note"]}')
        return
    names = list(rows) if a.all else a.scenes
    bad = [n for n in names if n not in rows]
    if bad or not names: sys.exit(f'unknown scene(s) {bad}; --list shows them' if bad else 'name a scene, or --all')
    iso = os.path.abspath(a.iso)
    menu_state(iso)
    state = a.state or a.all
    t0 = time.time()
    with cf.ThreadPoolExecutor(max(1, a.jobs)) as ex:
        ok = list(ex.map(lambda n: _safe(rows[n], iso, a, state), names))
    if a.sheet:
        sheet = os.path.join(D.SKILL, 'scripts', 'sheet.py')
        for n in names:
            subprocess.run([sys.executable, '-X', 'utf8', sheet, os.path.join(QA, n), '--out', os.path.join(QA, n, 'sheet.png')],
                           stdout=subprocess.DEVNULL)
    print(f'{sum(ok)}/{len(ok)} ok in {time.time() - t0:.0f}s; shots in {QA}')
    sys.exit(0 if all(ok) else 1)


def _safe(scene, iso, a, state):
    try:
        return warp(scene, iso, a.shot_every, a.frames, state)
    except Exception as e:  # one broken scene must not hide the rest
        print(f'{scene["name"]:24} FAIL {type(e).__name__}: {e}')
        return False


if __name__ == '__main__':
    main()
