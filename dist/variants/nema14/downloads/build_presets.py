"""Generate and check 12 models: two motors, three strokes and two bearing layouts."""
from pathlib import Path
import gzip,argparse,concurrent.futures,hashlib,json,subprocess,sys,threading
ROOT=Path(__file__).resolve().parent
PRESETS=[40,100,150]
LAYOUTS=['standard','short']
def folder_for(motor,stroke,layout='standard'):
 if layout=='short':return ROOT/'dist/variants'/motor/'short'/str(stroke)
 if stroke==40:return ROOT/'dist' if motor=='nema17' else ROOT/'dist/variants/nema14'
 return ROOT/'dist/variants'/motor/str(stroke)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--jobs',type=int,default=4);p.add_argument('--strokes',type=int,nargs='+',default=PRESETS);p.add_argument('--motors',nargs='+',default=['nema17','nema14']);p.add_argument('--layouts',nargs='+',default=LAYOUTS);a=p.parse_args()
 assert 1<=a.jobs<=6 and set(a.strokes)<=set(PRESETS) and set(a.motors)<={'nema17','nema14'} and set(a.layouts)<=set(LAYOUTS)
 source_hash=hashlib.sha256((ROOT/'model.py').read_bytes()).hexdigest();geometry_hash=hashlib.sha256((ROOT/'model.py').read_text().split('\n# Clear obsolete generated meshes')[0].encode()).hexdigest();logs=ROOT/'work/presets';logs.mkdir(parents=True,exist_ok=True);failed=threading.Event()
 def build(item):
  motor,stroke,layout=item;out=folder_for(motor,stroke,layout);report=out/'downloads/validation.json';tag=f'{motor}-{stroke}-{layout}'
  if report.exists():
   r=json.loads(report.read_text())
   if r.get('source_sha256')==source_hash and r.get('layout')==layout and r.get('motor','').lower()==motor and r.get('stroke_mm')==stroke and r.get('motion_samples')==41 and not r['explosion_failures'] and not r['motion_failures']:
    print('Cached',tag,flush=True);return True
  if failed.is_set():return False
  print('Building',tag,flush=True)
  skip=[];mesh=out/'assets/assembly.json';compressed=out/'assets/assembly.json.gz'
  if mesh.exists() or compressed.exists():
   d=json.loads(mesh.read_text() if mesh.exists() else gzip.decompress(compressed.read_bytes()))
   if d.get('geometrySourceSha256')==geometry_hash and d.get('layout')==layout and d.get('stroke')==stroke and d.get('motor','').lower()==motor:skip=['--skip-export']
  with (logs/f'{tag}.log').open('w') as log:
   r=subprocess.run([sys.executable,str(ROOT/'model.py'),'--motor',motor,'--stroke',str(stroke),'--layout',layout,'--out',str(out),'--check',*skip],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
  if r.returncode:failed.set();print('FAILED',tag,'see',logs/f'{tag}.log',flush=True);return False
  print('Passed',tag,flush=True);return True
 order=[s for s in [40,150,100] if s in a.strokes]
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:results=list(pool.map(build,[(m,s,l) for s in order for l in a.layouts for m in a.motors]))
 if not all(results):sys.exit('Preset generation failed; see work/presets logs.')
 print('All requested presets generated and checked.',flush=True)
