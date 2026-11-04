"""Executed by model.py with its constructed CadQuery namespace.
Dense motion uses FCL triangle intersections with OCC confirmation of candidates.
Static pairs and selected mesh poses use OCC directly (including containment).
"""
import fcl
import numpy as np
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepTools import BRepTools

def validate():
 report={'experiment':f'worm-rack-{args.motor}-{STROKE}','geometry_cache_sha256':source_hash,'source_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'enclosure_source_sha256':hashlib.sha256((ROOT/'experiments/worm-rack/enclosure.py').read_bytes()).hexdigest(),'validation_source_sha256':hashlib.sha256((ROOT/'experiments/worm-rack/validate.py').read_bytes()).hexdigest(),'method':'All assembled pairs checked as OCC solids. Dense motion/separation: 0.002 mm absolute / 0.04 rad CAD tessellation, FCL triangle candidates confirmed by OCC intersections. Five mesh poses use full OCC intersections. Sampled checks, not continuous collision proof or FEA.','motor':MOTOR_NAME,'stroke_mm':STROKE,'module_mm':2,'axial_pressure_angle_deg':ns['PRESSURE_ANGLE'],'starts':1,'lead_mm':LEAD,'worm_pitch_diameter_mm':2*R,'worm_outside_diameter_mm':2*RA,'rack_preload_per_flank_mm':PRELOAD,'worm_flank_clearance_mm':.03,'parts':len(parts),'limits':['Unprinted experimental prototype','No load, wear, efficiency, thermal, self-locking, thrust-bearing life or motor-torque validation','Staged drive disassembly; guide hardware remains assembled','Nominal command increments are not measured accuracy']}
 def save(): (OUT/'validation.json').write_text(json.dumps(report,indent=2))
 def bvh(shape):
  BRepTools.Clean_s(shape.wrapped)
  BRepMesh_IncrementalMesh(shape.wrapped,.002,False,.04,True).Perform()
  # Existing absolute triangulation satisfies the loose request; do not remesh relatively.
  vs,ts=shape.tessellate(1,.04);m=fcl.BVHModel();m.beginModel(len(vs),len(ts));m.addSubModel(np.array([v.toTuple() for v in vs]),np.array(ts));m.endModel();return m
 def transform(p,dx=0,e=0):
  theta=0.;translation=np.zeros(3)
  if e:translation,theta=displacement(p['group'],e)
  elif p['group']=='rack':translation[0]=dx
  elif p.get('rotating'):theta=-dx/K
  c=math.cos(theta);s=math.sin(theta);rotation=np.array([[1,0,0],[0,c,-s],[0,s,c]])
  pivot=np.array(ORIGIN);translation=np.array(translation)+pivot-rotation@pivot
  # Guide rings are surfaces of revolution; their spin leaves occupied volume unchanged.
  return fcl.Transform(rotation,translation)
 def hit(a,b):return bool(fcl.collide(a,b,fcl.CollisionRequest(num_max_contacts=1),fcl.CollisionResult()))
 print('Checking assembled solids',flush=True)
 def allowed(a,b):
  if a.get('embedded_host')==b['name'] or b.get('embedded_host')==a['name']:return True
  return {a['name'],b['name']}=={WORM_NAME,'Matched compliant rack'}
 ignored=[];collisions=[]
 for pair_index,(a,b) in enumerate(itertools.combinations(parts,2)):
  if pair_index%100==0:print('Static pair',pair_index,flush=True)
  if {a['name'],b['name']}=={WORM_NAME,'Matched compliant rack'}:continue
  v=overlap(a['shape'],b['shape'])
  if v>.01:(ignored if allowed(a,b) else collisions).append({'parts':[a['name'],b['name']],'overlap_mm3':v})
 tool=ycyl(.85,SET_Y+30,SET_X,-30,Z)
 report['worm_set_screw_tool_access_collisions']=[{'part':p['name'],'overlap_mm3':v} for p in parts if p['group'] not in ['cover','cover_screws'] and (v:=overlap(tool,p['shape']))>.01]
 end_tool=xcyl(2.35,35,28.3)
 report['end_bolt_tool_access_collisions']=[{'part':p['name'],'overlap_mm3':v} for p in parts if p['group'] not in ['cover','cover_screws'] and (v:=overlap(end_tool,p['shape']))>.01]
 actual_insert_overlap=overlap(next(p['shape'] for p in parts if p['name']=='M5 axial heat-set insert'),worm)
 expected_insert_overlap=math.pi*((END_INSERT_OD/2)**2-(END_INSERT_PILOT/2)**2)*END_INSERT_LENGTH
 report['direct_drive']={'worm_length_mm':WORM_END-WORM_START,'printed_parts':sum(p['printed'] for p in parts),'bearing_count':sum(p['name'].startswith('625ZZ') for p in parts),'insert_thread':'M5','insert_od_mm':END_INSERT_OD,'insert_length_mm':END_INSERT_LENGTH,'insert_pilot_mm':END_INSERT_PILOT,'insert_interference_mm3':actual_insert_overlap,'expected_insert_interference_mm3':expected_insert_overlap,'bolt':'M5x16','bolt_to_pocket_bottom_clearance_mm':7.3-END_PILOT_START,'thread_engagement_mm':END_INSERT_LENGTH,'motor_socket_engagement_mm':16,'bearing_seat_diameter_mm':16.3,'bearing_pocket_width_mm':5.3,'bearing_installation_direction':'+Z','integral_axial_shoulders':True,'bearing_inner_race_spacer_od_mm':7.5,'spacer_length_mm':2,'outer_race_to_worm_axial_gap_mm':2,'keeper_screws':0,'separate_coupling':False,'motor_cartridge':False}
 report['assembled_collisions']=collisions;save()
 assert abs(actual_insert_overlap-expected_insert_overlap)<.01
 assert fixture_free.isValid() and len(fixture_free.Solids())==1
 # Compare all public mounting coordinates/planes against the published matching spur preset.
 refpath=ROOT/'dist' if (args.motor,STROKE)==('nema17',40) else ROOT/'dist/variants'/args.motor if STROKE==40 else ROOT/'dist/variants'/args.motor/str(STROKE)
 ref=json.loads(gzip.decompress((refpath/'assets/assembly.json.gz').read_bytes()))
 pairs=[('top.xy',MOUNTING['top']['xy'],ref['topMounts']),('top.planeZ',top,ref['topMountZ']),('side.xz',MOUNTING['side']['xz'],ref['caseMounts']),('side.planeY',ymax,ref['sideMountY']),('front.yz',MOUNTING['front']['yz'],ref['frontMounts']),('front.planeX',right,ref['frontMountX']),('output.xy',MOUNTING['output']['xy'],ref['outputMounts']),('output.planeZ',ns['OUTPUT_PAD_TOP'],ref['outputMountZ'])]
 mount_errors=[dict(interface=k,max_difference_mm=float(np.max(np.abs(np.array(a)-np.array(b))))) for k,a,b in pairs]
 assert all(q['max_difference_mm']<1e-8 for q in mount_errors)
 # Each mounting insert remains reachable by an M3 bolt from its mounting face.
 mount_access=[]
 for x,y in ns['CASE_CORNERS']:
  probe=cyl(1.45,hood_top-top+20,x,y,top)
  mount_access.append(dict(interface='top',center=[x,y,top],obstruction_mm3=overlap(probe,cover)+overlap(probe,tray)))
 for x,z in ns['CASE_MOUNTS']:
  probe=ycyl(1.45,20,x,ymax,z);mount_access.append(dict(interface='side',center=[x,ymax,z],obstruction_mm3=overlap(probe,tray)+overlap(probe,cover)))
 for y,z in ns['FRONT_MOUNTS']:
  probe=xcyl(1.45,20,right,y,z);mount_access.append(dict(interface='front',center=[right,y,z],obstruction_mm3=overlap(probe,tray)+overlap(probe,cover)))
 rear_access=rect(MOTOR_REAR-15,MOTOR_REAR+3.9,Y-MOTOR_SIZE/2-.5,Y+MOTOR_SIZE/2+.5,Z-MOTOR_SIZE/2-.5,Z+MOTOR_SIZE/2+.5)
 rear_obstruction=overlap(rear_access,tray)+overlap(rear_access,cover)
 report['enclosure']={'mounting':MOUNTING,'case_bounds_mm':CASE_BOUNDS,'interface_comparisons':mount_errors,'mounting_access':mount_access,'motor_back_face_x_mm':MOTOR_REAR,'motor_bracket_to_hood_side_gap_mm':hood_ymax-wall-(Y+(MOTOR_SIZE+3)/2),'motor_bracket_to_hood_roof_gap_mm':hood_top-wall-bracket_top,'motor_rear_exposure_mm':new_left-MOTOR_REAR,'rear_mount_access_obstruction_mm3':rear_obstruction,'tool_access_configuration':'cover removed','printed_parts':sum(p['printed'] for p in parts)}
 assert hood_ymax-wall-(Y+(MOTOR_SIZE+3)/2)>=.8
 assert rear_obstruction<.01 and all(q['obstruction_mm3']<.01 for q in mount_access)
 report['assembled_collisions']=collisions;report['intentional_insert_intersections']=ignored;save()
 print('Static collisions',collisions,flush=True)
 if collisions:report['passed']=False;save();return report
 print('Tessellating collision models',flush=True)
 objects=[fcl.CollisionObject(bvh(p['shape'])) for p in parts]
 # Bare chassis drops into the tray before guide hardware is installed.
 bare_object=fcl.CollisionObject(bvh(fixture_free));tray_object=objects[next(i for i,p in enumerate(parts) if p['name']==TRAY_NAME)]
 installation=[]
 for dz in np.linspace(0,80,161):
  bare_object.setTransform(fcl.Transform(np.array([0.,0.,dz])))
  if hit(bare_object,tray_object):
   v=overlap(fixture_free.translate((0,0,dz)),tray)
   if v>.01:installation.append({'lift_mm':dz,'overlap_mm3':v})
 report['chassis_installation']={'samples':161,'direction':'+Z','configuration':'bare unloaded chassis; rack, motor, guide hardware and cover installed afterward','collisions':installation};save()
 print('Chassis installation collisions',installation,flush=True)
 # Guide hardware is assembled on the unloaded chassis outside the tray.
 # Check each independent insertion/removal path through the added supports.
 guide_names={p['name'] for p in parts if p['group']=='guide'}
 guides=[];hardware_access=[];access_samples=0
 bare_object.setTransform(fcl.Transform())
 for p in ns['parts']:
  if p['name'] not in guide_names:continue
  lower=p['group'].startswith('lower_');shape=p['shape'].translate((0,0,ns['SPRING_PRELOAD'])) if lower else p['shape']
  obj=fcl.CollisionObject(bvh(shape));group=p['group']
  if lower and group.endswith('axles'):direction=(0,-1,0);distance=35
  elif lower and group.endswith('nuts'):direction=(0,1,0);distance=25
  elif group in ['front_nuts','rear_nuts','front_axles','rear_axles']:
   q=next(q for q in ns['UPPER'] if p['name'].endswith(f"{q['side']} {q['x']}"));sign=-1 if group.endswith('nuts') else 1
   direction=tuple(sign*v for v in q['axis']);distance=40 if sign<0 else 30
  else:direction=(0,0,1);distance=40
  for travel in np.linspace(0,distance,int(distance*2)+1):
   delta=np.array(direction)*travel;obj.setTransform(fcl.Transform(delta));access_samples+=1
   if hit(obj,bare_object):
    v=overlap(shape.translate(tuple(delta)),fixture_free)
    if v>.01:hardware_access.append({'part':p['name'],'travel_mm':travel,'overlap_mm3':v})
  obj.setTransform(fcl.Transform());guides.append(dict(name=p['name'],shape=shape,object=obj,lower_axle=lower and group.endswith('axles')))
 report['guide_hardware_access']={'samples':access_samples,'configuration':'unloaded chassis outside enclosure; nuts and lower bearings first, then axles and upper rollers','collisions':hardware_access};save()
 print('Guide hardware access collisions',hardware_access,flush=True)
 # Keep the guide as a subassembly. Retract lower bolts 8 mm, lift 6 mm,
 # slide rearward 10 mm, then lift out. Install in reverse before adding the rack.
 fixture_object=fcl.CollisionObject(bvh(fixture_free))
 moving=[dict(name=CHASSIS_NAME,shape=fixture_free,object=fixture_object,lower_axle=False)]+guides
 enclosure_parts=[(p,objects[i]) for i,p in enumerate(parts) if p['group']=='tray']
 assembly_poses=[(0.,0.,v) for v in np.linspace(0,8,17)]+[(0.,z,8.) for z in np.linspace(0,6,13)]+[(x,6.,8.) for x in np.linspace(0,-10,21)]+[(-10.,z,8.) for z in np.linspace(6,86,161)]
 assembly_collisions=[];checked_poses=set()
 for dx,dz,retraction in assembly_poses:
  for m in moving:
   delta=(dx,-retraction if m['lower_axle'] else 0.,dz);key=(m['name'],delta)
   if key in checked_poses:continue
   checked_poses.add(key);m['object'].setTransform(fcl.Transform(np.array(delta)))
   for p,obj in enclosure_parts:
    if not hit(m['object'],obj):continue
    v=overlap(m['shape'].translate(delta),p['shape'])
    if v>.01:assembly_collisions.append({'part':m['name'],'enclosure_part':p['name'],'offset_mm':list(delta),'overlap_mm3':v})
 report['guided_chassis_installation']={'samples':len(assembly_poses),'lower_axle_retraction_mm':8,'initial_lift_mm':6,'rearward_slide_mm':10,'configuration':'unloaded chassis with six bearings and axle hardware; motor, worm, rack and cover absent','collisions':assembly_collisions};save()
 print('Guided chassis installation collisions',assembly_collisions,flush=True)
 if hardware_access or assembly_collisions:report['passed']=False;save();return report
 nominal_object=fcl.CollisionObject(bvh(nominal));worm_object=objects[next(i for i,p in enumerate(parts) if p['name']==WORM_NAME)]
 rack_index=next(i for i,p in enumerate(parts) if p['name']=='Matched compliant rack')
 worm_index=next(i for i,p in enumerate(parts) if p['name']==WORM_NAME)
 # Dense relative phase coverage plus full travel endpoints and all millimetre positions.
 samples=sorted(set([LEAD*j/96 for j in range(97)]+list(np.linspace(-STROKE/2,STROKE/2,41))))
 nominal_mesh_hits=[];lost_engagement=[]
 for dx in samples:
  worm_object.setTransform(transform(parts[worm_index],dx));nominal_object.setTransform(transform(parts[rack_index],dx));objects[rack_index].setTransform(transform(parts[rack_index],dx))
  if hit(worm_object,nominal_object):nominal_mesh_hits.append(dx)
  if not hit(worm_object,objects[rack_index]):lost_engagement.append(dx)
 report['dense_mesh']={'phase_samples':97,'full_stroke_samples':41,'distinct_samples':len(samples),'nominal_triangle_intersections_at_mm':nominal_mesh_hits,'preloaded_loss_of_engagement_at_mm':lost_engagement,'tessellation_linear_tolerance_mm':.002,'tessellation_angular_tolerance_rad':.04,'absolute_tolerance':True};save()
 print('Dense mesh',report['dense_mesh'],flush=True)
 # OCC volume corroboration at center, non-symmetric phases and both stroke extremes.
 mesh_rows=[]
 for dx in [-STROKE/2,0,LEAD*.173,LEAD*.517,STROKE/2]:
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
 report['output_through_holes']={'diameter_mm':ns['OUTPUT_THROUGH_DIAMETER'],'length_mm':18,'intersections_mm3':[overlap(ns['cyl'](ns['OUTPUT_THROUGH_DIAMETER']/2,18.2,x,y,2.9),rack) for x,y in ns['OUTPUT_MOUNTS']]}
 report['valid_single_solids']=all(p['shape'].isValid() and len(p['shape'].Solids())==1 for p in parts)
 # Backing spine starts at y=25; maximum worm radius reaches y=20.
 report['rigid_backbone_clearance_mm']=ns['RELIEF_Y']-(Y+RA)
 motion=[]
 for dx in np.linspace(-STROKE/2,STROKE/2,41):
  for o,p in zip(objects,parts):o.setTransform(transform(p,dx))
  for i,a in enumerate(parts):
   for j in range(i+1,len(parts)):
    b=parts[j]
    if allowed(a,b):continue
    am=a['group']=='rack' or a.get('rotating');bm=b['group']=='rack' or b.get('rotating')
    if not(am or bm) or a['group']==b['group']=='rack' or (a.get('rotating') and b.get('rotating')):continue
    if not hit(objects[i],objects[j]):continue
    v=overlap(posed(a,dx),posed(b,dx))
    if v>.01:motion.append({'travel_mm':dx+STROKE/2,'parts':[a['name'],b['name']],'overlap_mm3':v})
  if dx%10==0:print('Motion',dx,'collisions',len(motion),flush=True)
 report['motion_samples']=41;report['motion_collisions']=motion;save()
 explosion=[];nominal_explosion=[];seen_relative=set()
 assert all(t['radians']==0 for seq in TRACKS.values() for t in seq),"Relative-pose reuse assumes translation-only disassembly"
 boundaries=sorted({0.,1.}|{t[key] for seq in TRACKS.values() for t in seq for key in ['start','end']})
 times={0.}
 for lo,hi in zip(boundaries,boundaries[1:]):
  distance=max(math.dist(displacement(g,lo)[0],displacement(g,hi)[0])+RA*abs(displacement(g,hi)[1]-displacement(g,lo)[1]) for g in TRACKS)
  n=max(1,math.ceil(distance/.5));times.update(lo+(hi-lo)*j/n for j in range(1,n+1))
 times=sorted(times)
 for n,e in enumerate(times):
  for o,p in zip(objects,parts):o.setTransform(transform(p,e=e))
  nominal_object.setTransform(transform(parts[rack_index]))
  if hit(worm_object,nominal_object):nominal_explosion.append(e)
  for i,a in enumerate(parts):
   for j in range(i+1,len(parts)):
    b=parts[j]
    if a['group']==b['group'] or (not TRACKS[a['group']] and not TRACKS[b['group']]) or allowed(a,b):continue
    da=displacement(a['group'],e)[0];db=displacement(b['group'],e)[0]
    relative=tuple(round(da[k]-db[k],12) for k in range(3))
    if relative==(0.,0.,0.):continue  # Exact assembled relative pose, already checked with OCC.
    key=(i,j,relative)
    if key in seen_relative:continue
    seen_relative.add(key)
    if not hit(objects[i],objects[j]):continue
    v=overlap(posed(a,e=e),posed(b,e=e))
    if v>.01:explosion.append({'separation':e,'parts':[a['name'],b['name']],'overlap_mm3':v})
  if n%40==0:print('Separation',n,'collisions',len(explosion),flush=True)
 report['distinct_explosion_pair_poses']=len(seen_relative);report['explosion_samples']=len(times);report['explosion_collisions']=explosion;report['maximum_explosion_point_increment_mm']=.5;report['nominal_mesh_separation_triangle_collisions']=nominal_explosion
 report['passed']=max(nominal_values)<.01 and min(preloaded_values)>0 and not(nominal_mesh_hits or lost_engagement or collisions or installation or hardware_access or assembly_collisions or motion or explosion or nominal_explosion or report['worm_set_screw_tool_access_collisions'] or report['end_bolt_tool_access_collisions']) and report['valid_single_solids'] and report['unchanged_lower_guide_difference_mm3']<.01 and report['unchanged_output_mount_difference_mm3']<.01 and max(report['output_through_holes']['intersections_mm3'])<.01
 save();print('Validation',report['passed'],flush=True)
 return report
