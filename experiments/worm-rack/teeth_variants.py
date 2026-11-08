"""Build stronger compliant and solid racks over the unchanged checked worm chassis.
Run after model.py/build_presets.py: python experiments/worm-rack/teeth_variants.py --motor nema17 --stroke 40
"""
import argparse, pathlib, sys, json, gzip, hashlib, math, copy, zipfile, os
import cadquery as cq
import numpy as np
import fcl
from OCP.BRepTools import BRepTools
from OCP.BRepMesh import BRepMesh_IncrementalMesh
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--motor',choices=['nema17','nema14'],default='nema17');p.add_argument('--stroke',type=int,choices=[40,100,150],default=40);a=p.parse_args()
folder=ROOT/'dist/experiments/worm-rack'
if (a.motor,a.stroke)!=('nema17',40):folder=folder/'variants'/a.motor/str(a.stroke)
baseline=json.loads((folder/'validation.json').read_text());assert baseline['passed']
# Each preset keeps the exact source packaged with its checked baseline.
# Older presets predate the NEMA17/40 motor-flange revision.
baseline_root=ROOT/'work/worm-baselines'/f'{a.motor}-{a.stroke}'
with zipfile.ZipFile(folder/'worm-rack-experiment.zip') as bundle:
 for file in ['model.py','experiments/worm-rack/model.py','experiments/worm-rack/validate.py','experiments/worm-rack/flexures.py','experiments/worm-rack/enclosure.py']:
  dest=baseline_root/file;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(bundle.read(file))
for key,file in [('source_sha256','model.py'),('validation_source_sha256','validate.py'),('flexure_source_sha256','flexures.py'),('enclosure_source_sha256','enclosure.py')]:assert baseline[key]==hashlib.sha256((baseline_root/'experiments/worm-rack'/file).read_bytes()).hexdigest(),file
cache_link=baseline_root/'work';cache_link.symlink_to(ROOT/'work',target_is_directory=True) if not cache_link.exists() else None
model=baseline_root/'experiments/worm-rack/model.py';source=model.read_text();prefix=source[:source.index("exec(compile((ROOT/'experiments/worm-rack/validate.py')")]
sys.argv=[str(model),'--motor',a.motor,'--stroke',str(a.stroke)]
m={'__file__':str(model),'__name__':'rack_variant_base','BRepTools':BRepTools}
exec(compile(prefix,str(model),'exec'),m)
assert baseline['geometry_cache_sha256']==m['source_hash']
old_rack=m['rack'];parts=m['parts'];worm=m['worm'];overlap=m['overlap'];box=m['box'];pose=m['posed'];lead=m['LEAD'];origin=m['ORIGIN'];K=m['K'];tracks=m['TRACKS'];displacement=m['displacement']
base_ns=m['ns'];original_make=base_ns['make_rack']
raw_source=(baseline_root/'model.py').read_text();raw_source=raw_source[raw_source.index('def make_rack(preload):'):raw_source.index('\ncentral_relief_radius=')]
# Close the thin split tip with a rounded bridge and increase the two nominal
# flank walls from 0.6 to 0.9 mm. The external mating profile stays unchanged.
start=raw_source.index('  slot=');end=raw_source.index(' # Semicircular caps',start)
strong_slot="""  slot_y=TIP_Y+1.;tip_radius=half(slot_y)-wall
  assert tip_radius>.05
  slot=(cq.Workplane('XY').moveTo(x-tip_radius,slot_y)
        .threePointArc((x,slot_y-tip_radius),(x+tip_radius,slot_y))
        .lineTo(x+radius,ROOT_Y).lineTo(x+radius,cap_y)
        .threePointArc((x,RELIEF_Y),(x-radius,cap_y)).lineTo(x-radius,ROOT_Y)
        .close().extrude(8.2).translate((0,0,12.9)).val())
  rack=rack.fuse(tooth).cut(slot)
"""
strong_source=raw_source[:start]+strong_slot+raw_source[end:]
solid_source=raw_source[:raw_source.index('  radius=h1-wall;')]+"  rack=rack.fuse(tooth)\n"+raw_source[raw_source.index(' # Beveled faces'):]
variant_hash=hashlib.sha256(pathlib.Path(__file__).read_bytes()+model.read_bytes()+(baseline_root/'model.py').read_bytes()).hexdigest()
geometry_hash=hashlib.sha256(strong_source.encode()+solid_source.encode()+model.read_bytes()+(baseline_root/'model.py').read_bytes()).hexdigest()
cache=ROOT/'work/worm-teeth-cache'/f'{a.motor}-{a.stroke}'/geometry_hash;cache.mkdir(parents=True,exist_ok=True)
def make(style,preload):
 ns=dict(base_ns);ns['wall']=.9;exec(compile(strong_source if style=='compliant' else solid_source,'rack-tooth-section','exec'),ns);m['ns']=ns
 name=f'{style}-{preload:g}';dest=cache/(name+'.brep')
 if dest.exists():return cq.Shape.importBrep(str(dest))
 print('Building rack',a.motor,a.stroke,name,flush=True);shape=m['matched_rack'](preload);assert shape.isValid() and len(shape.Solids())==1;shape.exportBrep(str(dest));return shape
strong=make('compliant',.1);nominal=make('compliant',0);solid=make('solid',-.1)
def bvh(shape):
 BRepTools.Clean_s(shape.wrapped);BRepMesh_IncrementalMesh(shape.wrapped,.002,False,.04,True).Perform();vs,ts=shape.tessellate(1,.04)
 model=fcl.BVHModel();model.beginModel(len(vs),len(ts));model.addSubModel(np.array([v.toTuple() for v in vs]),np.array(ts));model.endModel();return model
objects={q['name']:fcl.CollisionObject(bvh(q['shape'])) for q in parts if q['group']!='rack'}
def transform(q,dx=0,e=0):
 theta=0.;translation=np.zeros(3)
 if e:
  translation,theta=displacement(q['group'],e)
  if 'lowerStation' in q:translation[2]+=m['guide_lift'](q['lowerStation'],e)
 elif q['group']=='rack':translation[0]=dx
 elif q.get('rotating'):theta=-dx/K*q.get('rotationFactor',1)
 c=math.cos(theta);s=math.sin(theta);rotation=np.array([[1,0,0],[0,c,-s],[0,s,c]]);pivot=np.array(q.get('rotationCenter',origin));translation=np.array(translation)+pivot-rotation@pivot
 return fcl.Transform(rotation,translation)
def hit(x,y):return bool(fcl.collide(x,y,fcl.CollisionRequest(num_max_contacts=1),fcl.CollisionResult()))
# Parts with changed spring geometry are remeshed once per original state.
springs={};base_rack_part=next(q for q in parts if q['name']=='Matched compliant rack')
phase_samples=sorted(set([lead*j/96 for j in range(97)]+list(np.linspace(-a.stroke/2,a.stroke/2,41))))
boundaries=sorted({0.,1.}|{t[k] for seq in tracks.values() for t in seq for k in ['start','end']});times={0.}
for lo,hi in zip(boundaries,boundaries[1:]):
 distance=max(math.dist(displacement(g,lo)[0],displacement(g,hi)[0]) for g in tracks);n=max(1,math.ceil(distance/.5));times.update(lo+(hi-lo)*j/n for j in range(1,n+1))
times=sorted(times)
reports={};rack_parts={};coupons={}
# All changed tooth walls and reliefs lie below the unchanged spine in this
# eight-mm-wide band. Check the whole band, including its retained material.
tooth_zone=box(4000,8.2,100,(0,m['Y'],m['SPINE_Z']+.01-50))
old_outside=old_rack.cut(tooth_zone)
for style,rack in [('compliant',strong),('solid',solid)]:
 print('Checking rack variant',style,flush=True)
 target=folder/'teeth'/style;target.mkdir(parents=True,exist_ok=True)
 rack_part=dict(base_rack_part,shape=rack);added=rack.intersect(tooth_zone);outside=rack.cut(tooth_zone)
 outside_difference=outside.cut(old_outside).Volume()+old_outside.cut(outside).Volume()
 print('Tooth band',style,added.Volume(),'outside difference',outside_difference,flush=True);assert outside_difference<.01
 rack_obj=fcl.CollisionObject(bvh(added));clear_rack=nominal if style=='compliant' else rack;clear_obj=fcl.CollisionObject(bvh(clear_rack.intersect(tooth_zone)));engagement_obj=fcl.CollisionObject(bvh(strong.intersect(tooth_zone)))
 report={'passed':False,'style':style,'variant_source_sha256':variant_hash,'base_validation_sha256':hashlib.sha256((folder/'validation.json').read_bytes()).hexdigest(),'tooth_band_y_mm':[m['Y']-4.1,m['Y']+4.1],'tooth_band_top_z_mm':m['SPINE_Z']+.01,'base_checks_reused':'Unchanged chassis, bearings, motor, enclosure, mounting interfaces and their internal installation paths use the existing matching-source validation. The complete changed tooth band is checked through all poses below; a solid difference check confirms all geometry outside that band matches the baseline. Nominal/solid worm engagement uses the complete tooth band and five additional full-rack solid checks.','outside_tooth_band_difference_mm3':outside_difference,'wall_mm':.9 if style=='compliant' else None,'previous_wall_mm':.6,'closed_tip':True,'flank_preload_mm':.1 if style=='compliant' else -.1,'solid_flank_relief_mm':.1 if style=='solid' else 0,'method':'OCC static intersections; 0.002 mm / 0.04 rad FCL candidates confirmed as OCC volumes. Reinforced nominal teeth or actual solid teeth must clear the worm. No strength, fatigue, wear or elastic preload simulation.'}
 def save():(target/'validation.json').write_text(json.dumps(report,indent=2))
 static=[];motion=[];exploded=[];mesh=[];engagement=[]
 for q in parts:
  if q['group']=='rack' or q['name']==m['WORM_NAME']:continue
  v=overlap(added,q['shape'])
  if v>.01:static.append(dict(part=q['name'],overlap_mm3=v))
 report['static_collisions']=static;save();assert not static,static
 for dx in phase_samples:
  rack_obj.setTransform(transform(rack_part,dx));clear_obj.setTransform(transform(rack_part,dx));engagement_obj.setTransform(transform(rack_part,dx))
  for q in parts:
   if q['group']=='rack':continue
   obj=objects[q['name']];obj.setTransform(transform(q,dx))
   if q['name']==m['WORM_NAME']:
    if hit(clear_obj,obj):
     v=overlap(clear_rack.translate((dx,0,0)),pose(q,dx))
     if v>.01:mesh.append(dict(travel_from_center_mm=dx,overlap_mm3=v))
    if not hit(engagement_obj,obj):engagement.append(dx)
   elif hit(rack_obj,obj):
    v=overlap(added.translate((dx,0,0)),pose(q,dx))
    if v>.01:motion.append(dict(part=q['name'],travel_from_center_mm=dx,overlap_mm3=v))
 report.update(motion_samples=len(phase_samples),motion_collisions=motion,mesh_collisions=mesh,loss_of_potential_engagement=engagement);save()
 print('Motion',style,len(motion),'mesh',len(mesh),flush=True)
 # Confirm nominal/solid phase clearances as solids even if triangle screening misses containment.
 mesh_rows=[]
 for dx in [-a.stroke/2,0,lead*.173,lead*.517,a.stroke/2]:
  w=m['spin'](worm,dx);mesh_rows.append(dict(travel_from_center_mm=dx,clearance_model_overlap_mm3=overlap(w,clear_rack.translate((dx,0,0))),actual_rack_overlap_mm3=overlap(w,rack.translate((dx,0,0)))))
 seen=set()
 for e in times:
  rack_obj.setTransform(transform(rack_part,e=e));clear_obj.setTransform(transform(rack_part,e=e))
  state=m['spring_key'](e)
  for q in parts:
   if q['group']=='rack':continue
   da=displacement('rack',e)[0];db=displacement(q['group'],e)[0]
   if 'lowerStation' in q:db[2]+=m['guide_lift'](q['lowerStation'],e)
   relative=tuple(round(da[i]-db[i],8) for i in range(3));theta=round(displacement(q['group'],e)[1],8)
   key=(q['name'],relative,theta,state if q['name']==m['CHASSIS_NAME'] else None)
   if key in seen:continue
   seen.add(key)
   obj=objects[q['name']]
   if q['name']==m['CHASSIS_NAME'] and state!=(0,0):
    if state not in springs:springs[state]=fcl.CollisionObject(bvh(m['spring_shape'](state)))
    obj=springs[state]
   obj.setTransform(transform(q,e=e));probe=clear_obj if q['name']==m['WORM_NAME'] else rack_obj
   if hit(probe,obj):
    r=clear_rack if q['name']==m['WORM_NAME'] else added
    v=overlap(r.translate(tuple(da)),pose(q,e=e))
    if v>.01:exploded.append(dict(part=q['name'],separation=e,overlap_mm3=v))
 report.update(explosion_samples=len(times),explosion_collisions=exploded,mesh_pose_checks=mesh_rows)
 # The mounting pad and complete bearing guide must match the checked original.
 low=base_ns['rail_shape'](3000);pad=box(40,80,50,(base_ns['right']+20,30,0))
 unchanged=[]
 for name,region in [('guide',low),('mount',pad)]:
  old=old_rack.intersect(region);new=rack.intersect(region);unchanged.append(dict(region=name,difference_mm3=old.cut(new).Volume()+new.cut(old).Volume()))
 report['unchanged_interfaces']=unchanged
 report['passed']=not(static or motion or mesh or engagement or exploded) and all(r['clearance_model_overlap_mm3']<.01 for r in mesh_rows) and (style!='solid' or all(r['actual_rack_overlap_mm3']<.01 for r in mesh_rows)) and all(r['difference_mm3']<.01 for r in unchanged) and rack.isValid() and len(rack.Solids())==1
 save();assert report['passed'],report
 BRepTools.Clean_s(rack.wrapped);vs,ts=rack.tessellate(.025,.1)
 name='Matched compliant rack' if style=='compliant' else 'Matched solid rack'
 part={k:v for k,v in base_rack_part.items() if k!='shape'};part.update(name=name,vertices=[[round(v.x,5),round(v.y,5),round(v.z,5)] for v in vs],triangles=ts)
 with gzip.open(target/'part.json.gz','wt') as f:json.dump({'part':part,'style':style,'wall':.9 if style=='compliant' else None,'preload':.1 if style=='compliant' else -.1,'revision':variant_hash},f,separators=(',',':'))
 shape=rack.rotate((0,0,0),(1,0,0),180);BRepTools.Clean_s(shape.wrapped);bb=shape.BoundingBox();shape=shape.translate((-bb.xmin,-bb.ymin,-bb.zmin));stl=cache/(style+'.stl');cq.exporters.export(shape,str(stl),tolerance=.025,angularTolerance=.1)
 # Reuse the common closed-mesh verifier without running its CAD generator.
 lead_source=(ROOT/'experiments/t8-leadscrew/model.py').read_text();fn=lead_source[lead_source.index('def verify_print_mesh('):lead_source.index('\ndef export(')]
 scope={};exec(fn,scope);report['print_mesh']=scope['verify_print_mesh'](stl);save()
 with gzip.open(target/'rack.stl.gz','wb',compresslevel=9) as f:f.write(stl.read_bytes())
 coupon=rack.intersect(box(44,70,40,(0,15,5))).rotate((0,0,0),(1,0,0),180);BRepTools.Clean_s(coupon.wrapped);bb=coupon.BoundingBox();coupon=coupon.translate((-bb.xmin,-bb.ymin,-bb.zmin));coupon_file=cache/(style+'-coupon.stl');cq.exporters.export(coupon,str(coupon_file),tolerance=.025,angularTolerance=.1);scope['verify_print_mesh'](coupon_file)
 with gzip.open(target/'coupon.stl.gz','wb',compresslevel=9) as f:f.write(coupon_file.read_bytes())
 reports[style]=report;rack_parts[style]=stl;coupons[style]=coupon_file
 print('Rack complete',a.motor,a.stroke,style,flush=True)
# One family bundle includes both racks, their reports and the unchanged chassis.
bundle=folder/'worm-rack-experiment.zip';temporary=cache/'bundle.zip'
with zipfile.ZipFile(bundle) as src,zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as dst:
 for info in src.infolist():
  if info.filename in ['stl/matched_compliant_rack.stl','stl/matched_solid_rack.stl','stl/rack_mesh_coupon.stl','stl/solid_rack_mesh_coupon.stl','experiments/worm-rack/teeth_variants.py'] or info.filename.startswith('teeth/'):continue
  dst.writestr(info,src.read(info.filename))
 for style,stl in rack_parts.items():
  dst.write(stl,'stl/matched_'+style+'_rack.stl');dst.write(folder/'teeth'/style/'validation.json','teeth/'+style+'/validation.json');dst.write(coupons[style],'stl/'+('rack_mesh_coupon.stl' if style=='compliant' else 'solid_rack_mesh_coupon.stl'))
 dst.write(pathlib.Path(__file__),'experiments/worm-rack/teeth_variants.py')
os.replace(temporary,bundle)
print('Both rack variants packaged',a.motor,a.stroke,flush=True)
