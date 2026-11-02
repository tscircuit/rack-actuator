import numpy as np,math,json
q=math.sqrt(.5);rows=[]
for side in [-1,1]:
 for x in [-23,23]:
  r=np.array([x,side*5.5,-1.5]);n=np.array([0,-side*q,-q]);rows.append(np.r_[n,np.cross(r,n)])
for x,y in [(-23,-1),(23,1)]:
 r=np.array([x,y,-9]);n=np.array([0,0,1]);rows.append(np.r_[n,np.cross(r,n)])
a=np.array(rows);rank=np.linalg.matrix_rank(a,tol=1e-9);weights=np.array([1]*4+[math.sqrt(2)]*2)
residual=float(np.linalg.norm(a.T@weights));assert rank==5 and residual<1e-9 and np.all(a[:,0]==0)
print(json.dumps({'contact_constraint_rank':int(rank),'free_rigid_motion':'X translation','lower_lateral_offsets_mm':[-1,1],'positive_preload_equilibrium_residual':residual,'interpretation':'Rigid contact geometry restrains five axes; positive opposed preload is possible. Does not predict elastic stiffness or load capacity.'}))
