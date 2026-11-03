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
 worm=worm.intersect(box(LENGTH,40,40,ORIGIN)).fuse(xcyl(3.65,28,-14))
 worm=worm.cut(dshaft(2.65,-15,30,-2.15)).cut(ycyl(1.25,14,0,-9,Z))
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
parts=[record('Matched compliant rack',rack,'#5eead4','rack',True),record('Single-start worm',worm,'#fbbf24','drive',True,rotating=True)]
for p in ns['parts']:
 if p['group']=='rack' and p.get('embedded_host'):
  parts.append(record(p['name'],p['shape'],p['color'],'rack',embedded_host='Matched compliant rack'))
 elif p['name'].startswith(('625ZZ','M5 upper','M5x16 angled','M5 angled','M5 lower','M5x25 lower')):
  parts.append(record(p['name'],p['shape'],p['color'],'guide',**{k:p[k] for k in ['spinAxis','spinCenter','spinSign'] if k in p}))
# Open fixture: the original guide is relieved for a side-removable drive cartridge.
bay=box(56,39,70,(0,-4.5,-2))
plate=box(200,90,6,(-40,19,-38))
supports=box(96.6,10,32,(5.3,55,-19))
for x0,x1 in [(-43,-28),(28,53.6)]:
 bottom=-28.7 if x0<0 else -35.
 supports=supports.fuse(box(x1-x0,11,-3-bottom,((x0+x1)/2,-17.5,(-3+bottom)/2)))
# Preserve wrench/bolt clearance through the new support web.
for p in ns['UPPER']:
 if p['side']=='rear':supports=supports.cut(acyl(5.5,35,p['center'],p['axis'],-30))
for p in ns['BOTTOM']:supports=supports.cut(ycyl(3.1,20,p['x'],46,-17))
def fixture(chassis):
 s=chassis.cut(bay).fuse(plate,supports)
 for x in [-80,0]:
  s=s.cut(cyl(2.1,5.7,x,-21,-40.4)).cut(cyl(2.4,.4,x,-21,-35.3))
 # Four through holes for fixing the test plate to a bench.
 for x in [-130,51]:
  for y in [-18,56]:s=s.cut(cyl(2.25,7,x,y,-41.5))
 return s.clean()
fixture_s=fixture(ns['base']);fixture_free=fixture(ns['base_print'])
parts.append(record('Open guide fixture',fixture_s,'#475569',printed=True))
# Carrier / motor bracket. Driver remains exposed behind the reference motor.
carrier=box(168,38.5,6,(-56,-5.75,-32)).fuse(box(52,58.5,6,(-114,4.25,-32)))
carrier=carrier.fuse(box(5,53,69,(-92.5,6.5,5.5)))
carrier=carrier.cut(xcyl(11.2,7,-96))
motor_holes=[(Y+dy,Z+dz) for dy in [-15.5,15.5] for dz in [-15.5,15.5]]
for y,z in motor_holes:carrier=carrier.cut(xcyl(1.7,7,-96,y,z))
for sign in [-1,1]:
 x=sign*18
 tower=box(6.5,19.5,60,(sign*17.25,3.75,1))
 # Outward-open bearing seat; inward lip contacts only the outer race.
 tower=tower.cut(xcyl(8.15,7,x-2.5 if sign>0 else x-4.5))
 tower=tower.cut(xcyl(4.25,10,x-5))
 for z in [5,29]:tower=tower.cut(xcyl(1.25,10,x-5,-1,z))
 carrier=carrier.fuse(tower)
 capx=sign*21.75
 cap=box(2.5,19.5,28,(capx,3.75,17)).cut(xcyl(6.5,4,capx-2))
 for z in [5,29]:cap=cap.cut(xcyl(1.7,4,capx-2,-1,z))
 parts.append(record(f'Bearing keeper {sign}',cap,'#64748b','drive',True))
 bearing=ring(8,2.5,5,(x,Y,Z),AXIS,-2.5)
 parts.append(record(f'625ZZ worm support {sign}',bearing,'#cbd5e1','drive'))
 spacer=ring(3.75,2.65,1.5,(sign*14,Y,Z),AXIS,0 if sign>0 else -1.5)
 parts.append(record(f'Inner-race spacer {sign}',spacer,'#94a3b8','drive'))
 washer=ring(3.75,2.65,.3,(sign*20.5,Y,Z),AXIS,0 if sign>0 else -.3)
 parts.append(record(f'Shaft washer {sign}',washer,'#94a3b8','drive'))
 collar=ring(5,2.65,5,(sign*20.9,Y,Z),AXIS,0 if sign>0 else -5).cut(ycyl(1.25,5,sign*23.4,1,Z))
 parts.append(record(f'5 mm shaft collar {sign}',collar,'#94a3b8','drive',rotating=True))
 sets=ycyl(1.2,3,sign*23.4,1,Z)
 parts.append(record(f'M3 collar set screw {sign}',sets,'#94a3b8','drive',rotating=True))
 for z in [5,29]:
  # M3×8 keeper screw; pilot is tapped M3 in the printed carrier.
  u=(sign,0,0);c=(sign*23,Y-7,z)
  screw=acyl(1.2,8,c,u,-8).fuse(acyl(2.75,3,c,u)).cut(acyl(1.3,1.5,c,u,1.5))
  parts.append(record(f'M3x8 keeper screw {sign} {z}',screw,'#94a3b8','drive'))
for x in [-80,0]:carrier=carrier.cut(cyl(1.7,7,x,-21,-35.5))
parts.append(record('Worm motor cartridge',carrier.clean(),'#64748b','drive',True))
motor=box(40,42,42,(-115,Y,Z)).fuse(xcyl(11,2,-95))
for y,z in motor_holes:motor=motor.cut(xcyl(1.65,6,-100,y,z))
parts.append(record('NEMA17 42 × 42 × 40 reference',motor,'#374151','drive'))
for y,z in motor_holes:
 screw=xcyl(1.45,10,-100,y,z).fuse(xcyl(2.75,3,-90,y,z)).cut(xcyl(1.3,1.5,-88.5,y,z))
 parts.append(record(f'M3x10 motor screw {y} {z}',screw,'#94a3b8','drive'))
parts.append(record('NEMA17 D shaft',dshaft(2.5,-93,22,-2),'#94a3b8','drive',rotating=True))
parts.append(record('5 mm steel D drive shaft',dshaft(2.5,-70.5,96.5,-2),'#94a3b8','drive',rotating=True))
coupler=xcyl(5,16,-78).cut(dshaft(2.65,-79,18,-2.15))
for x in [-75,-65]:coupler=coupler.cut(ycyl(1.25,5,x,1,Z))
parts.append(record('D-shaft coupler',coupler,'#fbbf24','drive',True,rotating=True))
for x in [-75,-65]:parts.append(record(f'M3x3 coupler set screw {x}',ycyl(1.2,3,x,1,Z),'#94a3b8','drive',rotating=True))
parts.append(record('M3x8 worm set screw',ycyl(1.2,8,0,-4,Z).cut(ycyl(.9,1.2,0,-4,Z)),'#94a3b8','drive',rotating=True))
for x in [-80,0]:
 insert=cyl(2.3,5,x,-21,-40.3).cut(cyl(1.6,5,x,-21,-40.3))
 parts.append(record(f'M3 cartridge heat-set {x}',insert,'#d4a54a',embedded_host='Open guide fixture'))
 bolt=cyl(1.45,10,x,-21,-39).fuse(cyl(2.75,3,x,-21,-29)).cut(cyl(1.3,1.5,x,-21,-27.5))
 parts.append(record(f'M3x10 cartridge bolt {x}',bolt,'#94a3b8','mount_bolts'))

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
  if p['group']=='drive':s=s.translate((0,-65*max(0,min(1,(e-.3)/.7)),0))
  elif p['group']=='mount_bolts':s=s.translate((0,-40*max(0,min(1,(e-.15)/.15)),15*min(1,e/.15)))
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
for i,p in enumerate(parts):
 s=p['shape'];BRepTools.Clean_s(s.wrapped);vs,ts=s.tessellate(.04,.12)
 scene.append({k:v for k,v in p.items() if k!='shape'}|{'vertices':[[round(v.x,5),round(v.y,5),round(v.z,5)] for v in vs],'triangles':ts})
 assembly.add(s,name=f'{i:02d} {p["name"]}',color=cq.Color(p['color']))
 if p['printed']:
  shape=fixture_free if p['name']=='Open guide fixture' else s
  # Rack prints on its planar Z=21 face; all other STLs retain assembly coordinates.
  if p['name']=='Matched compliant rack':shape=shape.rotate((0,0,0),(1,0,0),180)
  bb=shape.BoundingBox();shape=shape.translate((-bb.xmin,-bb.ymin,-bb.zmin))
  cq.exporters.export(shape,str(mesh_dir/(p['name'].lower().replace(' ','_')+'.stl')),tolerance=.03,angularTolerance=.12)
data={'type':'worm-experiment','motor':'NEMA17','stroke':40,'lead':LEAD,'pitchRadius':R,'axisOrigin':ORIGIN,'parts':scene}
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
