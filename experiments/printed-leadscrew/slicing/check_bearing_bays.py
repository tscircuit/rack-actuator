"""Check actual support and interface extrusion in bearing-adjustment bays.
Default: compare the published 40 mm / 1x printed-screw before and after slices.
Optional --paths, --configuration and --report: check another parsed base slice.
Whole segments are clipped, including paths crossing a region without endpoints inside.
"""
from pathlib import Path
import argparse,gzip,json,math
def clips(a,b,c,d,roi):
 lo,hi=0.,1.
 for start,delta,mn,mx in [(a,c-a,roi[0],roi[1]),(b,d-b,roi[2],roi[3])]:
  if abs(delta)<1e-10:
   if not mn<=start<=mx:return False
  else:
   x,y=sorted([(mn-start)/delta,(mx-start)/delta]);lo=max(lo,x);hi=min(hi,y)
   if hi<lo:return False
 return hi-lo>1e-8 and math.hypot(c-a,d-b)>1e-8
def inspect(data,stations,centers,widen):
 checks=[]
 for i,station in enumerate(stations):
  bx=centers[2*i][0]
  for side in [-1,1]:
   ya,yb=sorted([side*(19+widen),side*(34+widen)]);roi=[min(station-7,bx-10),station+7,ya,yb]
   counts={label:sum(clips(*paths[j:j+4],roi) for layer in data['layers'] for paths in [layer['paths'][group]] for j in range(0,len(paths),4)) for group,label in [(1,'support'),(2,'interface')]}
   checks.append(dict(station_x_mm=station,side=side,region_xy_mm=roi,height_scope="all sliced layers",extrusion_segments=counts))
 return dict(stl_sha256=data['meta']['stl_sha256'],support_grams=data['meta']['support_grams'],checks=checks)
def read(path):return json.loads(gzip.decompress(path.read_bytes()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--paths',type=Path);p.add_argument('--configuration',type=Path);p.add_argument('--report',type=Path);args=p.parse_args()
 if args.paths:
  if not args.configuration or not args.report:p.error('--paths requires --configuration and --report')
  data=read(args.paths);config=json.loads(args.configuration.read_text());report=inspect(data,config['stations'],config['adjustmentBoltCenters'],(config['baseWidth']-80)/2)
  assert all(sum(q['extrusion_segments'].values())==0 for q in report['checks']),report
  report.update(configuration=dict(family=config['experiment'],width=config['widthMultiple'],stroke_mm=config['stroke'],screw_length_mm=config['screwLength'],support=config['screwSupport']),meta=data['meta'],passed=True)
  args.report.write_text(json.dumps(report,indent=2)+'\n')
 else:
  root=Path('dist/experiments/printed-leadscrew/slice');reports={}
  for version in ['before-bearing-slopes','after']:
   reports[version]=inspect(read(root/f'{version}.paths.json.gz'),[63,137],[[51,-26],[51,26],[125,-26],[125,26]],0)
   assert all((sum(q['extrusion_segments'].values())>0 if version=='before-bearing-slopes' else sum(q['extrusion_segments'].values())==0) for q in reports[version]['checks']),reports
  summary=json.loads((root/'summary.json').read_text());summary['bearing_bay_supports']=dict(scope='Actual automatic-support-everywhere P2S PETG slice; all four bearing/adjustment bays checked by segment clipping.',comparisons=reports)
  (root/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 print('PASS: zero support and interface paths in all four bearing-adjustment bays.')
if __name__=='__main__':main()
