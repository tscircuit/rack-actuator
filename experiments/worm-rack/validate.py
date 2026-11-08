"""Executed by model.py with its constructed CadQuery namespace.
Dense motion uses FCL triangle intersections with OCC confirmation of candidates.
Static pairs and selected mesh poses use OCC directly (including containment).
"""
import fcl
import numpy as np
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepTools import BRepTools

def validate():
 report={'experiment':f'worm-rack-{args.motor}-{STROKE}','geometry_cache_sha256':source_hash,'source_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'enclosure_source_sha256':hashlib.sha256((ROOT/'experiments/worm-rack/enclosure.py').read_bytes()).hexdigest(),'flexure_source_sha256':hashlib.sha256((ROOT/'experiments/worm-rack/flexures.py').read_bytes()).hexdigest(),'validation_source_sha256':hashlib.sha256((ROOT/'experiments/worm-rack/validate.py').read_bytes()).hexdigest(),'method':'All assembled pairs checked as OCC solids. Dense motion/separation: 0.002 mm absolute / 0.04 rad CAD tessellation, FCL triangle candidates confirmed by OCC intersections. Five mesh poses use full OCC intersections. Sampled checks, not continuous collision proof or FEA.','motor':MOTOR_NAME,'stroke_mm':STROKE,'module_mm':2,'axial_pressure_angle_deg':ns['PRESSURE_ANGLE'],'starts':1,'lead_mm':LEAD,'worm_pitch_diameter_mm':2*R,'worm_outside_diameter_mm':2*RA,'rack_preload_per_flank_mm':PRELOAD,'worm_flank_clearance_mm':.03,'parts':len(parts),'limits':['Unprinted experimental prototype','Axial fit allowance is 0.3 mm; printed endplay and motor axial load capacity require physical testing','No load, wear, efficiency, thermal, self-locking, thrust-bearing life or motor-torque validation','Staged drive disassembly; motor and worm form a removable subassembly','Nominal command increments are not measured accuracy']}
 def save(): (OUT/'validation.json').write_text(json.dumps(report,indent=2))
 # Check springs independently of the fused chassis: assembled part pairs
 # cannot detect a support accidentally welded to an integral flexure.
 fixed_chassis=fixture(ns['frame'])
 flexure_checks=[]
 for d in np.linspace(0,ns['SPRING_CHECK_TRAVEL'],27):
  rounded_chassis=ns['chassis']((float(d),float(d)))
  assert rounded_chassis.isValid() and len(rounded_chassis.Solids())==1
  for q,envelope in zip(ns['BOTTOM'],flexure_envelopes):
   # The new standalone seat contains all rounded transitions. Test it
   # before any union with the frame so unintended welding cannot be hidden.
   seat=ns['spring_seat'](q,float(d))
   assert seat.isValid() and len(seat.Solids())==1
   # Exclude only the embedded root and a 0.05 mm tolerance at its wall.
   # The complete 5 mm curved transition remains inside the checked region.
   sign=1 if q['x']>0 else -1
   ends=sorted([q['x']-sign*(SPRING_ROOT_OFFSET-.05),q['x']+sign*6])
   moving=seat.intersect(ns['rect_cut'](*ends,20,45,-35,0))
   row={'station_x_mm':q['x'],'deflection_mm':float(d),
    'worm_support_gap_mm':seat.distance(worm_structure),
    'fixed_chassis_overlap_mm3':overlap(moving,fixed_chassis),
    'tray_overlap_mm3':overlap(seat,tray),
    'cover_overlap_mm3':overlap(seat,cover),
    'outside_reserved_envelope_mm3':seat.cut(envelope).Volume()}
   flexure_checks.append(row)
  print('Rounded flexure sample',round(float(d),2),flush=True)
 retained=[];leaf_sections=[]
 for d in [0,ns['SPRING_PRELOAD'],ns['SPRING_CHECK_TRAVEL']]:
  reference=ns['base_print'] if d==0 else ns['base'] if d==ns['SPRING_PRELOAD'] else ns['chassis']((d,d))
  shape=fixture_free if d==0 else fixture_s if d==ns['SPRING_PRELOAD'] else fixture(reference)
  assert shape.isValid() and len(shape.Solids())==1
  for q,envelope in zip(ns['BOTTOM'],flexure_envelopes):
   # Added structure is completely excluded from this box, so fixture() can
   # only remove material here. Compare separately clipped, rounded source
   # and final shapes rather than Booleaning coincident spline surfaces.
   before=reference.intersect(envelope);after=shape.intersect(envelope)
   assert before.isValid() and after.isValid() and overlap(worm_structure,envelope)<.01
   retained.append({'station_x_mm':q['x'],'deflection_mm':d,'removed_spring_mm3':abs(before.Volume(tol=1e-9)-after.Volume(tol=1e-9))})
   mid_x=q['x']-math.copysign((SPRING_ROOT_OFFSET+5)/2,q['x']);mid_z=-27+ns['SPRING_THICKNESS']/2-d/2
   gauge=box(.2,1,4,(mid_x,27,mid_z))
   thickness=shape.intersect(gauge).Volume(tol=1e-9)/.2
   assert abs(thickness-ns['SPRING_THICKNESS'])<.005
   leaf_sections.append({'station_x_mm':q['x'],'deflection_mm':d,'midspan_thickness_mm':thickness})
 report['flexure_clearance']={'reserved_support_gap_mm':FLEXURE_CLEARANCE,'checked_deflection_mm':[0,ns['SPRING_CHECK_TRAVEL']],
  'samples_per_flexure':27,'checks':flexure_checks,'retained_springs':retained,'leaf_sections':leaf_sections,
  'root_and_carrier_blend_radius_mm':SPRING_BLEND_RADIUS,'blend_radius_reference':'Unloaded print geometry; the rounded profiles deform with the prescribed leaf displacement.','previous_blend_radius_mm':2.,'bearing_facing_blend_radius_mm':ns['FRONT_BLEND_RADIUS'],'previous_leaf_span_mm':14.,
  'leaf_thickness_mm':ns['SPRING_THICKNESS'],'nominal_leaf_span_mm':ns['LEAF_LENGTH'],
  'method':'Independent spring solids including actual rounded transitions versus added worm supports, fixed chassis outside the intentional root, tray and cover. Conservative bounding envelopes clear the prescribed spring travel; OCC checks sample at 0.1 mm. Minimum leaf thickness is retained. Prescribed shapes are not an elastic simulation.'}
 report['flexure_clearance']['passed']=all(r['worm_support_gap_mm']>=FLEXURE_CLEARANCE-1e-5 and max(r[k] for k in ['fixed_chassis_overlap_mm3','tray_overlap_mm3','cover_overlap_mm3','outside_reserved_envelope_mm3'])<.01 for r in flexure_checks) and all(r['removed_spring_mm3']<.01 for r in retained)
 save();print('Flexure clearance',report['flexure_clearance']['passed'],flush=True)
 if not report['flexure_clearance']['passed']:report['passed']=False;save();return report
 # Compare the reinforced motor load path with the same chassis without its
 # new webs. Cross-sectional areas are geometric evidence, not a stiffness rating.
 unreinforced=fixture(ns['base'],reinforced=False)
 added=fixture_s.cut(unreinforced)
 sections=[]
 for x in [MOTOR_FRONT+8,(MOTOR_FRONT-43)/2,-42,-38,-24]:
  slab=ns['rect_cut'](x-.1,x+.1,ns['CHASSIS_FRONT']-.1,Y+20.1,-40,5)
  old_area=overlap(unreinforced,slab)/.2;new_area=overlap(fixture_s,slab)/.2
  sections.append({'x_mm':x,'previous_area_mm2':old_area,'reinforced_area_mm2':new_area})
 assert added.Volume()>100 and all(r['reinforced_area_mm2']>r['previous_area_mm2']+1 for r in sections)
 report['motor_mount_reinforcement']={'web_count':2,'web_thickness_mm':MOTOR_WEB_THICKNESS,
  'web_root_radius_mm':MOTOR_WEB_ROOT_RADIUS,'web_upper_corner_radius_mm':3.,
  'added_material_mm3':added.Volume(),'sections':sections,
  'design':'Two deep longitudinal webs join the motor faceplate to the rear bridge and existing support floor, with tangent roots. Existing motor, guide, flexure and fastener clearances are retained.',
  'mechanical_validation':'Geometry only; no stiffness, stress or fatigue rating. Physical print/load testing required.'}
 save()
 if POINT_BRIDGES_ENABLED:
  no_upper=fixture(ns['base'],upper_bridges=False)
  bridge_sections=[]
  retained_flange=fixture_s.intersect(motor_flange)
  assert retained_flange.isValid() and len(retained_flange.Solids())==1
  assert abs(motor_flange.BoundingBox().zmax-MOTOR_FLANGE_TOP)<1e-6
  for index,(ya,yb) in enumerate([(Y+4.8,Y+20),(ns['CHASSIS_FRONT'],Y-4.8)]):
   for x in np.linspace(MOTOR_FRONT+.5,MOTOR_FLANGE_REAR_FACE,31):
    slab=ns['rect_cut'](x-.05,x+.05,ya,yb,MOTOR_FLANGE_TOP-MOTOR_BRIDGE_HEIGHT,MOTOR_FLANGE_TOP)
    # Exclude neighboring braces: the flange itself must provide a continuous
    # section, independent of the nearby sloping outer support.
    section=retained_flange.intersect(slab)
    bridge_sections.append({'bridge':index+1,'x_mm':float(x),'area_mm2':section.Volume()/.1,'connected_sections':len(section.Solids())})
  assert all(q['area_mm2']>20 and q['connected_sections']==1 for q in bridge_sections),bridge_sections
  # A 7 mm deep solid ligament now extends behind the formerly exposed face.
  probe=box(7,1.5,1.5,(-46.5,THIN_SUPPORT_MARK[1],THIN_SUPPORT_MARK[2]))
  old_ligament=overlap(no_upper,probe);new_ligament=overlap(fixture_s,probe)
  assert old_ligament<.01 and new_ligament>probe.Volume()-.01,(old_ligament,new_ligament,probe.Volume())
  report['marked_motor_bridges']={'pairs':[[list(a),list(b)] for a,b in BRIDGE_MARKS],
   'source_model_revision':'a6cdc21f13d68ddda01110f8b5bfd3255b0895ae22764a50c92fa1613db7a5ad',
   'design':'One face-aligned U flange with a shared top plane, motor-plate cap, inward-set rails, rounded opening and smoothly flared shoulders. Marked coordinates identify regions only.',
   'top_plane_z_mm':MOTOR_FLANGE_TOP,'motor_face_x_mm':MOTOR_FRONT,'chassis_face_x_mm':MOTOR_FLANGE_REAR_FACE,'inside_corner_radius_mm':MOTOR_FLANGE_INNER_RADIUS,
   'nominal_width_mm':MOTOR_BRIDGE_WIDTH,'nominal_height_mm':MOTOR_BRIDGE_HEIGHT,'edge_radius_mm':MOTOR_BRIDGE_RADIUS,
   'sections':bridge_sections,'minimum_section_mm2':min(q['area_mm2'] for q in bridge_sections),
   'thin_upright_point_mm':list(THIN_SUPPORT_MARK),'new_ligament_mm':[7,1.5,1.5],
   'previous_ligament_volume_mm3':old_ligament,'reinforced_ligament_volume_mm3':new_ligament,'passed':True}
  # Exact continuous swept solids cover every position in both directions,
  # supplementing the assembly-wide sampled animation checks below.
  bolt_sweeps=[]
  for index,(y,z) in enumerate(motor_holes):
   axial=xcyl(1.45,10+MOTOR_SCREW_RELEASE,MOTOR_FRONT-5,y,z).fuse(xcyl(2.75,3+MOTOR_SCREW_RELEASE,MOTOR_FRONT+5,y,z))
   dz=60 if z>MOTOR_Z else -50
   def vertical_capsule(radius,length,x):
    return xcyl(radius,length,x,y,z).fuse(xcyl(radius,length,x,y,z+dz),box(length,2*radius,abs(dz),(x+length/2,y,z+dz/2)))
   vertical=vertical_capsule(1.45,10,MOTOR_FRONT-5+MOTOR_SCREW_RELEASE).fuse(vertical_capsule(2.75,3,MOTOR_FRONT+5+MOTOR_SCREW_RELEASE))
   for phase,sweep,e in [('axial release / insertion',axial,.73),('vertical removal / approach',vertical,.75)]:
    hits=[]
    for part in parts:
     if part['group']==f'motor_screw_{index}':continue
     volume=overlap(sweep,posed(part,e=e))
     if volume>.01:hits.append({'part':part['name'],'overlap_mm3':volume})
    bolt_sweeps.append({'bolt':index+1,'center_yz_mm':[y,z],'phase':phase,'collisions':hits})
  report['motor_bolt_insertion']={'method':'Exact continuous swept shaft and head solids for each axis-aligned segment, against the assembly at that stage. Insertion reverses the same collision-checked path. Socket recesses conservatively treated as solid.',
   'axial_release_mm':MOTOR_SCREW_RELEASE,'upper_vertical_mm':60,'lower_vertical_mm':-50,'paths':bolt_sweeps,'passed':all(not q['collisions'] for q in bolt_sweeps)}
  save();print('Continuous motor bolt insertion',report['motor_bolt_insertion']['passed'],flush=True)
  if not report['motor_bolt_insertion']['passed']:report['passed']=False;save();return report
  access_collisions=[];access_samples=0
  for y,z in motor_holes:
   for dx in [0,MOTOR_KEY_RELEASE/2,MOTOR_KEY_RELEASE]:
    for degrees in range(0,61,5):
     angle=math.radians(degrees);sign=1 if y>Y else -1
     shaft=xcyl(1.5,MOTOR_DRIVER_X-(MOTOR_FRONT+8.05),MOTOR_FRONT+8.05+dx,y,z)
     leg=acyl(1.5,MOTOR_KEY_LENGTH,(MOTOR_DRIVER_X+dx,y,z),(0,sign*math.sin(angle),(1 if z>MOTOR_Z else -1)*math.cos(angle)))
     access_samples+=1
     for p in parts:
      # The lid and rack are removed before servicing the motor. The probe
      # begins beyond the screw head; the socket itself is a simplified bore.
      if p['group'] in ['cover','cover_screws','rack','motor_screws'] or p['group'].startswith('motor_screw_'):continue
      v=overlap(shaft,p['shape'])+overlap(leg,p['shape'])
      if v>.01:access_collisions.append({'bolt_yz_mm':[y,z],'release_mm':dx,'angle_deg':degrees,'part':p['name'],'overlap_mm3':v})
  support_access=[];insert_walls=[]
  for x,y in REAR_SUPPORT_POINTS:
   tool=cyl(1.5,65-(SUPPORT_PAD_TOP+3.05),x,y,SUPPORT_PAD_TOP+3.05)
   for p in parts:
    if p['group'] in ['cover','cover_screws','rack']:continue
    v=overlap(tool,p['shape'])
    if v>.01:support_access.append({'center_mm':[x,y],'part':p['name'],'overlap_mm3':v})
   # Retain a complete 2 mm plastic collar outside the insert's nominal OD.
   outer=ns['INSERT_OD']/2+2
   collar=cyl(outer,ns['INSERT_LENGTH'],x,y,SUPPORT_PAD_BOTTOM-ns['INSERT_LENGTH']).cut(cyl(ns['INSERT_OD']/2+.1,ns['INSERT_LENGTH'],x,y,SUPPORT_PAD_BOTTOM-ns['INSERT_LENGTH']))
   missing=abs(collar.Volume()-overlap(collar,tray))
   insert_walls.append({'center_mm':[x,y],'radial_wall_mm':2,'missing_wall_mm3':missing})
  assert not support_access and all(q['missing_wall_mm3']<.01 for q in insert_walls),(support_access,insert_walls)
  report['motor_bolt_tool_access']={'configuration':'Upper bolts from above with cover and rack removed; lower bolts from underneath. Motor/chassis remain installed. Compact 2.5 mm hex key, 8 mm short-leg reach and 40 mm long leg.',
   'probe_radius_mm':1.5,'clearance_radius_mm':MOTOR_DRIVER_RADIUS,'screw_head_pocket_diameter_mm':2*MOTOR_HEAD_CLEARANCE,
   'outward_swing_deg':[0,60],'screw_release_mm':MOTOR_SCREW_RELEASE,'key_release_mm':MOTOR_KEY_RELEASE,'samples':access_samples,
   'rear_support_shift_mm':{'forward':27,'outward':0},'support_tool_collisions':support_access,'insert_walls':insert_walls,'collisions':access_collisions,'passed':not access_collisions}
  save();print('Upper bridges and motor tool access',not access_collisions,flush=True)
  if access_collisions:report['passed']=False;save();return report
 def bvh(shape):
  BRepTools.Clean_s(shape.wrapped)
  BRepMesh_IncrementalMesh(shape.wrapped,.002,False,.04,True).Perform()
  # Existing absolute triangulation satisfies the loose request; do not remesh relatively.
  vs,ts=shape.tessellate(1,.04);m=fcl.BVHModel();m.beginModel(len(vs),len(ts));m.addSubModel(np.array([v.toTuple() for v in vs]),np.array(ts));m.endModel();return m
 def transform(p,dx=0,e=0):
  theta=0.;translation=np.zeros(3)
  if e:
   translation,theta=displacement(p['group'],e)
   if 'lowerStation' in p:translation[2]+=guide_lift(p['lowerStation'],e)
  elif p['group']=='rack':translation[0]=dx
  elif p.get('rotating'):theta=-dx/K*p.get('rotationFactor',1)
  c=math.cos(theta);s=math.sin(theta);rotation=np.array([[1,0,0],[0,c,-s],[0,s,c]])
  pivot=np.array(p.get('rotationCenter',ORIGIN));translation=np.array(translation)+pivot-rotation@pivot
  # Guide rings are surfaces of revolution; their spin leaves occupied volume unchanged.
  return fcl.Transform(rotation,translation)
 def hit(a,b):return bool(fcl.collide(a,b,fcl.CollisionRequest(num_max_contacts=1),fcl.CollisionResult()))
 # Exact local clipping accelerates tangent bearing/rack checks without
 # changing their intersection: this fixed Y/Z box contains every guide
 # bearing, including its full spring lift, at all tested translations.
 rb=rack.BoundingBox()
 guide_rack=rack.intersect(box(rb.xlen+2,200,200,((rb.xmin+rb.xmax)/2,113,-87)))
 for p in parts:
  if p['group']=='guide' and p['name'].startswith('625ZZ'):
   bb=p['shape'].BoundingBox();assert bb.ymin>=13 and bb.ymax<=213 and bb.zmin>=-187 and bb.zmax+(ns['SPRING_PRELOAD'] if 'lowerStation' in p else 0)<=13
 def pair_overlap(a,b,dx=0,e=0):
  if b['name']=='Matched compliant rack':a,b=b,a
  if a['name']=='Matched compliant rack' and b['group']=='guide' and b['name'].startswith('625ZZ'):
   shift=displacement('rack',e)[0][0] if e else dx
   return overlap(guide_rack.translate((shift,0,0)),posed(b,dx,e))
  return overlap(posed(a,dx,e),posed(b,dx,e))
 report['guide_contact_acceleration']='Exact rack clipping to Y=13..213, Z=-187..13; every guide bearing bounding box, including spring lift, is asserted inside it. This preserves solid intersection volumes.'
 print('Checking assembled solids',flush=True)
 def allowed(a,b):
  if a.get('embedded_host')==b['name'] or b.get('embedded_host')==a['name']:return True
  return {a['name'],b['name']}=={WORM_NAME,'Matched compliant rack'}
 ignored=[];collisions=[]
 for pair_index,(a,b) in enumerate(itertools.combinations(parts,2)):
  if pair_index%100==0:print('Static pair',pair_index,flush=True)
  if {a['name'],b['name']}=={WORM_NAME,'Matched compliant rack'}:continue
  v=pair_overlap(a,b)
  if v>.01:(ignored if allowed(a,b) else collisions).append({'parts':[a['name'],b['name']],'overlap_mm3':v})
 tool=ycyl(.85,SET_Y+30,SET_X,-30,MOTOR_Z)
 report['worm_set_screw_tool_access_collisions']=[{'part':p['name'],'overlap_mm3':v} for p in parts if p['group']=='motor' and (v:=overlap(tool,p['shape']))>.01]
 end_tools=[xcyl(2.35,right+30-28.3,28.3)]
 report['end_bolt_tool_access_collisions']=[{'end':i,'part':p['name'],'overlap_mm3':v} for i,tool in enumerate(end_tools) for p in parts if p['group'] not in ['cover','cover_screws','motor'] and (v:=overlap(tool,p['shape']))>.01]
 expected_insert_overlap=math.pi*((END_INSERT_OD/2)**2-(END_INSERT_PILOT/2)**2)*END_INSERT_LENGTH
 insert_checks=[]
 for side in ['front']:
  actual=overlap(next(p['shape'] for p in parts if p['name']==f'M5 {side} axial heat-set insert'),worm)
  insert_checks.append({'end':side,'actual_interference_mm3':actual,'expected_interference_mm3':expected_insert_overlap});assert abs(actual-expected_insert_overlap)<.01
 report['direct_drive']={'worm_length_mm':WORM_END-WORM_START,'printed_parts':sum(p['printed'] for p in parts),'bearing_count':sum(p['name'].startswith('625ZZ') for p in parts),'worm_revolutions_per_motor_revolution':1,'travel_per_motor_revolution_mm':LEAD,'insert_thread':'M5','insert_count':1,'insert_od_mm':END_INSERT_OD,'insert_length_mm':END_INSERT_LENGTH,'insert_pilot_mm':END_INSERT_PILOT,'insert_checks':insert_checks,'bolts':'1 × M5x16','bolt_to_pocket_bottom_clearance_mm':.6,'thread_engagement_mm':8,'motor_socket_engagement_mm':21.2,'bearing_seat_diameter_mm':16.3,'bearing_axial_fit_allowance_mm':.3,'bearing_inner_race_spacer_od_mm':7.5,'spacer_length_mm':2,'keeper_screws':0,'separate_coupling':False,'motor_cartridge':False,'spur_gears':0,'tooth_drop_mm':1-Z,'motor_axis':[MOTOR_FRONT,MOTOR_Y,MOTOR_Z]}
 bearing=next(p['shape'] for p in parts if p['group']=='front_bearing')
 report['bearing_axial_capture']={'rear_shoulder_overlap_after_0_5mm_shift_mm3':overlap(bearing.translate((-.5,0,0)),fixture_s),'front_stop_overlap_after_0_5mm_shift_mm3':overlap(bearing.translate((.5,0,0)),tray),'nominal_axial_fit_allowance_mm':.3,'note':'Geometric capture, not a preload or bearing-life calculation; check actual endplay after printing.'}
 assert min(report['bearing_axial_capture'][k] for k in ['rear_shoulder_overlap_after_0_5mm_shift_mm3','front_stop_overlap_after_0_5mm_shift_mm3'])>.1
 # Recorded coordinates from the published geared prototype (v32).
 previous_rear={'nema17':{40:-113.,100:-168.,150:-218.},'nema14':{40:-107.,100:-163.,150:-213.}}[args.motor][STROKE]
 motor_difference=max(abs(MOTOR_REAR-previous_rear),abs(MOTOR_Y-(0 if IS14 else -1)),abs(MOTOR_Z-(-18 if IS14 else -20)))
 report['direct_drive']['motor_pose_change_from_geared_v32_mm']=motor_difference
 assert motor_difference<1e-8
 # The inner-race spacer bears on the metal insert face, not a thin printed lip.
 assert abs(END_INSERT_FACE-WORM_END)<1e-9
 spacer=next(p['shape'] for p in parts if p['group']=='front_spacer')
 insert_shape=next(p['shape'] for p in parts if p['group']=='front_insert')
 contact_area=min(overlap(insert_shape,ring(3.5,2.65,.01,(WORM_END-.01,Y,Z),AXIS)),overlap(spacer,ring(3.5,2.65,.01,(WORM_END,Y,Z),AXIS)))/.01
 assert contact_area>16
 report['direct_drive'].update(insert_recess_mm=END_INSERT_RECESS,spacer_metal_contact_area_mm2=contact_area)
 report['assembled_collisions']=collisions;save()
 assert fixture_free.isValid() and len(fixture_free.Solids())==1
 # Compare all public mounting coordinates/planes against the published matching spur preset.
 refpath=ROOT/'dist' if (args.motor,STROKE)==('nema17',40) else ROOT/'dist/variants'/args.motor if STROKE==40 else ROOT/'dist/variants'/args.motor/str(STROKE)
 ref=json.loads(gzip.decompress((refpath/'assets/assembly.json.gz').read_bytes()))
 pairs=[('enclosure.bounds',CASE_BOUNDS,ref['caseBounds']),('top.xy',MOUNTING['top']['xy'],ref['topMounts']),('top.planeZ',top,ref['topMountZ']),('side.xz',MOUNTING['side']['xz'],ref['caseMounts']),('side.planeY',ymax,ref['sideMountY']),('front.yz',MOUNTING['front']['yz'],ref['frontMounts']),('front.planeX',right,ref['frontMountX']),('output.yz',MOUNTING['output']['yz'],ref['outputMounts']),('output.planeX',ns['OUTPUT_FACE_X'],ref['outputMountX'])]
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
 rear_access=rect(MOTOR_REAR-15,MOTOR_REAR+.1,MOTOR_Y-MOTOR_SIZE/2-.5,MOTOR_Y+MOTOR_SIZE/2+.5,MOTOR_Z-MOTOR_SIZE/2-.5,MOTOR_Z+MOTOR_SIZE/2+.5)
 rear_obstruction=overlap(rear_access,tray)+overlap(rear_access,cover)
 actual_case=cq.Compound.makeCompound([tray,cover]).BoundingBox()
 actual_bounds=[actual_case.xmin,actual_case.xmax,actual_case.ymin,actual_case.ymax,actual_case.zmin,actual_case.zmax]
 assert max(abs(a-b) for a,b in zip(actual_bounds,CASE_BOUNDS))<1e-5,(actual_bounds,CASE_BOUNDS)
 report['enclosure']={'mounting':MOUNTING,'case_bounds_mm':CASE_BOUNDS,'actual_case_bounds_mm':actual_bounds,'interface_comparisons':mount_errors,'mounting_access':mount_access,'motor_back_face_x_mm':MOTOR_REAR,'motor_center_z_mm':MOTOR_Z,'motor_rear_exposure_mm':new_left-MOTOR_REAR,'rear_mount_access_obstruction_mm3':rear_obstruction,'tool_access_configuration':'M3 set screw on motor/worm subassembly outside housing; front M5 bolt through enclosure service port','printed_parts':sum(p['printed'] for p in parts)}
 assert rear_obstruction<.01 and all(q['obstruction_mm3']<.01 for q in mount_access)
 retention=[]
 for part in parts:
  if part.get('embedded_host')!=TRAY_NAME or not any(t in part['name'] for t in ['top mount','side mount','front mount']):continue
  reference=overlap(part['shape'],ns['tray']);actual=overlap(part['shape'],tray)
  retention.append({'part':part['name'],'reference_interference_mm3':reference,'actual_interference_mm3':actual,'lost_engagement_mm3':max(0,reference-actual)})
 report['enclosure']['external_insert_retention']=retention
 assert all(q['lost_engagement_mm3']<.01 for q in retention)
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
 bearing_access=[]
 bearing_times=np.linspace(0,right+8-BEARING_X,math.ceil((right+8-BEARING_X)*2)+1)
 for dx in bearing_times:
  v=overlap(bearing.translate((dx,0,0)),fixture_free)
  if v>.01:bearing_access.append({'withdrawal_mm':float(dx),'overlap_mm3':v})
 report['end_bearing_installation']={'configuration':'insert bearing from +X into chassis outside enclosure, then lower chassis into tray','samples':len(bearing_times),'collisions':bearing_access}
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
 # slide rearward 2.5 mm, then lift out. Install in reverse before adding the rack.
 fixture_object=fcl.CollisionObject(bvh(fixture_free))
 moving=[dict(name=CHASSIS_NAME,shape=fixture_free,object=fixture_object,lower_axle=False),dict(name='625ZZ front worm support',shape=bearing,object=fcl.CollisionObject(bvh(bearing)),lower_axle=False)]+guides
 enclosure_parts=[(p,objects[i]) for i,p in enumerate(parts) if p['group']=='tray']
 assembly_poses=[(0.,0.,v) for v in np.linspace(0,8,17)]+[(0.,z,8.) for z in np.linspace(0,6,13)]+[(x,6.,8.) for x in np.linspace(0,-2.5,6)]+[(-2.5,z,8.) for z in np.linspace(6,86,161)]
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
 report['guided_chassis_installation']={'samples':len(assembly_poses),'lower_axle_retraction_mm':8,'initial_lift_mm':6,'rearward_slide_mm':2.5,'configuration':'unloaded chassis with seven bearings and guide axle hardware; motor, worm, rack and cover absent','collisions':assembly_collisions};save()
 print('Guided chassis installation collisions',assembly_collisions,flush=True)
 if bearing_access or hardware_access or assembly_collisions:report['passed']=False;save();return report
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
  row={'travel_from_center_mm':dx,'matched_nominal_overlap_mm3':overlap(w,nominal.translate((dx,0,0))),'matched_preloaded_overlap_mm3':overlap(w,rack.translate((dx,0,0)))}
  mesh_rows.append(row);report['mesh_pose_checks']=mesh_rows;save();print('OCC mesh',row,flush=True)
 nominal_values=[r['matched_nominal_overlap_mm3'] for r in mesh_rows];preloaded_values=[r['matched_preloaded_overlap_mm3'] for r in mesh_rows]
 report['mesh']={'solid_pose_samples':len(mesh_rows),'phase_samples':97,'full_stroke_samples':41,'matched_nominal_max_overlap_mm3':max(nominal_values),'matched_preloaded_overlap_mm3':[min(preloaded_values),max(preloaded_values)],'tolerance_mm3':.01}
 lower_box=ns['rail_shape'](3000);old=ns['rack'].intersect(lower_box);new=rack.intersect(lower_box)
 report['unchanged_lower_guide_difference_mm3']=old.cut(new).Volume()+new.cut(old).Volume()
 pad_box=box(40,80,50,(ns['right']+20,30,0))
 old_pad=ns['rack'].intersect(pad_box);new_pad=rack.intersect(pad_box)
 report['unchanged_output_mount_difference_mm3']=old_pad.cut(new_pad).Volume()+new_pad.cut(old_pad).Volume()
 report['output_through_holes']={'diameter_mm':ns['OUTPUT_THROUGH_DIAMETER'],'length_mm':ns['OUTPUT_PAD_DEPTH'],'axis':[1,0,0],'intersections_mm3':[overlap(ns['output_cylinder'](ns['OUTPUT_THROUGH_DIAMETER']/2,ns['OUTPUT_PAD_DEPTH']+.2,ns['right']-.1,y,z),rack) for y,z in ns['OUTPUT_MOUNTS']]}
 report['valid_single_solids']=all(p['shape'].isValid() and len(p['shape'].Solids())==1 for p in parts)
 # Backing spine starts at y=25; maximum worm radius reaches y=20.
 report['rigid_backbone_clearance_mm']=R+ns['RELIEF_Y']-ns['PITCH_Y']-RA
 motion=[]
 for dx in np.linspace(-STROKE/2,STROKE/2,41):
  for o,p in zip(objects,parts):o.setTransform(transform(p,dx))
  for i,a in enumerate(parts):
   for j in range(i+1,len(parts)):
    b=parts[j]
    if allowed(a,b):continue
    am=a['group']=='rack' or a.get('rotating');bm=b['group']=='rack' or b.get('rotating')
    if not(am or bm) or a['group']==b['group']=='rack' or (a.get('rotating') and b.get('rotating') and a.get('rotationCenter',ORIGIN)==b.get('rotationCenter',ORIGIN)):continue
    if not hit(objects[i],objects[j]):continue
    v=pair_overlap(a,b,dx=dx)
    if v>.01:motion.append({'travel_mm':dx+STROKE/2,'parts':[a['name'],b['name']],'overlap_mm3':v})
  if dx%10==0:print('Motion',dx,'collisions',len(motion),flush=True)
 report['motion_samples']=41;report['motion_collisions']=motion;save()
 explosion=[];nominal_explosion=[];seen_relative=set()
 boundaries=sorted({0.,1.}|{t[key] for seq in TRACKS.values() for t in seq for key in ['start','end']})
 times={0.}
 for lo,hi in zip(boundaries,boundaries[1:]):
  distance=max(math.dist(displacement(g,lo)[0],displacement(g,hi)[0]) for g in TRACKS)
  n=max(1,math.ceil(distance/.5));times.update(lo+(hi-lo)*j/n for j in range(1,n+1))
 times=sorted(times)
 chassis_index=next(i for i,p in enumerate(parts) if p['name']==CHASSIS_NAME);spring_objects={(0,0):objects[chassis_index]}
 for n,e in enumerate(times):
  key_state=spring_key(e)
  if key_state not in spring_objects:spring_objects[key_state]=fcl.CollisionObject(bvh(spring_shape(key_state)))
  objects[chassis_index]=spring_objects[key_state]
  for o,p in zip(objects,parts):o.setTransform(transform(p,e=e))
  nominal_object.setTransform(transform(parts[rack_index],e=e))
  if hit(worm_object,nominal_object):nominal_explosion.append(e)
  for i,a in enumerate(parts):
   for j in range(i+1,len(parts)):
    b=parts[j]
    dynamic=any('lowerStation' in p or p['name']==CHASSIS_NAME for p in [a,b])
    if allowed(a,b) or (not dynamic and (a['group']==b['group'] or (not TRACKS[a['group']] and not TRACKS[b['group']]))):continue
    da=displacement(a['group'],e)[0];db=displacement(b['group'],e)[0]
    if 'lowerStation' in a:da[2]+=guide_lift(a['lowerStation'],e)
    if 'lowerStation' in b:db[2]+=guide_lift(b['lowerStation'],e)
    relative=tuple(round(da[k]-db[k],12) for k in range(3))
    angles=tuple(round(displacement(p['group'],e)[1]%(2*math.pi),10) for p in [a,b])
    if relative==(0.,0.,0.) and abs((angles[0]-angles[1]+math.pi)%(2*math.pi)-math.pi)<1e-8 and (not dynamic or key_state==(0,0)):continue  # Common rigid rotation preserves the assembled intersection volume.
    key=(i,j,relative,angles,key_state if dynamic else None)
    if key in seen_relative:continue
    seen_relative.add(key)
    if not hit(objects[i],objects[j]):continue
    v=pair_overlap(a,b,e=e)
    if v>.01:explosion.append({'separation':e,'parts':[a['name'],b['name']],'overlap_mm3':v})
  if n%40==0:
   report['explosion_collisions']=explosion;save();print('Separation',n,'collisions',len(explosion),flush=True)
 report['spring_states_checked']=[list(k) for k in spring_objects]
 report['valid_spring_solids']=all(spring_shape(k).isValid() and len(spring_shape(k).Solids())==1 for k in spring_objects)
 report['distinct_explosion_pair_poses']=len(seen_relative);report['explosion_samples']=len(times);report['explosion_collisions']=explosion;report['maximum_explosion_translation_increment_mm']=.5;report['nominal_mesh_separation_triangle_collisions']=nominal_explosion
 report['passed']=max(nominal_values)<.01 and min(preloaded_values)>0 and not(nominal_mesh_hits or lost_engagement or collisions or installation or bearing_access or hardware_access or assembly_collisions or motion or explosion or nominal_explosion or report['worm_set_screw_tool_access_collisions'] or report['end_bolt_tool_access_collisions']) and report['valid_single_solids'] and report['valid_spring_solids'] and report['unchanged_lower_guide_difference_mm3']<.01 and report['unchanged_output_mount_difference_mm3']<.01 and max(report['output_through_holes']['intersections_mm3'])<.01
 save();print('Validation',report['passed'],flush=True)
 return report
