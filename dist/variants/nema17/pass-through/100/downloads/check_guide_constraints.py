"""Check rigid guide constraints using this preset's validated bearing stations."""
import argparse,json,math
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser()
p.add_argument('--report',type=Path,default=Path(__file__).with_name('validation.json'))
p.add_argument('--span',type=float,help='Override the station spacing in mm for a kinematic study')
a=p.parse_args()
if a.span is not None:
 if a.span<=0:p.error('Span must be positive')
 stations=[-a.span/2,a.span/2]
else:
 data=json.loads(a.report.read_text());stations=data['bearing_stations_x_mm']
assert len(stations)==2 and stations[0]<stations[1] and all(math.isfinite(x) for x in stations)
q=math.sqrt(.5);rows=[]
for side in [-1,1]:
 for x in stations:
  r=np.array([x,side*5.5,-1.5]);n=np.array([0,-side*q,-q]);rows.append(np.r_[n,np.cross(r,n)])
for x,y in zip(stations,[-1,1]):
 r=np.array([x,y,-9]);n=np.array([0,0,1]);rows.append(np.r_[n,np.cross(r,n)])
contacts=np.array(rows);rank=np.linalg.matrix_rank(contacts,tol=1e-9);weights=np.array([1]*4+[math.sqrt(2)]*2)
residual=float(np.linalg.norm(contacts.T@weights))
assert rank==5 and residual<1e-9 and np.all(contacts[:,0]==0)
print(json.dumps({'bearing_stations_x_mm':stations,'station_spacing_mm':stations[1]-stations[0],'contact_constraint_rank':int(rank),'free_rigid_motion':'X translation','lower_lateral_offsets_mm':[-1,1],'positive_preload_equilibrium_residual':residual,'interpretation':'Rigid contact geometry restrains five axes; positive opposed preload is possible. Does not predict elastic stiffness or load capacity.'}))
