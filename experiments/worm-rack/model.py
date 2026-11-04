"""Isolated NEMA17 / 40 mm direct worm-to-compliant-rack feasibility model.
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
P=argparse.ArgumentParser();P.add_argument('--check',action='store_true');P.add_argument('--out',default='dist/experiments/worm-rack');args=P.parse_args()
ROOT=pathlib.Path(__file__).resolve().parents[2];OUT=ROOT/args.out;OUT.mkdir(parents=True,exist_ok=True)
CACHE=ROOT/'work/worm-cache';CACHE.mkdir(parents=True,exist_ok=True)
# Reuse the tested rack and six-bearing guidance. Execute only definitions, no exports.
saved_argv=sys.argv;sys.argv=['model.py','--motor','nema17','--stroke','40','--out',str(CACHE/'baseline')]
ns={'__file__':str(ROOT/'model.py'),'__name__':'baseline'}
exec(compile((ROOT/'model.py').read_text().split('\n# Clear obsolete generated meshes')[0],str(ROOT/'model.py'),'exec'),ns)
sys.argv=saved_argv
box=ns['box'];cyl=ns['cyl'];acyl=ns['acyl'];ring=ns['ring'];ycyl=ns['ycyl']
PITCH=ns['TOOTH_PITCH'];LEAD=PITCH;K=LEAD/(2*math.pi);R=12.;Y=6.;Z=17.;RR=9.5;RA=14.;LENGTH=24.;PRELOAD=.1
AXIS=(1,0,0);ORIGIN=(0,Y,Z);ANGLE=math.radians(20)
WORM_START=-87.;WORM_END=16.;STEM_RADIUS=6.5
END_INSERT_OD=7.;END_INSERT_LENGTH=8.;END_INSERT_PILOT=6.6;END_INSERT_RECESS=.3
END_INSERT_FACE=WORM_END-END_INSERT_RECESS;END_PILOT_START=6.7
BEARING_X=20.5;SET_X=-80.;SET_Y=0.
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
 worm=worm.intersect(box(LENGTH,40,40,ORIGIN)).fuse(xcyl(STEM_RADIUS,75,WORM_START),xcyl(5.5,4,12))
 # Rounded shoulders join the integral stem and insert boss to the active worm.
 for x,r in [(-12,STEM_RADIUS),(12,5.5)]:
  edges=[e for e in worm.Edges() if e.geomType()=='CIRCLE' and abs(e.Center().x-x)<1e-6 and abs(e.radius()-r)<1e-6]
  assert len(edges)==1,(x,len(edges))
  worm=cq.Workplane(obj=worm).newObject(edges).fillet(1.2).val()
 # Blind D socket fits the actual motor shaft; the other end accepts an axial M5 insert.
 worm=worm.cut(dshaft(2.65,WORM_START-.1,17.1,-2.15)).cut(ycyl(1.25,6,SET_X,-1,Z))
 worm=worm.cut(xcyl(END_INSERT_PILOT/2,WORM_END-END_PILOT_START+.1,END_PILOT_START))
 worm=worm.cut(xcyl(END_INSERT_OD/2+.15,END_INSERT_RECESS+.1,END_INSERT_FACE))
 return worm.clean()

def loft(wires):
 b=BRepOffsetAPI_ThruSections(True,False);b.SetMaxDegree(3)
 for w in wires:b.AddWire(w.wrapped)
 b.Build();return cq.Solid(b.Shape())

def matched_rack(preload):
 original=ns['make_rack'](preload)
 zone=box(70,80,8,(0,20,17))
 section=cq.Workplane('XY').newObject([original.intersect(zone)]).section(Z).val()
 ROOT_Y=ns['ROOT_Y'];RELIEF_Y=ns['RELIEF_Y']
 def warp(v,z):
  x,y=v.x,v.y
  if y>=RELIEF_Y-1e-8:return cq.Vector(x,y,z)
  r=y-Y;theta=math.asin((z-Z)/r)
  t=max(0,(y-ROOT_Y)/(RELIEF_Y-ROOT_Y));blend=1-t*t*(3-2*t)
  tx=max(0,min(1,(abs(x)-29)/6));blend*=1-tx*tx*(3-2*tx)
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
source_hash=hashlib.sha256(pathlib.Path(__file__).read_text().split('def cached')[0].encode()+(ROOT/'model.py').read_bytes()).hexdigest()
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
# One chassis includes the guide, motor bracket and single end-bearing block.
bay=box(56,39,70,(0,-4.5,-2))
plate=box(200,90,6,(-40,19,-38))
supports=box(96.6,10,32,(5.3,55,-19))
for x0,x1 in [(-43,-28),(28,53.6)]:
 supports=supports.fuse(box(x1-x0,11,32,((x0+x1)/2,-17.5,-19)))
for p in ns['UPPER']:
 if p['side']=='rear':supports=supports.cut(acyl(5.5,35,p['center'],p['axis'],-30))
for p in ns['BOTTOM']:supports=supports.cut(ycyl(3.1,20,p['x'],46,-17))
motor_holes=[(Y+dy,Z+dz) for dy in [-15.5,15.5] for dz in [-15.5,15.5]]
land=box(168,38.5,6,(-56,-5.75,-32)).fuse(box(52,58.5,6,(-114,4.25,-32)))
bracket=box(5,53,69,(-92.5,6.5,5.5)).cut(xcyl(11.2,7,-96))
for y,z in motor_holes:bracket=bracket.cut(xcyl(1.7,7,-96,y,z))
# Top-loading saddle with integral shoulders on both axial faces. The bolt
# passes through the cheeks; only its spacers touch the rotating inner race.
end_block=box(11.5,19.5,60,(22.25,3.75,1)).cut(xcyl(8.15,5.3,17.85))
end_block=end_block.cut(box(5.3,16.3,25,(20.5,Y,29.5)))
end_block=end_block.cut(xcyl(4.25,2.1,16)).cut(xcyl(5.6,6,23))
def fixture(chassis):
 result=chassis.cut(bay).fuse(plate,supports,land,bracket,end_block)
 for x,y in [(-130,44),(-130,56),(51,-18),(51,56)]:result=result.cut(cyl(2.25,83,x,y,-42))
 return result.clean()
fixture_s=fixture(ns['base']);fixture_free=fixture(ns['base_print'])
parts.append(record(CHASSIS_NAME,fixture_s,'#475569',printed=True))
motor=box(40,42,42,(-115,Y,Z)).fuse(xcyl(11,2,-95))
for y,z in motor_holes:motor=motor.cut(xcyl(1.65,6,-100,y,z))
parts.append(record('NEMA17 42 × 42 × 40 reference',motor,'#374151','motor'))
for y,z in motor_holes:
 screw=xcyl(1.45,10,-100,y,z).fuse(xcyl(2.75,3,-90,y,z)).cut(xcyl(1.3,1.5,-88.5,y,z))
 parts.append(record(f'M3x10 motor screw {y} {z}',screw,'#94a3b8','motor_screws'))
parts.append(record('NEMA17 D shaft',dshaft(2.5,-93,22,-2),'#94a3b8','motor',rotating=True))
parts.append(record('M3x4 direct-drive set screw',ycyl(1.2,4,SET_X,SET_Y,Z).cut(ycyl(.9,1.2,SET_X,SET_Y,Z)),'#94a3b8','set_screw',rotating=True))
insert=ring(END_INSERT_OD/2,2.55,END_INSERT_LENGTH,(END_INSERT_FACE-END_INSERT_LENGTH,Y,Z),AXIS)
parts.append(record('M5 axial heat-set insert',insert,'#d4a54a','worm_insert',rotating=True,embedded_host=WORM_NAME))
parts.append(record('625ZZ end support',ring(8,2.5,5,(BEARING_X,Y,Z),AXIS,-2.5),'#cbd5e1','end_bearing'))
parts.append(record('M5 inner-race spacer 2 mm',ring(3.75,2.65,2,(16,Y,Z),AXIS),'#94a3b8','inner_spacer',rotating=True))
parts.append(record('M5 inner-race washer 0.3 mm',ring(3.75,2.65,.3,(23,Y,Z),AXIS),'#94a3b8','end_fastener',rotating=True))
end_bolt=xcyl(2.45,16,7.3).fuse(xcyl(4.75,5,23.3)).cut(xcyl(2.5,2.5,25.8))
parts.append(record('M5x16 end-bearing bolt',end_bolt,'#94a3b8','end_fastener',rotating=True))

# Shared CAD/viewer tracks. Remove the end-bearing stack first so the
# one-piece worm can leave radially after the motor shaft is withdrawn.
def track(start,end,delta=(0,0,0),radians=0):return dict(start=start,end=end,delta=list(delta),radians=radians)
worm_tracks=[track(.64,.84,(0,-65,0))]
TRACKS={
 'fixed':[],'guide':[],'rack':[],
 'set_screw':[track(0,.08,(0,-10,0)),track(.08,.14,(0,0,35))],
 'end_fastener':[track(0,.12,(55,0,0))],
 'end_bearing':[track(.12,.28,(0,0,25))],
 'inner_spacer':[track(.28,.38,(18,0,0))],
 'motor_screws':[track(.38,.48,(18,0,0))],
 'motor':[track(.48,.64,(-30,0,0))],
 'worm':worm_tracks,
 'worm_insert':worm_tracks+[track(.84,1,(14,0,0))],
}
STAGES=[dict(start=0,end=.14,label='Release shaft set screw and M5 end bolt'),dict(start=.12,end=.28,label='Lift end bearing from chassis saddle'),dict(start=.28,end=.38,label='Remove inner-race spacer'),dict(start=.38,end=.48,label='Remove motor mounting screws'),dict(start=.48,end=.64,label='Withdraw motor and shaft'),dict(start=.64,end=.84,label='Move worm sideways out of mesh'),dict(start=.84,end=1,label='Axial M5 insert installation path')]
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
  # Rack prints on its planar Z=21 face; all other STLs retain assembly coordinates.
  if p['name']=='Matched compliant rack':shape=shape.rotate((0,0,0),(1,0,0),180)
  if p['name']==WORM_NAME:shape=shape.rotate((0,0,0),(0,1,0),-90)
  bb=shape.BoundingBox();shape=shape.translate((-bb.xmin,-bb.ymin,-bb.zmin))
  cq.exporters.export(shape,str(mesh_dir/(p['name'].lower().replace(' ','_')+'.stl')),tolerance=.03,angularTolerance=.12)
data={'type':'worm-experiment','motor':'NEMA17','stroke':40,'lead':LEAD,'pitchRadius':R,'axisOrigin':ORIGIN,'tracks':TRACKS,'stages':STAGES,'wormName':WORM_NAME,'chassisName':CHASSIS_NAME,'bearingCount':7,'wormLength':WORM_END-WORM_START,'endInsert':{'thread':'M5','od':END_INSERT_OD,'length':END_INSERT_LENGTH,'pilot':END_INSERT_PILOT},'parts':scene}
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
with zipfile.ZipFile(OUT/'worm-rack-experiment.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as bundle:
 bundle.writestr('README.md',notes)
 bundle.write(step,'worm-rack.step')
 for f in mesh_dir.glob('*.stl'):bundle.write(f,'stl/'+f.name)
 for f in ['model.py','requirements.txt','experiments/worm-rack/model.py','experiments/worm-rack/validate.py','experiments/worm-rack/requirements.txt','experiments/worm-rack/README.md']:bundle.write(ROOT/f,f)
 if (OUT/'validation.json').exists():bundle.write(OUT/'validation.json','validation.json')
print('Bundle complete',flush=True)
