"""Solid geometry checks for the isolated T8 carriage, not structural analysis."""
def validate():
 import itertools,time
 import numpy as np
 report={'passed':False,'units':'mm','intersection_tolerance_mm3':.01,'source_sha256':hashlib.sha256((ROOT/'experiments/t8-leadscrew/model.py').read_bytes()).hexdigest(),'validation_source_sha256':hashlib.sha256((ROOT/'experiments/t8-leadscrew/validate.py').read_bytes()).hexdigest()}
 def save(): (OUT/'validation.json').write_text(json.dumps(report,indent=2))
 # Only screw/rib intersections are intentional. Verify the actual intersection
 # is confined to those three ribs; never waive an entire fastener/host pair.
 joints=[];joint_pairs=set();by_name={p['name']:p for p in parts}
 for j in THREAD_JOINTS:
  host=by_name[j['host']]['shape'];screw=by_name[j['bolt']]['shape']
  ribs=ridge_material(j['diameter'],j['length'],j['center'],j['axis'],j['start'])
  intersection=host.intersect(screw)
  extra=intersection.cut(ribs).Volume();missing=ribs.cut(host).Volume()
  rib_contacts=[overlap(r,screw) for r in ribs.Solids()]
  spec=THREAD_PROFILES[j['diameter']]
  projections=[sum((v.toTuple()[i]-j['center'][i])*j['axis'][i] for i in range(3)) for v in screw.Vertices()]
  engagement=max(0,min(j['start']+j['length'],max(projections))-max(j['start']+spec['lead_in'],min(projections)))
  row={k:v for k,v in j.items()};row.update(ridge_count=len(ribs.Solids()),missing_ridge_mm3=missing,unexpected_overlap_mm3=extra,ridge_contact_volumes_mm3=rib_contacts,full_depth_engagement_mm=engagement)
  row['passed']=len(rib_contacts)==3 and min(rib_contacts)>0 and extra<.01 and missing<.01 and engagement>=j['diameter']*1.5
  joints.append(row)
  if row['passed']:joint_pairs.add(frozenset([j['host'],j['bolt']]))
 output_seats=[]
 for j in OUTPUT_PILOTS:
  ribs=ridge_material(j['diameter'],j['length'],j['center'],j['axis'])
  hole=ridge_hole(j['diameter'],j['length'],j['center'],j['axis'])
  wall=ring(3.45,1.75,8,j['center'],j['axis'])
  q=dict(center_mm=j['center'],ridge_count=len(ribs.Solids()),missing_ridge_mm3=ribs.cut(beam).Volume(),blocked_pilot_mm3=overlap(beam,hole),missing_wall_mm3=wall.cut(beam).Volume())
  q['passed']=q['ridge_count']==3 and max(q[k] for k in ['missing_ridge_mm3','blocked_pilot_mm3','missing_wall_mm3'])<.01
  output_seats.append(q)
 report['output_mount']={'pattern':'Uniform 31 mm grid of overlapping NEMA17 patterns','pitch_mm':[31,31],'outer_pitch_mm':[max(GRID_Y)-min(GRID_Y),31] if WIDTH>1 else None,'thread':'M3 three-ridge plastic forming pilot','pilot_depth_mm':8,'full_depth_thread_length_mm':7.4,'maximum_screw_entry_mm':8,'face_size_mm':[OUTPUT_WIDTH,42],'face_home_x_mm':EXIT_X,'holes':output_seats,'passed':len(output_seats)=={1:4,2:8,4:12}[WIDTH] and set(output_holes)=={(y,SCREW_Z+z) for y in [-15.5,15.5] for z in [-15.5,15.5]}|{(31*(j-({1:2,2:4,4:6}[WIDTH]-1)/2),SCREW_Z+z) for j in range({1:2,2:4,4:6}[WIDTH]) for z in [-15.5,15.5]} and all(q['passed'] for q in output_seats)}
 # Test the actual M3 head, shank and short hex-key route, not just the pilot.
 output_access=[]
 if WIDTH==1:
  for y,z in output_holes:
   end=GUIDE_END
   ribs=ridge_material(3,8,(EXIT_X,y,z),(-1,0,0))
   initial=xcyl(2.75,3,end-15,y,z).fuse(xcyl(1.5,12,end-12,y,z))
   load_direction=-1 if z<SCREW_Z else 1
   radial=[initial.translate((0,0,load_direction*d)) for d in [20,15,10,5,2,0]]
   axial=xcyl(2.75,15,end-15,y,z).fuse(xcyl(1.5,24,end-12,y,z))
   # Short arm along X, with its long arm entering through the same opening.
   driver=xcyl(1.5,15,end-18,y,z).fuse(cyl(1.5,20,(end-18,y,z),(0,0,load_direction)))
   host_blocked=max([overlap(beam,q) for q in radial]+[beam.intersect(axial).cut(ribs).Volume(),overlap(beam,driver)])
   approach_obstacles=[]
   for part in parts:
    if part['name']=='Hollow triangular carriage':continue
    placed=pose(part,STROKE)
    for q in radial+[axial,driver]:
     v=overlap(q.translate((STROKE,0,0)),placed)
     if v>.01:approach_obstacles.append(dict(part=part['name'],overlap_mm3=v))
   # Exact swept cylinders cover installed bolt heads/shanks throughout travel.
   installed_sweep=xcyl(2.75,STROKE+3,end-3,y,z).fuse(xcyl(1.5,STROKE+12,end,y,z))
   running_obstacles=[]
   for part in parts:
    if part['group']=='carriage':continue
    v=overlap(installed_sweep,part['shape'])
    if v>.01:running_obstacles.append(dict(part=part['name'],overlap_mm3=v))
   output_access.append(dict(center_yz_mm=[y,z],carriage_blockage_mm3=host_blocked,extended_loading_collisions=approach_obstacles,installed_travel_collisions=running_obstacles,passed=host_blocked<.01 and not approach_obstacles and not running_obstacles))
 report['output_bolt_access']={'applicable':WIDTH==1,'reference_bolt':'M3x12 socket head, diameter 5.5 mm, height 3 mm','driver_envelope_diameter_mm':3,'installation_travel_mm':STROKE,'checks':output_access,'passed':all(q['passed'] for q in output_access),'note':'1x output plate only. Full flange thickness and three-ridge pilots are retained. Insert from the inside with the carriage fully extended; thread forming is bounded to the pilot ribs.'}
 print('Inside output-bolt access',report['output_bolt_access']['passed'],flush=True)
 if not report['output_bolt_access']['passed']:save();return report
 report['plastic_thread_seats']={'method':'Three axial rounded ribs at 120 degrees, with tapered entry. Unformed rib/shaft overlap is intentional and bounded to each verified rib solid. Thread forming and stripping torque are not simulated.',
  'profiles':THREAD_PROFILES,'fastener_nuts':1 if PRINTED else 0,'joints':joints,'passed':all(q['passed'] for q in joints) and len(joints)==(6 if PRINTED else 10)}
 save();print('Three-ridge seats',report['plastic_thread_seats']['passed'],flush=True)
 if not report['plastic_thread_seats']['passed'] or not report['output_mount']['passed']:return report
 insert_checks=[];printed_carrier=by_name[CARRIER_NAME]['freeShape'];installed_carrier=by_name[CARRIER_NAME]['shape']
 for j,(x,y) in enumerate(ADJUST_CENTERS):
  insert=by_name[f'M5 heat-set insert {j+1}']['shape']
  pilot=cyl(3.2,10.5,(x,y,9.5));wall=ring(5.8,3.61,9.5,(x,y,10.5));approach=cyl(4.3,55,(x,y,20.01))
  row=dict(center_mm=[x,y,20],blocked_printed_pilot_mm3=overlap(pilot,printed_carrier),missing_wall_mm3=wall.cut(printed_carrier).Volume(),installed_interference_mm3=overlap(insert,installed_carrier),tool_approach_blockage_mm3=overlap(approach,printed_carrier),insert_to_pilot_bottom_mm=1,engagement_mm=9.5)
  row['passed']=max(row[k] for k in ['blocked_printed_pilot_mm3','missing_wall_mm3','installed_interference_mm3','tool_approach_blockage_mm3'])<.01;insert_checks.append(row)
 displacement=printed_carrier.cut(installed_carrier)
 for x,y in ADJUST_CENTERS:displacement=displacement.cut(cyl(3.57,9.5,(x,y,10.5)))
 report['carrier_heat_set_inserts']={'specification':INSERT,'count':4,'checks':insert_checks,'unexpected_plastic_change_mm3':displacement.Volume(),'installation':'Heat set into the loose carrier before assembling it. Inserts stay bonded to the carrier during adjustment and exploded disassembly. STL uses Ø6.4 mm pilots; assembly cavity represents displaced plastic.','passed':all(q['passed'] for q in insert_checks) and displacement.Volume()<.01}
 if not report['carrier_heat_set_inserts']['passed']:save();return report
 collisions=[]
 for a,b in itertools.combinations(parts,2):
  if frozenset([a['name'],b['name']]) in joint_pairs:continue

  v=overlap(a['shape'],b['shape'])
  if v>.01:collisions.append({'parts':[a['name'],b['name']],'overlap_mm3':v})
 report['assembled_collisions']=collisions;save();print('Static collisions',collisions,flush=True)
 if collisions:return report
 if PRINTED:
  host=by_name['Printed 20 mm lead screw with integral shaft clamp']['shape'];nut=by_name['M3 shaft clamp hex nut']['shape'];clamp_bolt=by_name['M3x12 shaft clamp bolt']['shape']
  shaft_fit=shaft.intersect(rect(9,24,-4,4,38,46))
  wrong_flat=shaft_fit.rotate((0,0,SCREW_Z),(1,0,SCREW_Z),180)
  seat=hex_prism(5.5,1,(17,5,36.9)).cut(cyl(1.7,1,(17,5,36.9)))
  nut_access=[]
  for dz in [0,-.5,-1,-2,-3,-5,-8,-12,-20]:
   nut_access.append({'offset_z_mm':dz,'hub_collision_mm3':overlap(host,nut.translate((0,0,dz)))})
  bolt_access=[]
  for dz in [0,.5,1,2,3,5,8,12,20,30]:
   bolt_access.append({'offset_z_mm':dz,'hub_collision_mm3':overlap(host,clamp_bolt.translate((0,0,dz)))})
  turned_nut=nut.rotate((17,5,0),(17,5,1),30)
  report['shaft_clamp']={'specification':CLAMP,'shaft_interference_mm3':overlap(host,shaft_fit),'incorrect_flat_orientation_interference_mm3':overlap(host,wrong_flat),'missing_nut_seat_mm3':seat.cut(host).Volume(),'nut_anti_rotation_interference_mm3':overlap(host,turned_nut),'nut_insertion':nut_access,'bolt_insertion':bolt_access,'nut_thread_engagement_mm':2.4,'bolt_projection_past_nut_mm':1.5,'clamp_threads_in_plastic':False}
  q=report['shaft_clamp'];q['passed']=q['shaft_interference_mm3']<.01 and q['incorrect_flat_orientation_interference_mm3']>.1 and q['missing_nut_seat_mm3']<.01 and q['nut_anti_rotation_interference_mm3']>.1 and all(row['hub_collision_mm3']<.01 for row in nut_access+bolt_access)
  print('D shaft / bolt-and-nut clamp',q['passed'],flush=True)
  if not q['passed']:save();return report
 # The printed support contacts only a small annular inner-race land.
 # Check the full land volume and both bearing-face clearance regions against
 # every printed part, not just a nominal support diameter in metadata.
 seats=[]
 for b in bearings:
  c,u=b['center'],b['axis'];host=by_name[BASE_NAME if b['kind']=='upper' else CARRIER_NAME]['shape']
  land=ring(3.7,2.8,2,c,u,2.5)
  back=ring(7.95,4.15,1.95,c,u,2.5);front=ring(7.95,4.15,.75,c,u,-3.25)
  blocked=[]
  for p in parts:
   if not p['printed']:continue
   # Retaining rails intentionally flank the rim 0.5 mm from its faces.
   rear_probe=ring(7.95,4.15,.45,c,u,2.5) if p['group']=='carriage' else back
   front_probe=ring(7.95,4.15,.45,c,u,-2.95) if p['group']=='carriage' else front
   v=overlap(rear_probe,p['shape'])+overlap(front_probe,p['shape'])
   if v>.01:blocked.append({'part':p['name'],'overlap_mm3':v})
  missing=land.cut(host).Volume()
  seats.append({'station_x_mm':b['station'],'kind':b['kind'],'side':b['sign'],'land_diameter_mm':7.4,'support_face_recess_mm':2,'missing_land_mm3':missing,'blocked_face_clearance':blocked,'passed':missing<.01 and not blocked})
 report['bearing_face_relief']={'inner_race_land_diameter_mm':7.4,'surrounding_relief_diameter_mm':17,'recess_depth_mm':2,'loose_support_spacers':0,'seats':seats,'passed':len(seats)==len(bearings) and all(q['passed'] for q in seats)}
 print('Bearing face relief',report['bearing_face_relief']['passed'],flush=True)
 if not report['bearing_face_relief']['passed']:save();return report
 # Validate open relief slots, free prongs, retained heads and connected roots.
 # Record head passage as required material deformation, never a free slide fit.
 axles=[]
 for b in bearings:
  c,u=b['center'],b['axis'];host=by_name[BASE_NAME if b['kind']=='upper' else CARRIER_NAME]
  printed=host['freeShape'];installed=host['shape'];pin=snap_pin(c,u)
  slot=axle_slot(c,u)
  journal=cyl(2.4,5,c,u,-2.5).cut(slot);root=cyl(2.4,7,c,u,2.5).cut(slot)
  slot_probe=slot.intersect(local_box(c,u,-4,4,-2.3,2.3,-3.3,9.59))
  clearance=ring(2.69,2.41,8.3,c,u,2.6)
  bearing=ring(8,2.5,5,c,u,-2.5);swept=ring(8,2.5,5+SNAP['bearing_release_mm'],c,u,-2.5-SNAP['bearing_release_mm'])
  shoulder=cyl(3.2,.55,c,u,SNAP['head_back_t']-.55).intersect(local_box(c,u,-3.4,3.4,-1.2,1.2,-3.31,-2.74))
  shoulder=shoulder.cut(slot)
  bent_end=pin.intersect(local_box(c,u,-6,6,-6,6,SNAP['tip_t']-.1,SNAP['bend_start_t']))
  head_passage=overlap(pin,swept);unexpected=installed.intersect(swept).cut(pin).Volume()
  row=dict(blocked_relief_slot_mm3=overlap(printed,slot_probe),blocked_root_clearance_mm3=overlap(printed,clearance),station_x_mm=b['station'],kind=b['kind'],side=b['sign'],missing_split_journal_mm3=journal.cut(printed).Volume(),missing_split_root_mm3=root.cut(printed).Volume(),missing_retaining_shoulder_mm3=shoulder.cut(printed).Volume(),bent_tip_volume_mm3=bent_end.Volume(),seated_bearing_overlap_mm3=overlap(installed,bearing),head_passage_interference_mm3=head_passage,unexpected_insertion_path_overlap_mm3=unexpected)
  row['passed']=max(row[k] for k in ['blocked_relief_slot_mm3','blocked_root_clearance_mm3','missing_split_journal_mm3','missing_split_root_mm3','missing_retaining_shoulder_mm3','seated_bearing_overlap_mm3','unexpected_insertion_path_overlap_mm3'])<.01 and head_passage>.1 and bent_end.Volume()>1 and pin.isValid() and len(pin.Solids())==1
  axles.append(row)
 report['split_axles']={'count':len(bearings),'specification':AXLE_SPEC,'checks':axles,'passed':all(q['passed'] for q in axles),'head_passage_requires_deformation':True,'physical_installability_verified':False,'note':'Split Ø4.8 mm journals retain the existing 6.4 mm head and 30-degree bent tip. Tapered slots end in a 0.6 mm radius; deep root clearance frees both prongs. Passing the bearing bore over the head requires inward flex; force, strain and retention are not simulated.'}
 print('Split bearing axles / relief slots',report['split_axles']['passed'],flush=True)
 if not report['split_axles']['passed']:save();return report
 # Smooth running faces must have no raised side rails. Check the entire
 # former rail region above each face, plus +/-1 mm axial bearing displacement.
 face_checks=[]
 for track in TRACKS:
  c,u,n=track['contact'],track['axis'],track['normal']
  for side in [-1,1]:
   lo,hi=sorted([side*track['inner'],side*(track['inner']+4)])
   def wire(x):
    pts=[cq.Vector(x,c[1]+u[1]*t+n[1]*h,c[2]+u[2]*t+n[2]*h) for t,h in [(lo,.02),(hi,.02),(hi,4.02),(lo,4.02)]]
    return cq.Wire.makePolygon(pts+[pts[0]])
   probe=cq.Solid.makeLoft([wire(TAIL_HOME+8),wire(GUIDE_END)],ruled=True)
   volume=overlap(probe,beam)
   face_checks.append(dict(kind=track['kind'],contact_mm=c,side=side,raised_material_mm3=volume,passed=volume<.01))
 float_checks=[]
 for b in bearings:
  c,u=b['center'],b['axis'];bearing=ring(8,2.5,5,c,u,-2.5)
  for shift in [-1,0,1]:
   v=overlap(beam,bearing.translate(tuple(shift*q for q in u)))
   float_checks.append(dict(station_x_mm=b['station'],kind=b['kind'],side=b['sign'],axial_shift_mm=shift,carriage_overlap_mm3=v,passed=v<.01))
 report['smooth_running_faces']={'raised_retaining_rails':False,'axial_displacement_checked_mm':[-1,1],'former_rail_regions':face_checks,'bearing_clearance':float_checks,'passed':all(q['passed'] for q in face_checks+float_checks),'note':'Raised side rails are removed. Checks cover nominal bearing geometry and +/-1 mm axial displacement relative to the carriage, not bearing tilt, preload or printed surface friction. Existing support clearance channels are retained.'}
 print('Smooth running faces',report['smooth_running_faces']['passed'],flush=True)
 if not report['smooth_running_faces']['passed']:save();return report
 # Matched NEMA17 patterns use short, open-bottom M3 insert seats.
 mounts=[];attachment_access=[]
 for j in MOUNT_SEATS:
  c,u=j['center'],j['axis'];host=by_name[j['host']];length=j['depth']
  printed=host['freeShape'];installed=host['shape'];insert=by_name[j['insert_name']]['shape']
  hole=mount_pilot(c,u,length);wall=ring(4,2.41,4,c,u)
  row=dict(kind=j['kind'],host=j['host'],center_mm=list(c),axis=list(u),pilot_diameter_mm=4,depth_mm=length,blocked_printed_pilot_mm3=overlap(hole,printed),missing_wall_mm3=wall.cut(printed).Volume(),insert_collision_mm3=overlap(insert,installed),open_bottom=j['open_bottom'],backing_beyond_pilot_mm3=overlap(cyl(1.45,.1,c,u,length),printed),insert_tip_clearance_mm=length-MOUNT_INSERT['length_mm'])
  row['passed']=max(row[k] for k in ['blocked_printed_pilot_mm3','missing_wall_mm3','insert_collision_mm3'])<.01 and (row['backing_beyond_pilot_mm3']<.01 if j['kind']=='lid' else row['insert_tip_clearance_mm']>=1);mounts.append(row)
  probe=cyl(1.45,length,c,u).fuse(cyl(3,40,c,tuple(-q for q in u),.01))
  for travel in [0,STROKE/2,STROKE]:
   for p in parts:
    v=overlap(probe,pose(p,travel))
    if v>.01:attachment_access.append(dict(mount=j['kind'],center_mm=list(c),travel_mm=travel,part=p['name'],overlap_mm3=v))
 # Verify that the only print/installed difference is displaced insert plastic.
 displaced=[]
 for name in [BASE_NAME,LID_NAME]:
  host=by_name[name];extra=host['freeShape'].cut(host['shape'])
  for j in MOUNT_SEATS:
   if j['host']==name and extra.Volume()>1e-8:extra=extra.cut(cyl(2.32,4,j['center'],j['axis']))
  displaced.append(dict(host=name,unexpected_displacement_mm3=extra.Volume(),passed=extra.Volume()<.01))
 expected={(10.5+31*i,31*(j-({1:2,2:4,4:6}[WIDTH]-1)/2)) for i in range(math.floor((EXIT_X-14.5)/31)+1) for j in range({1:2,2:4,4:6}[WIDTH])}
 layout_checks=[]
 for layout in MOUNT_LAYOUTS:
  w=layout['width_multiple'];cx=layout['center_xy_mm'][0];n={1:2,2:4,4:6}[w]
  full={(cx+31*(j-(n-1)/2),y) for j in range(n) for y in [-15.5,15.5]}
  supported=full & expected
  central={(cx+dx,y) for dx in [-15.5,15.5] for y in [-15.5,15.5]}
  ok=set(map(tuple,layout['hole_centers_xy_mm']))==supported and central<=supported and len(supported)==(12 if w==4 and cx==88 and EXIT_X>=169.5 else {1:4,2:8,4:10}[w])
  layout_checks.append(dict(**layout,passed=ok))
 expected_lid={(10.5+31*i,y) for i in range(math.floor((EXIT_X-23.5)/31)+1) for y in GRID_Y}
 base_edge=EXIT_X-max(x for x,y in BASE_MOUNT_HOLES)
 lid_edge=EXIT_X-9-max(x for x,y in LID_MOUNTS)
 pattern_ok=set(BASE_MOUNT_HOLES)==expected and set(LID_MOUNTS)==expected_lid and 4<=lid_edge<35 and 4<=base_edge<35 and expected_lid<=expected and all(q['passed'] for q in layout_checks)

 height=max(p['shape'].BoundingBox().zmax for p in parts)
 closed_walls=[]
 for x in STATIONS:
  for sign in [-1,1]:closed_walls.append(cyl(5,6,(x,wide(sign*34),18),(0,sign,0)).cut(chassis_shape).Volume())
 side_holes=[]
 for x,z in [(22,12),(36,12)]+[(x-5,z) for x in STATIONS for z in [44,56]]:
  for sign in [-1,1]:
   missing=cyl(.8,5.8,(x,wide(sign*34)+sign*.1,z),(0,sign,0)).cut(chassis_shape).Volume()
   side_holes.append(dict(center_xz_mm=[x,z],side=sign,missing_wall_mm3=missing,passed=missing<.01))
 report['external_mount_inserts']={'specification':MOUNT_INSERT,'patterns':BASE_MOUNT_PATTERNS,'mounting_layouts':layout_checks,'grid_pitch_mm':31,'base_row_x_mm':GRID_X,'base_last_row_edge_distance_mm':base_edge,'lid_row_x_mm':LID_GRID_X,'lid_last_row_edge_distance_mm':lid_edge,'base_count':len(BASE_MOUNT_HOLES),'lid_count':len(LID_MOUNTS),'pattern_center_xy_mm':[26,0],'checks':mounts,'plastic_displacement':displaced,'access_collisions':attachment_access,'pattern_matches':pattern_ok,'passed':pattern_ok and not attachment_access and all(q['passed'] for q in mounts+displaced)}
 report['lid_and_attachment']={'lid_fixings':len(LID_FIXINGS),'lid_fixing_thread':'M3 three-ridge, 12 mm pilot depth','lid_thickness_mm':4,'lid_bottom_z_mm':64,'lid_top_z_mm':68,'assembly_height_mm':height,'original_height_limit_mm':68,'external_mount_thread':'M3 short heat-set insert','lid_open_bottom':True,'base_backing':'Retained below structural feet; otherwise open','top_mount_count':len(LID_MOUNTS),'side_mount_count':0,'floor_mount_count':len(BASE_MOUNT_HOLES),'floor_mount_type':'M3 insert seats entered from underside','checks':mounts,'insertion_collisions':attachment_access,'closed_lower_access_missing_mm3':closed_walls,'removed_side_hole_checks':side_holes,'passed':report['external_mount_inserts']['passed'] and height<=68.00001 and max(closed_walls)<.01 and not SIDE_MOUNTS and all(q['passed'] for q in side_holes)}
 print('Low lid / M3 insert patterns / closed sides',report['lid_and_attachment']['passed'],flush=True)
 if not report['lid_and_attachment']['passed']:save();return report
 window_checks=[]
 for name,layout in WINDOW_LAYOUTS.items():
  rects=layout['rectangles_mm'];gaps=[]
  for i,a in enumerate(rects):
   for b in rects[i+1:]:
    dx=max(a[0]-b[1],b[0]-a[1],0);dy=max(a[2]-b[3],b[2]-a[3],0)
    gaps.append(math.hypot(dx,dy))
  window_checks.append(dict(name=name,count=len(rects),minimum_gap_mm=min(gaps) if gaps else None,minimum_opening_mm=min(min(r[1]-r[0],r[3]-r[2]) for r in rects) if rects else None,passed=all(g>=6-1e-6 for g in gaps) and all(r[1]-r[0]>=8-1e-6 and r[3]-r[2]>=7-1e-6 for r in rects)))
 report['cutout_planning']={'stage':'final post-processing after all features','minimum_web_mm':6,'checks':window_checks,'passed':all(q['passed'] for q in window_checks),'note':'Window bounds are non-overlapping and separated by at least 6 mm. Complete insert/support bands and rounded windows replace overlapping or clipped legacy patterns. This checks planned webs, not a universal minimum-wall or structural-strength certification.'}
 print('Final cutout layout / minimum webs',report['cutout_planning']['passed'],flush=True)
 if not report['cutout_planning']['passed']:save();return report
 # Probe the support-removal openings independently of their rounded corners.
 access_checks=[]
 for a,b,c,d in SUPPORT_ACCESS:
  probe=rect(a+2.1,b-2.1,c+2.1,d-2.1,-.1,27.4)
  missing=overlap(probe,chassis_shape)
  access_checks.append(dict(bounds_xy_mm=[a,b,c,d],blocked_mm3=missing,passed=missing<.01))
 motor_fill=rect(.1,5.9,-19.9,19.9,5.1,15.9).cut(chassis_shape).Volume()
 report['printability']={'support_access':access_checks,'motor_foot_missing_mm3':motor_fill,'side_roof_degrees':45,'passed':motor_fill<.01 and all(q['passed'] for q in access_checks)}
 print('Support access / filled motor foot',report['printability']['passed'],flush=True)
 if not report['printability']['passed']:save();return report
 guard_checks=[dict(index=i,missing_mm3=base_before_lightening.intersect(g).cut(base_after_lightening).Volume()) for i,g in enumerate(BASE_CUT_GUARDS)]
 base_empty=sum(overlap(c,chassis_print_without_pins) for c in CUTOUTS['base'])
 report['base_lightening']={'floor':LIGHTENING['base_floor'],'sides':LIGHTENING['base_sides'],'total':LIGHTENING['base'],'protected_supports':guard_checks,'blocked_cutouts_mm3':base_empty,'passed':all(q['missing_mm3']<.01 for q in guard_checks) and base_empty<.01 and all(LIGHTENING[k]['removed_mm3']>0 for k in ['base_floor','base_sides']) and chassis_print_without_pins.isValid() and len(chassis_print_without_pins.Solids())==1}
 print('Base floor / side windows',report['base_lightening']['passed'],flush=True)
 if not report['base_lightening']['passed']:save();return report
 lid_removed=LIGHTENING['lid']['removed_mm3'];lid_blocked=sum(overlap(cut,lid) for cut in CUTOUTS['lid'])
 report['lid_lightening']={**LIGHTENING['lid'],'blocked_cutouts_mm3':lid_blocked,'passed':lid_removed>0 and lid_blocked<.01 and lid.isValid() and len(lid.Solids())==1}
 if not report['lid_lightening']['passed']:save();return report
 # The formerly recessed Z=32 underside is filled down to the Z=28 bolt shelf.
 feet=[]
 for b in bearings:
  if b['kind']!='upper':continue
  x,sign=b['station'],b['sign'];ya,yb=sorted([wide(sign*21.1),wide(sign*36.9)])
  filled=rect(x-5.9,x+5.9,ya,yb,28.001,31.999)
  y=wide(sign*25.885)
  below=rect(x+.841,x+1.841,y-.5,y+.5,27.6,27.99)
  missing=filled.cut(chassis_print_without_pins).Volume();below_volume=overlap(below,chassis_print_without_pins)
  feet.append(dict(station_x_mm=x,side=sign,underside_z_mm=28,added_depth_mm=4,missing_fill_mm3=missing,below_underside_mm3=below_volume,passed=missing<.01 and below_volume<.01))
 report['bearing_support_feet']={'shelf_underside_z_mm':28,'checks':feet,'passed':len(feet)==4 and all(q['passed'] for q in feet),'note':'The four bearing-support undersides are coplanar with the adjacent adjustment-bolt shelves. This removes the local four-millimetre recess; it is not a claim that the whole print requires no supports.'}
 print('Flush bearing-support undersides',report['bearing_support_feet']['passed'],flush=True)
 if not report['bearing_support_feet']['passed']:save();return report
 # Adjustment is a rigid guided translation, not flexure deformation.
 adjustment_checks=[]
 for values in [(0,),(.25,),(.5,),(.75,),(1,)]:
  hits=[]
  for i,a in enumerate(parts):
   for b in parts[i+1:]:
    if 'adjustIndex' not in a and 'adjustIndex' not in b:continue
    for travel in [0,STROKE]:
     aa=pose(a,travel,values);bb=pose(b,travel,values)
     if overlap(aa,bb)<.01:continue
     hit=aa.intersect(bb)
     for j in THREAD_JOINTS:
      if frozenset([a['name'],b['name']])!=frozenset([j['host'],j['bolt']]):continue
      host=by_name[j['host']]
      ribs=ridge_material(j['diameter'],j['length'],j['center'],j['axis'],j['start'])
      if 'adjustIndex' in host:ribs=ribs.translate((0,0,values[host['adjustIndex']]-1))
      hit=hit.cut(ribs)
     if hit.Volume()>.01:hits.append({'parts':[a['name'],b['name']],'travel_mm':travel,'overlap_mm3':hit.Volume()})
  adjustment_checks.append({'settings_mm':values,'collisions':hits,'passed':not hits})
 report['adjustable_bearings']={'count':LOWER_COUNT,'carrier_count':1,'adjustment_bolts':4,'travel_mm':[0,1],'mechanism':'Four top-entry M5x25 bolts bear on fixed shelves and pull one rigid carrier holding all lower bearings upward into M5 heat-set inserts; nominal contact at 1 mm. Tighten evenly. No elastic preload or carrier tilt is simulated.','flexures':0,'checks':adjustment_checks,'passed':all(q['passed'] for q in adjustment_checks)}
 print('Adjustment checks',report['adjustable_bearings']['passed'],flush=True)
 if not report['adjustable_bearings']['passed']:save();return report
 # Accelerate exact confirmation with precise triangle screening. Cylindrical
 # references are conservative screw/nut envelopes; thread flank contact is not modeled.
 import fcl,numpy as np
 from OCP.BRepTools import BRepTools
 from OCP.BRepMesh import BRepMesh_IncrementalMesh
 def bvh(s):
  BRepTools.Clean_s(s.wrapped);BRepMesh_IncrementalMesh(s.wrapped,.02,False,.12,True).Perform();vs,ts=s.tessellate(1,.12)
  m=fcl.BVHModel();m.beginModel(len(vs),len(ts));m.addSubModel(np.array([v.toTuple() for v in vs]),np.array(ts));m.endModel();return m
 models=[fcl.CollisionObject(bvh(p['shape'])) for p in parts]
 moving=[i for i,p in enumerate(parts) if p['group']=='carriage'];fixed=[i for i,p in enumerate(parts) if p['group']!='carriage']
 motion=[]
 for travel in np.linspace(0,STROKE,int(STROKE*2)+1):
  for i,p in enumerate(parts):
   if p['group']=='carriage':models[i].setTransform(fcl.Transform(np.array([travel,0.,0.])))
   elif p['group']=='rotor':
    angle=-travel*2*math.pi/LEAD;c=math.cos(angle);ss=math.sin(angle);r=np.array([[1,0,0],[0,c,-ss],[0,ss,c]]);pivot=np.array([0.,0.,SCREW_Z]);models[i].setTransform(fcl.Transform(r,pivot-r@pivot))
  for i in moving:
   for j in fixed:
    if not fcl.collide(models[i],models[j],fcl.CollisionRequest(),fcl.CollisionResult()):continue
    v=overlap(pose(parts[i],float(travel)),pose(parts[j],float(travel)))
    if v>.01:motion.append({'travel_mm':float(travel),'parts':[parts[i]['name'],parts[j]['name']],'overlap_mm3':v})
  if travel%10==0:print('Travel',travel,'collisions',len(motion),flush=True)
 report['motion']={'samples':int(STROKE*2)+1,'increment_mm':.5,'travel_mm':[0,STROKE],'collisions':motion,'passed':not motion}
 contacts=[]
 for b in bearings:
  n=(0,b['sign']*math.sqrt(3)/2,.5) if b['kind']=='upper' else (0,0,-1)
  center=np.array(b['center']);contact=center-8*np.array(n)
  expected=float(np.dot(contact-np.array([b['station'],0,SCREW_Z]),np.array(n))-16-(WIDEN*math.sqrt(3)/2 if b['kind']=='upper' else 0))
  contacts.append({'kind':b['kind'],'station_x_mm':b['station'],'normal':list(n),'contact_mm':list(contact),'plane_error_mm':float(abs(expected)),'rear_end_margin_at_full_extension_mm':b['station']-8-(TAIL_HOME+STROKE),'rear_running_face_margin_mm':b['station']-8-(TAIL_HOME+STROKE+4),'front_end_margin_at_retraction_mm':GUIDE_END-(b['station']+8)})
 running_faces=[]
 for q in contacts:
  # Include the full bearing radius at both travel limits. Output-flange
  # screw reliefs beyond this swept envelope are not rolling surfaces.
  lo=q['station_x_mm']-STROKE-8;hi=q['station_x_mm']+8
  c=q['contact_mm'];n=q['normal'];plane=cq.Plane(origin=(lo,c[1],c[2]),xDir=(1,0,0),normal=tuple(n))
  strip=cq.Workplane(plane).center((hi-lo)/2,0).rect(hi-lo,7).extrude(-2).val()
  missing=strip.cut(beam).Volume();running_faces.append(dict(kind=q['kind'],contact_mm=c,swept_x_mm=[lo,hi],missing_track_mm3=missing,passed=missing<.01 and lo>=TAIL_HOME+4 and hi<=GUIDE_END))
 report['running_faces']={'checks':running_faces,'skin_thickness_mm':2,'track_width_mm':7,'coverage':'Full travel plus the entire 8 mm bearing radius at both limits','passed':all(q['passed'] for q in running_faces)}
 rows=[]
 for q in contacts:
  n=np.array(q['normal']);r=np.array(q['contact_mm']);r[2]-=SCREW_Z
  torque=np.cross(r,n);rows.append([n[1],n[2],*torque])
 constraint_rank=int(np.linalg.matrix_rank(np.array(rows)))
 report['guidance']={'screw_axis_yz_mm':[0,SCREW_Z],'section_reference_yz_mm':[0,SCREW_Z],'width_multiple':WIDTH,'external_screw_bearings':0,'bearing_mount':'fixed base','carriage_type':'moving chamfered tube with two integral threaded bands' if PRINTED else 'moving hollow triangular tube with internal flange nut','transverse_constraint_rank':constraint_rank,'fully_constrained':True,'note':'At nominal contact, the two triangles provide rank-5 constraint, leaving X translation free. This is not a stiffness or load rating.','lower_contact_y_mm':[lower_positions(x) for x in STATIONS],'bearing_count':len(bearings),'bearing_type':'625ZZ, 5x16x5','station_count':2,'bearings_per_station':len(bearings)//2,'station_spacing_mm':STATIONS[-1]-STATIONS[0],'contacts':contacts,'passed':constraint_rank==5 and STATIONS[1]-STATIONS[0]>=40 and all(q['plane_error_mm']<1e-7 and q['rear_running_face_margin_mm']>=1-1e-7 and q['front_end_margin_at_retraction_mm']>=2-1e-7 for q in contacts)}
 # Straight tool approaches to motor, flange and guide axles. Each probe begins
 # outside the head/socket; screw bodies and sockets are not compared to themselves.
 probes=[]
 # Extend the carriage to expose the two lower motor bolts. Their heads
 # still clear the retracted carriage by 1 mm in the assembled fit check.
 for y,z in motor_holes:probes.append(('motor at full extension',xcyl(1.5,20,9.1,y,z),STROKE))
 for y,z in motor_holes:probes.append(('motor key long leg at full extension',cyl(1.5,45,(29,y,z),(0,1 if y>0 else -1,0)),STROKE))
 for travel in [0,STROKE]:
  for y,z in nut_holes:probes.append(('flange',xcyl(1.5,max(100,EXIT_X-NUT_HOME+20),NUT_HOME+6.6+travel,y,z),travel))
  for x,y in LID_FIXINGS:probes.append(('lid screw',cyl(1.2,55,(x,y,67.95)),travel))
 for x,y in ADJUST_CENTERS:probes.append(('carrier adjustment',cyl(2.35,75,(x,y,38.1)),0))
 if PRINTED:probes.append(('shaft clamp at full extension',cyl(1.5,65,(17,5,48.1)),STROKE))
 access=[]
 for name,tool,travel in probes:
  for p in parts:
   v=overlap(tool,pose(p,travel))
   if v>.01:access.append({'tool':name,'extension_mm':travel,'part':p['name'],'overlap_mm3':v})
 report['base_mount_access']={'insertion_direction':'from underside (+Z)','thread':'M3 heat-set insert','hole_type':'Ø4 mm printed pilot; backing retained beneath structural feet','maximum_screw_entry_mm':5,'pattern_center_xy_mm':[26,0],'patterns':BASE_MOUNT_PATTERNS,'holes':[q for q in mounts if q['kind']=='base'],'passed':report['external_mount_inserts']['passed']}
 print('Base insert mounting access',report['base_mount_access']['passed'],flush=True)
 report['tool_access']={'probe_count':len(probes),'collisions':access,'passed':not access}
 exploded=[];press_on=[]
 compressed_models={}
 explosion_samples=sorted(set([round(float(t),6) for t in np.linspace(0,1,101)]+EXPLODE_KEYS))
 for t in explosion_samples:
  offsets=[explosion_offset(p,float(t)) for p in parts]
  local=max(0,min(1,(float(t)-.2)/.8));distance=CARRIAGE_WITHDRAWAL*max(0,min(1,local/.2))
  for i,m in enumerate(models):
   if parts[i].get('snapBearings'):
    compression=round(snap_compression(t),6);key=(i,compression)
    if key not in compressed_models:compressed_models[key]=fcl.CollisionObject(bvh(compressed_support(parts[i],compression) if compression else parts[i]['shape']))
    m=models[i]=compressed_models[key]
   if parts[i]['group']=='rotor':
    angle=-distance*2*math.pi/LEAD;c=math.cos(angle);ss=math.sin(angle);r=np.array([[1,0,0],[0,c,-ss],[0,ss,c]]);pivot=np.array([0.,0.,SCREW_Z]);m.setTransform(fcl.Transform(r,np.array(offsets[i])+pivot-r@pivot))
   else:m.setTransform(fcl.Transform(np.array(offsets[i])))
  for i,j in itertools.combinations(range(len(parts)),2):
   if offsets[i]==offsets[j] and (parts[i]['group']=='rotor')==(parts[j]['group']=='rotor') and not(snap_compression(t) and (parts[i].get('snapBearings') or parts[j].get('snapBearings'))):continue
   if not fcl.collide(models[i],models[j],fcl.CollisionRequest(),fcl.CollisionResult()):continue
   a=exploded_pose(parts[i],float(t));b=exploded_pose(parts[j],float(t));hit=a.intersect(b);v=hit.Volume()
   if v<.01:continue
   for seat in THREAD_JOINTS:
    if frozenset([parts[i]['name'],parts[j]['name']])==frozenset([seat['host'],seat['bolt']]):
     host_i=i if parts[i]['name']==seat['host'] else j
     ribs=ridge_material(seat['diameter'],seat['length'],seat['center'],seat['axis'],seat['start'])
     if parts[host_i]['group']=='rotor':ribs=ribs.rotate((0,0,SCREW_Z),(1,0,SCREW_Z),-distance*360/LEAD)
     ribs=ribs.translate(tuple(offsets[host_i]));v=max(0,v-overlap(hit,ribs))
   # Only the matching bearing's exact free-end axle volume can account for
   # deliberate head passage. All collisions beyond that volume still fail.
   for host_i,bearing_i in [(i,j),(j,i)]:
    host,br=parts[host_i],parts[bearing_i]
    if not host.get('snapBearings') or not br.get('bearing'):continue
    for spec in host['snapBearings']:
     if list(spec['center'])!=br['center'] or list(spec['axis'])!=br['axis']:continue
     cap=snap_pin(spec['center'],spec['axis']).intersect(local_box(spec['center'],spec['axis'],-6,6,-6,6,SNAP['tip_t']-.2,-2.5)).translate(tuple(offsets[host_i]))
     contact=overlap(hit,cap)
     if contact>.01:
      press_on.append({'fraction':float(t),'parts':[host['name'],br['name']],'head_interference_mm3':contact})
      v=max(0,v-contact)
   if v>.01:exploded.append({'fraction':float(t),'parts':[parts[i]['name'],parts[j]['name']],'overlap_mm3':v})
 report['explosion']={'samples':len(explosion_samples),'collisions':exploded,'press_on_head_interferences':press_on,'passed':not exploded,'collision_free':not(exploded or press_on),'physical_head_passage_verified':False,'note':'Staged disassembly with synchronized screw rotation. Undeformed retaining heads visibly intersect their own bearing bores during snap removal/insertion. These exact head contacts are recorded separately; every other collision fails. No elastic bending is animated or validated. Thread rib contact is bounded separately.'}
 print('Explosion collisions',exploded[:15],flush=True)
 report['valid_single_solids']=all(p['shape'].isValid() and len(p['shape'].Solids())==1 for p in parts)
 output_positions=[]
 for travel in [0,STROKE]:
  face=pose(by_name['Hollow triangular carriage'],travel).BoundingBox().xmax
  output_positions.append({'travel_mm':travel,'output_face_x_mm':face,'extension_beyond_base_mm':face-EXIT_X})
 report['compact_layout']={'base_length_mm':EXIT_X-(-36 if PRINTED else BASE_REAR),'base_width_mm':2*HALF_WIDTH,'width_multiple':WIDTH,'output_plate_width_mm':OUTPUT_WIDTH,'upper_bearing_span_mm':24*math.sqrt(3)+2*WIDEN,'retracted_overall_length_mm':EXIT_X+40,'extended_overall_length_mm':EXIT_X+40+STROKE,'motor_front_x_mm':0,'bearing_station_x_mm':STATIONS,'exit_plane_x_mm':EXIT_X,'screw_end_x_mm':ROD_END,'tip_recess_at_home_mm':EXIT_X-ROD_END,'output_positions':output_positions,'passed':all(abs(q['extension_beyond_base_mm']-q['travel_mm'])<1e-5 for q in output_positions) and abs(chassis_shape.BoundingBox().xmax-EXIT_X)<1e-5}
 upper_centers=[p['shape'].Center().toTuple() for p in parts if p.get('bearing') and p['name'].startswith('625ZZ upper')]
 lower_centers=[p['shape'].Center().toTuple() for p in parts if p.get('bearing') and p['name'].startswith('625ZZ lower')]
 measured_span=max(c[1] for c in upper_centers)-min(c[1] for c in upper_centers)
 # Clear the collision-screening triangulation before exact CAD bounds.
 BRepTools.Clean_s(beam.wrapped);BRepTools.Clean_s(chassis_shape.wrapped)
 measured_width=beam.BoundingBox().ylen
 report['width_variant']={'multiple':WIDTH,'output_plate_width_mm':measured_width,'base_width_mm':chassis_shape.BoundingBox().ylen,'upper_bearing_center_span_mm':measured_span,'upper_bearing_centers_mm':upper_centers,'lower_bearing_centers_mm':lower_centers,'outward_shift_per_side_mm':WIDEN,'motor_and_screw_center_y_mm':0,'height_mm':height,'passed':abs(measured_width-OUTPUT_WIDTH)<1e-5 and abs(chassis_shape.BoundingBox().ylen-2*HALF_WIDTH)<1e-5 and abs(measured_span-(24*math.sqrt(3)+2*WIDEN))<1e-5 and len(upper_centers)==4 and len(lower_centers)==LOWER_COUNT and all(min(abs(c[1]-y) for y in lower_positions(STATIONS[0] if abs(c[0]-STATIONS[0])<.01 else STATIONS[1]))<1e-5 and abs(c[2]-18)<1e-5 for c in lower_centers) and height<=68.00001}
 if PRINTED:
  light_checks=[]
  for name,shape in [('base',chassis_shape),('carriage',beam)]:
   blocked=sum(overlap(cut,shape) for cut in CUTOUTS[name]);row=dict(part=name,**LIGHTENING[name],blocked_cutouts_mm3=blocked);row['passed']=blocked<.01 and row['removed_mm3']>0;light_checks.append(row)
  motor_keepout=rect(-40,0,-22.49,22.49,21,63)
  brace_intrusion=sum(overlap(brace,motor_keepout) for brace in MOTOR_BRACES)
  report['lightening']={'checks':light_checks,'carriage_pocket_floor_mm':4,'passed':all(q['passed'] for q in light_checks) and report['running_faces']['passed']}
  report['motor_bracing']={'length_mm':42,'width_mm':12,'motor_side_margin_mm':1.5,'rear_x_mm':-36,'motor_keepout_intersection_mm3':brace_intrusion,'passed':len(MOTOR_BRACES)==2 and brace_intrusion<.01}
 report['kinematics']={'lead_mm_per_rev':8,'pitch_mm':8 if PRINTED else 2,'starts':1 if PRINTED else 4,'revolutions_over_stroke':STROKE/LEAD,'full_step_mm':.04,'sixteenth_microstep_mm':.0025,'microsteps_are_command_resolution_not_accuracy':True}
 if PRINTED:
  thread_checks=[]
  screw=by_name['Printed 20 mm lead screw with integral shaft clamp']
  for travel in sorted(set([0,1,2,3,4,8,STROKE/2,STROKE])):
   thread_checks.append({'travel_mm':travel,'screw_angle_deg':-travel*360/LEAD,'overlap_mm3':overlap(pose(screw,travel),pose(by_name['Hollow triangular carriage'],travel))})
  bands=[{'home_x_mm':[lo,hi],'full_extension_x_mm':[lo+STROKE,hi+STROKE],'fully_engaged':lo>=30 and hi+STROKE<=ROD_END} for lo,hi in THREAD_BANDS]
  report['printed_thread']={'major_diameter_mm':20,'root_diameter_mm':16,'lead_mm':8,'starts':1,'radial_relief_mm':.35,'axial_relief_per_flank_mm':.25,'smooth_bore_diameter_mm':21.2,'threaded_bands':bands,'checks':thread_checks,'tip_recess_mm':EXIT_X-ROD_END,'passed':all(q['overlap_mm3']<.01 for q in thread_checks) and len(bands)==2 and all(q['fully_engaged'] for q in bands) and EXIT_X-ROD_END>=3}
  print('Printed thread',report['printed_thread']['passed'],flush=True)
 if not PRINTED:
  # Measure exact CAD bounds, excluding the collision mesh's tessellation padding.
  BRepTools.Clean_s(by_name[f'T8x8 threaded rod {T8_LENGTH:g} mm']['shape'].wrapped)
  BRepTools.Clean_s(by_name['T8x8 brass flange nut']['shape'].wrapped)
  rod=by_name[f'T8x8 threaded rod {T8_LENGTH:g} mm']['shape'].BoundingBox()
  nut=by_name['T8x8 brass flange nut']['shape'].BoundingBox()
  engagement=[]
  for travel in [0,STROKE/2,STROKE]:
   lo,hi=nut.xmin+travel,nut.xmax+travel
   engagement.append(dict(travel_mm=travel,nut_bounds_x_mm=[lo,hi],engaged_length_mm=max(0,min(rod.xmax,hi)-max(rod.xmin,lo)),tip_margin_mm=rod.xmax-hi))
  report['t8_screw_length']={'nominal_length_mm':T8_LENGTH,'measured_length_mm':rod.xlen,'rod_bounds_x_mm':[rod.xmin,rod.xmax],'coupling_engagement_mm':34-rod.xmin,'nut_length_mm':nut.xlen,'usable_stroke_mm':STROKE,'checks':engagement,'passed':abs(rod.xlen-T8_LENGTH)<1e-5 and abs(rod.xmin-ROD_START)<1e-5 and 34-rod.xmin>=8-1e-5 and EXIT_X-rod.xmax>=3 and all(abs(q['engaged_length_mm']-nut.xlen)<1e-5 and q['tip_margin_mm']>=TIP_MARGIN-1e-5 for q in engagement)}
 report['limits']=['Geometry prototype; no stress, stiffness, fatigue or physical fit validation.',('Printed screw and female bands have real helices and synchronized motion; thread clearance is checked, but friction, wear and print fit require testing.' if PRINTED else 'T8 screw and nut use smooth fit envelopes; helical thread engagement, backlash and friction are not simulated.'),'Motor and purchased hardware dimensions are reference assumptions; confirm actual parts. No external screw-support bearings are modeled.','Bearing-block adjustment is rigid translation; clamp force, stiffness and print creep require physical testing.','Three-ridge pilot dimensions are prototype values; test forming torque and pull-out with the actual screw and print material. Unformed ridge overlap is intentional, not a simulated formed thread.']
 report['passed']=(not PRINTED or report['shaft_clamp']['passed']) and (PRINTED or report['t8_screw_length']['passed']) and report['smooth_running_faces']['passed'] and report['carrier_heat_set_inserts']['passed'] and report['running_faces']['passed'] and (not PRINTED or (report['lightening']['passed'] and report['motor_bracing']['passed'])) and report['width_variant']['passed'] and not(collisions or motion or access or exploded) and report['printability']['passed'] and report['cutout_planning']['passed'] and report['bearing_support_feet']['passed'] and report['adjustable_bearings']['passed'] and report['bearing_face_relief']['passed'] and report['split_axles']['passed'] and report['lid_and_attachment']['passed'] and report['lid_lightening']['passed'] and report['guidance']['passed'] and report['valid_single_solids'] and report['compact_layout']['passed'] and report['output_mount']['passed'] and report['output_bolt_access']['passed'] and report['base_mount_access']['passed'] and (not PRINTED or report['printed_thread']['passed'])
 save();print('Validation',report['passed'],flush=True);return report
