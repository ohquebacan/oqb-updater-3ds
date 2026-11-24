#!/usr/bin/env python3
"""Stage the native application's RomFS from the checked-in 3ds/romfs.

The default build is lightweight: banners, galleries and GitHub pages download from our
resource repository after installation. FORGE_SELF_CONTAINED=1 produces the alternative
edition with all artwork and encoded video previews inside the CIA/3DSX.

Music and sounds become Ogg Vorbis; fonts, kerning and the large JSON files are
gzip-compressed. Every step is deterministic: identical inputs produce identical output.
"""
import gzip, hashlib, importlib.util, json, os, shutil, struct, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
source = ROOT / '3ds/romfs'
target = ROOT / '3ds/build/romfs'
tools = ROOT / '3ds/build/tools'
spec = importlib.util.spec_from_file_location('store_packs', ROOT / '3ds/tools/store_packs.py')
store_packs = importlib.util.module_from_spec(spec); spec.loader.exec_module(store_packs)
self_contained = os.environ.get('FORGE_SELF_CONTAINED', '0') == '1'

VORBIS_QUALITY = '0.4'  # about 80 kbit/s: transparent on the console speakers, close on headphones
GZIP = ('gfx/fonts.bin', 'gfx/kerning.bin', 'catalog.json', 'strings.json', 'universal.json')

if target.exists(): shutil.rmtree(target)
moved = {Path(m).name for m in store_packs.MOVED}
ignore = () if self_contained else ('banner', *moved)
shutil.copytree(source, target, ignore=shutil.ignore_patterns(*ignore, '.DS_Store', 'forge-default.key'))
if private_manifest := os.environ.get('FORGE_PERSONAL_MANIFEST'):
    sealed = Path(private_manifest).read_bytes()
    if len(sealed) < 56 or len(sealed) > 56 + 16384 or sealed[:4] != b'FM01':
        raise ValueError('Expected a sealed Forge Mode manifest')
    (target / 'personal-assets.fme').write_bytes(sealed)
if activation := os.environ.get('FORGE_DEFAULT_ACTIVATION'):
    if not private_manifest:
        raise ValueError('FORGE_DEFAULT_ACTIVATION requires FORGE_PERSONAL_MANIFEST')
    saved = Path(activation).read_bytes()
    if len(saved) != 68 or saved[:4] != b'FMK1' or saved[4:36] != hashlib.sha256(sealed).digest():
        raise ValueError('Activation does not match the personal manifest')
    (target / 'forge-default.key').write_bytes(saved)
if not self_contained:
    for folder in store_packs.MOVED:
        assert not (target / folder).exists(), folder

# ---- my ports' banners: one sequential bank; individual files remain available -------------
apps = json.loads((source / 'catalog.json').read_text())['apps']
files = store_packs.core_banner_files()
start = 12 + 72 * len(files); index = bytearray(); payload = bytearray()
meta = json.loads((target / 'gfx/banners.json').read_text())
for app in apps:
    meta.setdefault(app['id'], {})['_bytes'] = 0
for app in apps:
    for layer in ('bg', 'fg'):
        p = source / 'gfx/banner' / f"{app['id']}-{layer}.ftx"
        if p.exists():
            data = p.read_bytes(); at = 12 + data[9] * 8
            meta[app['id']]['_bytes'] += struct.unpack_from('<I', data, at)[0]
for p in files:
    data = p.read_bytes(); name = p.name.encode(); assert len(name) < 64
    index.extend(struct.pack('<64sII', name, start + len(payload), len(data))); payload.extend(data)
bank = struct.pack('<4sII', b'FBN1', len(files), start + len(payload)) + index + payload
assert len(bank) <= 8 * 1024 * 1024
(target / 'gfx/banner-bank.bin').write_bytes(bank)
(target / 'gfx/banners.json').write_text(json.dumps(meta, separators=(',', ':')) + '\n')
print(f'Banner bank: {len(files)} sheets of my ports, {len(bank)} bytes')

# ---- sound: Ogg Vorbis ----------------------------------------------------------------------
encoder = tools / 'vorbis-encode'
encoder_source = ROOT / '3ds/tools/vorbis-encode.c'
if not encoder.exists() or encoder.stat().st_mtime < encoder_source.stat().st_mtime:
    tools.mkdir(parents=True, exist_ok=True)
    subprocess.run(['clang', '-O2', '-I/opt/homebrew/include', str(encoder_source), '-L/opt/homebrew/lib',
                    '-lvorbisenc', '-lvorbis', '-logg', '-o', str(encoder)], check=True)
cache = ROOT / '3ds/build/audio-cache'; cache.mkdir(parents=True, exist_ok=True)
before = after = 0
for pcm in sorted((target / 'audio').glob('*.pcm')):
    raw = pcm.read_bytes()
    key = hashlib.sha256(raw + VORBIS_QUALITY.encode() + encoder_source.read_bytes()).hexdigest()[:16]
    cached = cache / f'{pcm.stem}-{key}.ogg'
    if not cached.exists():
        subprocess.run([str(encoder), VORBIS_QUALITY, str(pcm), str(cached)], check=True)
    shutil.copyfile(cached, pcm.with_suffix('.ogg')); pcm.unlink()
    before += len(raw); after += cached.stat().st_size
print(f'Audio: {before} → {after} bytes (Ogg Vorbis q{VORBIS_QUALITY})')

# ---- gzip ------------------------------------------------------------------------------------
for rel in GZIP:
    p = target / rel; raw = p.read_bytes()
    p.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
    print(f'{rel}: {len(raw)} → {p.stat().st_size} bytes (gzip)')

# ---- resources -------------------------------------------------------------------------------
if self_contained:
    videos = sorted((ROOT / 'assets/store-resources').glob('*.fvid'))
    assert videos, 'No encoded video previews found'
    (target / 'video').mkdir(parents=True, exist_ok=True)
    for video in videos:
        shutil.copyfile(video, target / 'video' / video.name)
    manifest = {'format': 1, 'packs': []}
    print(f'Self-contained resources: all RomFS art/pages and {len(videos)} video previews included')
else:
    manifest = store_packs.build()
    print(f"Resource packs: {len(manifest['packs'])} packs, {sum(p['bytes'] for p in manifest['packs'])} bytes downloaded after install")
(target / 'packs.json').write_bytes(store_packs.manifest_bytes(manifest))
