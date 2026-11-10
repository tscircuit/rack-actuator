"""Check actual support paths around both motor-side lid mounts.

Uses the current published base slice.
Counts segments that intersect either mount region; no midpoint approximation.
"""
from pathlib import Path
import gzip,json,math
root=Path('dist/experiments/printed-leadscrew/slice')
def clips(a,b,c,d,rect):
 lo,hi=0.,1.
 for start,delta,mn,mx in [(a,c-a,rect[0],rect[1]),(b,d-b,rect[2],rect[3])]:
  if abs(delta)<1e-10:
   if start<mn or start>mx:return False
  else:
   x,y=sorted([(mn-start)/delta,(mx-start)/delta]);lo=max(lo,x);hi=min(hi,y)
   if hi<lo:return False
 return hi-lo>1e-8 and math.hypot(c-a,d-b)>1e-8
reports={}
for version in ['after']:
 data=json.loads(gzip.decompress((root/f'{version}.paths.json.gz').read_bytes()));checks=[]
 for sign in [-1,1]:
  ya,yb=sorted([20*sign,41*sign]);roi=[3,18,ya,yb];counts={'support':0,'interface':0}
  for layer in data['layers']:
   if layer['z']>=64:continue
   for group,name in [(1,'support'),(2,'interface')]:
    paths=layer['paths'][group]
    counts[name]+=sum(clips(*paths[i:i+4],roi) for i in range(0,len(paths),4))
  checks.append({'side':sign,'region_xy_mm':roi,'below_z_mm':64,'extrusion_segments':counts})
 reports[version]={'stl_sha256':data['meta']['stl_sha256'],'support_grams':data['meta']['support_grams'],'checks':checks}
 assert all(sum(q['extrusion_segments'].values())==0 for q in checks),checks
summary=json.loads((root/'summary.json').read_text())
summary['motor_lid_brace_supports']={'scope':'Actual P2S / Generic PETG / 0.20 mm / tree(auto) everywhere slice of the 40 mm 1x base; checks both motor-side mount regions.','comparisons':reports}
(root/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('PASS both motor-side mounts have zero support and interface paths.')
