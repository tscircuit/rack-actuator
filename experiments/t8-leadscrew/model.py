"""NEMA17 lead-screw prototypes: standard-length T8x8 and printed screw. Units: mm.
Hardware meshes are fit envelopes. Lower bearings share one rigid four-bolt adjustable carrier.
"""
import argparse,gzip,hashlib,json,math,pathlib,sys,zipfile
import cadquery as cq
P=argparse.ArgumentParser();P.add_argument('--travel',type=int,choices=[40,120],default=40,help='Printed-screw usable travel in mm');P.add_argument('--check',action='store_true');P.add_argument('--quick',action='store_true');P.add_argument('--width',type=int,choices=[1,2,4],default=1);P.add_argument('--width-build-root',type=pathlib.Path);P.add_argument('--screw-length',type=int,default=100,help='Overall purchased T8 rod length in mm, including coupling engagement');P.add_argument('--support',choices=['standard','6805'],default='standard');P.add_argument('--variant',choices=['t8','printed'],default='t8');args=P.parse_args();PRINTED=args.variant=='printed';EXPERIMENT='printed-leadscrew' if PRINTED else 't8-leadscrew'
if not PRINTED and args.screw_length<70:P.error('T8 screw length must be at least 70 mm for this bearing layout.')
Z_SUPPORT=not PRINTED and args.support=='6805'
if PRINTED and args.support!='standard':P.error('6805 integration is a T8 option.')
if args.width!=1 and not ((PRINTED and args.travel==40) or (not PRINTED and args.screw_length==100)):P.error('Wide variants require printed 40 mm travel or a 100 mm T8 rod.')
WIDTH=args.width;WIDEN=21.*(WIDTH-1);HALF_WIDTH=40+WIDEN
OUTPUT_WIDTH={1:42.,2:104.,4:168.}[WIDTH];GRID_Y=[31*(j-({1:2,2:4,4:6}[WIDTH]-1)/2) for j in range({1:2,2:4,4:6}[WIDTH])]
def wide(y):return y+math.copysign(WIDEN,y) if y else 0.
ROOT=pathlib.Path(__file__).resolve().parents[2];OUT=ROOT/'dist/experiments'/EXPERIMENT;OUT=(args.width_build_root/EXPERIMENT if args.width_build_root else OUT)
if not PRINTED and args.screw_length!=100:OUT=OUT/'lengths'/f'{args.screw_length}mm'
if PRINTED and args.travel!=40:OUT=OUT/'travel'/f'{args.travel}mm'
if WIDTH!=1:OUT=OUT/'widths'/f'{WIDTH}x'
if Z_SUPPORT:OUT=OUT/'support-6805'
OUT.mkdir(parents=True,exist_ok=True)
SQ=math.sqrt(.5);LEAD=8.;AXIS=(1,0,0);SCREW_Z=42.
# Purchased rod length includes the fixed coupling/retaining-nut engagement.
T8_LENGTH=float(args.screw_length);ROD_START=26.5 if Z_SUPPORT else 26.;NUT_HOME=74. if Z_SUPPORT else 48.;NUT_REAR=11.5;NUT_FRONT=3.5;TIP_MARGIN=4.5
ROD_END=112.+args.travel if PRINTED else ROD_START+T8_LENGTH
T8_STATION_SPACING=80. if T8_LENGTH==300 else 40.
T8_THREAD_TRAVEL=math.floor(ROD_END-(NUT_HOME+NUT_FRONT)-TIP_MARGIN)
STROKE=float(args.travel) if PRINTED else T8_THREAD_TRAVEL-(T8_STATION_SPACING-40)
TAIL_HOME=46. if Z_SUPPORT else 10.
STATIONS=[STROKE+23,STROKE+97] if PRINTED else [TAIL_HOME+STROKE+13,TAIL_HOME+STROKE+13+T8_STATION_SPACING]
EXIT_X=STATIONS[-1]+18+(14 if not PRINTED and WIDTH>1 else 0);GUIDE_END=EXIT_X-8;BASE_REAR=-8.;MOTOR_FRONT=0.;GUIDE_RADIUS=16.;TRI_SQ=math.sqrt(3);THREAD_BANDS=[(36.,48.),(96.,108.)]
# Wide T8 noses provide bolt access without reducing the 40 mm guide spacing.
if PRINTED and WIDTH>1:STATIONS[-1]-=14
ADJUST_REAR_SHIFT=0.
# Preserve the original grid origin; add every row that leaves a 4 mm seat radius.
GRID_X=[10.5+31*j for j in range(math.floor((EXIT_X-4-10.5)/31)+1)]
LID_GRID_X=[10.5+31*j for j in range(math.floor((EXIT_X-9-4-10.5)/31)+1)]
ADJUST_FRONT_SHIFT=6. if not PRINTED and any(math.hypot(STATIONS[-1]-12-x,wide(y)-gy)<8 for x in LID_GRID_X for gy in GRID_Y for y in [-26,26]) else 0.
BEARING_SUPPORT_BOTTOM=43.
ADJUST_SHELF_TOP=47.;ADJUST_BOLT_LENGTH=40.;BEARING_UNDERSIDES=[]
BASE_NAME='Adjustable six-bearing base';CARRIER_NAME='Shared lower bearing carrier';ADJUST_CENTERS=[(x-12-(ADJUST_REAR_SHIFT if x==STATIONS[0] else ADJUST_FRONT_SHIFT),wide(y)) for x in STATIONS for y in [-26,26]]
CARRIAGE_WITHDRAWAL=2*EXIT_X-110 if PRINTED else 2*EXIT_X-42.
LID_NAME='Structural mounting lid';LID_Z=64.;LID_FIXINGS=[(12,sign*(HALF_WIDTH-5)) for sign in [-1,1]]+[(x+2,wide(y)) for x in STATIONS for y in [-35,35]];LID_MOUNTS=[];SIDE_MOUNTS=[]
ATTACH_PILOTS=[];MOUNT_SEATS=[]
MOUNT_INSERT=dict(type='ruthex RX-M3Sx4.0',thread='M3',od_mm=4.6,length_mm=4,pilot_diameter_mm=4,entry_diameter_mm=4.8,minimum_wall_mm=1.65,lid_open_bottom=True,base_backing="Retained below structural feet; otherwise open",lid_max_screw_entry_mm=4,base_max_screw_entry_mm=5)
LIGHTENING={};CUTOUTS={};MOTOR_BRACES=[];BRACE_CUTS=[];CARRIAGE_CUTS=[];WINDOW_LAYOUTS={}
MIN_WINDOW_WEB=6.
CLAMP=dict(shaft_diameter_mm=5,shaft_across_flat_mm=4.5,bore_diameter_mm=5.3,bore_across_flat_mm=4.8,radial_clearance_mm=.15,flat_clearance_mm=.15,hub_diameter_mm=22,shaft_engagement_mm=15,split_gap_mm=1,bolt='M3x12 socket-head',nut='M3 hex nut',nut_across_flats_mm=5.5,nut_thickness_mm=2.4,nut_pocket_across_flats_mm=5.9,nut_pocket_top_z_mm=36.9,bolt_center_xy_mm=[17,5],nut_installation='Insert from underneath into the hex pocket before fitting the screw to the motor; start the bolt, align the D flat, then tighten through the lid access hole with the carriage extended.')
INSERT=dict(type='ruthex RX-M5x9.5',thread='M5',od_mm=7.1,length_mm=9.5,pilot_diameter_mm=6.4,pilot_depth_mm=10.5,entry_diameter_mm=7.2,minimum_wall_mm=2.6)
def lower_positions(x):return [-10.5*WIDTH,10.5*WIDTH] if WIDTH>1 else [-1 if x==STATIONS[0] else 1]
LOWER_COUNT=4 if WIDTH>1 else 2
AXLE_SPEC=dict(type='split retained-head axle',material='PETG',printed_diameter_mm=4.8,assembled_diameter_mm=4.8,bearing_bore_mm=5,head_width_mm=6.4,tip_bend_degrees=30,relief_slot=True,bent_tip=True,retaining_head=True,installation='Pinch the split retaining head and slide the bearing on while supporting its inner race. The tapered relief slot and root clearance allow inward flex. Insertion force and strain are not validated; the viewer shows the undeformed geometry.')
SNAP=dict(shaft_radius=2.4,head_radius=3.2,tip_radius=2.3,slot_width=1.2,root_t=9.6,head_back_t=-2.75,tip_t=-8.1,compression=0,shaft_bias_slope=0,bend_start_t=-3.75,tip_bend_degrees=30,extension_mm=3,bearing_release_mm=12,head_slot_width=2.0,tip_slot_width=2.2)
parts=[]
def box(x,y,z,c):return cq.Workplane('XY').box(x,y,z).translate(c).val()
def rect(xa,xb,ya,yb,za,zb):return box(xb-xa,yb-ya,zb-za,((xa+xb)/2,(ya+yb)/2,(za+zb)/2))
def at(c,u,t):return tuple(c[i]+u[i]*t for i in range(3))
def cyl(r,h,c,u=(0,0,1),t=0):return cq.Solid.makeCylinder(r,h,cq.Vector(*at(c,u,t)),cq.Vector(*u))
def xcyl(r,h,x,y=0,z=SCREW_Z):return cyl(r,h,(x,y,z),AXIS)
def hex_prism(af,height,center):
 r=af/math.sqrt(3);points=[(r*math.cos(k*math.pi/3),r*math.sin(k*math.pi/3)) for k in range(6)]
 return cq.Workplane('XY',origin=center).polyline(points).close().extrude(height).val()
def d_shaft(radius,flat_y,length,x):
 return xcyl(radius,length,x).intersect(rect(x,x+length,-radius,flat_y,SCREW_Z-radius,SCREW_Z+radius))
def ring(ro,ri,h,c,u=(0,0,1),t=0):return cyl(ro,h,c,u,t).cut(cyl(ri,h,c,u,t))
def bolt(r,length,head_r,head_h,c,u=(0,0,1),t=0):
 # c+t is the shaft tip; the head follows the shaft along +u.
 return cyl(r,length,c,u,t).fuse(cyl(head_r,head_h,c,u,t+length)).cut(cyl(r*.8,head_h*.55,c,u,t+length+head_h*.45))
# Prototype three-ridge pilots: circular relief with three inward rounded ribs.
# The ribs run axially at 120 degrees; the screw forms its thread on assembly.
THREAD_PROFILES={3:dict(relief_radius=1.65,tip_radius=1.30,rib_radius=.65,lead_in=.6),5:dict(relief_radius=2.65,tip_radius=2.20,rib_radius=.90,lead_in=.6)}
def ridge_hole(d,length,c,u,t=0):
 spec=THREAD_PROFILES[d];rr=spec['rib_radius'];rho=spec['tip_radius']+rr
 start=at(c,u,t);plane=cq.Plane(origin=start,xDir=(0,1,0) if abs(u[0])>.9 else (1,0,0),normal=u)
 hole=cyl(spec['relief_radius'],length,start,u)
 for k in range(3):
  a=2*math.pi*k/3;center=plane.toWorldCoords((rho*math.cos(a),rho*math.sin(a),0)).toTuple()
  hole=hole.cut(cyl(rr,length,center,u))
 lead=cq.Solid.makeCone(spec['relief_radius']+.1,spec['tip_radius'],spec['lead_in'],cq.Vector(*start),cq.Vector(*u))
 return hole.fuse(lead)
def mount_pilot(c,u,depth):
 return cyl(2,depth,c,u).fuse(cq.Solid.makeCone(2.4,2,.35,cq.Vector(*c),cq.Vector(*u)))
def ridge_material(d,length,c,u,t=0):
 return cyl(THREAD_PROFILES[d]['relief_radius'],length,c,u,t).cut(ridge_hole(d,length,c,u,t))
THREAD_JOINTS=[];OUTPUT_PILOTS=[]
def thread_joint(host,bolt,d,length,c,u,t=0):
 THREAD_JOINTS.append(dict(host=host,bolt=bolt,diameter=d,length=length,center=c,axis=u,start=t))
def add(name,s,color,group='fixed',printed=False,**kw):
 s=s.clean();assert s.isValid() and len(s.Solids())==1,(name,s.isValid(),len(s.Solids()))
 p=dict(name=name,shape=s,color=color,group=group,printed=printed,**kw);parts.append(p);return p

def rounded_cut(xa,xb,ya,yb,za,zb,r=3):
 return cq.Workplane(obj=rect(xa,xb,ya,yb,za,zb)).edges('|Z').fillet(min(r,(xb-xa)/2-.1,(yb-ya)/2-.1)).val()
def bays(lo,hi,maximum=28,rib=6):
 count=max(1,math.ceil((hi-lo+rib)/(maximum+rib)));span=(hi-lo-rib*(count-1))/count
 return [(lo+i*(span+rib),lo+i*(span+rib)+span) for i in range(count)]
def lighten(shape,cuts,name):
 before=shape.Volume();result=shape
 for cut in cuts:result=result.cut(cut)
 after=result.Volume();LIGHTENING[name]=dict(before_mm3=before,after_mm3=after,removed_mm3=before-after,reduction_percent=100*(before-after)/before,cutout_count=len(cuts));CUTOUTS[name]=cuts
 return result.clean()
def prism(points,xa,xb):return cq.Workplane('YZ',origin=(xa,0,0)).polyline(points).close().extrude(xb-xa).val()
# The screw runs through the center of the triangular moving section.
# Six bearings stay on the fixed base; one shared lower carrier adjusts vertically.
def section_wire(x,r):
 # Clip 12 mm radially from each original 32 mm triangle tip at r=16.
 # Keep the three full-width contact flats and the central service bore.
 v=[(-TRI_SQ*r,SCREW_Z-r),(TRI_SQ*r,SCREW_Z-r),(0,SCREW_Z+2*r)]
 pts=[]
 for i,a in enumerate(v):
  b=v[(i+1)%3]
  for t in [.25,.75]:pts.append(cq.Vector(x,wide(a[0]+t*(b[0]-a[0])),a[1]+t*(b[1]-a[1])))
 return cq.Wire.makePolygon(pts+[pts[0]])
beam=cq.Solid.makeLoft([section_wire(x,r) for x,r in [(TAIL_HOME,15),(TAIL_HOME+4,16),(GUIDE_END,16)]],ruled=True)
# An eight-millimetre square output flange establishes the exit/extension datum.
flange_plate=box(8,OUTPUT_WIDTH,42,(EXIT_X-4,0,SCREW_Z))
flange_plate=cq.Workplane(obj=flange_plate).edges('|X').fillet(2).val()
beam=beam.fuse(flange_plate)
# Both versions retain the same outer running section and output interface.
nut_holes=[]
def helical_ridge(radius0,radius1,halfroot,halfcrest,length):
 path=cq.Wire.makeHelix(LEAD,length,8)
 q=cq.Workplane('XZ').polyline([(radius0,-halfroot),(radius1,-halfcrest),(radius1,halfcrest),(radius0,halfroot)]).close().sweep(path,isFrenet=True).val()
 return q.rotate((0,0,0),(0,1,0),90).translate((30,0,SCREW_Z))
if PRINTED:
 print('Building printable helix and two threaded bands',flush=True)
 male=helical_ridge(7.9,10,2.5,1,ROD_END-30).fuse(xcyl(8,ROD_END-30,30)).intersect(xcyl(10.1,ROD_END-30,30)).clean()
 # Matching continuous phase in both bands, with .35 radial / .25 axial relief.
 cutter=helical_ridge(8.25,10.35,2.75,1.25,122).fuse(xcyl(8.35,124,29)).clean()
 beam=beam.cut(xcyl(13.5,25,9))
 previous=34
 for lo,hi in THREAD_BANDS:
  if lo>previous:beam=beam.cut(xcyl(10.6,lo-previous,previous))
  beam=beam.cut(cutter.intersect(xcyl(11,hi-lo,lo)))
  previous=hi
 beam=beam.cut(xcyl(10.6,EXIT_X+1-previous,previous))
else:
 beam=beam.cut(xcyl(12.2,NUT_HOME-8-(TAIL_HOME-1),TAIL_HOME-1)).cut(xcyl(12.2,EXIT_X+1-NUT_HOME,NUT_HOME)).cut(xcyl(5.3,14,NUT_HOME-13))
 nut_holes=[(8*math.cos(math.pi/4+j*math.pi/2),SCREW_Z+8*math.sin(math.pi/4+j*math.pi/2)) for j in range(4)]
 for y,z in nut_holes:beam=beam.cut(ridge_hole(3,8,(NUT_HOME,y,z),(-1,0,0)))
output_holes=[(y,SCREW_Z+z) for y in GRID_Y for z in [-15.5,15.5]]
for y,z in output_holes:
 beam=beam.cut(ridge_hole(3,8,(EXIT_X,y,z),(-1,0,0))).cut(xcyl(1.65,2,GUIDE_END-2,y,z))
 OUTPUT_PILOTS.append(dict(diameter=3,length=8,center=(EXIT_X,y,z),axis=(-1,0,0),start=0))
if PRINTED:
 cuts=[rounded_cut(a,b,-4,4,42,65,2.5) for a,b in [(52,88)]+bays(112,GUIDE_END-8,32,6)]
 if WIDTH>1:
  for a,b in [(18,30),(52,88)]+bays(112,GUIDE_END-8,32,6):
   for lo,hi in bays(16,WIDEN+2,24,5):
    for sign in [-1,1]:
     ya,yb=sorted([sign*lo,sign*hi]);cuts.append(rounded_cut(a,b,ya,yb,30,65,2.5))
 CARRIAGE_CUTS=cuts
# Side-load M3 output bolts behind the flange, outside the bearing sweep.
# Keep the full flange thickness and all bearing-running faces. These cutters
# join the final carriage pass, after every feature has been placed.
OUTPUT_BOLT_ACCESS=None
def output_access_cut(y,z=SCREW_Z-15.5):
 if z>SCREW_Z:return output_access_cut(y,2*SCREW_Z-z).mirror("XY",(0,0,SCREW_Z))
 z=SCREW_Z-15.5
 # Round the opening in plan; pitch its roof at 45 degrees for printing.
 length=16 if WIDTH>1 else 20
 footprint=rounded_cut(GUIDE_END-length,GUIDE_END+3.5,y-3.5,y+3.5,18,z+7,1 if WIDTH>1 else 3)
 roof=prism([(y-3.5,18),(y+3.5,18),(y+3.5,z+3),(y,z+6.5),(y-3.5,z+3)],GUIDE_END-length,GUIDE_END)
 return footprint.intersect(roof).clean()
access_centers=[(y,z) for y,z in output_holes if WIDTH>1 or z<SCREW_Z]
CARRIAGE_CUTS.extend(output_access_cut(y,z) for y,z in access_centers)
OUTPUT_BOLT_ACCESS=dict(pocket_width_mm=7,pocket_length_mm=16 if WIDTH>1 else 20,roof_degrees=45,loading='Load lower bolts from underneath with carriage fully extended; upper bolts enter from above.',bolt='M3x12 socket-head reference',head_diameter_mm=5.5,head_height_mm=3,driver_diameter_mm=3,driver_reach_mm=14 if WIDTH>1 else 18,lower_centers_yz_mm=[[y,z] for y,z in output_holes if z<SCREW_Z],access_centers_yz_mm=access_centers,front_bearing_shift_mm=14 if PRINTED and WIDTH>1 else 0,flange_thickness_mm=8)
# Smooth carriage running faces. Keep the existing support clearance channels
# so previously printed bases and bearing carriers remain usable.
TRACKS=[]
for sign in [-1,1]:
 n=(0,sign*math.sqrt(3)/2,.5);u=(0,sign*.5,-math.sqrt(3)/2)
 c=(0,sign*(16*math.sqrt(3)/2+WIDEN),50)
 TRACKS.append(dict(kind='upper',contact=c,axis=u,normal=n,inner=3.))
for y in ([-10.5*WIDTH,10.5*WIDTH] if WIDTH>1 else [0]):
 TRACKS.append(dict(kind='lower',contact=(0,y,26),axis=(0,1,0),normal=(0,0,-1),inner=3. if WIDTH>1 else 4.))
def track_rail(track,side,clearance=False):
 c,u,n=track['contact'],track['axis'],track['normal'];inner=track['inner'];margin=.35 if clearance else 0
 lo,hi=sorted([side*inner,side*(inner+4)]);lo-=margin;hi+=margin
 def wire(x,height):
  pts=[cq.Vector(x,c[1]+u[1]*t+n[1]*h,c[2]+u[2]*t+n[2]*h) for t,h in [(lo,-.6),(hi,-.6),(hi,height),(lo,height)]]
  return cq.Wire.makePolygon(pts+[pts[0]])
 sections=[(TAIL_HOME-1,4.2),(EXIT_X+STROKE+1,4.2)] if clearance else [(TAIL_HOME+4,0),(TAIL_HOME+8,4),(GUIDE_END,4)]
 return cq.Solid.makeLoft([wire(x,h) for x,h in sections],ruled=True)
RAIL_CLEARANCES=[track_rail(t,side,True) for t in TRACKS for side in [-1,1]]
def relieve_tracks(shape):
 for cut in RAIL_CLEARANCES:shape=shape.cut(cut)
 return shape.clean()
add('Hollow triangular carriage',beam,'#50cbb1','carriage',True)
base=rect(BASE_REAR,EXIT_X,-HALF_WIDTH,HALF_WIDTH,0,5)
base=base.fuse(rect(0,6,-max(wide(26),34.5) if PRINTED else wide(-26),max(wide(26),34.5) if PRINTED else wide(26),SCREW_Z-26,SCREW_Z+26))
for sign in [-1,1]:
 ya,yb=sorted([wide(sign*20),wide(sign*26)]);base=base.fuse(rect(0,6,ya,yb,5,SCREW_Z-25))
 if PRINTED:
  ya,yb=sorted([sign*22.5,sign*34.5])
  brace=cq.Workplane('XZ',origin=(0,yb,0)).polyline([(-36,5),(6,5),(6,50)]).close().extrude(yb-ya).val()
  window=cq.Workplane('XZ',origin=(0,yb+1,0)).polyline([(-22,11),(-2,11),(-2,31)]).close().extrude(yb-ya+2).edges('|Y').fillet(2).val()
  BRACE_CUTS.append(window);brace=brace.fuse(rect(-36,6,ya,yb,0,5));MOTOR_BRACES.append(brace);base=base.fuse(brace,rect(0,6,ya,yb,5,17))
 else:
  gusset=cq.Workplane('XZ',origin=(0,yb,0)).polyline([(BASE_REAR,5),(6,5),(6,SCREW_Z-2)]).close().extrude(yb-ya).val();base=base.fuse(gusset)
# Wide T8 plates retain the central motor braces as well as their outer feet.
if not PRINTED and WIDTH>1:
 for sign in [-1,1]:
  ya,yb=sorted([sign*20,sign*26])
  gusset=cq.Workplane('XZ',origin=(0,yb,0)).polyline([(BASE_REAR,5),(6,5),(6,SCREW_Z-2)]).close().extrude(yb-ya).val()
  base=base.fuse(gusset,rect(0,6,ya,yb,5,SCREW_Z-25))
# Fill the unused opening below the motor face down to the print bed.
base=base.fuse(rect(0,6,-20,20,5,SCREW_Z-26))
base=base.cut(rect(-41,0,-21.5,21.5,SCREW_Z-21.5,SCREW_Z+21.5)).cut(xcyl(11.3,8,-1))
motor_holes=[(y,SCREW_Z+z) for y in [-15.5,15.5] for z in [-15.5,15.5]]
for y,z in motor_holes:base=base.cut(xcyl(1.7,8,-1,y,z)).cut(xcyl(4,35,6,y,z))
BASE_MOUNT_WIDTHS=[w for w in [1,2,4] if w<=WIDTH]
BASE_MOUNT_PATTERNS=[dict(width_multiple=w,pitch_xy_mm=[31,31],hole_centers_xy_mm=[(x,31*(j-({1:2,2:4,4:6}[w]-1)/2)) for x in GRID_X for j in range({1:2,2:4,4:6}[w])]) for w in BASE_MOUNT_WIDTHS]
BASE_MOUNT_HOLES=[(x,y) for x in GRID_X for y in GRID_Y]
BASE_MOUNT_OUTER=[c for c in BASE_MOUNT_HOLES if abs(c[1])==max(GRID_Y)];BASE_MOUNT_INNER=[c for c in BASE_MOUNT_HOLES if c not in BASE_MOUNT_OUTER]
LID_MOUNTS=[(x,y) for x in LID_GRID_X for y in GRID_Y]
MOUNT_LAYOUTS=[]
for w,cx in [(1,26.),(2,57.),(2,88.),(4,57.),(4,88.)]:
 n={1:2,2:4,4:6}[w];columns=[cx+31*(j-(n-1)/2) for j in range(n)]
 holes=[(x,y) for x in columns for y in [-15.5,15.5]]
 supported=[c for c in holes if c in BASE_MOUNT_HOLES]
 MOUNT_LAYOUTS.append(dict(width_multiple=w,center_xy_mm=[cx,0],plate_width_axis='X',hole_centers_xy_mm=supported,unsupported_holes_xy_mm=[c for c in holes if c not in supported],fastener_count=len(supported)))

motor=rect(-40,0,-21,21,SCREW_Z-21,SCREW_Z+21).fuse(xcyl(11,2,0)).cut(xcyl(2.6,2.2,-.1))
for y,z in motor_holes:motor=motor.cut(xcyl(1.65,7,-6,y,z))
add('NEMA17 42x42x40 reference',motor,'#26394a','motor')
shaft=xcyl(2.5,4,0).fuse(d_shaft(2.5,2.,20,4)) if PRINTED or Z_SUPPORT else xcyl(2.5,24,0)
add('NEMA17 5 mm D shaft' if PRINTED or Z_SUPPORT else 'NEMA17 5 mm shaft',shaft,'#b7c8d5','rotor')
if not Z_SUPPORT:
 for y,z in motor_holes:add(f'M3x10 motor bolt {y:g} {z:g}',bolt(1.45,10,2.75,3,(-4,y,z),AXIS),'#94a3b8')
if PRINTED:
 # The metal nut takes the clamp load; the hub has clearance bores only.
 shaft_bore=d_shaft(2.65,2.15,17,8)
 hub=xcyl(11,21.5,9).cut(shaft_bore).cut(rect(8,26,0,12,41.5,42.5))
 hub=hub.cut(cyl(1.65,26,(17,5,28))).cut(cyl(3,14,(17,5,45)))
 nut_pocket=hex_prism(5.9,11.9,(17,5,25))
 hub=hub.cut(nut_pocket)
 printed_screw=hub.fuse(male).clean()
 add('Printed 20 mm lead screw with integral shaft clamp',printed_screw,'#e8b84a','rotor',True)
 add('M3x12 shaft clamp bolt',bolt(1.45,12,2.75,3,(17,5,33)),'#94a3b8','rotor',explodeKind='clampBolt')
 clamp_nut=hex_prism(5.5,2.4,(17,5,34.5)).cut(cyl(1.55,2.6,(17,5,34.4)))
 add('M3 shaft clamp hex nut',clamp_nut,'#b7c8d5','rotor',explodeKind='clampNut')
elif not Z_SUPPORT:
 coupling=xcyl(9.5,25,9).cut(xcyl(2.55,15,8)).cut(xcyl(4.05,13,22))
 for x in [14,29]:coupling=coupling.cut(cyl(1.55,12,(x,-10,SCREW_Z),(0,1,0)))
 add('5 to 8 mm rigid coupling reference',coupling,'#86b9d4','rotor')
if Z_SUPPORT:exec(compile((ROOT/'experiments/t8-leadscrew/support_6805.py').read_text(),'t8-6805','exec'),globals())
if not PRINTED:add(f'T8x8 threaded rod {T8_LENGTH:g} mm',xcyl(4,T8_LENGTH,ROD_START),'#b7c8d5','rotor')
bearings=[]
for x in STATIONS:
 for sign in [-1,1]:
  c=(x,sign*(24*math.sqrt(3)/2+WIDEN),SCREW_Z+12);u=(0,sign*.5,-math.sqrt(3)/2)
  bearings.append(dict(station=x,kind='upper',sign=sign,center=c,axis=u))
 for y in lower_positions(x):
  sign=-1 if WIDTH>1 and y<0 else 1
  bearings.append(dict(station=x,kind='lower',sign=sign,center=(x,y,SCREW_Z-24),axis=(0,sign,0)))
def snap_local(c,u):return cq.Plane(origin=c,xDir=(1,0,0),normal=u)
def local_box(c,u,xa,xb,ya,yb,ta,tb):
 return cq.Workplane(snap_local(c,u)).center((xa+xb)/2,(ya+yb)/2).workplane(offset=ta).rect(xb-xa,yb-ya).extrude(tb-ta).val()
def axle_slot(c,u):
 # Tapered through-slot, with a round end to avoid a sharp flexing root.
 plane=snap_local(c,u)
 def wire(t,half):
  pts=[plane.toWorldCoords((x,y,t)) for x,y in [(-half,-4),(half,-4),(half,4),(-half,4)]]
  return cq.Wire.makePolygon(pts+[pts[0]])
 slot=cq.Solid.makeLoft([wire(SNAP['tip_t']-.1,SNAP['tip_slot_width']/2),wire(SNAP['head_back_t']-.55,SNAP['head_slot_width']/2),wire(9,SNAP['slot_width']/2)],ruled=True)
 v=plane.yDir.toTuple()
 return slot.fuse(cyl(SNAP['slot_width']/2,8,at(at(c,u,9),v,-4),v))
def snap_pin(c,u,compression=0,printed=False):
 # The widest shoulder sits 0.25 mm beyond the bearing face. A long taper
 # narrows toward the extended 30-degree tip; the bearing journal is coaxial.
 back=SNAP['head_back_t'];tip=SNAP['tip_t'];bend=SNAP['bend_start_t'];root=SNAP['root_t']
 shaft=cyl(2.4,12.5-back,c,u,back)
 head=cyl(3.2,.55,c,u,back-.55).fuse(cq.Solid.makeCone(2.3,3.2,back-.55-tip,cq.Vector(*at(c,u,tip)),cq.Vector(*u)))
 head=head.intersect(local_box(c,u,-3.4,3.4,-1.2,1.2,tip-.1,back+.05))
 pin=shaft.fuse(head).cut(axle_slot(c,u)).clean()
 k=math.tan(math.radians(SNAP['tip_bend_degrees']))
 n=(0,math.copysign(math.sqrt(3)/2,u[1]),.5) if abs(u[2])>.01 else (0,0,-1)
 straight=pin.intersect(local_box(c,u,-4,4,-4,4,bend,13))
 end=pin.intersect(local_box(c,u,-4,4,-4,4,tip-.2,bend))
 cu=sum(c[i]*u[i] for i in range(3))+bend
 rows=[[float(i==j)+k*n[i]*u[j] for j in range(3)]+[-k*n[i]*cu] for i in range(3)]
 return straight.fuse(end.transformGeometry(cq.Matrix(rows+[[0,0,0,1]]))).clean()
def inner_race_seat(shape,c,u):
 # Ø7.4 fixed inner-race land; clearance behind it frees the split prongs.
 # Open the entire Ø17 bearing insertion corridor, removing the former lip.
 start=-12 if abs(u[2])<.01 else -25
 result=shape.cut(cyl(8.5,4.5-start,c,u,start)).fuse(cyl(3.7,2.6,c,u,2.5))
 return result.cut(cyl(2.7,8.5,c,u,2.5)).clean()
def shared_carrier(support_top=21., chamfer_support=True):
 a,b=STATIONS[0]-18-ADJUST_REAR_SHIFT,STATIONS[-1]+5
 body=rect(a,b,wide(14),wide(32),8,20).fuse(rect(a,b,wide(-32),wide(-20),8,20))
 for x in STATIONS:
  shift=ADJUST_REAR_SHIFT if x==STATIONS[0] else ADJUST_FRONT_SHIFT
  body=body.fuse(rect(x-15-shift,x-9-shift,wide(-32),wide(32),8,20))
  for bearing in bearings:
   if bearing['kind']!='lower' or bearing['station']!=x:continue
   cy=bearing['center'][1];sign=bearing['sign'];end=wide(16) if sign>0 else wide(-22)
   ya,yb=sorted([cy+sign*3.3,end])
   block=rect(x-5,x+5,ya,yb,8,support_top)
   # A 1 mm reinforcement rises from the rails with 45-degree shoulders.
   # Apply before the bearing relief so the outer-ring corridor stays open.
   if chamfer_support and support_top>20:
    block=cq.Workplane(obj=block).edges('>Z').chamfer(support_top-20).val()
   body=body.fuse(block)
 for x,y in ADJUST_CENTERS:
  body=body.cut(cyl(3.2,10.5,(x,y,9.5))).cut(cyl(2.7,13,(x,y,7)))
  body=body.cut(cq.Solid.makeCone(3.2,3.6,.6,cq.Vector(x,y,19.4),cq.Vector(0,0,1)))
 for b in bearings:
  if b['kind']=='lower':body=inner_race_seat(body,b['center'],b['axis'])
 return relieve_tracks(body)
def supported_ledge(xa,xb,inner,outer,inner_bottom,top,sign):
 pts=[(sign*wide(inner),inner_bottom),(sign*wide(outer),inner_bottom-(outer-inner)),(sign*wide(outer),top),(sign*wide(inner),top)]
 shape=prism(pts,xa,xb)
 BEARING_UNDERSIDES.append(dict(shape=shape,x_mm=[xa,xb],side=sign,inner_y_mm=wide(inner),outer_y_mm=wide(outer),inner_bottom_z_mm=inner_bottom,minimum_angle_degrees=45))
 return shape
frame=base.fuse(rect(STATIONS[0]-6,STATIONS[-1]+6,wide(34),wide(40),5,61),rect(STATIONS[0]-6,STATIONS[-1]+6,wide(-40),wide(-34),5,61))
for side in [-1,1]:
 ya,yb=sorted([wide(side*34),wide(side*40)])
 wall=cq.Workplane('XZ',origin=(0,yb,0)).polyline([(6,5),(EXIT_X-6,5),(EXIT_X-6,50),(69,50),(35,20),(6,12)]).close().extrude(yb-ya).val()
 frame=frame.fuse(wall)
for b in bearings:
 if b['kind']!='upper':continue
 x=b['station'];sign=b['sign'];c=b['center'];u=b['axis']
 frame=frame.fuse(supported_ledge(x-6,x+6,21,37,BEARING_SUPPORT_BOTTOM,61,sign))
 # Trim the rounded root boss to the same roof: its lower arc would otherwise
 # protrude beneath the slope and seed inaccessible support trees.
 boss=cyl(6,14.2,c,u,3.3)
 roof=prism([(sign*wide(10),54),(sign*wide(45),19),(sign*wide(45),80),(sign*wide(10),80)],x-7,x+7)
 frame=frame.fuse(boss.intersect(roof))
# Four top-entry bolts pull a single guided carrier upward. A continuous
# channel permits insertion from the exit after the carriage is removed.
for x,y in ADJUST_CENTERS:
 ya,yb=(wide(20),wide(35)) if y>0 else (wide(-35),wide(-20))
 frame=frame.fuse(supported_ledge(x-9,x+7,20,35,43,ADJUST_SHELF_TOP,1 if y>0 else -1))
 frame=frame.cut(cyl(2.7,25,(x,y,25))).cut(cyl(5.2,90,(x,y,ADJUST_SHELF_TOP)))
for sign in [-1,1]:
 ya,yb=(wide(20),wide(35)) if sign>0 else (wide(-35),wide(-20))
 frame=frame.fuse(rect(STATIONS[0]-22-ADJUST_REAR_SHIFT,STATIONS[0]-18.3-ADJUST_REAR_SHIFT,ya,yb,5,32))
 ya,yb=(wide(32.3),wide(35)) if sign>0 else (wide(-35),wide(-32.3))
 frame=frame.fuse(rect(STATIONS[0]-18.3-ADJUST_REAR_SHIFT,STATIONS[-1]+6,ya,yb,5,27.5))
frame=frame.cut(rect(STATIONS[0]-18.3-ADJUST_REAR_SHIFT,STATIONS[-1]+5.3,wide(-32.3),wide(32.3),6,27.5))
clearance=cq.Solid.makeLoft([section_wire(TAIL_HOME-.2,16.8),section_wire(EXIT_X+STROKE+1,16.8)],ruled=True)
frame=frame.cut(clearance)
# Rear lid mounts grow from the motor wall on 45-degree undersides.
# Root overlap is 2 mm into the 6 mm motor face; outward widening slopes too.
MOTOR_LID_GUSSETS=[]
def motor_lid_gusset(sign):
 inner=max(wide(21),22.5) if Z_SUPPORT else wide(21);outer=HALF_WIDTH;motor_half=max(wide(26),34.5) if PRINTED else max(wide(26),inner+1) if Z_SUPPORT else wide(26)
 root_z=37-(outer-motor_half)
 def wire(x):
  rise=x-4
  points=[(inner,root_z+rise),(motor_half,root_z+rise),(outer,root_z+rise+outer-motor_half),(outer,LID_Z),(inner,LID_Z)]
  vs=[cq.Vector(x,sign*y,z) for y,z in points]
  return cq.Wire.makePolygon(vs+[vs[0]])
 return cq.Solid.makeLoft([wire(4),wire(17)],ruled=True),root_z,motor_half
for x,y in LID_FIXINGS:
 if x==12:
  sign=1 if y>0 else -1;gusset,root_z,motor_half=motor_lid_gusset(sign)
  frame=frame.fuse(gusset)
  MOTOR_LID_GUSSETS.append(dict(shape=gusset,sign=sign,root_z=root_z,motor_half=motor_half,inner_y=max(wide(21),22.5) if Z_SUPPORT else wide(21),center=(x,y,LID_Z)))
 else:frame=frame.fuse(rect(x-5,x+5,y-5,y+5,51,LID_Z))
 frame=frame.cut(ridge_hole(3,12,(x,y,LID_Z),(0,0,-1)))
# External side bosses and side attachment holes are removed.
for x,y in ADJUST_CENTERS:frame=frame.cut(cyl(5.2,90,(x,y,ADJUST_SHELF_TOP)))
for x,y in LID_FIXINGS:frame=frame.cut(ridge_hole(3,12,(x,y,LID_Z),(0,0,-1)))
lid=rect(6.3,EXIT_X-9,-HALF_WIDTH,HALF_WIDTH,LID_Z,LID_Z+4)
for x,y in LID_FIXINGS:
 # Clearance in the lid allows it to clamp; its receiving base pilot has ribs.
 # Recessed button heads stay below the original motor-mount height.
 lid=lid.cut(cyl(1.7,6,(x,y,LID_Z-1))).cut(cyl(3.2,2,(x,y,66.2)))
for x,y in LID_MOUNTS:
 lid=lid.cut(mount_pilot((x,y,68),(0,0,-1),4))
 MOUNT_SEATS.append(dict(host=LID_NAME,center=(x,y,68),axis=(0,0,-1),depth=4,kind='lid'))
if PRINTED or Z_SUPPORT:lid=lid.cut(cyl(3,6,(17,5,LID_Z-1)))
if Z_SUPPORT:lid=lid.cut(cyl(3,6,(49,6.5,LID_Z-1)))
for x,y in ADJUST_CENTERS:lid=lid.cut(cyl(3,6,(x,y,LID_Z-1)))
# Through pilot seats accept short M3 inserts from the underside of the base.
for x,y in BASE_MOUNT_HOLES:
 frame=frame.cut(mount_pilot((x,y,0),(0,0,1),5))
 MOUNT_SEATS.append(dict(host=BASE_NAME,center=(x,y,0),axis=(0,0,1),depth=5,kind='base'))
# Complete bearing reliefs, mounting pilots and clearance channels before
# planning any volume-reduction windows. Lightening is the final solid pass.
for x in STATIONS:frame=frame.cut(rect(x-8.7,x+8.7,wide(-30),wide(30),56,76))
for b in bearings:
 if b['kind']=='upper':frame=inner_race_seat(frame,b['center'],b['axis'])
frame=relieve_tracks(frame)
chassis_print_without_pins=frame.clean();lid_print=lid
for seat in MOUNT_SEATS:
 host=chassis_print_without_pins if seat['kind']=='base' else lid_print
 seat['open_bottom']=host.intersect(cyl(1.45,.1,seat['center'],seat['axis'],seat['depth'])).Volume()<.01
 cavity=cyl(2.32,4,seat['center'],seat['axis'])
 if seat['kind']=='base':frame=frame.cut(cavity)
 else:lid=lid.cut(cavity)
chassis_without_pins=frame.clean();carrier_print_without_pins=shared_carrier();carrier_without_pins=carrier_print_without_pins
# The viewer depicts the installed cavity after heat setting; the STL retains
# the undersized printed pilot. The displaced annulus is checked explicitly.
for x,y in ADJUST_CENTERS:carrier_without_pins=carrier_without_pins.cut(cyl(3.57,9.5,(x,y,10.5)))
def with_pins(shape,kind,compression=0,printed=False):
 for b in bearings:
  if b['kind']==kind:shape=shape.fuse(snap_pin(b['center'],b['axis'],compression,printed=printed))
 return shape.clean()
chassis_shape=with_pins(chassis_without_pins,'upper');carrier_shape=with_pins(carrier_without_pins,'lower')
add(BASE_NAME,chassis_shape,'#475b70',printed=True,freeShape=with_pins(chassis_print_without_pins,'upper',printed=True),snapBearings=[b for b in bearings if b['kind']=='upper'])
add(CARRIER_NAME,carrier_shape,'#748aa0',printed=True,freeShape=with_pins(carrier_print_without_pins,'lower',printed=True),adjustIndex=0,explodeKind='block',snapBearings=[b for b in bearings if b['kind']=='lower'])
add(LID_NAME,lid,'#607d91',printed=True,freeShape=lid_print,explodeKind='lid')
for j,seat in enumerate(MOUNT_SEATS):
 name=f"M3 {seat['kind']} mounting insert {j+1}";seat['insert_name']=name
 add(name,ring(2.3,1.5,4,seat['center'],seat['axis']),'#d8ad4c',heatSet=True,mountHost=seat['host'],**({'explodeKind':'lid'} if seat['kind']=='lid' else {}))
for j,(x,y) in enumerate(LID_FIXINGS):
 name=f'M3x12 button-head lid bolt {j+1}'
 add(name,bolt(1.45,12,2.85,1.65,(x,y,54.2)),'#94a3b8',explodeKind='lidBolt')
 thread_joint(BASE_NAME,name,3,12,(x,y,LID_Z),(0,0,-1))
for j,(x,y) in enumerate(ADJUST_CENTERS):
 add(f'M5x40 carrier adjustment bolt {j+1}',bolt(2.45,40,4.25,5,(x,y,8)),'#91a7ba',explodeKind='adjustBolt')
 add(f'M5 adjustment washer {j+1}',ring(5,2.65,1,(x,y,ADJUST_SHELF_TOP)),'#b7c8d5',explodeKind='adjustWasher')
 add(f'M5 heat-set insert {j+1}',ring(3.55,2.5,9.5,(x,y,10.5)),'#d8ad4c',adjustIndex=0,explodeKind='block',heatSet=True)
for i,b in enumerate(bearings):
 c=b['center'];u=b['axis'];extra=dict(station=b['station'],explodeX=(-33 if b['kind']=='upper' else -45) if b['station']==STATIONS[0] else 55);extra.update(dict(adjustIndex=0) if b['kind']=='lower' else {});tag=f'{b["kind"]} {b["station"]:g}'+(f' {b["sign"]:+d}' if b['kind']=='upper' or WIDTH>1 else '')
 add('625ZZ '+tag,ring(8,2.5,5,c,u,-2.5),'#d9e2e9','guide',bearing=True,axis=list(u),center=list(c),explodeKind='bearing',explodeAxis=list(u),explodeNormal=[0,b['sign']*math.sqrt(3)/2,.5] if b['kind']=='upper' else [0,0,-1],**extra)
if not PRINTED:
 flange=xcyl(5,11.5,NUT_HOME-11.5).fuse(xcyl(11,3.5,NUT_HOME)).cut(xcyl(4.1,17,NUT_HOME-12))
 for y,z in nut_holes:flange=flange.cut(xcyl(1.75,5,NUT_HOME-.5,y,z))
 add('T8x8 brass flange nut',flange,'#dfb84b','carriage')
 for i,(y,z) in enumerate(nut_holes):
  add(f'M3x12 flange bolt {i+1}',bolt(1.45,12,2.75,3,(NUT_HOME-8.5,y,z),AXIS),'#9cafbf','carriage')
  thread_joint('Hollow triangular carriage',f'M3x12 flange bolt {i+1}',3,8,(NUT_HOME,y,z),(-1,0,0))
def window_spans(lo,hi,protected,minimum=8,maximum=34,rib=MIN_WINDOW_WEB):
 """Complement complete feature bands; skip narrow gaps instead of clipping windows."""
 spans=[]
 for a,b in sorted(protected):
  a=max(lo,a);b=min(hi,b)
  if b<=a:continue
  if spans and a<=spans[-1][1]:spans[-1]=(spans[-1][0],max(b,spans[-1][1]))
  else:spans.append((a,b))
 free=[];cursor=lo
 for a,b in spans+[(hi,hi)]:
  if a-cursor>=minimum:
   free.extend((x,y) for x,y in bays(cursor,a,maximum,rib) if y-x>=minimum)
  cursor=max(cursor,b)
 return free

def plan_windows(name,xspans,yspans,zlo,zhi,side_axis=False):
 """Create whole rounded windows on XY, or XZ for side walls. No clipped fragments."""
 cuts=[];windows=[]
 for xa,xb in xspans:
  for ya,yb in yspans:
   if side_axis:
    # A 45-degree pitched roof closes progressively instead of bridging a flat top.
    rise=(xb-xa)/2
    assert rise<=yb-ya-1
    cut=cq.Workplane('XZ',origin=(0,zhi,0)).polyline([(xa,ya),(xb,ya),(xb,yb-rise),((xa+xb)/2,yb),(xa,yb-rise)]).close().extrude(zhi-zlo).val()
   else:cut=rounded_cut(xa,xb,ya,yb,zlo,zhi,3)
   cuts.append(cut);windows.append([xa,xb,ya,yb])
 WINDOW_LAYOUTS[name]=dict(plane='XZ' if side_axis else 'XY',rectangles_mm=windows,minimum_web_mm=MIN_WINDOW_WEB)
 return cuts

# FINAL LIGHTENING PASS. No feature unions or clearance cuts follow this pass.
# All printed and installed representations use the same coordinated cutters.
ybands=[(y-5.5,y+5.5) for y in GRID_Y]
ywindows=window_spans(-HALF_WIDTH+8,HALF_WIDTH-8,ybands,maximum=30)
protected_x=[(0,18)]+[(x-10,x+10) for x in STATIONS]+[(x-10,x+10) for x,y in ADJUST_CENTERS]+[(STATIONS[0]-25,STATIONS[0]-15)]
BASE_CUT_GUARDS=[rect(a,b,-HALF_WIDTH-1,HALF_WIDTH+1,-1,70) for a,b in protected_x]
# Dedicated floor access below each adjustment shelf / bearing block lets
# supports reach the bed and lets pliers enter from below. Reserve full bands
# around these openings before laying out any other floor windows.
# Keep the full insert-seat bands on wide bases too: for 2x the access
# opening sits slightly inboard of the bolt, between the 31 mm grid columns.
access_candidates=[max(a,min(wide(21),b-11)) for a,b in ywindows if a>0 and b-a>=11-1e-6]
assert access_candidates, 'No 11 mm support access corridor between mount rows'
access_y=min(access_candidates,key=lambda a:abs(a-wide(21)))
SUPPORT_ACCESS=[(x-17-(ADJUST_REAR_SHIFT if x==STATIONS[0] else ADJUST_FRONT_SHIFT),x+6,*sorted([sign*access_y,sign*(access_y+11)])) for x in STATIONS for sign in [-1,1]]
assert all(not(a-4<x<b+4 and c-4<y<d+4) for a,b,c,d in SUPPORT_ACCESS for x,y in BASE_MOUNT_HOLES), 'Support access cuts an insert seat'
access_bands=[(a-6,b+6) for a,b,c,d in SUPPORT_ACCESS]
floor_x=window_spans(8,EXIT_X-8,protected_x+access_bands+[(x-5.5,x+5.5) for x in GRID_X])
floor_cuts=plan_windows('base_floor',floor_x,ywindows,-1,5.1)
access_cuts=[rounded_cut(a,b,c,d,-1,5.1,2) for a,b,c,d in SUPPORT_ACCESS]
floor_cuts+=access_cuts
WINDOW_LAYOUTS['base_floor']['rectangles_mm']+=list(map(list,SUPPORT_ACCESS))
# These intentional floor openings are the sole exception to protected bands;
# bearing supports, shelf undersides and side guide walls remain protected.
for i,g in enumerate(BASE_CUT_GUARDS):
 for cut in access_cuts:g=g.cut(cut)
 BASE_CUT_GUARDS[i]=g
side_cuts=[]
for sign in [-1,1]:
 ya,yb=sorted([wide(sign*32),wide(sign*41)])
 for low,high,start in [(12,23,46),(36,43,70)]:
  xs=window_spans(start,EXIT_X-14,protected_x,maximum=2*(high-low-2),rib=8)
  side_cuts+=plan_windows(f'base_side_{sign}_{low}',xs,[(low,high)],ya,yb,True)
lid_bands=[(x-5.5,x+5.5) for x in LID_GRID_X]+[(x-6.5,x+6.5) for x,y in LID_FIXINGS]+[(x-6,x+6) for x,y in ADJUST_CENTERS]
if PRINTED or Z_SUPPORT:lid_bands.append((11,23))
if Z_SUPPORT:lid_bands.append((43,55))
lid_x=window_spans(14.3,EXIT_X-17,lid_bands,maximum=36)
lid_cuts=plan_windows('lid',lid_x,ywindows,63,69)
base_before_lightening=chassis_print_without_pins
chassis_print_without_pins=lighten(chassis_print_without_pins,floor_cuts,'base_floor')
chassis_print_without_pins=lighten(chassis_print_without_pins,side_cuts,'base_sides')
for cut in BRACE_CUTS:chassis_print_without_pins=chassis_print_without_pins.cut(cut)
base_after_lightening=chassis_print_without_pins
base_cuts=floor_cuts+side_cuts+BRACE_CUTS;CUTOUTS['base']=base_cuts
before=base_before_lightening.Volume();after=base_after_lightening.Volume()
LIGHTENING['base']=dict(before_mm3=before,after_mm3=after,removed_mm3=before-after,reduction_percent=100*(before-after)/before,cutout_count=len(base_cuts))
if CARRIAGE_CUTS:beam=lighten(beam,CARRIAGE_CUTS,'carriage')
lid_print=lighten(lid_print,lid_cuts,'lid')
for part in parts:
 cutters=base_cuts if part['name']==BASE_NAME else lid_cuts if part['name']==LID_NAME else CARRIAGE_CUTS if part['name']=='Hollow triangular carriage' else []
 if not cutters:continue
 for field in ['shape','freeShape']:
  if field not in part:continue
  for cut in cutters:part[field]=part[field].cut(cut)
  part[field]=part[field].clean()
  assert part[field].isValid() and len(part[field].Solids())==1,(part['name'],field,'final cutouts disconnected solid')
chassis_shape=next(p['shape'] for p in parts if p['name']==BASE_NAME)
lid=next(p['shape'] for p in parts if p['name']==LID_NAME)
for cut in base_cuts:chassis_without_pins=chassis_without_pins.cut(cut)
for seat in MOUNT_SEATS:
 host=chassis_print_without_pins if seat['kind']=='base' else lid_print
 seat['open_bottom']=host.intersect(cyl(1.45,.1,seat['center'],seat['axis'],seat['depth'])).Volume()<.01

def explosion_offset(p,fraction):
 t=max(0.,min(1.,(fraction-.2)/.8))
 def ramp(a,b):return max(0.,min(1.,(t-a)/(b-a)))
 v=[0.,0.,0.]
 if p.get('explodeKind')=='lidBolt':return [0,0,35*min(1.,fraction/.08)]
 if p.get('explodeKind')=='lid':return [0,(90+2*WIDEN)*max(0,min(1,(fraction-.14)/.06)),18*max(0,min(1,(fraction-.08)/.06))]
 if p['group']=='carriage':v[0]=CARRIAGE_WITHDRAWAL*ramp(0,.2)+(60*ramp(.7,.8) if PRINTED else 0)
 if p['name'].startswith('M3x10 motor bolt'):v[0]=35*ramp(.2,.3);v[2]=80*ramp(.3,.45)
 if p['group'] in ['motor','rotor']:v[0]=-(ROD_END+28)*ramp(.3,.45)
 if p.get('explodeKind')=='clampBolt':v[2]+=30*ramp(.45,.53)
 if p.get('explodeKind')=='clampNut':v[2]-=25*ramp(.45,.53)
 if p.get('explodeKind')=='axle':
  v=[-(55 if 'adjustIndex' in p else 25)*q*ramp(.45,.53) for q in p['explodeAxis']]
  if 'adjustIndex' in p:v[0]-=20*ramp(.53,.6)
  else:v[2]+=60*ramp(.53,.6)
 if p.get('explodeKind')=='adjustBolt':v[2]=70*ramp(.45,.6)
 if p.get('explodeKind')=='adjustWasher':v[2]=17*ramp(.72,.8)
 if p.get('explodeKind')=='block':v=[(EXIT_X-40)*ramp(.82,.9),-(85+2*WIDEN)*ramp(.9,.95),2.5*ramp(.8,.82)+60*ramp(.95,1)]
 if p.get('explodeKind')=='bearing':
  v=[-SNAP['bearing_release_mm']*p['explodeAxis'][i]*ramp(.62,.68) for i in range(3)]
  # Lift wide lower bearings clear of the carrier's retained axle heads
  # before the carrier slides sideways beneath their parked positions.
  if 'adjustIndex' in p:v[2]+=(20 if WIDTH>1 else 14 if PRINTED else 22)*ramp(.68,.72)
  v[0]+=p['explodeX']*ramp(.72,.8)
 if p['name'].startswith('M3x12 flange bolt'):v[0]+=75*ramp(.8,.9)
 if p['name']=='T8x8 brass flange nut':v[0]+=60*ramp(.9,1)
 if Z_SUPPORT:
  kind=p.get('explodeKind')
  if kind=='sharedMotorBolt':v=[6*ramp(.2,.25)+30*ramp(.3,.35)+40*ramp(.4,.45),0,120*ramp(.35,.4)+80*ramp(.45,.5)]
  if p['group']=='motor' or p['name']=='NEMA17 5 mm D shaft':v=[-(ROD_END+28)*ramp(.5,.53),0,0]
  elif p['group']=='rotor' or kind in ['supportHousing','supportBearing']:
   v=[30*ramp(.3,.35),0,120*ramp(.35,.4)]
   if kind=='supportHousing':v[0]+=85*ramp(.53,.6)
   if kind=='supportBearing':v[0]+=55*ramp(.6,.62)

 return v
def snap_compression(fraction):
 t=max(0.,min(1.,(fraction-.2)/.8))
 return SNAP['compression']*max(0,min(1,(t-.6)/.02, (.72-t)/.02))
EXPLODE_KEYS=sorted(set([0,.08,.14,.2]+[round(.2+.8*t,6) for t in [0,.2,.225,.25,.3,.35,.4,.45,.5,.53,.6,.62,.68,.7,.72,.8,.82,.9,.95,1]]))
for p in parts:p['explodeKeyframes']=[dict(t=t,offset=explosion_offset(p,t)) for t in EXPLODE_KEYS]
print('Built',len(parts),'parts',flush=True)

def overlap(a,b):
 aa=a.BoundingBox();bb=b.BoundingBox()
 if any(getattr(aa,k+'max')<=getattr(bb,k+'min')+1e-7 or getattr(bb,k+'max')<=getattr(aa,k+'min')+1e-7 for k in 'xyz'):return 0.
 return a.intersect(b).Volume()
def pose(p,travel=0,adjustment=(1,)):
 s=p['shape']
 if p['group']=='rotor':s=s.rotate((0,0,SCREW_Z),(1,0,SCREW_Z),-travel*360/LEAD)
 if p['group']=='carriage':s=s.translate((travel,0,0))
 if 'adjustIndex' in p:s=s.translate((0,0,adjustment[p['adjustIndex']]-1))
 return s
COMPRESSED_SUPPORTS={}
def compressed_support(p,compression):
 key=(p['name'],round(compression,6))
 if key not in COMPRESSED_SUPPORTS:
  lower=p['name']==CARRIER_NAME
  COMPRESSED_SUPPORTS[key]=with_pins(carrier_without_pins if lower else chassis_without_pins,'lower' if lower else 'upper',compression)
 return COMPRESSED_SUPPORTS[key]
def exploded_pose(p,t):
 local=max(0,min(1,(t-.2)/.8));distance=CARRIAGE_WITHDRAWAL*max(0,min(1,local/.2))
 s=pose(p,distance if p['group']=='rotor' else 0)
 compression=snap_compression(t)
 if compression and p.get('snapBearings'):
  s=compressed_support(p,compression)
 return s.translate(tuple(explosion_offset(p,t)))

def verify_print_mesh(path):
 import struct,collections
 raw=path.read_bytes();count=struct.unpack_from('<I',raw,80)[0]
 assert len(raw)==84+50*count,('STL length',path.name)
 edges=collections.Counter();winding=collections.Counter();volume6=0
 for row in struct.iter_unpack('<12fH',raw[84:]):
  a,b,c=[tuple(row[i:i+3]) for i in [3,6,9]]
  u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
  cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  assert any(cross),('Degenerate triangle',path.name)
  volume6+=a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0])
  for x,y in [(a,b),(b,c),(c,a)]:
   key=tuple(sorted([x,y]));edges[key]+=1;winding[key]+=1 if x<y else -1
 assert all(n==2 for n in edges.values()) and all(n==0 for n in winding.values()),('Non-manifold STL',path.name)
 assert volume6>0,('Inverted STL',path.name)
 return dict(file=path.name,triangles=count,watertight=True,consistently_oriented=True,volume_mm3=volume6/6)

def model_source_hash():
 source=pathlib.Path(__file__).read_bytes()
 if not PRINTED:source+=(ROOT/'experiments/t8-leadscrew/support_6805.py').read_bytes()
 if Z_SUPPORT:source+=(ROOT/'experiments/bearing-supported-screw/holder_geometry.py').read_bytes()
 return hashlib.sha256(source).hexdigest()

def export(report=None):
 from OCP.BRepTools import BRepTools
 scene=[];print_checks=[];stls=OUT/'stl';stls.mkdir(exist_ok=True)
 for obsolete in stls.glob('*.stl*'):obsolete.unlink()
 for p in parts:
  BRepTools.Clean_s(p['shape'].wrapped)
  vs,ts=p['shape'].tessellate(.06,.16)
  row={k:v for k,v in p.items() if k not in ['shape','freeShape']};row.update(vertices=[v.toTuple() for v in vs],triangles=ts)
  if p['printed']:
   name=p['name'].lower().replace(' ','_')+'.stl';row['stl']='stl/'+name+'.gz'
   dest=stls/name;BRepTools.Clean_s(p.get('freeShape',p['shape']).wrapped);cq.exporters.export(p.get('freeShape',p['shape']),str(dest),tolerance=.025,angularTolerance=.12)
   print_checks.append(verify_print_mesh(dest))
   with gzip.open(str(dest)+'.gz','wb') as f:f.write(dest.read_bytes())
  scene.append(row)
 source_hash=model_source_hash()
 data=dict(experiment=EXPERIMENT,revision=37 if Z_SUPPORT else 35,screwSupport='6805' if Z_SUPPORT else 'standard',support6805=SUPPORT_6805 if Z_SUPPORT else None,carrierShoulders={"body_top_z_mm":21,"rail_top_z_mm":20,"rise_mm":1,"chamfer_mm":1,"previous_top_z_mm":24.5,"lowered_mm":3.5,"bearing_seats_and_axles_preserved":True},motorLidBraces={'count':2,'minimum_underside_angle_degrees':45,'root_overlap_mm':2,'x_span_mm':[4,17],'mount_centers_mm':[list(q['center']) for q in MOTOR_LID_GUSSETS]},outputBoltAccess=OUTPUT_BOLT_ACCESS,printability={'orientation':'base floor on bed, Z up','side_window_roof_degrees':45,'support_access_xy_mm':SUPPORT_ACCESS,'motor_foot_filled':True},cutoutPlanning={'stage':'final post-processing after all features','minimum_web_mm':MIN_WINDOW_WEB,'layouts':WINDOW_LAYOUTS},bearingSupportFeet={'inner_bottom_z_mm':BEARING_SUPPORT_BOTTOM,'underside_angle_degrees':45,'adjustment_shelf_top_z_mm':ADJUST_SHELF_TOP,'adjustment_bolt':'M5x40 ISO 4762 socket head','adjustment_head_diameter_mm':8.5,'count':4},guideBearingCount=len(bearings),lowerBearingCount=LOWER_COUNT,lowerBearingY=[lower_positions(x) for x in STATIONS],carrierInserts=INSERT,shaftClamp=CLAMP if PRINTED else None,lightening=LIGHTENING,motorBraces={'rear_x_mm':-36,'length_mm':42,'width_mm':12,'motor_side_gap_mm':1.5} if PRINTED else None,widthMultiple=WIDTH,outputPlateWidth=OUTPUT_WIDTH,upperBearingSpan=24*math.sqrt(3)+2*WIDEN,baseWidth=2*HALF_WIDTH,stroke=STROKE,lead=LEAD,sizingBasis='screw_length' if not PRINTED else 'travel',screwLength=T8_LENGTH if not PRINTED else None,screwStartX=ROD_START if not PRINTED else 9,nutAxialBounds=[NUT_HOME-NUT_REAR,NUT_HOME+NUT_FRONT] if not PRINTED else None,motor='NEMA17',axisOrigin=[0,0,SCREW_Z],modelSourceSha256=source_hash,parts=scene,stations=STATIONS,adjustmentRange=[0,1],adjustmentHome=[1],carrierName=CARRIER_NAME,lidName=LID_NAME,lidFixings=LID_FIXINGS,lidMounts=LID_MOUNTS,sideMounts=SIDE_MOUNTS,attachmentPilots=ATTACH_PILOTS,envelopeHeight=68,lidTopZ=68,snapAxle=SNAP,bearingAxle=AXLE_SPEC,retainingTracks=[],retainingRailSize=[0,0],bearingRunningFaces=TRACKS,explosionPrelude=.2,carriageWithdrawal=CARRIAGE_WITHDRAWAL,adjustmentBoltCenters=ADJUST_CENTERS,adjustmentRearOffsetMm=ADJUST_REAR_SHIFT,adjustmentFrontOffsetMm=ADJUST_FRONT_SHIFT,bearingSeat={'land_diameter_mm':7.4,'relief_diameter_mm':17,'relief_depth_mm':2},baseName=BASE_NAME,printedDrive=PRINTED,threadBands=THREAD_BANDS if PRINTED else [],screwEndX=ROD_END,printedScrewDiameter=20 if PRINTED else None,exitPlaneX=EXIT_X,tailHomeX=TAIL_HOME,guideEndX=GUIDE_END,nutHomeX=NUT_HOME,homeTravel=0,baseBounds=[-36 if PRINTED else BASE_REAR,EXIT_X,-HALF_WIDTH,HALF_WIDTH,0,5],outputMount={'pitch_mm':[31,31],'outer_pitch_mm':[max(GRID_Y)-min(GRID_Y),31] if WIDTH>1 else None,'face_size_mm':[OUTPUT_WIDTH,42],'hole_centers_yz_mm':output_holes,'thread':'M3 three-ridge forming pilot','thread_depth_mm':8},threadProfiles=THREAD_PROFILES,cornerChamferRadialDepth=12,baseMount={'hole_centers_xy_mm':BASE_MOUNT_HOLES,'patterns':BASE_MOUNT_PATTERNS,'center_xy_mm':[26,0],'thread':'M3 heat-set insert','hole_type':'insert pilot; backing retained beneath structural feet','pilot_diameter_mm':4,'through_depth_mm':5,'entry_face':'underside','maximum_screw_entry_mm':5},mountingGrid={'pitch_mm':31,'x_mm':GRID_X,'lid_x_mm':LID_GRID_X,'y_mm':GRID_Y,'base_end_mm':EXIT_X,'base_last_row_edge_distance_mm':EXIT_X-GRID_X[-1],'lid_end_mm':EXIT_X-9,'lid_last_row_edge_distance_mm':EXIT_X-9-LID_GRID_X[-1]},mountingLayouts=MOUNT_LAYOUTS,externalMountInserts=MOUNT_INSERT,externalMountSeats=MOUNT_SEATS,explosion='Staged disassembly: carriage withdrawal, motor bolts, drive, axles, bearing packs, flange bolts and nut')
 with gzip.open(OUT/'assembly.json.gz','wt') as f:json.dump(data,f,separators=(',',':'))
 (OUT/'configuration.json').write_text(json.dumps({k:v for k,v in data.items() if k!='parts'},indent=2))
 if report:
  report['print_meshes']={'checks':print_checks,'passed':all(q['watertight'] for q in print_checks)}
  (OUT/'validation.json').write_text(json.dumps(report,indent=2))
 (OUT/'bill-of-materials.json').write_text(json.dumps({'printed_parts':[p['name'] for p in parts if p['printed']],'hardware_references':[p['name'] for p in parts if not p['printed']],'fastener_nuts':2 if Z_SUPPORT else 1 if PRINTED else 0,'shaft_clamp':CLAMP if PRINTED else None,'integral_split_axles':len(bearings),'bearing_axle_fit':AXLE_SPEC,'heat_set_inserts':4+len(MOUNT_SEATS),'carrier_heat_set_inserts':4,'heat_set_insert_spec':INSERT,'external_mount_inserts':len(MOUNT_SEATS),'external_mount_insert_spec':MOUNT_INSERT,'bearing_axle_bolts':0,'lid_fasteners':len(LID_FIXINGS),'plastic_thread_joints':len(THREAD_JOINTS),'output_mount_thread_pilots':len(OUTPUT_PILOTS),'guide_bearings':len(bearings),'screw_support_bearings':1 if Z_SUPPORT else 0,'screw_support':'6805' if Z_SUPPORT else 'standard','t8_brass_nuts':2 if Z_SUPPORT else 0 if PRINTED else 1,'note':'Z variant uses a captured second T8 flange nut and printed bolt/nut locking clamps; standard T8 uses a purchased 5-to-8 mm coupling. Hardware envelopes do not substitute for vendor drawings.'},indent=2))
 (OUT/'README.txt').write_text((f'T8 screw length: {T8_LENGTH:g} mm. Usable travel: {STROKE:g} mm. Overall retracted length: {EXIT_X+40:g} mm.\n' if not PRINTED else f'Printed screw travel: {STROKE:g} mm. Screw tip X={ROD_END:g} mm. Overall retracted length: {EXIT_X+40:g} mm.\n')+f'Width variant: {WIDTH}x. Output plate: {OUTPUT_WIDTH:g} x 42 mm. Base width: {2*HALF_WIDTH:g} mm. Upper bearing span: {24*math.sqrt(3)+2*WIDEN:.3f} mm.\n\n'+(ROOT/'experiments'/EXPERIMENT/'README.md').read_text())
 if args.quick:return
 with zipfile.ZipFile(OUT/(EXPERIMENT+'-prototype.zip'),'w',zipfile.ZIP_DEFLATED) as z:
  for f in stls.glob('*.stl'):z.write(f,'stl/'+f.name)
  for folder in ['t8-leadscrew']+(['printed-leadscrew'] if PRINTED else []):
   for f in (ROOT/'experiments'/folder).glob('*'):
    if f.is_file():z.write(f,'experiments/'+folder+'/'+f.name)
  if Z_SUPPORT:z.write(ROOT/'experiments/bearing-supported-screw/holder_geometry.py','experiments/bearing-supported-screw/holder_geometry.py')
  for name in ['configuration.json','validation.json','bill-of-materials.json','README.txt']:z.write(OUT/name,name)
 for f in stls.glob('*.stl'):f.unlink()
 print('Export complete',flush=True)
if __name__=='__main__':
 if args.quick:export();sys.exit()
 report=None
 if not args.quick:
  exec(compile((ROOT/'experiments/t8-leadscrew/validate.py').read_text(),'t8-validation','exec'),globals());report=validate()
  (OUT/'validation.json').write_text(json.dumps(report,indent=2));assert report['passed'],report
 export(report)
