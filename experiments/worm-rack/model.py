"""Standard-envelope spur-driven worm-to-compliant-rack family: NEMA17 / NEMA14, 40–150 mm.
Run from the repository: python experiments/worm-rack/model.py [--check]
The production model.py and its 12 presets are deliberately not modified.
"""
import argparse, gzip, hashlib, itertools, json, math, pathlib, sys, zipfile
import cadquery as cq
import faulthandler,signal
faulthandler.register(signal.SIGUSR1)
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
P=argparse.ArgumentParser();P.add_argument('--check',action='store_true');P.add_argument('--motor',choices=['nema17','nema14'],default='nema17');P.add_argument('--stroke',type=int,choices=[40,100,150],default=40);P.add_argument('--out');args=P.parse_args()
STROKE=args.stroke;IS14=args.motor=='nema14';MOTOR_NAME=args.motor.upper()
if args.out is None:args.out='dist/experiments/worm-rack'+('' if (args.motor,STROKE)==('nema17',40) else f'/variants/{args.motor}/{STROKE}')
ROOT=pathlib.Path(__file__).resolve().parents[2];OUT=ROOT/args.out;OUT.mkdir(parents=True,exist_ok=True)
CACHE=ROOT/f'work/worm-family-cache/{args.motor}-{STROKE}';CACHE.mkdir(parents=True,exist_ok=True)
# Reuse the tested rack and six-bearing guidance. Execute only definitions, no exports.
saved_argv=sys.argv;sys.argv=['model.py','--motor',args.motor,'--stroke',str(STROKE),'--out',str(CACHE/'baseline')]
ns={'__file__':str(ROOT/'model.py'),'__name__':'baseline'}
baseline_source=(ROOT/'model.py').read_text().split('\n# Clear obsolete generated meshes')[0]
marker='\nINSERT_OD=a.insert_od'
baseline_source=baseline_source.replace(marker,"\nCOVER_SEATS=[(CASE_LEFT+26,CASE_YMIN+5) if abs(x-(CASE_LEFT+7.5))<1e-6 and y<0 else (FRONT_STATION-20,CASE_YMIN+6) if abs(x-(CASE_RIGHT-7.5))<1e-6 and y<0 else (x,CASE_YMIN+6) if y<0 else (x,y) for x,y in COVER_SEATS]"+marker)
# Intermediate mounting cuts may split the old motor platform; fixture() rebuilds it.
baseline_source=baseline_source.replace("assert len(s.Solids())==1,(name,len(s.Solids()))","assert len(s.Solids())==1 or name=='01 Integral spring chassis',(name,len(s.Solids()))")
exec(compile(baseline_source,str(ROOT/'model.py'),'exec'),ns)
sys.argv=saved_argv
box=ns['box'];cyl=ns['cyl'];acyl=ns['acyl'];ring=ns['ring'];ycyl=ns['ycyl']
PITCH=ns['TOOTH_PITCH'];LEAD=PITCH;K=LEAD/(2*math.pi);R=11.;Y=0. if IS14 else -1.;Z=1.;RR=R-2.5;RA=R+2.;LENGTH=24.;PRELOAD=.1
AXIS=(1,0,0);ORIGIN=(0,Y,Z);ANGLE=math.radians(ns['PRESSURE_ANGLE'])
MOTOR_SIZE=ns['MOTOR_SIZE'];MOTOR_PITCH=ns['MOTOR_PITCH'];MOTOR_DEPTH=ns['MOTOR_DEPTH']
GEAR_MODULE=1.;WORM_TEETH=24;MOTOR_TEETH=14 if IS14 else 18;GEAR_RATIO=MOTOR_TEETH/WORM_TEETH
MOTOR_Y=Y;GEAR_DISTANCE=GEAR_MODULE*(WORM_TEETH+MOTOR_TEETH)/2
MOTOR_Z=Z-math.sqrt(GEAR_DISTANCE**2-(MOTOR_Y-Y)**2);MOTOR_ORIGIN=(0,MOTOR_Y,MOTOR_Z)
# Put the spur pair behind the complete swept tooth field, below the rack's spine.
GEAR_END=math.floor(ns['centers'][0]-PITCH/4-1.25*ns['MODULE']*math.tan(ANGLE)-PRELOAD-STROKE/2-1.)
MOTOR_FRONT=min(GEAR_END-24,ns['CASE_LEFT']-4+MOTOR_DEPTH);MOTOR_REAR=MOTOR_FRONT-MOTOR_DEPTH
GEAR_X=MOTOR_FRONT+18.;GEAR_WIDTH=6.;WORM_START=GEAR_X-5.;WORM_END=16.;STEM_RADIUS=7.5
END_INSERT_OD=7.;END_INSERT_LENGTH=8.;END_INSERT_PILOT=6.6;END_INSERT_RECESS=.3
END_INSERT_FACE=WORM_END-END_INSERT_RECESS;END_PILOT_START=6.7
BEARING_X=20.5;SET_X=GEAR_X-3.;SET_Y=MOTOR_Y-6.
WORM_NAME='Worm with integral 24T spur gear';MOTOR_GEAR_NAME=f'{MOTOR_TEETH}T motor spur gear';CHASSIS_NAME='Integral worm chassis'
def xcyl(r,length,x,y=Y,z=Z):return acyl(r,length,(x,y,z),AXIS)
def dshaft(r,x,length,flat):return xcyl(r,length,x,MOTOR_Y,MOTOR_Z).intersect(box(length,2*r+2,2*r+2,(x+length/2,MOTOR_Y+flat+(2*r+2)/2,MOTOR_Z)))
def spur(n,x,y,z,phase=0):
 rp=GEAR_MODULE*n/2;rb=rp*math.cos(math.radians(25));ra=rp+GEAR_MODULE;rr=rp-1.25*GEAR_MODULE
 inv=lambda r:math.sqrt(max(0,(r/rb)**2-1))-math.acos(min(1,rb/r))
 half=math.pi/(2*n)+inv(rp)-.06/rp;points=[]
 for i in range(n):
  center=2*math.pi*i/n+phase;vals=[(rr,-half),(rb,-half)]
  for j in range(1,17):
   r=rb+(ra-rb)*j/16;vals.append((r,-half+inv(r)))
  for j in range(16,-1,-1):
   r=rb+(ra-rb)*j/16;vals.append((r,half-inv(r)))
  vals.append((rr,half));points.extend([(r*math.cos(center+t),r*math.sin(center+t)) for r,t in vals])
 return cq.Workplane('YZ',origin=(x,y,z)).polyline(points).close().extrude(GEAR_WIDTH).val()
GEAR_LINE=math.atan2(MOTOR_Z-Z,MOTOR_Y-Y)
WORM_GEAR_PHASE=GEAR_LINE;MOTOR_GEAR_PHASE=GEAR_LINE+math.pi+math.pi/MOTOR_TEETH
def record(name,shape,color='#9ca3af',group='fixed',printed=False,**extra):
 assert shape.isValid() and len(shape.Solids())==1,(name,shape.isValid(),len(shape.Solids()))
 return dict(name=name,shape=shape,color=color,group=group,printed=printed,**extra)

def make_worm():
 def wire(t):
  pts=[]
  for r,sgn in [(RR-.2,-1),(RA,-1),(RA,1),(RR-.2,1)]:
   x=K*t+PITCH/2+sgn*(PITCH/4-(r-R)*math.tan(ANGLE)-.03)
   pts.append(cq.Vector(x,Y+r*math.cos(t),Z+r*math.sin(t)))
  return cq.Wire.makePolygon(pts+[pts[0]])
 turn=cq.Solid.makeLoft([wire(2*math.pi*j/64) for j in range(65)],ruled=False)
 worm=xcyl(RR,LENGTH,-LENGTH/2).fuse(*[turn.translate((j*PITCH,0,0)) for j in range(-3,3)])
 worm=worm.intersect(box(LENGTH,40,40,ORIGIN)).fuse(xcyl(STEM_RADIUS,-12-WORM_START,WORM_START),xcyl(5.5,4,12))
 # Rounded shoulders join the integral stem and insert boss to the active worm.
 for x,r in [(-12,STEM_RADIUS),(12,5.5)]:
  if abs(RR-r)<1e-6:continue
  edges=[e for e in worm.Edges() if e.geomType()=='CIRCLE' and abs(e.Center().x-x)<1e-6 and abs(e.radius()-r)<1e-6]
  assert len(edges)==1,(x,len(edges))
  worm=cq.Workplane(obj=worm).newObject(edges).fillet(min(1.2,(RR-r)*.45)).val()
 # Integral spur wheel; both ends use axial M5 inserts and bearing bolts.
 worm=worm.fuse(spur(WORM_TEETH,GEAR_X,Y,Z,WORM_GEAR_PHASE),xcyl(5.5,10,WORM_START))
 worm=worm.cut(xcyl(END_INSERT_PILOT/2,WORM_END-END_PILOT_START+.1,END_PILOT_START))
 worm=worm.cut(xcyl(END_INSERT_OD/2+.15,END_INSERT_RECESS+.1,END_INSERT_FACE))
 worm=worm.cut(xcyl(END_INSERT_PILOT/2,9.4,WORM_START-.1))
 worm=worm.cut(xcyl(END_INSERT_OD/2+.15,.4,WORM_START-.1))
 return worm.clean()

def loft(wires):
 b=BRepOffsetAPI_ThruSections(True,False);b.SetMaxDegree(3)
 for w in wires:b.AddWire(w.wrapped)
 b.Build();return cq.Solid(b.Shape())

def matched_rack(preload):
 original=ns['make_rack'](preload);warp_end=ns['centers'][-1]+10
 zone=box(warp_end*2,80,8,(0,20,17))
 section=cq.Workplane('XY').newObject([original.intersect(zone)]).section(17).val()
 ROOT_Y=ns['ROOT_Y'];RELIEF_Y=ns['RELIEF_Y']
 def warp(v,face):
  x,y=v.x,v.y;r=R+y-ns['PITCH_Y'];across=17-face
  if y>=RELIEF_Y-1e-8:return cq.Vector(x,Y+across,Z+r)
  theta=math.acos(across/r)
  t=max(0,(y-ROOT_Y)/(RELIEF_Y-ROOT_Y));blend=1-t*t*(3-2*t)
  tx=max(0,min(1,(abs(x)-(ns['centers'][-1]+4))/6));blend*=1-tx*tx*(3-2*tx)
  return cq.Vector(x+blend*K*theta,Y+across,Z+r+blend*(math.sqrt(r*r-across*across)-r))
 def layer(w,face):
  edges=[]
  for e in w.Edges():
   n=8 if e.geomType()=='CIRCLE' else 4
   edges.append(cq.Edge.makeSpline([warp(e.positionAt(j/n),face) for j in range(n+1)]))
  return cq.Wire.assembleEdges(edges)
 wires=section.Wires();outer=max(wires,key=lambda w:w.BoundingBox().xlen)
 teeth=loft([layer(outer,13+j) for j in range(9)])
 for w in wires:
  if w.BoundingBox().xlen<10:teeth=teeth.cut(cq.Solid.makeLoft([layer(w,13),layer(w,21)]))
 teeth=teeth.intersect(box(2*warp_end+4,100,100,(0,0,-29))) # Z <= 21
 keep=original.cut(box(2*warp_end,100,8.2,(0,RELIEF_Y-50,17)))
 spine_z=Z+R+RELIEF_Y-ns['PITCH_Y']
 bridge=box(2*warp_end,ns['BACK_Y']-Y+4,21-spine_z,(0,(ns['BACK_Y']+Y-4)/2,(21+spine_z)/2))
 return keep.fuse(teeth,bridge).clean()

def cached(name,fn):
 path=CACHE/(name+'.brep')
 if path.exists():return cq.Shape.importBrep(str(path))
 print('Building',name,flush=True);s=fn();s.exportBrep(str(path));return s
# Cache is local/ignored and keyed by both geometry sources.
import inspect
geometry_key={'functions':[inspect.getsource(f) for f in [make_worm,matched_rack,spur]],'motor':args.motor,'stroke':STROKE,'parameters':[PITCH,R,Y,Z,RR,RA,LENGTH,PRELOAD,ANGLE,STEM_RADIUS,WORM_START,WORM_END,GEAR_MODULE,WORM_TEETH,MOTOR_TEETH,GEAR_X,GEAR_WIDTH,WORM_GEAR_PHASE,END_INSERT_OD,END_INSERT_LENGTH,END_INSERT_PILOT,END_INSERT_RECESS,END_INSERT_FACE,END_PILOT_START]}
source_hash=hashlib.sha256(json.dumps(geometry_key,sort_keys=True).encode()+(ROOT/'model.py').read_bytes()).hexdigest()
if not (CACHE/'source-hash').exists() or (CACHE/'source-hash').read_text()!=source_hash:
 for p in CACHE.glob('*.brep'):p.unlink()
 (CACHE/'source-hash').write_text(source_hash)
worm=cached('worm',make_worm)
rack=cached('rack',lambda:matched_rack(PRELOAD))
nominal=cached('nominal-rack',lambda:matched_rack(0))
straight=cached('straight-rack',lambda:ns['make_rack'](0))
parts=[record('Matched compliant rack',rack,'#5eead4','rack',True),record(WORM_NAME,worm,'#fbbf24','worm',True,rotating=True)]
for p in ns['parts']:
 if p['group']=='rack' and p.get('embedded_host'):
  parts.append(record(p['name'],p['shape'],p['color'],'rack',embedded_host='Matched compliant rack'))
 elif p['name'].startswith(('625ZZ','M5 upper','M5x16 angled','M5 angled','M5 lower','M5x25 lower')):
  parts.append(record(p['name'],p['shape'],p['color'],'guide',**{k:p[k] for k in ['spinAxis','spinCenter','spinSign'] if k in p},**({'lowerStation':next(q['x'] for q in ns['BOTTOM'] if q['side'] in p['group'])} if p['group'].startswith('lower_') else {})))
# Preserve the guide seats and mounting interfaces; put the motor beside/below the worm.
bay=box(56,39,70,(0,-4.5,-2))
land=box(28-MOTOR_FRONT,Y+20-ns['CHASSIS_FRONT'],6,((MOTOR_FRONT+28)/2,(ns['CHASSIS_FRONT']+Y+20)/2,-26))
supports=box(8,32,30,(-18,Y+8,-14)).fuse(box(6,32,30,(31,Y+8,-14)))
supports=supports.fuse(box(29,4.8-ns['CHASSIS_FRONT'],33,(-28.5,(4.8+ns['CHASSIS_FRONT'])/2,-12.5)))
mount_clearances=[]
for x,y in ns['CHASSIS_MOUNTS']:
 clearance=cyl(6.8,27,x,y,-30)
 if y==ns['FRONT_MOUNT_Y']:clearance=clearance.fuse(ns['rect_cut'](x-2.8,x+2.8,ns['CASE_YMIN']-1,y+.8,-30,-3))
 if y==ns['FRONT_MOUNT_Y']:
  slide=cyl(6.8,21.2,x,y,-30).fuse(cyl(6.8,21.2,x+10,y,-30),box(10,13.6,21.2,(x+5,y,-19.4)),ns['rect_cut'](x-2.8,x+12.8,ns['CASE_YMIN']-1,y+.8,-30,-8.8))
  clearance=clearance.fuse(slide)
 mount_clearances.append(clearance)
 supports=supports.cut(clearance).cut(cyl(1.7,40,x,y,-30)).cut(cyl(3.5,12,x,y,0));land=land.cut(clearance)
for q in ns['BOTTOM']:
 for dz in [0,ns['SPRING_PRELOAD']]:supports=supports.cut(ycyl(5.5,60,q['x'],-30,-17+dz))
for p in ns['UPPER']:
 access=acyl(5.5,65,p['center'],p['axis'],-60)
 supports=supports.cut(access);land=land.cut(access)
REAR_SUPPORT_OFFSET=MOTOR_TEETH/2+6
REAR_SUPPORT_POINTS=[(MOTOR_FRONT+21,Y-REAR_SUPPORT_OFFSET),(MOTOR_FRONT+21,Y+REAR_SUPPORT_OFFSET)]
for x,y in REAR_SUPPORT_POINTS:land=land.cut(cyl(1.7,8,x,y,-30))
motor_holes=[(MOTOR_Y+dy,MOTOR_Z+dz) for dy in [-MOTOR_PITCH/2,MOTOR_PITCH/2] for dz in [-MOTOR_PITCH/2,MOTOR_PITCH/2]]
bracket_top=MOTOR_Z+MOTOR_PITCH/2+4;BRACKET_BOTTOM=MOTOR_Z-MOTOR_PITCH/2-4
bracket=box(5,MOTOR_PITCH+8,bracket_top-BRACKET_BOTTOM,(MOTOR_FRONT+2.5,MOTOR_Y,(bracket_top+BRACKET_BOTTOM)/2)).cut(xcyl(11.8,7,MOTOR_FRONT-1,MOTOR_Y,MOTOR_Z))
for y,z in motor_holes:bracket=bracket.cut(xcyl(1.7,7,MOTOR_FRONT-1,y,z))
def end_saddle():
 b=box(11.5,20,Z+9.5+29,(22.25,Y,(Z+9.5-29)/2)).cut(xcyl(8.15,11,17.85))
 return b.cut(xcyl(6.,2.1,16)).cut(box(12,9.6,25,(22.25,Y,Z+12.5)))
end_block=end_saddle();rear_block=end_block.mirror('YZ').translate((WORM_START+16,0,0))
def fixture(chassis):
 result=chassis.cut(bay).fuse(land,supports,bracket,end_block,rear_block)
 for clearance in mount_clearances:result=result.cut(clearance)
 # Clear motor body and the complete rotational envelopes of both spur gears.
 result=result.cut(box(MOTOR_DEPTH+.2,MOTOR_SIZE+1.6,MOTOR_SIZE+1.6,(MOTOR_FRONT-MOTOR_DEPTH/2-.1,MOTOR_Y,MOTOR_Z)))
 for n,y,z in [(WORM_TEETH,Y,Z),(MOTOR_TEETH,MOTOR_Y,MOTOR_Z)]:result=result.cut(xcyl(GEAR_MODULE*(n/2+1)+.8,GEAR_WIDTH+1.6,GEAR_X-.8,y,z))
 result=result.cut(xcyl(max(11.8,GEAR_MODULE*(MOTOR_TEETH/2+1)+.8),25,MOTOR_FRONT,MOTOR_Y,MOTOR_Z))
 result=result.cut(xcyl(STEM_RADIUS+.8,-12-(GEAR_X+GEAR_WIDTH),GEAR_X+GEAR_WIDTH))
 for a,b,r in [(WORM_START-.3,WORM_END+.3,STEM_RADIUS+.8),(GEAR_X-.8,GEAR_X+GEAR_WIDTH+.8,13.8),(-12.3,12.3,RA+.8)]:
  result=result.cut(ns['rect_cut'](a,b,Y-r,Y+r,-20,24))
 result=result.cut(xcyl(8.8,ns['CASE_RIGHT']-23+2,23))
 result=result.cut(xcyl(8.8,WORM_START-7.15-(ns['CASE_LEFT']-1),ns['CASE_LEFT']-1))
 for y,z in motor_holes:result=result.cut(xcyl(3.55,10,MOTOR_FRONT+5,y,z))
 for x,y in REAR_SUPPORT_POINTS:result=result.cut(cyl(1.7,8,x,y,-30)).cut(cyl(3.1,4,x,y,-23)).cut(cyl(1.6,40,x,y,-19))
 for x,y in ns['COVER_SEATS']:
  result=result.cut(cyl(5.3,80,x,y,-40))
  if y<0:
   result=result.cut(cyl(5.3,80,x+3,y,-40)).cut(box(3,10.6,80,(x+1.5,y,0)))
   result=result.cut(ns['rect_cut'](x-5.3,x+8.3,ns['CASE_YMIN']-1,y,-40,24))
 # Discard only tiny trimming chips outside the retained structural body.
 pieces=sorted(result.Solids(),key=lambda q:q.Volume(),reverse=True)
 assert all(q.Volume()<5 for q in pieces[1:]),[(q.Volume(),q.BoundingBox().xmin) for q in pieces]
 return pieces[0]
fixture_s=fixture(ns['base']);fixture_free=fixture(ns['base_print'])
parts.append(record(CHASSIS_NAME,fixture_s,'#475569',printed=True))
motor=box(MOTOR_DEPTH,MOTOR_SIZE,MOTOR_SIZE,(MOTOR_FRONT-MOTOR_DEPTH/2,MOTOR_Y,MOTOR_Z)).fuse(xcyl(11,2,MOTOR_FRONT,MOTOR_Y,MOTOR_Z))
for y,z in motor_holes:motor=motor.cut(xcyl(1.65,6,MOTOR_FRONT-5,y,z))
parts.append(record(f'{MOTOR_NAME} {MOTOR_SIZE:g} × {MOTOR_SIZE:g} × {MOTOR_DEPTH:g} reference',motor,'#374151','motor'))
for y,z in motor_holes:
 screw=xcyl(1.45,10,MOTOR_FRONT-5,y,z).fuse(xcyl(2.75,3,MOTOR_FRONT+5,y,z)).cut(xcyl(1.3,1.5,MOTOR_FRONT+6.5,y,z))
 parts.append(record(f'M3x10 motor screw {y} {z}',screw,'#94a3b8','motor_screws'))
parts.append(record(f'{MOTOR_NAME} D shaft',dshaft(2.5,MOTOR_FRONT+2,22,-2),'#94a3b8','motor',rotating=True,rotationCenter=MOTOR_ORIGIN,rotationFactor=-1/GEAR_RATIO))
motor_gear=spur(MOTOR_TEETH,GEAR_X,MOTOR_Y,MOTOR_Z,MOTOR_GEAR_PHASE).fuse(xcyl(6,6,GEAR_X-6,MOTOR_Y,MOTOR_Z))
motor_gear=motor_gear.cut(dshaft(2.65,GEAR_X-6.1,12.2,-2.15)).cut(ycyl(1.25,5,SET_X,MOTOR_Y-7,MOTOR_Z))
parts.append(record(MOTOR_GEAR_NAME,motor_gear,'#f59e0b','motor',True,rotating=True,rotationCenter=MOTOR_ORIGIN,rotationFactor=-1/GEAR_RATIO))
parts.append(record('M3x4 motor gear set screw',ycyl(1.2,4,SET_X,SET_Y,MOTOR_Z).cut(ycyl(.9,1.2,SET_X,SET_Y,MOTOR_Z)),'#94a3b8','motor',rotating=True,rotationCenter=MOTOR_ORIGIN,rotationFactor=-1/GEAR_RATIO))
insert=ring(END_INSERT_OD/2,2.55,END_INSERT_LENGTH,(END_INSERT_FACE-END_INSERT_LENGTH,Y,Z),AXIS)
end_bolt=xcyl(2.45,16,7.3).fuse(xcyl(4.75,5,23.3)).cut(xcyl(2.5,2.5,25.8))
for side in ['front','rear']:
 mirror=lambda q:q if side=='front' else q.mirror('YZ').translate((WORM_START+16,0,0))
 parts.append(record(f'M5 {side} axial heat-set insert',mirror(insert),'#d4a54a',side+'_insert',rotating=True,embedded_host=WORM_NAME))
 parts.append(record('625ZZ '+side+' worm support',mirror(ring(8,2.5,5,(BEARING_X,Y,Z),AXIS,-2.5)),'#cbd5e1',side+'_bearing'))
 parts.append(record('M5 '+side+' inner-race spacer 2 mm',mirror(ring(3.75,2.65,2,(16,Y,Z),AXIS)),'#94a3b8',side+'_spacer',rotating=True))
 parts.append(record('M5 '+side+' inner-race washer 0.3 mm',mirror(ring(3.75,2.65,.3,(23,Y,Z),AXIS)),'#94a3b8',side+'_fastener',rotating=True))
 parts.append(record('M5x16 '+side+' bearing bolt',mirror(end_bolt),'#94a3b8',side+'_fastener',rotating=True))

exec(compile((ROOT/'experiments/worm-rack/enclosure.py').read_text(),'worm-enclosure','exec'),globals())

# Shared CAD/viewer tracks. The motor and its pinion stay together.
def track(start,end,delta=(0,0,0),radians=0):return dict(start=start,end=end,delta=list(delta),radians=radians)
WITHDRAW=ns['CASE_RIGHT']-ns['left']+20.
worm_tracks=[track(.55,.61,(0,0,-7)),track(.82,.94,(0,0,80))]
TRACKS={
 'fixed':[],'guide':[],'tray':[],'chassis_screws':[],
 'rack':[track(.61,.82,(WITHDRAW,0,0))],
 'cover_screws':[track(0,.05,(0,0,55)),track(.05,.09,(0,-140,0))],
 'cover':[track(.09,.17,(0,0,100))],
 'motor_screws':[track(.17,.21,(5.5,0,0))],
 'motor':[track(.21,.33,(-80,0,0))],
 'front_fastener':[track(.33,.41,(55,0,0))],
 'rear_fastener':[track(.33,.41,(-55,0,0))],
 'front_bearing':[track(.41,.49,(55,0,0))],
 'rear_bearing':[track(.41,.49,(-55,0,0))],
 'front_spacer':[track(.49,.55,(40,0,0))],
 'rear_spacer':[track(.49,.55,(-40,0,0))],
 'worm':worm_tracks,
 'front_insert':worm_tracks+[track(.94,1,(14,0,0))],
 'rear_insert':worm_tracks+[track(.94,1,(-14,0,0))],
}
STAGES=[dict(start=a,end=b,label=t) for a,b,t in [
 (0,.09,'Remove and park lid screws'),(.09,.17,'Lift the flat cover'),
 (.17,.21,'Back out motor screws; leave them in the chassis'),(.21,.33,'Withdraw motor and pinion together'),
 (.33,.41,'Remove both M5 bearing bolts'),(.41,.49,'Slide both 625ZZ bearings out axially'),
 (.49,.55,'Remove inner-race spacers'),(.55,.61,'Lower worm clear of rack teeth'),
 (.61,.82,'Slide rack out; guide floors relax'),(.82,.94,'Lift worm and integral spur gear'),(.94,1,'Both M5 insert installation paths')]]
def displacement(group,e):
 delta=[0.,0.,0.];theta=0.
 for t in TRACKS[group]:
  f=max(0,min(1,(e-t['start'])/(t['end']-t['start'])))
  delta=[delta[i]+f*t['delta'][i] for i in range(3)];theta+=f*t['radians']
 return delta,theta

def guide_lift(station,e):
 edge=ns['left']+displacement('rack',e)[0][0]
 if edge>station+8:return ns['SPRING_PRELOAD']
 d=max(0,edge-station)
 raw=max(0,min(ns['SPRING_PRELOAD'],8-math.sqrt(max(0,64-d*d))))
 step=ns['SPRING_PRELOAD']/4
 return math.floor(raw/step+1e-8)*step
def spring_key(e):
 return tuple(round(guide_lift(x,e)/ns['SPRING_PRELOAD']*4) for x in ns['STATIONS'])
spring_shapes={(0,0):fixture_s,(4,4):fixture_free}
def spring_shape(key):
 if key not in spring_shapes:spring_shapes[key]=fixture(ns['chassis'](tuple(ns['SPRING_PRELOAD']*(1-v/4) for v in key)))
 return spring_shapes[key]

# Geometry checks use B-reps, not the visualization triangles.
def overlap(a,b):
 # Control-hull boxes are conservative and avoid repeated expensive spline extrema.
 def bounds(s):
  bb=Bnd_Box();BRepBndLib.Add_s(s.wrapped,bb,False);return bb.Get()
 aa,bb=bounds(a),bounds(b)
 if any(aa[i+3]<=bb[i]+1e-7 or bb[i+3]<=aa[i]+1e-7 for i in range(3)):return 0.
 return a.intersect(b).Volume()
def spin(s,dx):return s.rotate(ORIGIN,(1,Y,Z),-dx/K*180/math.pi)
def posed(p,dx=0,e=0):
 s=spring_shape(spring_key(e)) if e and p['name']==CHASSIS_NAME else p['shape']
 if e:
  delta,theta=displacement(p['group'],e)
  if theta:s=s.rotate(ORIGIN,(1,Y,Z),math.degrees(theta))
  if 'lowerStation' in p:delta[2]+=guide_lift(p['lowerStation'],e)
  s=s.translate(tuple(delta))
 elif p['group']=='rack':s=s.translate((dx,0,0))
 elif p.get('rotating'):
  c=p.get('rotationCenter',ORIGIN);s=s.rotate(c,(c[0]+1,c[1],c[2]),-dx/K*180/math.pi*p.get('rotationFactor',1))
 elif 'spinAxis' in p:
  c=p['spinCenter'];u=p['spinAxis'];s=s.rotate(c,tuple(c[i]+u[i] for i in range(3)),p['spinSign']*dx/8*180/math.pi)
 return s

exec(compile((ROOT/'experiments/worm-rack/validate.py').read_text(),'worm-validation','exec'),globals())

print('Assembly built',len(parts),flush=True)
if args.check:
 report=validate()
 assert report['passed'], 'Experimental validation failed; see validation.json'
print('Exporting',len(parts),'parts',flush=True)
scene=[];assembly=cq.Assembly(name='Worm rack experiment')
mesh_dir=OUT/'stl';mesh_dir.mkdir(exist_ok=True)
expected={p['name'].lower().replace(' ','_')+'.stl' for p in parts if p['printed']}|{'rack_mesh_coupon.stl'}
for f in mesh_dir.glob('*.stl*'):
 if f.name.removesuffix('.gz') not in expected:f.unlink()
for i,p in enumerate(parts):
 s=p['shape'];BRepTools.Clean_s(s.wrapped);vs,ts=s.tessellate(.04,.12)
 scene.append({k:v for k,v in p.items() if k!='shape'}|{'vertices':[[round(v.x,5),round(v.y,5),round(v.z,5)] for v in vs],'triangles':ts})
 assembly.add(s,name=f'{i:02d} {p["name"]}',color=cq.Color(p['color']))
 if p['printed']:
  shape=fixture_free if p['name']==CHASSIS_NAME else s
  # Rack and cover print top-face down; the worm prints vertically.
  if p['name']=='Matched compliant rack':shape=shape.rotate((0,0,0),(1,0,0),180)
  if p['name']==WORM_NAME:shape=shape.rotate((0,0,0),(0,1,0),-90)
  if p['name']==MOTOR_GEAR_NAME:shape=shape.rotate((0,0,0),(0,1,0),90)
  if p['name']==COVER_NAME:shape=shape.rotate((0,0,0),(1,0,0),180)
  bb=shape.BoundingBox();shape=shape.translate((-bb.xmin,-bb.ymin,-bb.zmin))
  cq.exporters.export(shape,str(mesh_dir/(p['name'].lower().replace(' ','_')+'.stl')),tolerance=.03,angularTolerance=.12)
data={'type':'worm-experiment','motor':MOTOR_NAME,'stroke':STROKE,'lead':LEAD,'pitchRadius':R,'axisOrigin':ORIGIN,'tracks':TRACKS,'stages':STAGES,'wormName':WORM_NAME,'chassisName':CHASSIS_NAME,'bearingCount':8,'mounting':MOUNTING,'caseBounds':CASE_BOUNDS,'motorRearFaceX':MOTOR_REAR,'motorRearExposure':new_left-MOTOR_REAR,'stemDiameter':2*STEM_RADIUS,'pressureAngle':ns['PRESSURE_ANGLE'],'wormLength':WORM_END-WORM_START,'endInsert':{'thread':'M5','od':END_INSERT_OD,'length':END_INSERT_LENGTH,'pilot':END_INSERT_PILOT},'parts':scene}
data.update(spurGearX=GEAR_X+GEAR_WIDTH/2,motorAxisOrigin=MOTOR_ORIGIN,motorGearName=MOTOR_GEAR_NAME,trayName=TRAY_NAME,gearRatio=GEAR_RATIO,motorTeeth=MOTOR_TEETH,wormTeeth=WORM_TEETH,spurModule=GEAR_MODULE,travelPerMotorRevolution=LEAD*GEAR_RATIO,rackLeft=ns['left'],stations=ns['STATIONS'],springPreload=ns['SPRING_PRELOAD'],springSteps=4)
spring_scene=[]
for key in [(j,0) for j in range(1,5)]+[(4,j) for j in range(1,5)]:
 shape=spring_shape(key);BRepTools.Clean_s(shape.wrapped);vs,ts=shape.tessellate(.12,.22)
 spring_scene.append({'key':key,'vertices':[[round(v.x,5),round(v.y,5),round(v.z,5)] for v in vs],'triangles':ts})
with gzip.open(OUT/'spring-states.json.gz','wt') as f:json.dump(spring_scene,f,separators=(',',':'))
with gzip.open(OUT/'assembly.json.gz','wt') as f:json.dump(data,f,separators=(',',':'))
step=CACHE/'worm-rack.step';assembly.save(str(step))
with gzip.open(OUT/'worm-rack.step.gz','wb') as f:f.write(step.read_bytes())
coupon=rack.intersect(box(44,70,40,(0,15,5))).rotate((0,0,0),(1,0,0),180)
bb=coupon.BoundingBox();coupon=coupon.translate((-bb.xmin,-bb.ymin,-bb.zmin))
cq.exporters.export(coupon,str(mesh_dir/'rack_mesh_coupon.stl'),tolerance=.03,angularTolerance=.12)
print('Export complete',flush=True)
# Package only the isolated experiment; retain the production preset outputs unchanged.
notes=(ROOT/'experiments/worm-rack/README.md').read_text().replace('../../dist/experiments/worm-rack/validation.json','validation.json')
(OUT/'README.md').write_text(notes)
(OUT/'configuration.json').write_text(json.dumps({'drive':'worm','motor':args.motor,'stroke':STROKE,'motor_depth':MOTOR_DEPTH,'tooth_module':ns['MODULE'],'worm_pitch_radius':R,'stem_diameter':2*STEM_RADIUS,'motor_spur_teeth':MOTOR_TEETH,'worm_spur_teeth':WORM_TEETH,'spur_module':GEAR_MODULE,'spur_pressure_angle':25,'travel_per_motor_revolution':LEAD*GEAR_RATIO,'worm_length':WORM_END-WORM_START,'case_bounds':CASE_BOUNDS,'motor_rear_face_x':MOTOR_REAR,'motor_rear_exposure':new_left-MOTOR_REAR},indent=2))
(OUT/'mounting.json').write_text(json.dumps(MOUNTING,indent=2))
(OUT/'bill-of-materials.json').write_text(json.dumps({'motor':MOTOR_NAME,'stroke_mm':STROKE,'printed_parts':[p['name'] for p in parts if p['printed']],'hardware':[p['name'] for p in parts if not p['printed']],'bearing':'8 × 625ZZ (5 × 16 × 5 mm)','M3_inserts':'4.6 mm OD × 5 mm length; 4.2 mm pilot','M5_worm_inserts':'2 × 7 mm OD × 8 mm length; 6.6 mm pilot','rear_motor_face_exposed_mm':new_left-MOTOR_REAR,'flat_standard_cover':True},indent=2))
with zipfile.ZipFile(OUT/'worm-rack-experiment.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as bundle:
 bundle.writestr('README.md',notes)
 bundle.write(step,'worm-rack.step')
 for f in mesh_dir.glob('*.stl'):bundle.write(f,'stl/'+f.name)
 for f in ['model.py','requirements.txt','experiments/worm-rack/model.py','experiments/worm-rack/validate.py','experiments/worm-rack/enclosure.py','experiments/worm-rack/build_presets.py','experiments/worm-rack/requirements.txt','experiments/worm-rack/README.md']:bundle.write(ROOT/f,f)
 for name in ['configuration.json','mounting.json','bill-of-materials.json']:bundle.write(OUT/name,name)
 if (OUT/'validation.json').exists():bundle.write(OUT/'validation.json','validation.json')
print('Bundle complete',flush=True)
