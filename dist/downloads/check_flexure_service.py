"""Check bearing and enclosure service paths at <=0.5 mm hardware increments.
Run after build_presets.py; emits a separate source-bound report per preset.
"""
from pathlib import Path
import argparse,concurrent.futures,hashlib,itertools,json,math,subprocess,sys
from build_presets import PRESETS,folder_for
ROOT=Path(__file__).resolve().parent

def check(motor,stroke):
 source=(ROOT/'model.py').read_text();sha=hashlib.sha256(source.encode()).hexdigest()
 out=folder_for(motor,stroke);dest=out/'downloads/flexure-service-validation.json'
 if dest.exists():
  old=json.loads(dest.read_text())
  if old.get('source_sha256')==sha and old.get('checker_sha256')==hashlib.sha256(Path(__file__).read_bytes()).hexdigest() and not old['failures']:
   print('Cached service paths',motor,stroke,flush=True);return
 sys.argv=['model.py','--motor',motor,'--stroke',str(stroke),'--skip-export','--out',str(out)]
 ns={'__file__':str(ROOT/'model.py'),'__name__':'cad_geometry'}
 exec(compile(source.split('\n# Clear obsolete generated meshes')[0],str(ROOT/'model.py'),'exec'),ns)
 parts=ns['parts'];tracks=ns['tracks'];offset=ns['offset'];angle=ns['angle']
 bounds=sorted({.38,1.}|{t[k] for ts in tracks.values() for t in ts for k in ['start','end'] if .38<=t[k]<=1})
 times={.38,1.}
 for lo,hi in zip(bounds[:-1],bounds[1:]):
  travel=max(math.dist(offset(g,lo),offset(g,hi)) for g in tracks)
  n=max(2,math.ceil(travel/.5));times.update(lo+(hi-lo)*k/n for k in range(n+1))
 assert all(abs(angle(g,.38)-angle(g,1.))<1e-7 for g in tracks),'Service checker expects constant rotations'
 moved={g for g in tracks if offset(g,.38)!=offset(g,1.)}
 pairs=[(i,j) for i,j in itertools.combinations(range(len(parts)),2) if (parts[i]['group'] in moved or parts[j]['group'] in moved) and parts[i]['group']!=parts[j]['group']]
 poses={};relative={};fail=[];exact=0
 def pose(i,e):
  p=parts[i];t=offset(p['group'],e);a=angle(p['group'],e);key=(i,tuple(round(v,8) for v in t),round(a%360,8))
  if key not in poses:
   v=ns['base_print'] if p.get('flex_chassis') else p['shape']
   if a%360:v=ns['rotate_drive'](v,a)
   v=v.translate(t);poses[key]=(v,v.BoundingBox())
  return poses[key]
 for e in sorted(times):
  for i,j in pairs:
   p,q=parts[i],parts[j];pi=offset(p['group'],e);pj=offset(q['group'],e)
   # No moving group in this tail rotates; all other rotations are constant.
   key=(i,j,tuple(round(pj[k]-pi[k],8) for k in range(3)))
   if key not in relative:
    s,b=pose(i,e);t,c=pose(j,e)
    if b.xmax<=c.xmin or c.xmax<=b.xmin or b.ymax<=c.ymin or c.ymax<=b.ymin or b.zmax<=c.zmin or c.zmax<=b.zmin:v=0.
    else:v=max(0,s.intersect(t).Volume());exact+=1
    relative[key]=v
   v=relative[key]
   if v>.01:fail.append({'at':round(e,8),'a':p['name'],'b':q['name'],'volume_mm3':round(v,6)})
 report={'revision':21,'motor':motor,'stroke_mm':stroke,'source_sha256':sha,'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'explosion_interval':[.38,1.],'maximum_translation_increment_mm':.5,'samples':len(times),'part_pairs':len(pairs),'exact_intersections':exact,'failures':fail,'method':'Exact solid intersections at <=0.5 mm hardware increments; relative-pose cache and bounding-box rejection. Covers angled axle extraction and parking, roller and motor removal, the chassis slide and tray withdrawal, and lower bearing hardware removal. Sampled geometry, not a continuous proof.'}
 dest.write_text(json.dumps(report,indent=2)+'\n')
 print('Service paths',motor,stroke,len(times),'samples;',len(fail),'failures',flush=True)
 assert not fail,fail[:8]

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--motor',choices=['nema17','nema14']);p.add_argument('--stroke',type=int,choices=PRESETS);p.add_argument('--jobs',type=int,default=4);a=p.parse_args()
 if a.motor and a.stroke:check(a.motor,a.stroke)
 else:
  def run(item):
   m,s=item
   return subprocess.run([sys.executable,str(Path(__file__).resolve()),'--motor',m,'--stroke',str(s)],cwd=ROOT).returncode
  with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:results=list(pool.map(run,itertools.product(['nema17','nema14'],PRESETS)))
  assert not any(results),'Service-path check failed'
