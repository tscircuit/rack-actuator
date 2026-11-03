"""Generate and check twelve models: two motors, three strokes and two enclosure variants."""
from pathlib import Path
import gzip,argparse,concurrent.futures,hashlib,json,subprocess,sys,threading
ROOT=Path(__file__).resolve().parent
PRESETS=[40,100,150]
ENCLOSURES=["enclosed","pass-through"]
def folder_for(motor,stroke,enclosure="enclosed"):
 if enclosure=="pass-through":return ROOT/"dist/variants"/motor/enclosure/str(stroke)
 if stroke==40:return ROOT/'dist' if motor=='nema17' else ROOT/'dist/variants/nema14'
 return ROOT/'dist/variants'/motor/str(stroke)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--jobs',type=int,default=4);p.add_argument('--strokes',type=int,nargs='+',default=PRESETS);p.add_argument('--motors',nargs='+',default=['nema17','nema14']);p.add_argument('--enclosures',nargs='+',choices=ENCLOSURES,default=ENCLOSURES);a=p.parse_args()
 assert 1<=a.jobs<=6 and set(a.strokes)<=set(PRESETS) and set(a.motors)<={'nema17','nema14'}
 source_hash=hashlib.sha256((ROOT/'model.py').read_bytes()).hexdigest();geometry_hash=hashlib.sha256((ROOT/'model.py').read_text().split('\n# Clear obsolete generated meshes')[0].encode()).hexdigest();logs=ROOT/'work/presets';logs.mkdir(parents=True,exist_ok=True);failed=threading.Event()
 def build(item):
  motor,stroke,enclosure=item;out=folder_for(motor,stroke,enclosure);report=out/'downloads/validation.json';tag=f'{motor}-{stroke}-{enclosure}'
  if report.exists():
   r=json.loads(report.read_text())
   if r.get('source_sha256')==source_hash and r.get('motor','').lower()==motor and r.get('stroke_mm')==stroke and r.get('enclosure_variant')==enclosure and r.get('motion_samples')==41 and not r['explosion_failures'] and not r['motion_failures']:
    print('Cached',tag,flush=True);return True
  if failed.is_set():return False
  print('Building',tag,flush=True)
  skip=[];mesh=out/'assets/assembly.json';compressed=out/'assets/assembly.json.gz'
  if mesh.exists() or compressed.exists():
   d=json.loads(mesh.read_text() if mesh.exists() else gzip.decompress(compressed.read_bytes()))
   if d.get('geometrySourceSha256')==geometry_hash and d.get('stroke')==stroke and d.get('motor','').lower()==motor and d.get('enclosureVariant')==enclosure:skip=['--skip-export']
  with (logs/f'{tag}.log').open('w') as log:
   r=subprocess.run([sys.executable,str(ROOT/'model.py'),'--motor',motor,'--stroke',str(stroke),'--enclosure',enclosure,'--out',str(out),'--check',*skip],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
  if r.returncode:failed.set();print('FAILED',tag,'see',logs/f'{tag}.log',flush=True);return False
  print('Passed',tag,flush=True);return True
 order=[s for s in [40,150,100] if s in a.strokes]
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:results=list(pool.map(build,[(m,s,e) for e in a.enclosures for s in order for m in a.motors]))
 if not all(results):sys.exit('Preset generation failed; see work/presets logs.')
 print('All requested presets generated and checked.',flush=True)
