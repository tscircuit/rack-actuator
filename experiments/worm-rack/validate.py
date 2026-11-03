"""Executed by model.py with its constructed CadQuery namespace.
Dense motion uses FCL triangle intersections with OCC confirmation of candidates.
Static pairs and selected mesh poses use OCC directly (including containment).
"""
import fcl
import numpy as np
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepTools import BRepTools

def validate():
 report={'experiment':'worm-rack-nema17-40','geometry_cache_sha256':source_hash,'source_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'validation_source_sha256':hashlib.sha256((ROOT/'experiments/worm-rack/validate.py').read_bytes()).hexdigest(),'method':'All assembled pairs checked as OCC solids. Dense motion/separation: 0.002 mm absolute / 0.04 rad CAD tessellation, FCL triangle candidates confirmed by OCC intersections. Five mesh poses use full OCC intersections. Sampled checks, not continuous collision proof or FEA.','motor':'NEMA17','stroke_mm':40,'module_mm':2,'axial_pressure_angle_deg':20,'starts':1,'lead_mm':LEAD,'worm_pitch_diameter_mm':24,'worm_outside_diameter_mm':28,'rack_preload_per_flank_mm':PRELOAD,'worm_flank_clearance_mm':.03,'parts':len(parts),'limits':['Unprinted experimental prototype','No load, wear, efficiency, thermal, self-locking, thrust-bearing life or motor-torque validation','Module separation only; guide hardware remains assembled','Nominal command increments are not measured accuracy']}
 def save(): (OUT/'validation.json').write_text(json.dumps(report,indent=2))
 def bvh(shape):
  BRepTools.Clean_s(shape.wrapped)
  BRepMesh_IncrementalMesh(shape.wrapped,.002,False,.04,True).Perform()
  # Existing absolute triangulation satisfies the loose request; do not remesh relatively.
  vs,ts=shape.tessellate(1,.04);m=fcl.BVHModel();m.beginModel(len(vs),len(ts));m.addSubModel(np.array([v.toTuple() for v in vs]),np.array(ts));m.endModel();return m
 def transform(p,dx=0,e=0):
  rotation=np.eye(3);translation=np.zeros(3)
  if e:
   if p['group']=='drive':translation[1]=-65*max(0,min(1,(e-.3)/.7))
   elif p['group']=='mount_bolts':translation=[0,-40*max(0,min(1,(e-.15)/.15)),15*min(1,e/.15)]
  elif p['group']=='rack':translation[0]=dx
  elif p.get('rotating'):
   theta=-dx/K;c=math.cos(theta);s=math.sin(theta);rotation=np.array([[1,0,0],[0,c,-s],[0,s,c]]);pivot=np.array(ORIGIN);translation=pivot-rotation@pivot
  # Guide rings are surfaces of revolution; their spin leaves occupied volume unchanged.
  return fcl.Transform(rotation,np.array(translation))
 def hit(a,b):return bool(fcl.collide(a,b,fcl.CollisionRequest(num_max_contacts=1),fcl.CollisionResult()))
 print('Checking assembled solids',flush=True)
 def allowed(a,b):
  if a.get('embedded_host')==b['name'] or b.get('embedded_host')==a['name']:return True
  return {a['name'],b['name']}=={'Single-start worm','Matched compliant rack'}
 ignored=[];collisions=[]
 for pair_index,(a,b) in enumerate(itertools.combinations(parts,2)):
  if pair_index%100==0:print('Static pair',pair_index,flush=True)
  if {a['name'],b['name']}=={'Single-start worm','Matched compliant rack'}:continue
  v=overlap(a['shape'],b['shape'])
  if v>.01:(ignored if allowed(a,b) else collisions).append({'parts':[a['name'],b['name']],'overlap_mm3':v})
 tool=ycyl(.85,26,0,-30,Z)
 report['worm_set_screw_tool_access_collisions']=[{'part':p['name'],'overlap_mm3':v} for p in parts if (v:=overlap(tool,p['shape']))>.01]
 report['assembled_collisions']=collisions;report['intentional_insert_intersections']=ignored;save()
 print('Static collisions',collisions,flush=True)
 print('Tessellating collision models',flush=True)
 objects=[fcl.CollisionObject(bvh(p['shape'])) for p in parts]
 nominal_object=fcl.CollisionObject(bvh(nominal));worm_object=objects[next(i for i,p in enumerate(parts) if p['name']=='Single-start worm')]
 rack_index=next(i for i,p in enumerate(parts) if p['name']=='Matched compliant rack')
 worm_index=next(i for i,p in enumerate(parts) if p['name']=='Single-start worm')
 # Dense relative phase coverage plus full travel endpoints and all millimetre positions.
 samples=sorted(set([LEAD*j/96 for j in range(97)]+list(range(-20,21))))
 nominal_mesh_hits=[];lost_engagement=[]
 for dx in samples:
  worm_object.setTransform(transform(parts[worm_index],dx));nominal_object.setTransform(transform(parts[rack_index],dx));objects[rack_index].setTransform(transform(parts[rack_index],dx))
  if hit(worm_object,nominal_object):nominal_mesh_hits.append(dx)
  if not hit(worm_object,objects[rack_index]):lost_engagement.append(dx)
 report['dense_mesh']={'phase_samples':97,'full_stroke_samples':41,'distinct_samples':len(samples),'nominal_triangle_intersections_at_mm':nominal_mesh_hits,'preloaded_loss_of_engagement_at_mm':lost_engagement,'tessellation_linear_tolerance_mm':.002,'tessellation_angular_tolerance_rad':.04,'absolute_tolerance':True};save()
 print('Dense mesh',report['dense_mesh'],flush=True)
 # OCC volume corroboration at center, non-symmetric phases and both stroke extremes.
 mesh_rows=[]
 for dx in [-20,0,LEAD*.173,LEAD*.517,20]:
  w=spin(worm,dx)
  row={'travel_from_center_mm':dx,'unchanged_straight_nominal_overlap_mm3':overlap(w,straight.translate((dx,0,0))),'matched_nominal_overlap_mm3':overlap(w,nominal.translate((dx,0,0))),'matched_preloaded_overlap_mm3':overlap(w,rack.translate((dx,0,0)))}
  mesh_rows.append(row);report['mesh_pose_checks']=mesh_rows;save();print('OCC mesh',row,flush=True)
 nominal_values=[r['matched_nominal_overlap_mm3'] for r in mesh_rows];preloaded_values=[r['matched_preloaded_overlap_mm3'] for r in mesh_rows];straight_values=[r['unchanged_straight_nominal_overlap_mm3'] for r in mesh_rows]
 report['mesh']={'solid_pose_samples':len(mesh_rows),'phase_samples':97,'full_stroke_samples':41,'unchanged_straight_rack_nominal_overlap_mm3':[min(straight_values),max(straight_values)],'matched_nominal_max_overlap_mm3':max(nominal_values),'matched_preloaded_overlap_mm3':[min(preloaded_values),max(preloaded_values)],'tolerance_mm3':.01}
 lower_box=box(300,100,30,(0,30,-2));old=ns['rack'].intersect(lower_box);new=rack.intersect(lower_box)
 report['unchanged_lower_guide_difference_mm3']=old.cut(new).Volume()+new.cut(old).Volume()
 pad_box=box(40,80,50,(ns['right']+20,30,0))
 old_pad=ns['rack'].intersect(pad_box);new_pad=rack.intersect(pad_box)
 report['unchanged_output_mount_difference_mm3']=old_pad.cut(new_pad).Volume()+new_pad.cut(old_pad).Volume()
 report['valid_single_solids']=all(p['shape'].isValid() and len(p['shape'].Solids())==1 for p in parts)
 # Backing spine starts at y=25; maximum worm radius reaches y=20.
 report['rigid_backbone_clearance_mm']=ns['RELIEF_Y']-(Y+RA)
 motion=[]
 for dx in range(-20,21):
  for o,p in zip(objects,parts):o.setTransform(transform(p,dx))
  for i,a in enumerate(parts):
   for j in range(i+1,len(parts)):
    b=parts[j]
    if allowed(a,b):continue
    am=a['group']=='rack' or a.get('rotating');bm=b['group']=='rack' or b.get('rotating')
    if not(am or bm) or a['group']==b['group']=='rack' or (a.get('rotating') and b.get('rotating')):continue
    if not hit(objects[i],objects[j]):continue
    v=overlap(posed(a,dx),posed(b,dx))
    if v>.01:motion.append({'travel_mm':dx+20,'parts':[a['name'],b['name']],'overlap_mm3':v})
  if dx%10==0:print('Motion',dx,'collisions',len(motion),flush=True)
 report['motion_samples']=41;report['motion_collisions']=motion;save()
 explosion=[];nominal_explosion=[]
 times=[.15*j/30 for j in range(31)]+[.15+.15*j/80 for j in range(1,81)]+[.3+.7*j/130 for j in range(1,131)]
 for n,e in enumerate(times):
  for o,p in zip(objects,parts):o.setTransform(transform(p,e=e))
  nominal_object.setTransform(transform(parts[rack_index]))
  if hit(worm_object,nominal_object):nominal_explosion.append(e)
  for i,a in enumerate(parts):
   for j in range(i+1,len(parts)):
    b=parts[j]
    if a['group']==b['group'] or (a['group'] not in ['drive','mount_bolts'] and b['group'] not in ['drive','mount_bolts']) or allowed(a,b):continue
    if not hit(objects[i],objects[j]):continue
    v=overlap(posed(a,e=e),posed(b,e=e))
    if v>.01:explosion.append({'separation':e,'parts':[a['name'],b['name']],'overlap_mm3':v})
  if n%40==0:print('Separation',n,'collisions',len(explosion),flush=True)
 report['module_separation_samples']=len(times);report['module_separation_collisions']=explosion;report['nominal_mesh_separation_triangle_collisions']=nominal_explosion
 report['passed']=max(nominal_values)<.01 and min(preloaded_values)>0 and not(nominal_mesh_hits or lost_engagement or collisions or motion or explosion or nominal_explosion or report['worm_set_screw_tool_access_collisions']) and report['valid_single_solids'] and report['unchanged_lower_guide_difference_mm3']<.01 and report['unchanged_output_mount_difference_mm3']<.01
 save();print('Validation',report['passed'],flush=True)
 return report
