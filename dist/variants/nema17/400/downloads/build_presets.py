"""Generate and check the 12 selectable models. Run package_designs.py afterward."""
from pathlib import Path
import gzip,argparse,concurrent.futures,hashlib,json,subprocess,sys,threading
ROOT=Path(__file__).resolve().parent
PRESETS=[40,100,150,200,250,400]
def folder_for(motor,stroke):
 if stroke==40:return ROOT/'dist' if motor=='nema17' else ROOT/'dist/variants/nema14'
 return ROOT/'dist/variants'/motor/str(stroke)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--jobs',type=int,default=4);p.add_argument('--strokes',type=int,nargs='+',default=PRESETS);p.add_argument('--motors',nargs='+',default=['nema17','nema14']);a=p.parse_args()
 assert 1<=a.jobs<=6 and set(a.strokes)<=set(PRESETS) and set(a.motors)<={'nema17','nema14'}
 source_hash=hashlib.sha256((ROOT/'model.py').read_bytes()).hexdigest();geometry_hash=hashlib.sha256((ROOT/'model.py').read_text().split('\n# Clear obsolete generated meshes')[0].encode()).hexdigest();logs=ROOT/'work/presets';logs.mkdir(parents=True,exist_ok=True);failed=threading.Event()
 def build(item):
  motor,stroke=item;out=folder_for(motor,stroke);report=out/'downloads/validation.json'
  if report.exists():
   r=json.loads(report.read_text())
   if r.get('source_sha256')==source_hash and r.get('stroke_mm')==stroke and r.get('motion_samples')==41 and not r['explosion_failures'] and not r['motion_failures']:
    print('Cached',motor,stroke,flush=True);return True
  if failed.is_set():return False
  print('Building',motor,stroke,flush=True)
  skip=[];mesh=out/'assets/assembly.json'
  compressed=out/'assets/assembly.json.gz'
  if mesh.exists() or compressed.exists():
   d=json.loads(mesh.read_text() if mesh.exists() else gzip.decompress(compressed.read_bytes()))
   if d.get('geometrySourceSha256')==geometry_hash and d.get('stroke')==stroke and d.get('motor','').lower()==motor:skip=['--skip-export']
  with (logs/f'{motor}-{stroke}.log').open('w') as log:
   r=subprocess.run([sys.executable,str(ROOT/'model.py'),'--motor',motor,'--stroke',str(stroke),'--out',str(out),'--check',*skip],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
  if r.returncode:failed.set();print('FAILED',motor,stroke,'see',logs/f'{motor}-{stroke}.log',flush=True);return False
  print('Passed',motor,stroke,flush=True);return True
 order=[s for s in [40,400,100,150,200,250] if s in a.strokes]
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:results=list(pool.map(build,[(m,s) for s in order for m in a.motors]))
 if not all(results):sys.exit('Preset generation failed; see work/presets logs.')
 print('All requested presets generated and checked.',flush=True)
