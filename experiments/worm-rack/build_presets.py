"""Build and validate six enclosed worm presets; keep the spur geometry untouched."""
import argparse, concurrent.futures, gzip, json, os, pathlib, subprocess, sys, zipfile
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--jobs',type=int,default=2);p.add_argument('--skip-valid',action='store_true');a=p.parse_args()
def build(config):
 motor,stroke=config
 out=ROOT/'dist/experiments/worm-rack'
 if config!=('nema17',40):out=out/'variants'/motor/str(stroke)
 if a.skip_valid and (out/'validation.json').exists():
  import hashlib
  r=json.loads((out/'validation.json').read_text())
  sources=[('source_sha256','model.py'),('validation_source_sha256','validate.py'),('enclosure_source_sha256','enclosure.py')]
  if r.get('passed') and all(r.get(k)==hashlib.sha256((ROOT/'experiments/worm-rack'/f).read_bytes()).hexdigest() for k,f in sources):
   try:
    with zipfile.ZipFile(out/'worm-rack-experiment.zip') as z:
     complete=z.read('validation.json')==(out/'validation.json').read_bytes() and all(z.read('experiments/worm-rack/'+f)==(ROOT/'experiments/worm-rack'/f).read_bytes() for _,f in sources)
    d=json.loads(gzip.decompress((out/'assembly.json.gz').read_bytes()))
    if complete and (d['motor'].lower(),d['stroke'])==config:return config
   except (OSError,KeyError,zipfile.BadZipFile):pass
 log=ROOT/f'work/worm-enclosed-{motor}-{stroke}.log';log.parent.mkdir(exist_ok=True)
 with log.open('w') as f:subprocess.run([sys.executable,str(ROOT/'experiments/worm-rack/model.py'),'--motor',motor,'--stroke',str(stroke),'--check'],cwd=ROOT,env=dict(os.environ,OPENBLAS_NUM_THREADS='1'),stdout=f,stderr=subprocess.STDOUT,check=True)
 print(motor,stroke,'checked and exported',flush=True);return config
with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:list(pool.map(build,[(m,s) for m in ['nema17','nema14'] for s in [40,100,150]]))
# Gzip the existing standalone spur STEP downloads to leave room for the worm family.
# Their bytes inside the ZIP bundles and all production CAD geometry are unchanged.
catalog_path=ROOT/'dist/presets.json';catalog=json.loads(catalog_path.read_text())
for preset in catalog['presets']:
 folder=ROOT/'dist'/preset['basePath'].removeprefix('./')/'downloads'
 step=folder/preset['stepFile']
 if step.suffix=='.step':
  compressed=step.with_suffix('.step.gz')
  with gzip.open(compressed,'wb',compresslevel=9) as f:f.write(step.read_bytes())
  assert gzip.decompress(compressed.read_bytes())==step.read_bytes()
  step.unlink();preset['stepFile']=compressed.name
catalog_path.write_text(json.dumps(catalog,indent=2)+'\n')
print('Six worm presets ready; standalone STEP downloads compressed without geometry changes.')
# Keep raw, ready-to-print STLs in each ZIP; compress duplicate standalone files
# so all six presets fit within the static host's artifact budget.
for motor in ['nema17','nema14']:
 for stroke in [40,100,150]:
  folder=ROOT/'dist/experiments/worm-rack'
  if (motor,stroke)!=('nema17',40):folder=folder/'variants'/motor/str(stroke)
  for stl in (folder/'stl').glob('*.stl'):
   raw=stl.read_bytes();compressed=stl.with_suffix('.stl.gz')
   with gzip.open(compressed,'wb',compresslevel=9) as f:f.write(raw)
   assert gzip.decompress(compressed.read_bytes())==raw
   stl.unlink()
  notes=(ROOT/'experiments/worm-rack/README.md').read_text().replace('../../dist/experiments/worm-rack/validation.json','validation.json')
  (folder/'README.md').write_text(notes)
  replacements={'README.md':notes.encode(),'experiments/worm-rack/README.md':(ROOT/'experiments/worm-rack/README.md').read_bytes(),'experiments/worm-rack/build_presets.py':pathlib.Path(__file__).read_bytes()}
  bundle=folder/'worm-rack-experiment.zip';temp=ROOT/f'work/worm-bundle-{motor}-{stroke}.zip'
  with zipfile.ZipFile(bundle) as src,zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as dst:
   for info in src.infolist():dst.writestr(info,replacements.get(info.filename,src.read(info.filename)))
  os.replace(temp,bundle)
files=[p for p in (ROOT/'dist').rglob('*') if p.is_file()]
assert sum(p.stat().st_size for p in files)<250*1024**2,'Static site exceeds 250 MiB'
assert max(p.stat().st_size for p in files)<25*1024**2,'One static file exceeds 25 MiB'
print('Standalone STLs compressed; ZIP bundles retain ordinary STEP and STL files.',flush=True)
