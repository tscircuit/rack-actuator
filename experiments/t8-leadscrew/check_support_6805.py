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
 # Loosen shared motor screws while they remain captured in the holder;
 # then lift the complete support module before extracting their full length.
 insertion=[]
 for y,z in z_holder_holes:
  sweep=xcyl(1.6,40,-5.7,y,z).fuse(xcyl(2.8,9,34.3,y,z))
  obstacles=[]
  for name in [BASE_NAME,SUPPORT_HOLDER_NAME,SUPPORT_HUB_NAME,'6805 outer race reference','6805 inner race reference','NEMA17 42x42x40 reference']:
   v=overlap(sweep,by_name[name]['shape'])
   if v>.01:obstacles.append(dict(part=name,overlap_mm3=v))
  # Lid off, carriage withdrawn: short key leg followed by an upward handle.
  tool=xcyl(1.5,10,37.3,y,z).fuse(cyl(1.5,50,(46,y,z)))
  for name in [BASE_NAME,SUPPORT_HOLDER_NAME,SUPPORT_HUB_NAME]:
   v=overlap(tool,by_name[name]['shape'])
   if v>.01:obstacles.append(dict(part=name,tool='front hex key',overlap_mm3=v))
  insertion.append(dict(center_yz_mm=[y,z],captured_unthreading_mm=6,motor_engagement_mm=5.7,collisions=obstacles))
 checks['mounting_bolt_loading_clear']=not any(q['collisions'] for q in insertion)
 checks['shared_motor_screws_only']=len([p for p in parts if p.get('explodeKind')=='sharedMotorBolt'])==4 and not any('separate motor bolt' in p['name'] or 'holder tie bolt' in p['name'] or 'holder locknut' in p['name'] for p in parts)
 lip=annulus(18.4,17.6,33.4,36.3)
 checks['continuous_outer_race_lip']=lip.cut(housing).Volume()<.01
 checks['full_depth_mount_columns']=all(q.cut(housing).Volume()<.01 for q in z_holder_columns)
 checks['nema17_mount_pattern']=sorted(z_holder_holes)==sorted(motor_holes)
 for x,y,label in [(17,5,'motor shaft'),(49,6.5,'T8 locking')]:
  nut=by_name[f'M3 {label} clamp hex nut']['shape'];bolt_shape=by_name[f'M3x12 {label} clamp bolt']['shape']
  checks[label+'_bolt_access']=all(overlap(host,bolt_shape.translate((0,0,d)))<.01 for d in [0,1,3,6,12,24])
  checks[label+'_nut_access']=all(overlap(host,nut.translate((0,0,-d)))<.01 for d in [0,1,3,6,12])
 hardware=[by_name[f'M3x40 shared motor holder bolt {i+1}']['shape'] for i in range(4)]
 structural=_housing.inspect_load_path(housing,by_name[BASE_NAME]['shape'],36.3,33.3,z_holder_columns,hardware)
 checks['structural_abutment_path']=structural['passed']
 return dict(passed=all(checks.values()),structural_load_path=structural,checks=checks,rotation_envelope=rotation,holder_bolt_insertion=insertion,motor_service="Remove lid and withdraw carriage. Unthread the four shared motor/holder screws 6 mm, slide/lift the module clear, then extract the bolts.",specification=SUPPORT_6805,load_path='Rod → captured T8 flange nut → four M3 bolts / printed hub → inner-race shoulder → 6805 → continuous housing lip → side walls / bolt head seats → four shared M3x40 screws → NEMA17 front threads and clamped base wall',service_travel_mm=8*math.floor(STROKE/8),limitations=['Geometry only; no validated PETG creep, vibration endurance or axial load rating.','Thrust toward screw tip only; no independent reverse-direction retainer.','T8 threads use purchased-hardware fit envelopes; flank stress and backlash are not simulated.'])
