"""Verify the optional thrust path, rear loading, hardware access and rotation."""
def check_support_6805(by_name):
 host=by_name[SUPPORT_HUB_NAME]['shape'];housing=by_name[SUPPORT_HOLDER_NAME]['shape']
 inner=by_name['6805 inner race reference']['shape'];outer=by_name['6805 outer race reference']['shape']
 def annulus(ro,ri,x0,x1):return xcyl(ro,x1-x0,x0).cut(xcyl(ri,x1-x0,x0))
 checks={}
 checks['rear_bearing_loading_clear']=overlap(annulus(18.5,12.5,6,33.3),housing)<.01
 checks['journal_bore_clear']=overlap(host,inner)<.01
 checks['hub_shoulder_stops_forward_motion']=overlap(host.translate((.2,0,0)),inner)>1
 checks['housing_lip_stops_forward_motion']=overlap(outer.translate((.2,0,0)),housing)>1
 checks['shoulder_clear_of_shield']=overlap(host,by_name['6805 shield envelope reference']['shape'])<.01
 checks['captured_nut_fully_on_rod']=abs(ROD_START-26.5)<1e-7 and ROD_END>41.5
 checks['captured_nut_rear_abutment']=overlap(z_retaining_nut.translate((-.2,0,0)),host)>1
 # Verify the four screw heads bear on the captive nut's front flange.
 for i in range(4):checks[f'nut_front_retention_{i+1}']=overlap(z_retaining_nut.translate((.2,0,0)),by_name[f'M3x12 retaining nut bolt {i+1}']['shape'])>.1
 # Fit the retaining-nut screws on the loose hub before the locking-clamp bolt.
 # Their straight front-loading passages cross the empty clamp cross-hole.
 for i,(y,z) in enumerate(z_nut_holes):
  sweep=xcyl(1.6,42,29.5,y,z).fuse(xcyl(2.9,33,41.5,y,z))
  ribs=ridge_material(3,9,(38,y,z),(-1,0,0))
  checks[f'nut_bolt_front_loading_{i+1}']=host.intersect(sweep).cut(ribs).Volume()<.01 and overlap(sweep,z_retaining_nut)<.01
  checks[f'nut_bolt_driver_{i+1}']=overlap(xcyl(1.5,45,44.6,y,z),host)<.01
 # Complete circumferential envelopes also cover angles between sampled poses.
 envelope=xcyl(11,15.3,9).fuse(xcyl(13.5,2,24.3),xcyl(12.45,18.2,26.3),xcyl(12,14.5,43.5))
 rotation=[]
 for name in [BASE_NAME,LID_NAME,SUPPORT_HOLDER_NAME,'Hollow triangular carriage','6805 outer race reference','6805 shield envelope reference']:
  v=overlap(envelope,by_name[name]['shape']);rotation.append(dict(part=name,overlap_mm3=v))
 checks['rotation_envelope_clear']=all(q['overlap_mm3']<.01 for q in rotation)
 # Holder bolts enter straight from the rear, outside the bearing body.
 insertion=[]
 for y,z in z_holder_holes:
  sweep=xcyl(1.6,100,-55.5,y,z).fuse(xcyl(3.25,58.5,-59,y,z))
  obstacles=[]
  for name in [BASE_NAME,SUPPORT_HOLDER_NAME,SUPPORT_HUB_NAME,'6805 outer race reference','6805 inner race reference']:
   v=overlap(sweep,by_name[name]['shape'])
   if v>.01:obstacles.append(dict(part=name,overlap_mm3=v))
  rear_tool=xcyl(4.25,30,-30,y,z)
  for name in [BASE_NAME,'NEMA17 42x42x40 reference']:
   v=overlap(rear_tool,by_name[name]['shape'])
   if v>.01:obstacles.append(dict(part=name,tool='rear bolt driver',overlap_mm3=v))
  insertion.append(dict(center_yz_mm=[y,z],collisions=obstacles))
 checks['mounting_bolt_loading_clear']=not any(q['collisions'] for q in insertion)
 # Motor fasteners are serviced with the support module removed.
 checks['separate_motor_screw_access']=all(overlap(xcyl(3,45,6,y,z),by_name[BASE_NAME]['shape'])<.01 for y,z in motor_holes)
 lip=annulus(18.4,17.6,33.4,36.3)
 checks['continuous_outer_race_lip']=lip.cut(housing).Volume()<.01
 checks['full_depth_mount_columns']=all(q.cut(housing).Volume()<.01 for q in z_holder_columns)
 checks['outward_mount_bosses']=all(abs(y)-3.5>21.5 for y,z in z_holder_holes)
 for x,y,label in [(17,5,'motor shaft'),(49,6.5,'T8 locking')]:
  nut=by_name[f'M3 {label} clamp hex nut']['shape'];bolt_shape=by_name[f'M3x12 {label} clamp bolt']['shape']
  checks[label+'_bolt_access']=all(overlap(host,bolt_shape.translate((0,0,d)))<.01 for d in [0,1,3,6,12,24])
  checks[label+'_nut_access']=all(overlap(host,nut.translate((0,0,-d)))<.01 for d in [0,1,3,6,12])
 hardware=[tuple(by_name[f'M3 {label} {i+1}']['shape'] if label!='holder tie bolt' else by_name[f'M3x45 {label} {i+1}']['shape'] for label in ['holder tie bolt','holder front washer','holder rear washer','holder locknut']) for i in range(4)]
 structural=_housing.inspect_load_path(housing,by_name[BASE_NAME]['shape'],36.3,33.3,z_holder_columns,hardware)
 checks['structural_abutment_path']=structural['passed']
 return dict(passed=all(checks.values()),structural_load_path=structural,checks=checks,rotation_envelope=rotation,holder_bolt_insertion=insertion,motor_service="Remove support module before accessing the separate NEMA17 screws",specification=SUPPORT_6805,load_path='Rod → captured T8 flange nut → four M3 bolts / printed hub → inner-race shoulder → 6805 → continuous housing lip → front flange / washers → four outboard M3 through-bolts / rear washers → base wall',service_travel_mm=8*math.floor(STROKE/8),limitations=['Geometry only; no validated PETG creep, vibration endurance or axial load rating.','Thrust toward screw tip only; no independent reverse-direction retainer.','T8 threads use purchased-hardware fit envelopes; flank stress and backlash are not simulated.'])
