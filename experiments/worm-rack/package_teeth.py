"""Package checked tooth variants and remove duplicate standalone STL payloads.
The viewer extracts the selected STL from its ZIP, with CRC32 verification.
"""
from pathlib import Path
import gzip,json,zipfile,os
ROOT=Path(__file__).resolve().parents[2]
available={}
for motor in ['nema17','nema14']:
 for stroke in [40,100,150]:
  folder=ROOT/'dist/experiments/worm-rack'
  if (motor,stroke)!=('nema17',40):folder=folder/'variants'/motor/str(stroke)
  bundle=folder/'worm-rack-experiment.zip';temporary=bundle.with_suffix('.tmp')
  with zipfile.ZipFile(bundle) as z:
   ready=all(f'teeth/{style}/validation.json' in z.namelist() and json.loads(z.read(f'teeth/{style}/validation.json'))['passed'] for style in ['compliant','solid'])
  available[f'{motor}-{stroke}']=ready
  if not ready:continue
  notes=(ROOT/'experiments/worm-rack/README.md').read_text().replace('../../dist/experiments/worm-rack/validation.json','validation.json')
  replacements={'README.md':notes.encode(),'experiments/worm-rack/README.md':(ROOT/'experiments/worm-rack/README.md').read_bytes(),'experiments/worm-rack/package_teeth.py':Path(__file__).read_bytes()}
  with zipfile.ZipFile(bundle) as src,zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as dst:
   for style in ['compliant','solid']:
    target=folder/'teeth'/style;report=json.loads((target/'validation.json').read_text());assert report['passed'];assert src.read(f'teeth/{style}/validation.json')==(target/'validation.json').read_bytes()
    for file,entry in [('rack',f'stl/matched_{style}_rack.stl'),('coupon','stl/'+('solid_rack_mesh_coupon.stl' if style=='solid' else 'rack_mesh_coupon.stl'))]:
     standalone=target/(file+'.stl.gz')
     if standalone.exists():assert gzip.decompress(standalone.read_bytes())==src.read(entry)
   for info in src.infolist():
    if info.filename not in replacements:dst.writestr(info,src.read(info.filename))
   for name,data in replacements.items():dst.writestr(name,data)
  os.replace(temporary,bundle);(folder/'README.md').write_text(notes)
  for style in ['compliant','solid']:
   for file in ['rack','coupon']:(folder/'teeth'/style/(file+'.stl.gz')).unlink(missing_ok=True)
  print('Packaged',motor,stroke,flush=True)
(ROOT/'dist/experiments/worm-rack/rack-options.json').write_text(json.dumps(available,indent=2))
# Four spur animation payloads are byte-identical across enclosure types.
# The main viewer shares their canonical enclosed paths; no CAD is changed.
for motor in ['nema17','nema14']:
 for stroke in [40,100]:
  canonical=ROOT/'dist'
  if stroke==40:
   if motor=='nema14':canonical=canonical/'variants/nema14'
  else:canonical=canonical/'variants'/motor/str(stroke)
  canonical=canonical/'assets/spring-states.json.gz'
  duplicate=ROOT/'dist/variants'/motor/'pass-through'/str(stroke)/'assets/spring-states.json.gz'
  if duplicate.exists():
   assert gzip.decompress(canonical.read_bytes())==gzip.decompress(duplicate.read_bytes());duplicate.unlink()
files=[p for p in (ROOT/'dist').rglob('*') if p.is_file()]
print('Static assets MiB',sum(p.stat().st_size for p in files)/2**20)
assert sum(p.stat().st_size for p in files)<250*2**20
assert max(p.stat().st_size for p in files)<25*2**20
