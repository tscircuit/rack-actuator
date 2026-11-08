"""Build and validate six enclosed worm presets; keep the spur geometry untouched."""
import argparse, concurrent.futures, gzip, json, os, pathlib, shutil, subprocess, sys, zipfile
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--jobs',type=int,default=2);p.add_argument('--skip-valid',action='store_true');p.add_argument('--step',action='store_true');p.add_argument('--motor',choices=['nema17','nema14']);p.add_argument('--stroke',type=int,choices=[40,100,150]);a=p.parse_args()
configs=[(m,s) for m in ([a.motor] if a.motor else ['nema17','nema14']) for s in ([a.stroke] if a.stroke else [40,100,150])]
def build(config):
 motor,stroke=config
 out=ROOT/'dist/experiments/worm-rack'
 if config!=('nema17',40):out=out/'variants'/motor/str(stroke)
 if a.skip_valid and (out/'validation.json').exists():
  import hashlib
  r=json.loads((out/'validation.json').read_text())
  sources=[('source_sha256','model.py'),('validation_source_sha256','validate.py'),('enclosure_source_sha256','enclosure.py'),('flexure_source_sha256','flexures.py')]
  if r.get('passed') and all(r.get(k)==hashlib.sha256((ROOT/'experiments/worm-rack'/f).read_bytes()).hexdigest() for k,f in sources):
   try:
    with zipfile.ZipFile(out/'worm-rack-experiment.zip') as z:
     complete=z.read('validation.json')==(out/'validation.json').read_bytes() and all(z.read('experiments/worm-rack/'+f)==(ROOT/'experiments/worm-rack'/f).read_bytes() for _,f in sources)
    d=json.loads(gzip.decompress((out/'assembly.json.gz').read_bytes()))
    if complete and (d['motor'].lower(),d['stroke'])==config and json.loads((out/'configuration.json').read_text()).get('step_exported',True)==a.step:return config
   except (OSError,KeyError,zipfile.BadZipFile):pass
 log=ROOT/f'work/worm-enclosed-{motor}-{stroke}.log';log.parent.mkdir(exist_ok=True)
 with log.open('w') as f:subprocess.run([sys.executable,str(ROOT/'experiments/worm-rack/model.py'),'--motor',motor,'--stroke',str(stroke),'--check']+(['--step'] if a.step else []),cwd=ROOT,env=dict(os.environ,OPENBLAS_NUM_THREADS='1'),stdout=f,stderr=subprocess.STDOUT,check=True)
 print(motor,stroke,'checked and exported',flush=True);return config
with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:list(pool.map(build,configs))
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
print(f'{len(configs)} worm presets ready; existing standalone spur STEP downloads preserved.')
# Keep raw, ready-to-print STLs in each ZIP; compress duplicate standalone files
# so all six presets fit within the static host's artifact budget.
for motor,stroke in configs:
 folder=ROOT/'dist/experiments/worm-rack'
 if (motor,stroke)!=('nema17',40):folder=folder/'variants'/motor/str(stroke)
 for stl in (folder/'stl').glob('*.stl'):
  raw=stl.read_bytes();compressed=stl.with_suffix('.stl.gz')
  with gzip.open(compressed,'wb',compresslevel=9) as f:f.write(raw)
  assert gzip.decompress(compressed.read_bytes())==raw
  stl.unlink()
 notes=(ROOT/'experiments/worm-rack/README.md').read_text().replace('../../dist/experiments/worm-rack/validation.json','validation.json')
 (folder/'README.md').write_text(notes)
 replacements={'README.md':notes.encode(),'experiments/worm-rack/README.md':(ROOT/'experiments/worm-rack/README.md').read_bytes(),'experiments/worm-rack/build_presets.py':pathlib.Path(__file__).read_bytes(),'experiments/worm-rack/requirements.txt':(ROOT/'experiments/worm-rack/requirements.txt').read_bytes()}
 bundle=folder/'worm-rack-experiment.zip';temp=ROOT/f'work/worm-bundle-{motor}-{stroke}.zip'
 with zipfile.ZipFile(bundle) as src,zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as dst:
  for info in src.infolist():dst.writestr(info,replacements.get(info.filename,src.read(info.filename)))
 os.replace(temp,bundle)
# Keep duplicate standalone CAD files in the public repository; the site hosts
# complete ZIP bundles and links directly to these repository downloads.
for motor,stroke in configs:
 folder=ROOT/'dist/experiments/worm-rack'
 if (motor,stroke)!=('nema17',40):folder=folder/'variants'/motor/str(stroke)
 destination=ROOT/'downloads/worm'/motor/str(stroke);destination.mkdir(parents=True,exist_ok=True)
 if any((folder/'stl').glob('*.stl.gz')):
  for old in destination.glob('*.stl.gz'):old.unlink()
 for name in ['validation-reference.json','validation-reference-model.py']:
  (folder/name).unlink(missing_ok=True)
 step=folder/'worm-rack.step.gz'
 if step.exists():os.replace(step,destination/step.name)
 elif not a.step:(destination/'worm-rack.step.gz').unlink(missing_ok=True)
 for stl in (folder/'stl').glob('*.stl.gz'):os.replace(stl,destination/stl.name)
 if (folder/'stl').exists() and not any((folder/'stl').iterdir()):(folder/'stl').rmdir()
 # Serve revised chassis and assembly downloads with this Site version;
 # the external public repository may still contain the previous geometry.
 for name in ['worm-rack.step.gz','integral_worm_chassis.stl.gz','standard-size_enclosure_tray.stl.gz']:
  if (destination/name).exists():shutil.copy2(destination/name,folder/name)
files=[p for p in (ROOT/'dist').rglob('*') if p.is_file()]
# Optimize only as much as needed to retain hosting headroom. Zopfli emits
# ordinary gzip; the decompressed STEP is byte-identical to the ZIP download.
if sum(p.stat().st_size for p in files)>249*1024**2:
 import zopfli.gzip
 steps=sorted((ROOT/'dist/experiments/worm-rack').rglob('worm-rack.step.gz'),key=lambda p:p.stat().st_size,reverse=True)
 for step in steps:
  if sum(p.stat().st_size for p in files)<=249*1024**2:break
  raw=gzip.decompress(step.read_bytes());compressed=zopfli.gzip.compress(raw,numiterations=1)
  assert gzip.decompress(compressed)==raw
  if len(compressed)>=step.stat().st_size:continue
  config=json.loads((step.parent/'configuration.json').read_text())
  step.write_bytes(compressed)
  shutil.copy2(step,ROOT/'downloads/worm'/config['motor']/str(config['stroke'])/step.name)
  print('Lossless STEP compression:',config['motor'],config['stroke'],flush=True)
assert sum(p.stat().st_size for p in files)<250*1024**2,'Static site exceeds 250 MiB'
assert max(p.stat().st_size for p in files)<25*1024**2,'One static file exceeds 25 MiB'
print('Standalone STLs compressed; ZIP bundles retain ordinary STL files'+(' and STEP.' if a.step else ' (STEP omitted).'),flush=True)
