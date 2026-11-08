"""Validate the rigid-carrier variants and export STL/viewer data from BREP snapshots."""
import pathlib,sys,json,math,gzip,hashlib,itertools,zipfile,struct,collections
import cadquery as cq
import numpy as np
import fcl
from OCP.BRepTools import BRepTools
from OCP.BRepMesh import BRepMesh_IncrementalMesh
ROOT=pathlib.Path(__file__).resolve().parents[2];HERE=pathlib.Path(__file__).resolve().parent
DRIVE=sys.argv[1];CACHE=ROOT/'work/adjustable-rack'/DRIVE;OUT=ROOT/'dist/experiments/adjustable-rack'/DRIVE
state=json.loads((CACHE/'state.json').read_text());parts=state['parts'];report=state['report'];report['passed']=False
for p in parts:
 for key in ['shape','printShape']:
  if key in p:p[key]=cq.Shape.importBrep(str(CACHE/p[key]))
byname={p['name']:p for p in parts};frame=byname[state['chassisName']]['shape'];carrier=byname[state['carrierName']]['shape'];rack=byname[state['rackName']]['shape'];bearings=state['bearings']
def cyl(r,h,c,u=(0,0,1),t=0):return cq.Solid.makeCylinder(r,h,cq.Vector(*at(c,u,t)),cq.Vector(*u))
def at(c,u,t):return tuple(c[i]+u[i]*t for i in range(3))
def ring(ro,ri,h,c,u,t=0):return cyl(ro,h,c,u,t).cut(cyl(ri,h,c,u,t))
lead=(ROOT/'experiments/t8-leadscrew/model.py').read_text();exec(compile((ROOT/'experiments/adjustable-rack/snap_axles.py').read_text(),'snap_axles','exec'),globals());exec(compile(lead[lead.index('def verify_print_mesh'):lead.index('\ndef export(')],'mesh_verification','exec'),globals())
def overlap(a,b):
 aa=a.BoundingBox();bb=b.BoundingBox()
 if any(getattr(aa,k+'max')<=getattr(bb,k+'min')+1e-7 or getattr(bb,k+'max')<=getattr(aa,k+'min')+1e-7 for k in 'xyz'):return 0.
 return max(0,a.intersect(b).Volume())
def save():(OUT/'validation.json').write_text(json.dumps(report,indent=2))
# Animated compression affects the pins only; roots and bearing seats stay rigid.
snap_states={}
for host,kind,keys in [(state['chassisName'],'upper',['front','rear']),(state['carrierName'],'lower',['lower'])]:
 base=cq.Shape.importBrep(str(CACHE/('frame_without_pins.brep' if kind=='upper' else 'carrier_without_pins.brep')))
 snap_states[host]={}
 for key in keys:
  shape=base
  for b in bearings:
   if b['kind']!=kind:continue
   compress=key=='lower' or (key=='front' and b['index']<2) or (key=='rear' and b['index']>=2)
   shape=shape.fuse(snap_pin(b['center'],b['axis'],.45 if compress else 0))
  solids=sorted(shape.clean().Solids(),key=lambda q:q.Volume(),reverse=True)
  assert all(s.Volume()<.01 for s in solids[1:])
  snap_states[host][key]=solids[0]
# Shared viewer/validation tracks. Reverse these tracks to assemble.
def track(a,b,d=(0,0,0),r=0):return dict(start=a,end=b,delta=list(d),radians=r)
T={p['group']:[] for p in parts};distance=math.ceil(state['withdraw']/state['travelPerRevolution'])*state['travelPerRevolution'];turn=-distance*2*math.pi/state['travelPerRevolution']
T['cover_screws']=[track(0,.05,(0,0,55)),track(.05,.08,(0,-180,0))];T['cover']=[track(.08,.12,(0,0,100))]
T['rack']=[track(.16,.32,(distance,0,0))]
T['adjust_screws']=[track(.12,.16,(0,0,1)),track(.32,.35,(0,0,40)),track(.35,.38,(0,100,0))]
release=[track(.12,.16,(0,0,-1))];unseat=([track(.72,.74,(0,0,6)),track(.74,.75,(-2.8,0,0)),track(.75,.76,(0,0,40))] if DRIVE=='worm' else [track(.72,.74,(0,0,6)),track(.74,.76,(-10,0,0))])
T['fixed']=unseat;T['carrier']=release+unseat+[track(.80,.88,(150,0,0))]
T['chassis_screws']=[track(.68,.70,(0,0,24)),track(.70,.72,(0,-90,0))];T['tray']=[track(.76,.80,(0,0,-80))]
for p in parts:
 if p['group'] in ['carrier','lower_bearings']:p['adjustable']=True
 if p.get('bearing'):
  b=p['bearing'];i=b['index'];u=b['axis'];g='snap_'+str(i);p['group']=g
  if i<4:
   a,btime=(.38,.40) if i<2 else (.44,.46)
   T[g]=[track(a,btime,tuple(-9*v for v in u)),track(btime,btime+.02,(0,0,(50 if i<2 else 30)+(20 if DRIVE=='worm' else 0))),track(btime+.02,btime+.04,(-100 if i%2==0 else 100,0,0))]
  else:T[g]=T['carrier']+[track(.88,.90,(0,-9,0)),track(.90,.93,(0,0,30))]
if DRIVE=='spur':
 for p in parts:
  if p['group'] in ['gear','shaft','set_screw']:p['rotating']=True
 T['gear']=[track(.16,.32,r=turn),track(.53,.56,(0,0,20)),track(.56,.58,(0,-55,0))]
 T['set_screw']=[track(.16,.32,r=turn),track(.50,.53,(0,-28,0))]
 T['shaft']=[track(.16,.32,r=turn),track(.62,.68,(0,0,-80))]
 T['motor']=[track(.62,.68,(0,0,-80))]
 T['motor_screws']=[track(.58,.60,(0,0,21)),track(.60,.62,(0,-80,0))]
else:
 wind=[track(.16,.32,r=turn)];withdraw=[track(.63,.68,(-220,0,0))]
 T['front_fastener']=wind+[track(.50,.54,(55,0,0))];T['front_spacer']=wind+[track(.54,.57,(0,0,50)),track(.57,.60,(100,0,0))]
 T['motor']=withdraw;T['worm']=wind+withdraw;T['front_insert']=wind+withdraw
 T['front_bearing']=unseat
 T['rear_support_screws']=[track(.68,.70,(0,0,8))]+unseat
 for p in parts:
  if p['name'].startswith('M3x8 rear motor support screw'):p['group']='rear_support_screws'
 for p in parts:
  if p['group'].startswith('motor_screw'):
   g=p['group'];z=p['shape'].Center().z;T[g]=[track(.57,.60,(11,0,0)),track(.60,.63,(0,0,60 if z>state['motorZ'] else -50)),track(.63,.68,(-70,0,0))]
stages=[dict(start=a,end=b,label=s) for a,b,s in [(0,.08,'Remove and park lid screws'),(.08,.12,'Lift cover'),(.12,.16,'Loosen four adjustment screws; lower the carrier 1 mm'),(.16,.32,'Withdraw rack while turning the drive'),(.32,.38,'Remove four carrier adjustment screws'),(.38,.44,'Compress front snap pins; remove and park bearings'),(.44,.50,'Compress rear snap pins; remove and park bearings'),(.50,.68,'Remove drive fasteners and motor'),(.68,.72,'Remove chassis screws; back out captive support screws' if DRIVE=='worm' else 'Remove chassis screws'),(.72,.76,'Lift 6 mm, shift rearward 2.8 mm, then lift clear' if DRIVE=='worm' else 'Lift chassis 6 mm, then slide rearward 10 mm'),(.76,.80,'Lower enclosure tray off the chassis'),(.80,.88,'Slide shared carrier out of its open-ended guides'),(.88,.93,'Compress lower snap pins; remove both bearings'),(.93,1.001,'Disassembled — reverse to assemble; inserts and captive support screws stay installed' if DRIVE=='worm' else 'Disassembled — reverse to assemble; inserts stay installed')]]
snapStages=[dict(start=.379999,end=.400001,key='front'),dict(start=.439999,end=.460001,key='rear'),dict(start=.879999,end=.900001,key='lower')]
def displacement(p,t):
 d=np.zeros(3);angle=0
 for q in T[p['group']]:
  f=max(0,min(1,(t-q['start'])/(q['end']-q['start'])));d+=np.array(q['delta'])*f;angle+=q['radians']*f
 return d,angle
origin=np.array(state['rotationOrigin']);axis=np.array(state['rotationAxis'])
def pose(p,t=0,dx=0,release=0):
 if t:d,angle=displacement(p,t)
 else:d=np.array([dx if p['group']=='rack' else 0,0,-release if p.get('adjustable') else release if p['group']=='adjust_screws' else 0]);angle=-dx*2*math.pi/state['travelPerRevolution'] if p.get('rotating') else 0
 c=math.cos(angle);s=math.sin(angle)
 R=np.array([[1,0,0],[0,c,-s],[0,s,c]]) if DRIVE=='worm' else np.array([[c,-s,0],[s,c,0],[0,0,1]])
 return R,d+origin-R@origin,angle

def shape_at(p,t=0,dx=0,release=0,reduced=False):
 shape=motion_shapes.get(p['name'],p['shape']) if reduced else p['shape']
 for s in snapStages:
  if s['start']<=t<=s['end'] and s['key'] in snap_states.get(p['name'],{}):shape=snap_states[p['name']][s['key']]
 R,d,a=pose(p,t,dx,release)
 if a:shape=shape.rotate(tuple(origin),tuple(origin+axis),math.degrees(a))
 # d includes pivot compensation already applied by CQ.rotate.
 return shape.translate(tuple(d-origin+R@origin))
report['motion_inheritance']='For chassis and tray, motion checks use exact added-material differences against the pinned baseline. Removing material cannot introduce a collision. All new carrier, screws, inserts and snap pins are checked; full solids are used for assembly.'
report['method']='Exact OCC solid checks for changed assembled pairs, bearing seats, continuous axial snap-in corridors and screw tool corridors. Full 40 mm travel sampled at 1 mm and carrier adjustment at 0.1 mm. Assembly paths sampled at <=1 mm translation, FCL mesh candidates confirmed with OCC solids; same tracks drive the viewer. Not FEA or a load rating.'
report['guide_contact_inheritance']='625ZZ rings and their nominal centers are unchanged from the baseline. Existing nominal running contact is retained; released lower-bearing poses and every changed snap-axle/support solid are checked.'
report['limits']=['PETG pin strain, creep, wear and stiffness require physical tests.','Rigid guide preload is set by hand, not by a validated torque specification. Tighten evenly only until play is removed.','The tooth profiles and their original compliant/solid engagement are retained; no new tooth-load rating.','Assembly collision checking is sampled, not a continuous-motion proof.']
# Continuous snap corridor, inner-ring seat and retention geometry.
rows=[]
for b in bearings:
 c=b['center'];u=b['axis'];host=frame if b['kind']=='upper' else carrier
 support= cq.Shape.importBrep(str(CACHE/('frame_without_pins.brep' if b['kind']=='upper' else 'carrier_without_pins.brep')))
 annulus=ring(7.95,4.15,1.95,c,u,2.5);front=ring(7.95,4.15,.75,c,u,-3.25);land=ring(3.9,2.8,2,c,u,2.5)
 swept=ring(8,2.5,13,c,u,-10.5);pin=snap_pin(c,u);compressed=snap_pin(c,u,.45)
 row=dict(bearing=b['index']+1,seat_missing_mm3=land.cut(host).Volume(),outer_race_recess_overlap_mm3=overlap(host,annulus)+overlap(host,front),snap_corridor_overlap_mm3=overlap(swept,compressed)+overlap(swept,support),retaining_head_interference_mm3=overlap(pin,ring(8,2.5,5,c,u,-3.15)))
 rows.append(row)
report['snap_axles']=rows;save();print('Snap checks',rows,flush=True)
# Tool corridors extend from seated heads to above the housing.
toolhits=[]
for i,(x,y) in enumerate(state['adjust']):
 tool=cyl(3,80,(x,y,7))
 for p in parts:
  if p['group'] in ['cover','cover_screws']:continue
  v=overlap(tool,p['shape'])
  if v>.01:toolhits.append(dict(screw=i+1,part=p['name'],volume_mm3=v))
report['adjustment_tool_collisions']=toolhits;save();print('Tool checks',toolhits,flush=True)
# Dense broad phase. OCC confirms every mesh candidate; initial containment was
# already checked with exact solids during construction.
def bvh(s):
 BRepTools.Clean_s(s.wrapped);BRepMesh_IncrementalMesh(s.wrapped,.01,False,.08,True).Perform();vs,ts=s.tessellate(1,.08)
 m=fcl.BVHModel();m.beginModel(len(vs),len(ts));m.addSubModel(np.array([v.toTuple() for v in vs]),np.array(ts));m.endModel();return m
objects={p['name']:fcl.CollisionObject(bvh(p['shape'])) for p in parts}
motion_shapes={state['chassisName']:cq.Shape.importBrep(str(CACHE/'frame_added.brep')),state['trayName']:cq.Shape.importBrep(str(CACHE/'tray_added.brep'))}
motion_objects={n:fcl.CollisionObject(bvh(s)) for n,s in motion_shapes.items() if s.Solids()}
snap_objects={n:{k:fcl.CollisionObject(bvh(s)) for k,s in states.items()} for n,states in snap_states.items()}
changed=set(state['changed'])|{state['trayName']}|{p['name'] for p in parts if p['group']=='cover' or 'lid -60 ' in p['name']}
def exempt(a,b):
 # Existing heat-set interference and the retained drive tooth fit.
 if a.get('embedded_host')==b['name'] or b.get('embedded_host')==a['name']:return True
 return (a['group']=='rack' and b['group'] in ['gear','worm']) or (b['group']=='rack' and a['group'] in ['gear','worm'])
pairs=[(a,b) for a,b in itertools.combinations(parts,2) if not exempt(a,b)]
extra_static=[]
for a,b in pairs:
 if not (a['name']==state['trayName'] or b['name']==state['trayName'] or a['group']=='cover' or b['group']=='cover' or 'lid -60 ' in a['name'] or 'lid -60 ' in b['name']):continue
 v=overlap(a['shape'],b['shape'])
 if v>.01:extra_static.append(dict(parts=[a['name'],b['name']],volume_mm3=v))
report['enclosure_static_collisions']=extra_static;save();print('Enclosure static checks',extra_static,flush=True)

exact_cache={}
def check(t=0,dx=0,release=0,assembly=False,only_rack=False):
 current={};poses={};posekeys={};snapkeys={};fail=[]
 for p in parts:
  n=p['name'];o=objects[n];snapkeys[n]='rest'
  for s in snapStages:
   if s['start']<=t<=s['end'] and s['key'] in snap_objects.get(n,{}):o=snap_objects[n][s['key']];snapkeys[n]=s['key']
  R,d,angle=pose(p,t,dx,release);o.setTransform(fcl.Transform(R,d));current[n]=o;poses[n]=(R,d);posekeys[n]=tuple(np.round(R.flatten(),9))+tuple(np.round(d,9))
  if n in motion_objects:motion_objects[n].setTransform(fcl.Transform(R,d))
 for a,b in pairs:
  na=a['name'];nb=b['name']
  if only_rack and state['rackName'] not in [na,nb]:continue
  guide=a.get('bearing') if b['group']=='rack' else b.get('bearing') if a['group']=='rack' else None
  # Guide ring solids/centers are copied directly from the checked baseline.
  # Only changed poses need another clearance check; the new pin/seat solids
  # remain in the changed chassis/carrier checks.
  if guide and ((guide['kind']=='upper' and t<=.32) or (guide['kind']=='lower' and ((not assembly and release==0) or (assembly and t<=.12)))):continue
  if only_rack and (a.get('bearing',{}).get('kind')=='upper' or b.get('bearing',{}).get('kind')=='upper'):continue
  if not assembly and na not in changed and nb not in changed:continue
  if posekeys[na]==posekeys[nb]:continue
  reduced_a=(not assembly or only_rack) and na in motion_objects and b['group'] in ['rack','worm','gear','shaft','set_screw']
  reduced_b=(not assembly or only_rack) and nb in motion_objects and a['group'] in ['rack','worm','gear','shaft','set_screw']
  oa=motion_objects[na] if reduced_a else current[na];ob=motion_objects[nb] if reduced_b else current[nb]
  if not fcl.collide(oa,ob,fcl.CollisionRequest(num_max_contacts=1),fcl.CollisionResult()):continue
  Ra,da=poses[na];Rb,db=poses[nb];key=(assembly,reduced_a,reduced_b,na,nb,snapkeys[na],snapkeys[nb],tuple(np.round((Ra.T@Rb).flatten(),7)),tuple(np.round(Ra.T@(db-da),7)))
  if key not in exact_cache:exact_cache[key]=overlap(shape_at(a,t,dx,release,reduced_a),shape_at(b,t,dx,release,reduced_b))
  v=exact_cache[key]
  if v>.02:fail.append(dict(parts=[na,nb],t=round(t,6),travel=dx,release=release,volume_mm3=v))
 return fail
motion=[]
for dx in range(-20,21):
 for rel in [0,1]:motion.extend(check(dx=dx,release=rel))
 print('Travel',dx,flush=True) if dx%10==0 else None
for rel in np.linspace(0,1,11):motion.extend(check(release=float(rel)))
report['motion_collisions']=motion;report['motion_samples']=93;save();print('Motion collisions',motion[:30],flush=True)
bounds=sorted({0.,1.}|{q[k] for seq in T.values() for q in seq for k in ['start','end']});times={0.}
for lo,hi in zip(bounds,bounds[1:]):
 distance=max(np.linalg.norm(displacement(p,hi)[0]-displacement(p,lo)[0]) for p in parts);n=max(1,math.ceil(distance))
 times.update(lo+(hi-lo)*j/n for j in range(1,n+1))
fail=[]
for i,t in enumerate(sorted(times)):
 hits=check(t=t,assembly=True);fail.extend(hits)
 if hits:print('Assembly collision',hits[:4],flush=True)
 if i%40==0:print('Assembly sample',i,len(times),round(t,4),flush=True)
 if len(fail)>100:break
report['assembly_collisions']=fail;report['assembly_samples']=i+1;report['assembly_samples_planned']=len(times);save()
variant_fail=[]
if DRIVE=='worm' and not fail and not motion:
 # The reinforced profile retains the same guide rail and output flange. Its
 # inherited upper-bearing contact is unchanged. Check the replacement tooth
 # profile against all added material, the shared carrier and its fasteners.
 rp=byname[state['rackName']];original=rp['shape'];old_object=objects[rp['name']]
 rp['shape']=cq.Shape.importBrep(str(CACHE/'rack_compliant.brep'));objects[rp['name']]=fcl.CollisionObject(bvh(rp['shape']));exact_cache.clear()
 for dx in range(-20,21):variant_fail.extend(check(dx=dx,only_rack=True))
 for t in sorted(times):variant_fail.extend(check(t=t,assembly=True,only_rack=True))
 rp['shape']=original;objects[rp['name']]=old_object
 report['reinforced_teeth_collisions']=variant_fail;report['reinforced_teeth_samples']=41+len(times)
 report['reinforced_teeth_inheritance']='Existing reinforced tooth/drive fit and unchanged upper guide contact retained. Added chassis/tray material and all new carrier/fastener geometry checked across motion and assembly.'
 save();print('Reinforced rack checks',variant_fail[:5],flush=True)
passed=not variant_fail and not extra_static and not toolhits and not motion and not fail and all(q['seat_missing_mm3']<.01 and q['outer_race_recess_overlap_mm3']<.01 and q['snap_corridor_overlap_mm3']<.01 and q['retaining_head_interference_mm3']>.01 for q in rows)
# Export previews even after a failed path check, but never label them verified.
def mesh(shape):
 BRepTools.Clean_s(shape.wrapped);vs,ts=shape.tessellate(.05,.12);return dict(vertices=[[round(v.x,6),round(v.y,6),round(v.z,6)] for v in vs],triangles=ts)
scene=[]
for p in parts:
 record={k:v for k,v in p.items() if k not in ['shape','printShape']};record.update(mesh(p['shape']));record['zipEntry']='stl/'+('solid_rack' if DRIVE=='worm' and p['name']==state['rackName'] else p['name'].lower().replace(' ','_'))+'.stl'
 if p['name'] in snap_states:record['snapStates']={k:mesh(s) for k,s in snap_states[p['name']].items()}
 scene.append(record)
data=dict(parts=scene,tracks=T,stages=stages,snapStages=snapStages,rotationOrigin=state['rotationOrigin'],rotationAxis=state['rotationAxis'],travelPerRevolution=state['travelPerRevolution'],revision=hashlib.sha256((HERE/'model.py').read_bytes()+pathlib.Path(__file__).read_bytes()).hexdigest())
with gzip.open(OUT/'assembly.json.gz','wt') as f:json.dump(data,f,separators=(',',':'))
for style in state['rackStyles']:
 shape=cq.Shape.importBrep(str(CACHE/('rack_'+style+'.brep')))
 with gzip.open(OUT/(style+'.json.gz'),'wt') as f:json.dump(mesh(shape)|dict(zipEntry=f'stl/{style}_rack.stl',name=('Solid rack' if style=='solid' else 'Reinforced compliant rack') if DRIVE=='worm' else state['rackName']),f,separators=(',',':'))
if not passed:print('Validation failed; viewer exported for inspection',flush=True);sys.exit(1)
meshdir=CACHE/'stl';meshdir.mkdir(exist_ok=True);meshchecks=[]
for p in parts:
 if not p['printed']:continue
 shape=p.get('printShape',p['shape']);assert shape.isValid() and len(shape.Solids())==1,p['name']
 filename=('solid_rack' if DRIVE=='worm' and p['name']==state['rackName'] else p['name'].lower().replace(' ','_'))+'.stl';dest=meshdir/filename
 bb=shape.BoundingBox();shape=shape.translate((-bb.xmin,-bb.ymin,-bb.zmin));cq.exporters.export(shape,str(dest),tolerance=.025,angularTolerance=.10);meshchecks.append(verify_print_mesh(dest))
for style in state['rackStyles']:
 shape=cq.Shape.importBrep(str(CACHE/('rack_'+style+'.brep')));bb=shape.BoundingBox();shape=shape.translate((-bb.xmin,-bb.ymin,-bb.zmin));dest=meshdir/(style+'_rack.stl');cq.exporters.export(shape,str(dest),tolerance=.025,angularTolerance=.10);meshchecks.append(verify_print_mesh(dest))
report['stl_checks']=meshchecks;report['validator_sha256']=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest();report['passed']=True;save()
notes=f'''# NEMA17 40 mm {DRIVE} — screw-adjusted guide variant

Separate prototype. Original flexure chassis remains available.

- Six 625ZZ guide bearings (5 × 16 × 5 mm), on six integral PETG snap axles.
- One rigid carrier holds both lower bearings, 76 mm apart. Four M3×20 socket screws pull the carrier upward; four M3 heat-set inserts (4.6 mm OD × 5 mm long) provide its threads. Pilot diameter 4.2 mm. Confirm the pilot on a coupon for your insert and printer.
- 1 mm release travel, guided carrier edges, four-point adjustment. Tighten evenly in small increments until play disappears and the rack still slides freely. No torque or load rating is established.
- Each axle has a 4.8 mm shank, split 1.2 mm relief with rounded root, and two tapered retaining ears (5.6 mm maximum width). Bearing support land Ø7.8 mm touches the inner ring; the outer ring has a recessed seat.
- Retain the 42 mm output plate with axial 31 × 31 mm NEMA17 mounting pattern.
- Worm shaft bearing and its axial fastener remain unchanged; the six rack-guide bearings use snap axles.

## Assembly

Follow the Assembly slider in reverse. Install heat-set inserts before placing the carrier. Snap guide bearings on while supporting the axle root; do not force a bearing if the printed ears cannot compress freely. Assemble carrier into the open-ended guides, then enclosure, motor/drive and rack. Fit the four adjustment screws and set them evenly after inserting the rack. Close the cover last. The worm's two rear support screws back out 8 mm and stay with the chassis during removal. To service, loosen/release the carrier before withdrawing the rack. The animation shows the split pins compressing schematically; this is not a PETG stress simulation.

## Printing and scope

STLs are in millimeters, one mesh per printed part. Check orientation and supports in your slicer; keep support out of the split slots and bearing running surfaces. Validate snap fit with a test print before committing to the full chassis. PETG creep, pin fatigue, screw torque, loaded rigidity and service life have not been measured. The report describes sampled geometric checks and their limits.

Use this variant's chassis, carrier and enclosure tray together. Do not mix its tray with the earlier flexure chassis.
'''
(OUT/'README.md').write_text(notes)
with zipfile.ZipFile(OUT/'adjustable-rack.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in sorted({q['file'] for q in meshchecks}):z.write(meshdir/name,'stl/'+name)
 z.write(OUT/'README.md','README.md');z.write(OUT/'validation.json','validation.json')
 for f in list(HERE.glob('*.py'))+list((HERE/'baseline').rglob('*.py'))+[ROOT/'model.py',ROOT/'experiments/t8-leadscrew/model.py',ROOT/'experiments/worm-rack/teeth_variants.py',HERE/'README.md',ROOT/'requirements.txt',ROOT/'experiments/worm-rack/requirements.txt']:
  if '/work/' not in str(f.relative_to(ROOT)):z.write(f,'source/'+str(f.relative_to(ROOT)))
print('VALIDATED AND EXPORTED',DRIVE,flush=True)
