"""Optional T8 Z-axis support, evaluated in the shared model namespace.
A second brass T8 flange nut carries axial load into the rotating printed hub.
The split clamp locks screw/nut rotation; it is not the sole axial load path.
"""
SUPPORT_6805=dict(bearing_mm=[25,37,7],bearing_x_mm=[26.3,33.3],holder_x_mm=[6,36.3],journal_diameter_mm=24.9,shoulder_diameter_mm=27,holder_bore_mm=37.2,retaining_nut_x_mm=[26.5,41.5],clamp_x_mm=[17,49],additional_t8_nuts=1,load_direction='+X toward screw tip',recess_opening='motor-facing',reverse_retainer=False)
SUPPORT_HUB_NAME='6805 T8 captured-nut drive hub';SUPPORT_HOLDER_NAME='6805 flanged bearing holder'
# Continuous hub: motor clamp, inner-race shoulder/journal, captured nut,
# and a separate rod clamp preventing the screw from winding out of its nut.
z_hub=xcyl(11,15.3,9).fuse(xcyl(13.5,2,24.3),xcyl(12.45,18.2,26.3),xcyl(12,14.5,43.5))
z_hub=z_hub.cut(d_shaft(2.65,2.15,17,8)).cut(xcyl(4.1,33,25.5)).cut(xcyl(5.2,12.5,26)).cut(xcyl(11.2,4,38))
for x,lo,hi in [(17,8,26),(49,42,59)]:
 cy=6.5 if x==49 else 5
 z_hub=z_hub.cut(rect(lo,hi,0,14,41.5,42.5)).cut(cyl(1.65,26,(x,cy,28))).cut(cyl(3,14,(x,cy,46 if x==49 else 45))).cut(hex_prism(5.9,12.9 if x==49 else 11.9,(x,cy,25)))
z_nut_holes=[(8*math.cos(j*math.pi/2),SCREW_Z+8*math.sin(j*math.pi/2)) for j in range(4)]
for y,z in z_nut_holes:
 z_hub=z_hub.cut(ridge_hole(3,9,(38,y,z),(-1,0,0))).cut(xcyl(2.9,17,42,y,z))
z_hub=z_hub.clean()
add(SUPPORT_HUB_NAME,z_hub,'#e8b84a','rotor',True)
z_retaining_nut=xcyl(5,11.5,26.5).fuse(xcyl(11,3.5,38)).cut(xcyl(4.1,17,26))
for y,z in z_nut_holes:z_retaining_nut=z_retaining_nut.cut(xcyl(1.75,5,37.5,y,z))
add('T8 captured retaining flange nut',z_retaining_nut,'#d8ad4c','rotor')
for i,(y,z) in enumerate(z_nut_holes):
 name=f'M3x12 retaining nut bolt {i+1}'
 add(name,bolt(1.45,12,2.75,3,(29.5,y,z),AXIS),'#94a3b8','rotor')
 thread_joint(SUPPORT_HUB_NAME,name,3,9,(38,y,z),(-1,0,0))
for x,label in [(17,'motor shaft'),(49,'T8 locking')]:
 cy=6.5 if x==49 else 5
 add(f'M3x12 {label} clamp bolt',bolt(1.45,12,2.75,3,(x,cy,34 if x==49 else 33)),'#94a3b8','rotor')
 add(f'M3 {label} clamp hex nut',hex_prism(5.5,2.4,(x,cy,35.5 if x==49 else 34.5)).cut(cyl(1.55,2.6,(x,cy,35.4 if x==49 else 34.4))),'#b7c8d5','rotor')
# Four shared NEMA17 screws and continuous side walls around the coupling.
import importlib.util
_hspec=importlib.util.spec_from_file_location('shared_holder',ROOT/'experiments/bearing-supported-screw/holder_geometry.py')
_housing=importlib.util.module_from_spec(_hspec);_hspec.loader.exec_module(_housing)
z_holder,z_holder_holes,z_holder_columns=_housing.make_holder(6,26.3,33.3,36.3)
for i,(y,z) in enumerate(z_holder_holes):
 add(f'M3x40 shared motor holder bolt {i+1}',bolt(1.45,40,2.75,3,(-5.7,y,z),AXIS),'#94a3b8',explodeKind='sharedMotorBolt')
add(SUPPORT_HOLDER_NAME,z_holder,'#39556c',printed=True,explodeKind='supportHousing')
SUPPORT_6805.update(mount_pattern_mm=[31,31],mount_bolts='4 M3x40 shared holder/wall/motor screws',motor_bolts='Same four screws; no separate holder bolts or nuts',holder_outer_width_mm=43,continuous_columns=4,side_walls=2,head_seat_x_mm=34.3,motor_thread_engagement_mm=5.7)
for name,ro,ri,x0,x1 in [('inner race',13.5,12.5,26.3,33.3),('outer race',18.5,17.5,26.3,33.3),('shield envelope',17.4,13.6,26.45,33.15)]:
 add('6805 '+name+' reference',xcyl(ro,x1-x0,x0).cut(xcyl(ri,x1-x0,x0)),'#a9bbc9','rotor' if name=='inner race' else 'fixed',explodeKind='supportBearing')
