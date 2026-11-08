"""Separate 40 mm NEMA17 racks with a four-screw rigid carrier and PETG snap axles."""
import pathlib,sys,argparse,math,json,gzip,hashlib,itertools,zipfile
import cadquery as cq
import numpy as np
from OCP.BRepTools import BRepTools
ROOT=pathlib.Path(__file__).resolve().parents[2];HERE=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--drive',choices=['spur','worm'],default='spur');parser.add_argument('--check',action='store_true');args=parser.parse_args();DRIVE=args.drive
OUT=ROOT/'dist/experiments/adjustable-rack'/DRIVE;OUT.mkdir(parents=True,exist_ok=True);WORK=ROOT/'work/adjustable-rack';WORK.mkdir(parents=True,exist_ok=True)
cachelink=HERE/'baseline/work'
if not cachelink.exists():cachelink.symlink_to('../../../work',target_is_directory=True)
basefile=HERE/'baseline/model.py';ns={'__file__':str(basefile),'__name__':'adjustable_baseline'}
if DRIVE=='spur':
 sys.argv=['model.py','--out',str(WORK/'baseline-spur')];exec(compile(basefile.read_text().split('\n# Clear obsolete generated meshes')[0],str(basefile),'exec'),ns);parts=ns['parts'];frame=ns['frame'];CHASSIS='01 Integral spring chassis';old=ns['base'];RACK='04 Beveled compliant rack';TRAY='05 Mounting enclosure tray'
else:
 file=HERE/'baseline/experiments/worm-rack/model.py';sys.argv=[str(file)];m={'__file__':str(file),'__name__':'adjustable_worm','BRepTools':BRepTools};text=file.read_text().split("exec(compile((ROOT/'experiments/worm-rack/validate.py')")[0];exec(compile(text,str(file),'exec'),m);ns=m['ns'];parts=m['parts'];old=m['fixture_s'];CHASSIS=m['CHASSIS_NAME'];RACK='Matched compliant rack';TRAY=m['TRAY_NAME'];frame=m['fixture'](ns['frame'])
box=ns['box'];at=ns['at'];ring=ns['ring'];STATIONS=ns['STATIONS'];CARRIER='Rigid adjustable two-bearing carrier';ADJUST=[(x,y) for x in [-16,12] for y in [44,53]]
def cyl(r,h,c,u=(0,0,1),t=0):return ns['acyl'](r,h,c,u,t)
def rect(xa,xb,ya,yb,za,zb):return box(xb-xa,yb-ya,zb-za,((xa+xb)/2,(ya+yb)/2,(za+zb)/2))
# Same proven split axle proportions as the independent lead-screw prototype.
pin_source=(ROOT/'experiments/adjustable-rack/snap_axles.py').read_text();exec(compile(pin_source,'snap_axles','exec'),globals())
# Remove the complete old flexible floor region; no spring geometry survives.
frame=frame.cut(rect(-44,54,20.5,44,-35,-5.5))
# Remove underside nut sockets and replace each upper axle root with solid material.
bearings=[]
for i,b in enumerate(ns['UPPER']):
 c=b['center'];u=tuple(-v for v in b['axis']);bearings.append(dict(kind='upper',index=i,center=c,axis=u))
 frame=frame.fuse(cyl(6,9,c,u,5.1))
 frame=inner_race_seat(frame,c,u)
# Shared carrier is a stiff beam behind the lower running surface.
carrier=rect(-39,51,37.5,51,-28,-10)
carrier=carrier.cut(rect(47,52,49,52,-30,-8))
for i,b in enumerate(ns['BOTTOM']):
 c=b['center'];u=(0,1,0);bearings.append(dict(kind='lower',index=i+4,center=c,axis=u))
 carrier=carrier.fuse(rect(c[0]-5,c[0]+5,c[1]+3.3,48,-24,-11))
 carrier=inner_race_seat(carrier,c,u)
# A rigid lower bridge replaces the spring floors and joins both chassis sides.
# The carrier slides forward out of an open-ended guide after tray removal.
deck=rect(-43,53.6,22.5,61,-35.5,-31.5)
for x in ns['REAR_MOUNT_XS']:deck=deck.cut(cyl(6,10,(x,54,-38)))
deck=deck.cut(rect(44.15,55,49,62,-38,-22))
frame=frame.fuse(deck)
for x in [-24,30]:frame=frame.fuse(rect(x-2,x+2,18,23,-35.5,-3))
for x in [-8,20]:frame=frame.fuse(rect(x-6,x+6,58,61,-35.5,-3))
frame=frame.fuse(rect(-43,-39.35,36.8,51.35,-31.5,-22))
for ya,yb in [(34,37.15),(51.35,54.5)]:
 frame=frame.fuse(rect(-39.35,47 if ya<40 else 44.15,ya,yb,-31.5,-26.5))
# Rear mounting posts need open slots through the low bridge during the
# 6 mm lift / 10 mm rearward chassis release.
for x in ns['REAR_MOUNT_XS']:
 frame=frame.cut(rect(x-6.35,x+16.35,49.65,61.35,-38,-9))
 carrier=carrier.cut(rect(x-4.35,x+14.35,49.65,58.35,-32,-9))
# Four screw heads bear on transverse ribs tied into the rear chassis wall.
for x in [-16,12]:frame=frame.fuse(rect(x-3.8,x+3.8,44,60,-7,-3))
# Inserts travel with the carrier.
for x,y in ADJUST:
 carrier=carrier.fuse(cyl(4.5,12,(x,y,-22)))
 frame=frame.fuse(cyl(3.8 if y==44 else 4.8,11,(x,y,-7)))
 frame=frame.cut(cyl(1.8,14,(x,y,-9))).cut(cyl(3.7,40,(x,y,4)))
 carrier=carrier.cut(cyl(2.1,5.5,(x,y,-15.5))).cut(cyl(1.75,8,(x,y,-18)))
 carrier=carrier.cut(cq.Solid.makeCone(2.1,2.45,.5,cq.Vector(x,y,-10.5),cq.Vector(0,0,1)))
# Clear the fixed tray/standoffs from the carrier across its adjustment travel.
tray=next(p['shape'] for p in parts if p['name']==TRAY);tray_original=tray
# Relocate the intermediate cover screw to a rearward, wall-tied post, outside
# both the carrier and its service path. Keep the external housing envelope.
tray=tray.cut(rect(-2.51,6.51,41.89,ns['CASE_YMAX']-ns['CASE_WALL'],ns['CASE_BOTTOM']+ns['CASE_WALL'],7.1))
tray=tray.fuse(cyl(4.5,7-ns['CASE_BOTTOM'],(-60,46.4,ns['CASE_BOTTOM'])),rect(-64.5,-55.5,46.4,ns['CASE_YMAX'],ns['CASE_BOTTOM'],7))
tray=tray.cut(cyl(1.7,53,(-60,46.4,-45))).cut(cyl(ns['INSERT_PILOT']/2,5.4,(-60,46.4,1.6)))
for p in parts:
 if p['group']=='cover':
  cover=p['shape'].cut(rect(-2.51,6.51,41.89,ns['CASE_YMAX']-ns['CASE_WALL'],6.9,22.5))
  cover=cover.fuse(cyl(3.11,2.41,(2,46.4,22.49)),cyl(4.5,17.9,(-60,46.4,7)),rect(-64.5,-55.5,46.4,ns['CASE_YMAX'],7,24.9))
  p['shape']=cover.cut(cyl(1.7,20,(-60,46.4,6))).cut(cyl(3.1,4.3,(-60,46.4,21.6))).clean()
 if p['name'] in ['M3 heat-set insert lid 2 46.4','M3x20 recessed lid screw 2 46.4']:
  p['shape']=p['shape'].translate((-62,0,0));p['name']=p['name'].replace(' 2 46.4',' -60 46.4')

# The receiving tray is preserved; the carrier has deliberately local corner reliefs.
carrier=carrier.cut(rect(22,32,49,55,-30,-8))
# Reopen the rear chassis screw clearances after rebuilding upper axle roots.
for x in ns['REAR_MOUNT_XS']:frame=frame.cut(cyl(3.1,25,(x,54,-16)))
# Open the enclosure rib locally around the new carrier. Its upper shelf remains
# tied to the rear wall; retain the enclosure floor and chassis mounting posts.
tray=tray.cut(rect(-39.35,47,37.15,51.35,-35.85,-9.65))
for x,y in ADJUST:tray=tray.cut(cyl(4.85,13.7,(x,y,-23.35)))
# Matching pockets accept the fixed lower bridge and its guide rails.
tray=tray.cut(rect(-43.35,47,22.15,58.35,-35.85,-31.15))
for x in [-24,30]:tray=tray.cut(rect(x-2.35,x+2.35,17.65,23.35,-35.85,-2.65))
for x in [-8,20]:tray=tray.cut(rect(x-6.35,x+6.35,57.65,61.35,-35.85,-2.65))
for ya,yb in [(33.65,37.5),(51,54.85)]:tray=tray.cut(rect(-43.35,47.35,ya,yb,-31.85,-21.65))
# Small local conformal pockets around new fixed axle roots and deck corners.
for delta in [(0,0,0),(.35,0,0),(-.35,0,0),(0,.35,0),(0,-.35,0),(0,0,.35),(0,0,-.35)]:tray=tray.cut(frame.translate(delta))
# Vertical service relief clears the rebuilt exit-side upper axle root.
tray=tray.cut(rect(43.9,50.45,49.55,57.7,-6.3,11.35)).clean()
print('Tray pieces',[(q.Volume(),q.Center().toTuple()) for q in tray.Solids()],flush=True)
tray.exportBrep(str(WORK/(DRIVE+'-tray-cut.brep')))
assert tray.isValid() and len(tray.Solids())==1,('tray solids',len(tray.Solids()))
for p in parts:
 if p['name']==TRAY:p['shape']=tray;p.pop('printShape',None)
# The worm's additional motor seats limit lateral chassis release to 2.8 mm.
# Vertical post reliefs allow it to lift clear after this short translation.
if DRIVE=='worm':
 for x,y,r in [(52.3,56.4,5.35),(52.3,-19.4,5.35),(26.8,-20.9,4.85),(-60.2,-21.9,4.85)]:frame=frame.cut(cyl(r,100,(x,y,-50)))
frame=frame.clean();carrier=carrier.clean();frame_without_pins=frame;carrier_print_without_pins=carrier
# Installed inserts displace only the pilot annulus; the printable STL keeps its pilot.
for x,y in ADJUST:carrier=carrier.cut(cyl(2.32,5,(x,y,-15)))
carrier_without_pins=carrier
for b in bearings:
 if b['kind']=='upper':frame=frame.fuse(snap_pin(b['center'],b['axis']))
 else:carrier=carrier.fuse(snap_pin(b['center'],b['axis']))
frame=frame.clean();carrier=carrier.clean();carrier_print=carrier_print_without_pins
# OCC can leave tiny trimming slivers at historical upper support tangencies.
pieces=sorted(frame.Solids(),key=lambda q:q.Volume(),reverse=True)
assert all(q.Volume()<.01 for q in pieces[1:]),[(q.Volume(),q.Center().toTuple()) for q in pieces]
frame=pieces[0]
for b in bearings:
 if b['kind']=='lower':carrier_print=carrier_print.fuse(snap_pin(b['center'],b['axis']))
carrier_print=carrier_print.clean()
print('Frame pieces',[(q.Volume(),q.Center().toTuple()) for q in frame.Solids()],flush=True)
print('Bodies:',[(n,len(s.Solids()),s.isValid()) for n,s in [('frame',frame),('carrier',carrier)]],flush=True)
for n,s in [('frame',frame),('carrier',carrier)]:assert len(s.Solids())==1 and s.isValid(),n
removed=[];kept=[]
for p in parts:
 if p['name']==CHASSIS:continue
 if p['name'].startswith(('625ZZ angled','625ZZ lower','M5 upper washer','M5 lower washer','M5x16 angled axle','M5 angled nut','M5x25 lower axle','M5 lower nut')):removed.append(p['name']);continue
 q={k:v for k,v in p.items() if k not in ['flex_chassis','lowerStation','spinAxis','spinCenter','spinSign']};kept.append(q)
parts=kept
parts += [dict(name='Rigid snap-axle chassis',shape=frame,color='#475569',group='fixed',printed=True),dict(name=CARRIER,shape=carrier,printShape=carrier_print,color='#748aa0',group='carrier',printed=True)]
CHASSIS='Rigid snap-axle chassis'
for j,(x,y) in enumerate(ADJUST):
 bolt=cyl(1.45,20,(x,y,-16)).fuse(cyl(2.75,3,(x,y,4))).cut(cyl(1.3,1.8,(x,y,5.2)))
 parts.append(dict(name=f'M3x20 adjustment screw {j+1}',shape=bolt,color='#94a3b8',group='adjust_screws',printed=False))
 parts.append(dict(name=f'M3 carrier heat-set insert {j+1}',shape=ring(2.3,1.6,5,(x,y,-15),(0,0,1)),color='#d4a54a',group='carrier',printed=False))
for b in bearings:parts.append(dict(name='625ZZ snap guide '+str(b['index']+1),shape=ring(8,2.5,5,b['center'],b['axis'],-2.5),color='#cbd5e1',group='lower_bearings' if b['kind']=='lower' else 'upper_bearings',printed=False,bearing=b))
# Keep the newly published axial NEMA17 end plate on every rack.
newsource=(ROOT/'model.py').read_text();exec(compile(newsource[newsource.index('OUTPUT_PAD_SIZE='):newsource.index('\ncentral_relief_radius=')],'axial_output','exec'),ns)
if DRIVE=='spur':rack=ns['make_rack'](.1);racks={'compliant':rack}
else:
 # Derive the exact reinforced/solid tooth recipes and their content-addressed
 # cache key. A clean checkout can rebuild them; no arbitrary cache selection.
 profile_source=(ROOT/'experiments/worm-rack/teeth_variants.py').read_text()
 profile_ns={'baseline_root':HERE/'baseline','cq':cq}
 exec(profile_source[profile_source.index('raw_source='):profile_source.index('variant_hash=')],profile_ns)
 strong_source=profile_ns['strong_source'];solid_source=profile_ns['solid_source']
 key=hashlib.sha256(strong_source.encode()+solid_source.encode()+(HERE/'baseline/experiments/worm-rack/model.py').read_bytes()+basefile.read_bytes()).hexdigest()
 caches=ROOT/'work/worm-teeth-cache/nema17-40'/key;caches.mkdir(parents=True,exist_ok=True);racks={}
 for style,preload in [('compliant',.1),('solid',-.1)]:
  source=caches/(f'{style}-{preload:g}.brep')
  if not source.exists():
   recipe=dict(ns);recipe['wall']=.9;exec(compile(strong_source if style=='compliant' else solid_source,'tooth-profile','exec'),recipe)
   m['ns']=recipe;shape=m['matched_rack'](preload);shape.exportBrep(str(source));m['ns']=ns
  axial_key=hashlib.sha256(source.read_bytes()+newsource[newsource.index('OUTPUT_PAD_SIZE='):newsource.index('\ncentral_relief_radius=')].encode()).hexdigest()
  axial_cache=WORK/(axial_key+'.brep')
  if axial_cache.exists():racks[style]=cq.Shape.importBrep(str(axial_cache))
  else:
   s=cq.Shape.importBrep(str(source));racks[style]=s.cut(rect(ns['right'],ns['right']+100,-150,150,-150,150)).fuse(ns['make_output_plate']()).clean();racks[style].exportBrep(str(axial_cache))
 rack=racks['solid']
for p in parts:
 if p['name']==RACK:p['shape']=rack
parts=[p for p in parts if not p['name'].startswith('M3 heat-set insert output')]
for y,z in ns['OUTPUT_MOUNTS']:
 face=ns['OUTPUT_FACE_X']-.3;shape=ring(2.3,1.6,5,(face-5,y,z),(1,0,0))
 parts.append(dict(name=f'M3 output insert {y:g} {z:g}',shape=shape,color='#d4a54a',group='rack',printed=False,embedded_host=RACK))
# A screw-adjusted carrier must be released before withdrawing the rack.
# Staged guides are defined below after clearance checks establish service paths.
def overlap(a,b):
 aa=a.BoundingBox();bb=b.BoundingBox()
 if any(getattr(aa,k+'max')<=getattr(bb,k+'min')+1e-7 or getattr(bb,k+'max')<=getattr(aa,k+'min')+1e-7 for k in 'xyz'):return 0.
 return max(0,a.intersect(b).Volume())
report={'passed':False,'drive':DRIVE,'stroke_mm':40,'source_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'adjustment_screws':4,'guide_bearings':6,'printed_snap_axles':6,'bearing_axle_bolts':0,'flexures':0}
def save():(OUT/'validation.json').write_text(json.dumps(report,indent=2))
# Compare only changed pairs; the retained rack/drive/enclosure use checked baselines.
changed={CHASSIS,CARRIER}|{p['name'] for p in parts if p['name'].startswith(('M3x20 adjustment','M3 carrier','625ZZ snap'))}
hits=[]
for a,b in itertools.combinations(parts,2):
 if a['name'] not in changed and b['name'] not in changed:continue
 v=overlap(a['shape'],b['shape'])
 if v>.01:
  cut=a['shape'].intersect(b['shape']);bb=cut.BoundingBox();hits.append(dict(parts=[a['name'],b['name']],volume_mm3=v,center=cut.Center().toTuple(),bounds=[bb.xmin,bb.xmax,bb.ymin,bb.ymax,bb.zmin,bb.zmax]))
report['static_collisions']=hits;save();print('Static collisions',hits,flush=True)
for n,s in [('chassis',frame),('carrier',carrier)]:s.exportBrep(str(WORK/(DRIVE+'-'+n+'.brep')))
scene=[]
for p in parts:
 vs,ts=p['shape'].tessellate(.08,.15);scene.append({k:v for k,v in p.items() if k not in ['shape','printShape']}|{'vertices':[v.toTuple() for v in vs],'triangles':ts})
(OUT/'preview.json').write_text(json.dumps(dict(parts=scene)))
assert not hits,'Resolve static collisions before validation/export'

# A BREP snapshot lets the independent path validator iterate without rebuilding
# the unchanged historical worm surfaces. Snapshots are local build products.
cache=WORK/DRIVE;cache.mkdir(exist_ok=True)
frame.cut(old).exportBrep(str(cache/'frame_added.brep'))
tray.cut(tray_original).exportBrep(str(cache/'tray_added.brep'))
records=[]
for i,p in enumerate(parts):
 record={k:v for k,v in p.items() if k not in ['shape','printShape']}
 for key in ['shape','printShape']:
  if key in p:
   filename=f'{i}-{key}.brep';p[key].exportBrep(str(cache/filename));record[key]=filename
 records.append(record)
for name,s in [('frame_without_pins',frame_without_pins),('carrier_without_pins',carrier_without_pins)]+[(f'rack_{k}',v) for k,v in racks.items()]:s.exportBrep(str(cache/(name+'.brep')))
state=dict(parts=records,bearings=bearings,adjust=ADJUST,drive=DRIVE,rackName=RACK,chassisName=CHASSIS,carrierName=CARRIER,trayName=TRAY,withdraw=ns['CASE_RIGHT']-ns['left']+240,rotationOrigin=list(m['ORIGIN']) if DRIVE=='worm' else list(ns['PIVOT']),rotationAxis=[1,0,0] if DRIVE=='worm' else [0,0,1],travelPerRevolution=m['LEAD'] if DRIVE=='worm' else 2*math.pi*ns['RP'],motorZ=m['MOTOR_Z'] if DRIVE=='worm' else 0,rackStyles=list(racks),changed=list(changed),report=report)
(cache/'state.json').write_text(json.dumps(state))
print('Snapshot ready',DRIVE,flush=True)
