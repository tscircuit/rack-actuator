"""Prove lid screw removal/parking continuously.
Usage: python check_lid_screw_parking.py nema17 40
Run from the directory containing model.py.
"""
import sys,math,json,itertools
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from build_presets import folder_for
motor,stroke=sys.argv[1],int(sys.argv[2]);source=Path('model.py').read_text()
sys.argv=['model.py','--motor',motor,'--stroke',str(stroke),'--skip-export']
ns={'__file__':str(Path('model.py').resolve()),'__name__':'cad_geometry'}
exec(compile(source.split('\n# Clear obsolete generated meshes')[0],'model.py','exec'),ns)
parts=ns['parts'];cyl=ns['cyl'];cq=ns['cq'];tracks=ns['tracks'];offset=ns['offset'];angle=ns['angle']
park=-tracks['cover_screws'][1]['delta'][1]
bounds=sorted({.05,1.}|{t[k] for ts in tracks.values() for t in ts for k in ['start','end'] if .05<=t[k]<=1})
minimum_y=math.inf;critical=None
for p in parts:
 if p['group']=='cover_screws':continue
 b=p['shape'].BoundingBox();lo=b.ymin
 if any(abs(angle(p['group'],t))>1e-7 for t in bounds):
  cx,cy,_=ns['PIVOT'];radius=max(math.hypot(x-cx,y-cy) for x in [b.xmin,b.xmax] for y in [b.ymin,b.ymax]);lo=cy-radius
 lo+=min(offset(p['group'],t)[1] for t in bounds)
 if lo<minimum_y:minimum_y=lo;critical=p['name']
checks=[];maximum_y=-math.inf
for p in parts:
 if p['group']!='cover_screws':continue
 c=p['shape'].Center();x,y=c.x,c.y;hz=ns['CASE_TOP']-3.3
 lift=cyl(1.45,55,x,y,hz-20).fuse(cyl(2.75,38,x,y,hz))
 def parked(r,h,z):return cq.Workplane('XY').slot2D(park+2*r,2*r,90).extrude(h).translate((x,y-park/2,z)).val()
 sideways=parked(1.45,20,hz+15).fuse(parked(2.75,3,hz+35))
 count=0;worst=0.
 for q in parts:
  if q['group']=='cover_screws':continue
  for sweep in [lift,sideways]:
   a,b=sweep.BoundingBox(),q['shape'].BoundingBox()
   if a.xmax<=b.xmin or b.xmax<=a.xmin or a.ymax<=b.ymin or b.ymax<=a.ymin or a.zmax<=b.zmin or b.zmax<=a.zmin:v=0.
   else:v=max(0,sweep.intersect(q['shape']).Volume())
   assert v<.01,(p['name'],q['name'],v)
   worst=max(worst,v)
  count+=1
 maximum_y=max(maximum_y,p['shape'].BoundingBox().ymax-park)
 checks.append({'part':p['name'],'stationary_part_pairs':count,'path':'Z +35 mm, then Y -180 mm','maximum_intersection_mm3':worst})
assert minimum_y-maximum_y>.5,(critical,minimum_y,maximum_y)
result={'motor':motor,'stroke':stroke,'parking_distance_mm':park,'screw_sweep_checks':checks,'stationary_after_fraction':.05,'parked_screws_maximum_y_mm':maximum_y,'all_other_parts_continuous_minimum_y_mm':minimum_y,'limiting_part':critical,'minimum_separating_y_gap_mm':minimum_y-maximum_y,'method':'Continuous solid swept envelopes prove extraction and parking until 5%. Thereafter every parked lid screw lies wholly below the global Y envelope of every other part across all piecewise-linear tracks. Rotating parts use full-circle bounding radii; flexure deformation changes only Z. Cover screws have equal translations and unchanged mutual spacing.'}
(folder_for(motor,stroke)/'downloads/lid-screw-clearance.json').write_text(json.dumps(result,indent=2)+'\n')
print(motor,stroke,'continuous parking proof gap',minimum_y-maximum_y,flush=True)
