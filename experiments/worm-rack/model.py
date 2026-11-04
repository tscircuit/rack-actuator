"""Enclosed direct worm-to-compliant-rack family: NEMA17 / NEMA14, 40–150 mm.
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
# The axial motor needs its lower screw path clear. Move only the internal rear/front
# lid seat; every external mounting interface retains the production coordinates.
marker='\nINSERT_OD=a.insert_od'
assert baseline_source.count(marker)==1
baseline_source=baseline_source.replace(marker,"\nCOVER_SEATS=[(CASE_LEFT+24,CASE_YMIN+6) if abs(x-(CASE_LEFT+7.5))<1e-6 and y<0 else (x,y) for x,y in COVER_SEATS]"+marker)
exec(compile(baseline_source,str(ROOT/'model.py'),'exec'),ns)
sys.argv=saved_argv
box=ns['box'];cyl=ns['cyl'];acyl=ns['acyl'];ring=ns['ring'];ycyl=ns['ycyl']
PITCH=ns['TOOTH_PITCH'];LEAD=PITCH;K=LEAD/(2*math.pi);R=11. if IS14 else 12.;Y=ns['PITCH_Y']-R;Z=17.;RR=R-2.5;RA=R+2.;LENGTH=24.;PRELOAD=.1
AXIS=(1,0,0);ORIGIN=(0,Y,Z);ANGLE=math.radians(ns['PRESSURE_ANGLE'])
MOTOR_SIZE=ns['MOTOR_SIZE'];MOTOR_PITCH=ns['MOTOR_PITCH'];MOTOR_DEPTH=ns['MOTOR_DEPTH']
MOTOR_FRONT=ns['left']-STROKE/2-10.;MOTOR_REAR=MOTOR_FRONT-MOTOR_DEPTH
WORM_START=MOTOR_FRONT+8.;WORM_END=16.;STEM_RADIUS=(6. if STROKE==40 else 6.5) if IS14 else (6.5 if STROKE==40 else 7.5 if STROKE==100 else 8.)
END_INSERT_OD=7.;END_INSERT_LENGTH=8.;END_INSERT_PILOT=6.6;END_INSERT_RECESS=.3
END_INSERT_FACE=WORM_END-END_INSERT_RECESS;END_PILOT_START=6.7
BEARING_X=20.5;SET_X=WORM_START+14.;SET_Y=Y-6.
WORM_NAME='One-piece direct-drive worm';CHASSIS_NAME='Integral worm chassis'
def xcyl(r,length,x,y=Y,z=Z):return acyl(r,length,(x,y,z),AXIS)
def dshaft(r,x,length,flat):return xcyl(r,length,x).intersect(box(length,2*r+2,2*r+2,(x+length/2,Y+flat+(2*r+2)/2,Z)))
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
  edges=[e for e in worm.Edges() if e.geomType()=='CIRCLE' and abs(e.Center().x-x)<1e-6 and abs(e.radius()-r)<1e-6]
  assert len(edges)==1,(x,len(edges))
  worm=cq.Workplane(obj=worm).newObject(edges).fillet(min(1.2,(RR-r)*.45)).val()
 # Blind D socket fits the actual motor shaft; the other end accepts an axial M5 insert.
 worm=worm.cut(dshaft(2.65,WORM_START-.1,17.1,-2.15)).cut(ycyl(1.25,STEM_RADIUS,SET_X,Y-STEM_RADIUS-1,Z))
 worm=worm.cut(xcyl(END_INSERT_PILOT/2,WORM_END-END_PILOT_START+.1,END_PILOT_START))
 worm=worm.cut(xcyl(END_INSERT_OD/2+.15,END_INSERT_RECESS+.1,END_INSERT_FACE))
 return worm.clean()

def loft(wires):
 b=BRepOffsetAPI_ThruSections(True,False);b.SetMaxDegree(3)
 for w in wires:b.AddWire(w.wrapped)
 b.Build();return cq.Solid(b.Shape())

def matched_rack(preload):
 original=ns['make_rack'](preload)
 warp_end=ns['centers'][-1]+10
 zone=box(warp_end*2,80,8,(0,20,17))
 section=cq.Workplane('XY').newObject([original.intersect(zone)]).section(Z).val()
 ROOT_Y=ns['ROOT_Y'];RELIEF_Y=ns['RELIEF_Y']
 def warp(v,z):
  x,y=v.x,v.y
  if y>=RELIEF_Y-1e-8:return cq.Vector(x,y,z)
  r=y-Y;theta=math.asin((z-Z)/r)
  t=max(0,(y-ROOT_Y)/(RELIEF_Y-ROOT_Y));blend=1-t*t*(3-2*t)
  tx=max(0,min(1,(abs(x)-(ns['centers'][-1]+4))/6));blend*=1-tx*tx*(3-2*tx)
  return cq.Vector(x+blend*K*theta,y+blend*(math.sqrt(r*r-(z-Z)**2)-r),z)
 def layer(w,z):
  edges=[]
  for e in w.Edges():
   if e.BoundingBox().ymin>=RELIEF_Y-1e-7:edges.append(e.translate((0,0,z-Z)));continue
   n=8 if e.geomType()=='CIRCLE' else 4
   edges.append(cq.Edge.makeSpline([warp(e.positionAt(j/n),z) for j in range(n+1)]))
  return cq.Wire.assembleEdges(edges)
 wires=section.Wires();outer=max(wires,key=lambda w:w.BoundingBox().xlen)
 top=loft([layer(outer,13+j) for j in range(9)])
 for w in wires:
  if w.BoundingBox().xlen<10:top=top.cut(cq.Solid.makeLoft([layer(w,13),layer(w,21)]))
 lower=original.cut(zone)
 return top.fuse(lower).clean()

def cached(name,fn):
 path=CACHE/(name+'.brep')
 if path.exists():return cq.Shape.importBrep(str(path))
 print('Building',name,flush=True);s=fn();s.exportBrep(str(path));return s
# Cache is local/ignored and keyed by both geometry sources.
source_hash=hashlib.sha256(pathlib.Path(__file__).read_text().split('def cached')[0].encode()+(ROOT/'model.py').read_bytes()+f'{args.motor}:{STROKE}'.encode()).hexdigest()
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
  parts.append(record(p['name'],p['shape'],p['color'],'guide',**{k:p[k] for k in ['spinAxis','spinCenter','spinSign'] if k in p}))
# Keep the production guide/chassis mounting interfaces; add integral drive supports.
bay=box(56,39,70,(0,-4.5,-2))
land=box(28-MOTOR_FRONT,19.5,6,((MOTOR_FRONT+28)/2,Y-2.25,-26))
supports=box(8,24,33,(-18,Y,-12.5)).fuse(box(6,24,33,(31,Y,-12.5)))
for p in ns['UPPER']:
 access=acyl(5.5,55,p['center'],p['axis'],-50)
 supports=supports.cut(access);land=land.cut(access)
# Braces sit between bearing stations, leaving axle/nut insertion paths open.
REAR_SUPPORT_POINTS=[(MOTOR_FRONT+12,Y-6),(MOTOR_FRONT+12,Y+3)]
for x,y in REAR_SUPPORT_POINTS:land=land.cut(cyl(1.7,8,x,y,-30))
motor_holes=[(Y+dy,Z+dz) for dy in [-MOTOR_PITCH/2,MOTOR_PITCH/2] for dz in [-MOTOR_PITCH/2,MOTOR_PITCH/2]]
bracket_top=Z+MOTOR_SIZE/2+2
bracket=box(5,MOTOR_SIZE+3,bracket_top+29,(MOTOR_FRONT+2.5,Y,(bracket_top-29)/2)).cut(xcyl(11.2,7,MOTOR_FRONT-1))
for y,z in motor_holes:bracket=bracket.cut(xcyl(1.7,7,MOTOR_FRONT-1,y,z))
# Top-loading saddle with integral axial shoulders; no keeper or keeper screws.
end_block=box(11.5,25.5-Y,60,(22.25,(Y+1.5)/2,1)).cut(xcyl(8.15,5.3,17.85))
end_block=end_block.cut(box(5.3,16.3,25,(20.5,Y,29.5)))
end_block=end_block.cut(xcyl(4.25,2.1,16)).cut(xcyl(5.6,6,23))
def fixture(chassis):
 result=chassis.cut(bay).fuse(land,supports,bracket,end_block)
 for x,y in ns['COVER_SEATS']:
  if abs(x-(ns['CASE_LEFT']+7.5))<1e-6:
   result=result.cut(cyl(5.3,80,x,y,-40))
   result=result.cut(ns['rect_cut'](ns['CASE_LEFT']-1,x,y-5.3,y+5.3,-40,40))
 return result.clean()
fixture_s=fixture(ns['base']);fixture_free=fixture(ns['base_print'])
parts.append(record(CHASSIS_NAME,fixture_s,'#475569',printed=True))
motor=box(MOTOR_DEPTH,MOTOR_SIZE,MOTOR_SIZE,(MOTOR_FRONT-MOTOR_DEPTH/2,Y,Z)).fuse(xcyl(11,2,MOTOR_FRONT))
for y,z in motor_holes:motor=motor.cut(xcyl(1.65,6,MOTOR_FRONT-5,y,z))
parts.append(record(f'{MOTOR_NAME} {MOTOR_SIZE:g} × {MOTOR_SIZE:g} × {MOTOR_DEPTH:g} reference',motor,'#374151','motor'))
for y,z in motor_holes:
 screw=xcyl(1.45,10,MOTOR_FRONT-5,y,z).fuse(xcyl(2.75,3,MOTOR_FRONT+5,y,z)).cut(xcyl(1.3,1.5,MOTOR_FRONT+6.5,y,z))
 parts.append(record(f'M3x10 motor screw {y} {z}',screw,'#94a3b8','motor_screws'))
parts.append(record(f'{MOTOR_NAME} D shaft',dshaft(2.5,MOTOR_FRONT+2,22,-2),'#94a3b8','motor',rotating=True))
parts.append(record('M3x4 direct-drive set screw',ycyl(1.2,4,SET_X,SET_Y,Z).cut(ycyl(.9,1.2,SET_X,SET_Y,Z)),'#94a3b8','set_screw',rotating=True))
insert=ring(END_INSERT_OD/2,2.55,END_INSERT_LENGTH,(END_INSERT_FACE-END_INSERT_LENGTH,Y,Z),AXIS)
parts.append(record('M5 axial heat-set insert',insert,'#d4a54a','worm_insert',rotating=True,embedded_host=WORM_NAME))
parts.append(record('625ZZ end support',ring(8,2.5,5,(BEARING_X,Y,Z),AXIS,-2.5),'#cbd5e1','end_bearing'))
parts.append(record('M5 inner-race spacer 2 mm',ring(3.75,2.65,2,(16,Y,Z),AXIS),'#94a3b8','inner_spacer',rotating=True))
parts.append(record('M5 inner-race washer 0.3 mm',ring(3.75,2.65,.3,(23,Y,Z),AXIS),'#94a3b8','end_fastener',rotating=True))
end_bolt=xcyl(2.45,16,7.3).fuse(xcyl(4.75,5,23.3)).cut(xcyl(2.5,2.5,25.8))
parts.append(record('M5x16 end-bearing bolt',end_bolt,'#94a3b8','end_fastener',rotating=True))

exec(compile((ROOT/'experiments/worm-rack/enclosure.py').read_text(),'worm-enclosure','exec'),globals())

# Shared CAD/viewer tracks. Remove the end-bearing stack first so the
# one-piece worm can leave radially after the motor shaft is withdrawn.
def track(start,end,delta=(0,0,0),radians=0):return dict(start=start,end=end,delta=list(delta),radians=radians)
worm_tracks=[track(.74,.78,(0,-8,0)),track(.78,.84,(0,0,40)),track(.84,.92,(0,-57,0))]
TRACKS={
 'fixed':[],'guide':[],'rack':[],'tray':[],'chassis_screws':[],
 'cover_screws':[track(0,.06,(0,0,55)),track(.06,.10,(0,-140,0))],
 'cover':[track(.10,.20,(0,0,100))],
 'set_screw':[track(.20,.26,(0,-12,0)),track(.26,.32,(0,-80,0))],
 'end_fastener':[track(.20,.32,(55,0,0))],
 'end_bearing':[track(.32,.44,(0,0,25))],
 'inner_spacer':[track(.44,.52,(18,0,0))],
 'motor_screws':[track(.52,.56,(18,0,0)),track(.56,.60,(0,0,55)),track(.60,.64,(0,100,0))],
 'motor':[track(.64,.74,(-50,0,0))],
 'worm':worm_tracks,
 'worm_insert':worm_tracks+[track(.92,1,(14,0,0))],
}
STAGES=[dict(start=a,end=b,label=s) for a,b,s in [
 (0,.10,'Remove and park cover screws'),(.10,.20,'Lift enclosure cover'),
 (.20,.32,'Release shaft set screw and M5 end bolt'),(.32,.44,'Lift end bearing from chassis saddle'),
 (.44,.52,'Remove inner-race spacer'),(.52,.64,'Remove and park motor mounting screws'),
 (.64,.74,'Withdraw motor through rear opening'),(.74,.78,'Move worm clear of rack teeth'),
 (.78,.84,'Lift worm above enclosure wall'),(.84,.92,'Move worm clear of enclosure'),(.92,1,'Axial M5 insert installation path')]]
def displacement(group,e):
 delta=[0.,0.,0.];theta=0.
 for t in TRACKS[group]:
  f=max(0,min(1,(e-t['start'])/(t['end']-t['start'])))
  delta=[delta[i]+f*t['delta'][i] for i in range(3)];theta+=f*t['radians']
 return delta,theta

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
 s=p['shape']
 if e:
  delta,theta=displacement(p['group'],e)
  if theta:s=s.rotate(ORIGIN,(1,Y,Z),math.degrees(theta))
  s=s.translate(tuple(delta))
 elif p['group']=='rack':s=s.translate((dx,0,0))
 elif p.get('rotating'):s=spin(s,dx)
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
for f in mesh_dir.glob('*.stl'):
 if f.name not in expected:f.unlink()
for i,p in enumerate(parts):
 s=p['shape'];BRepTools.Clean_s(s.wrapped);vs,ts=s.tessellate(.04,.12)
 scene.append({k:v for k,v in p.items() if k!='shape'}|{'vertices':[[round(v.x,5),round(v.y,5),round(v.z,5)] for v in vs],'triangles':ts})
 assembly.add(s,name=f'{i:02d} {p["name"]}',color=cq.Color(p['color']))
 if p['printed']:
  shape=fixture_free if p['name']==CHASSIS_NAME else s
  # Rack prints tooth-face down, worm vertically, enclosure cover roof down.
  if p['name']=='Matched compliant rack':shape=shape.rotate((0,0,0),(1,0,0),180)
  if p['name']==WORM_NAME:shape=shape.rotate((0,0,0),(0,1,0),-90)
  if p['name']==COVER_NAME:shape=shape.rotate((0,0,0),(1,0,0),180)
  bb=shape.BoundingBox();shape=shape.translate((-bb.xmin,-bb.ymin,-bb.zmin))
  cq.exporters.export(shape,str(mesh_dir/(p['name'].lower().replace(' ','_')+'.stl')),tolerance=.03,angularTolerance=.12)
data={'type':'worm-experiment','motor':MOTOR_NAME,'stroke':STROKE,'lead':LEAD,'pitchRadius':R,'axisOrigin':ORIGIN,'tracks':TRACKS,'stages':STAGES,'wormName':WORM_NAME,'chassisName':CHASSIS_NAME,'bearingCount':7,'mounting':MOUNTING,'caseBounds':CASE_BOUNDS,'motorRearFaceX':MOTOR_REAR,'motorRearExposure':4,'stemDiameter':2*STEM_RADIUS,'pressureAngle':ns['PRESSURE_ANGLE'],'wormLength':WORM_END-WORM_START,'endInsert':{'thread':'M5','od':END_INSERT_OD,'length':END_INSERT_LENGTH,'pilot':END_INSERT_PILOT},'parts':scene}
with gzip.open(OUT/'assembly.json.gz','wt') as f:json.dump(data,f,separators=(',',':'))
step=CACHE/'worm-rack.step';assembly.save(str(step))
with gzip.open(OUT/'worm-rack.step.gz','wb') as f:f.write(step.read_bytes())
coupon=rack.intersect(box(44,60,40,(0,25,5))).rotate((0,0,0),(1,0,0),180)
bb=coupon.BoundingBox();coupon=coupon.translate((-bb.xmin,-bb.ymin,-bb.zmin))
cq.exporters.export(coupon,str(mesh_dir/'rack_mesh_coupon.stl'),tolerance=.03,angularTolerance=.12)
print('Export complete',flush=True)
# Package only the isolated experiment; retain the production preset outputs unchanged.
notes=(ROOT/'experiments/worm-rack/README.md').read_text().replace('../../dist/experiments/worm-rack/validation.json','validation.json')
(OUT/'README.md').write_text(notes)
(OUT/'configuration.json').write_text(json.dumps({'drive':'worm','motor':args.motor,'stroke':STROKE,'motor_depth':MOTOR_DEPTH,'tooth_module':ns['MODULE'],'worm_pitch_radius':R,'stem_diameter':2*STEM_RADIUS,'worm_length':WORM_END-WORM_START,'case_bounds':CASE_BOUNDS,'motor_rear_face_x':MOTOR_REAR,'motor_rear_exposure':4},indent=2))
(OUT/'mounting.json').write_text(json.dumps(MOUNTING,indent=2))
(OUT/'bill-of-materials.json').write_text(json.dumps({'motor':MOTOR_NAME,'stroke_mm':STROKE,'printed_parts':[p['name'] for p in parts if p['printed']],'hardware':[p['name'] for p in parts if not p['printed']],'bearing':'7 × 625ZZ (5 × 16 × 5 mm)','M3_inserts':'4.6 mm OD × 5 mm length; 4.2 mm pilot','M5_worm_insert':'7 mm OD × 8 mm length; 6.6 mm pilot','rear_motor_face_exposed_mm':4,'top_mount_clearance':MOUNTING['raisedCoverClearance']},indent=2))
with zipfile.ZipFile(OUT/'worm-rack-experiment.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as bundle:
 bundle.writestr('README.md',notes)
 bundle.write(step,'worm-rack.step')
 for f in mesh_dir.glob('*.stl'):bundle.write(f,'stl/'+f.name)
 for f in ['model.py','requirements.txt','experiments/worm-rack/model.py','experiments/worm-rack/validate.py','experiments/worm-rack/enclosure.py','experiments/worm-rack/build_presets.py','experiments/worm-rack/requirements.txt','experiments/worm-rack/README.md']:bundle.write(ROOT/f,f)
 for name in ['configuration.json','mounting.json','bill-of-materials.json']:bundle.write(OUT/name,name)
 if (OUT/'validation.json').exists():bundle.write(OUT/'validation.json','validation.json')
print('Bundle complete',flush=True)
