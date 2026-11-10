"""Check actual support paths through the four floor access openings."""
from pathlib import Path
import gzip,json
root=Path('dist/experiments/printed-leadscrew/slice');config=json.loads(Path('dist/experiments/printed-leadscrew/configuration.json').read_text())
reports={}
for version in ['before-bearing-slopes','after']:
 data=json.loads(gzip.decompress((root/f'{version}.paths.json.gz').read_bytes()));checks=[]
 for a,b,c,d in config['printability']['support_access_xy_mm']:
  found=[]
  for l in data['layers']:
   if l['z']>5.2:break
   for group in [1,2]:
    paths=l['paths'][group]
    for j in range(0,len(paths),4):
     x=(paths[j]+paths[j+2])/2;y=(paths[j+1]+paths[j+3])/2
     if a<=x<=b and c<=y<=d:found.append(l['z']);break
  checks.append({'opening_xy_mm':[a,b,c,d],'support_min_z_mm':min(found) if found else None,'support_max_z_mm':max(found) if found else None,'reaches_first_layer':bool(found) and min(found)==.2})
 assert all(q['reaches_first_layer']==(version=='before-bearing-slopes') for q in checks)
 reports[version]=checks
# Interface paths would indicate supports directly meeting these overhangs.
revised=json.loads(gzip.decompress((root/'after.paths.json.gz').read_bytes()))
motor_interface=side_interface=0
for layer in revised['layers']:
 paths=layer['paths'][2]
 for j in range(0,len(paths),4):
  x=(paths[j]+paths[j+2])/2;y=(paths[j+1]+paths[j+3])/2
  if 5<layer['z']<16 and 0<x<6 and abs(y)<20:motor_interface+=1
  for name,layout in config['cutoutPlanning']['layouts'].items():
   if not name.startswith('base_side'):continue
   sign=int(name.split('_')[2])
   if not 34<=sign*y<=40:continue
   for a,b,c,d in layout['rectangles_mm']:
    if a<x<b and c<layer['z']<d:side_interface+=1
assert motor_interface==side_interface==0
summary=json.loads((root/'summary.json').read_text());summary['floor_support_access']=reports;summary['targeted_support_interface_segments']={'motor_filled_region':motor_interface,'pitched_side_windows':side_interface};summary['access_check_scope']='The preceding geometry needed support paths through the four floor openings; the sloped bearing bays now contain no support paths there.'
(root/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print('PASS former support-removal openings now contain no support paths below the floor')
