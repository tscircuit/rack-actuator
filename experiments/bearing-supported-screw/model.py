"""Independent 6805 supported printed-screw experiment. Units: mm.

Extract the existing screw construction without executing or changing its generator.
Only an additive bearing seat/shoulder is fused to that screw. Hardware is reference
geometry, not a manufacturing drawing. Run with the project's CadQuery Python.
"""
import ast, collections, gzip, hashlib, json, math, pathlib, struct, zipfile
import cadquery as cq
import importlib.util
_spec=importlib.util.spec_from_file_location("holder_geometry",pathlib.Path(__file__).with_name("holder_geometry.py"))
_holder=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_holder)

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'dist/experiments/bearing-supported-screw'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / 'experiments/t8-leadscrew/model.py'
tree = ast.parse(SOURCE.read_text())
LEAD, SCREW_Z, AXIS, ROD_END = 8., 42., (1, 0, 0), 152.
helpers = {'box', 'rect', 'at', 'cyl', 'xcyl', 'hex_prism', 'd_shaft', 'ring', 'bolt', 'helical_ridge', 'verify_print_mesh'}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in helpers], type_ignores=[]), str(SOURCE), 'exec'))
# Evaluate exactly the old male/hub construction, excluding its exports and carriage.
nodes = []
for n in tree.body:
    if isinstance(n, ast.If) and isinstance(n.test, ast.Name) and n.test.id == 'PRINTED':
        for statement in n.body:
            if isinstance(statement, ast.Assign) and any(isinstance(t, ast.Name) and t.id in {'male', 'shaft_bore', 'hub', 'nut_pocket', 'printed_screw'} for t in statement.targets):
                nodes.append(statement)
exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), 'exec'))
original_screw = printed_screw

def annulus(ro, ri, x0, x1):
    return xcyl(ro, x1-x0, x0).cut(xcyl(ri, x1-x0, x0))

# 1 mm shorter projection: wall front X4 to holder front X34.3 = 30.3.
# Recess opens toward the motor. The bearing's front outer race bears on the lip.
HOLDER_BACK, HOLDER_FRONT = 24.2, 34.3
BEARING_BACK, BEARING_FRONT = 24.3, 31.3
seat = xcyl(12.45, 7., BEARING_BACK).fuse(xcyl(13.5, 2., BEARING_BACK-2))
seat = seat.cut(xcyl(7.9, 9.2, BEARING_BACK-2.1))
# Keep the original coupling split open through the added shoulder/journal.
seat = seat.cut(rect(8,26,0,14,41.5,42.5))
screw = original_screw.fuse(seat).clean()
holes = [(y, 42+z) for y in (-15.5,15.5) for z in (-15.5,15.5)]
wall = rect(0,4,-32,32,16,68).cut(xcyl(11.3,4,0))
holder, holder_holes, holder_columns = _holder.make_holder(4,BEARING_BACK,BEARING_FRONT,HOLDER_FRONT)
for y,z in holes+holder_holes:wall=wall.cut(xcyl(1.7,4,0,y,z))

# Internal race/shield geometry is illustrative; d/D/B are authoritative.
inner = annulus(13.5,12.5,BEARING_BACK,BEARING_FRONT)
outer = annulus(18.5,17.5,BEARING_BACK,BEARING_FRONT)
shield = annulus(17.4,13.6,BEARING_BACK+.15,BEARING_FRONT-.15)
motor = rect(-40,0,-21,21,21,63).fuse(xcyl(11,2,0)).cut(xcyl(2.6,2.2,-.1))
for y,z in holes:
    motor = motor.cut(xcyl(1.65,7,-6,y,z))
shaft = xcyl(2.5,4,0).fuse(d_shaft(2.5,2.,20,4))

parts=[]
def add(name, shape, color, printed=False, group='fixed', stage=0, vector=(0,0,0)):
    shape=shape.clean()
    assert shape.isValid() and len(shape.Solids())==1, (name,'invalid solid')
    parts.append(dict(name=name,shape=shape,color=color,printed=printed,group=group,stage=stage,vector=vector))

add('NEMA17 motor reference',motor,'#26394a',stage=2,vector=(-300,0,0))
add('NEMA17 D shaft reference',shaft,'#b7c8d5',group='motorRotor',stage=2,vector=(-300,0,0))
add('4 mm NEMA17 wall',wall,'#7195a0',True,stage=3,vector=(-260,0,0))
add('Bearing holder',holder,'#39556c',True)
add('Printed lead screw with bearing seat',screw,'#e8b84a',True,'rotor',stage=4,vector=(-190,0,0))
for name,shape,color,group in [('6805 inner race reference',inner,'#c2ced7','bearingRotor'),('6805 outer race reference',outer,'#a2b1bd','fixed'),('6805 shield envelope reference',shield,'#718290','fixed')]:
    add(name,shape,color,group=group,stage=5,vector=(-55,0,0))
add('M3x12 shaft clamp bolt',bolt(1.45,12,2.75,3,(17,5,33)),'#94a3b8',group='rotor',stage=4,vector=(-190,0,0))
add('M3 shaft clamp nut',hex_prism(5.5,2.4,(17,5,34.5)).cut(cyl(1.55,2.6,(17,5,34.4))),'#b7c8d5',group='rotor',stage=4,vector=(-190,0,0))
for i,(y,z) in enumerate(holes):
    add(f'M3x10 motor bolt {i+1}',bolt(1.45,10,2.75,3,(-6,y,z),AXIS),'#a5b7c5')
for i,(y,z) in enumerate(holder_holes):
    # Rear-loaded bolt: washer at the wall rear and exposed nut at the front.
    add(f'M3x45 holder tie bolt {i+1}',bolt(1.45,45,2.75,3,(44.5,y,z),(-1,0,0)),'#a5b7c5')
    add(f'M3 holder front washer {i+1}',ring(3.5,1.6,.5,(HOLDER_FRONT,y,z),AXIS),'#b7c8d5')
    add(f'M3 holder rear washer {i+1}',ring(3.5,1.6,.5,(-.5,y,z),AXIS),'#b7c8d5')
    add(f'M3 holder locknut {i+1}',_holder.axial_locknut(HOLDER_FRONT+.5,y,z),'#b7c8d5')

def explosion_offset(p,t):
    def ramp(a,b):return max(0.,min(1.,(t-a)/(b-a)))
    name=p['name']
    if 'holder tie bolt' in name:return [-55*ramp(0,.1),math.copysign(45,p['shape'].Center().y)*ramp(.1,.2),0]
    if 'holder front washer' in name or 'holder locknut' in name:return [10*ramp(0,.1),math.copysign(45,p['shape'].Center().y)*ramp(.1,.2),0]
    if 'holder rear washer' in name:return [-20*ramp(0,.1),math.copysign(45,p['shape'].Center().y)*ramp(.1,.2),0]
    if name.startswith('M3x10 motor bolt'):return [60*ramp(.5,.6),0,0]
    if name.startswith('NEMA17'):return [-120*ramp(.6,.7),0,0]
    if name=='4 mm NEMA17 wall':return [-80*ramp(.7,.8),0,0]
    delta=[30*ramp(.2,.35),0,100*ramp(.35,.5)]
    if p['group']=='rotor':delta[0]-=190*ramp(.8,.9)
    if name.startswith('6805 '):delta[0]-=55*ramp(.9,1)
    return delta
for p in parts:p['explodeKeyframes']=[dict(t=t,offset=explosion_offset(p,t)) for t in [0,.1,.2,.35,.5,.6,.7,.8,.9,1]]

def overlap(a,b):
    return max(0.,a.intersect(b).Volume())

def validate():
    print('Checking assembled clearances, rotation and additive-only screw change',flush=True)
    collisions=[]
    for i,a in enumerate(parts):
        for b in parts[i+1:]:
            v=overlap(a['shape'],b['shape'])
            if v>1.e-5:collisions.append([a['name'],b['name'],v])
    assert not collisions,collisions
    removed=original_screw.cut(screw).Volume()
    outside=screw.cut(original_screw).cut(seat).Volume()
    assert abs(removed)<1e-5 and abs(outside)<1e-5
    # Exact original clamp voids and all original screw material stay intact.
    assert overlap(screw,shaft_bore)<1e-5
    assert overlap(screw,rect(8,26,0,14,41.5,42.5))<1e-5
    sweep=xcyl(11,13.3,9).fuse(xcyl(13.5,2,22.3)).fuse(xcyl(12.45,7,24.3)).fuse(xcyl(10.1,120.7,31.3))
    for name,shape in [('wall',wall),('holder',holder)]:
        assert overlap(sweep,shape)<1e-5,('rotation envelope',name)
    tool=cyl(1.5,35,(17,5,48))
    assert overlap(tool,holder)+overlap(tool,wall)<1e-5
    insertion_checks=[]
    for y,z in holder_holes:
        envelope=xcyl(1.6,100,-55.5,y,z).fuse(xcyl(3.25,58.5,-59,y,z))
        for name,obstacle in [('holder',holder),('wall',wall),('motor',motor),('screw',screw),('bearing',inner.fuse(outer).fuse(shield))]:
            assert overlap(envelope,obstacle)<1e-5,('straight holder bolt insertion',y,z,name)
        insertion_checks.append(dict(center_yz_mm=[y,z],straight_rear_loading=True,passed=True))
    # The separate motor screws are fitted before the support module.
    for y,z in holes:assert overlap(xcyl(3,40,4,y,z),wall)<1e-5
    # The bearing loads from behind the holder; it never passes through the lip.
    rear_path=annulus(18.5,12.5,4,BEARING_FRONT)
    assert overlap(rear_path,holder)<1e-5
    assert holder.BoundingBox().xmax==HOLDER_FRONT
    assert abs(holder.BoundingBox().xmin-4)<1e-5
    # Verify the forward retaining lip exists, and touches only the outer race.
    lip=annulus(18.4,17.6,31.4,34.3)
    retained=overlap(lip,holder)
    assert retained/lip.Volume()>.999
    forward=screw.intersect(rect(BEARING_BACK,153,-30,30,12,72))
    bearing_path=annulus(18.5,12.5,BEARING_BACK,159.2)
    assert overlap(forward,bearing_path)<1e-5
    by_name={p['name']:p['shape'] for p in parts}
    hardware=[tuple(by_name[f'M3 {label} {i+1}'] if label!='holder tie bolt' else by_name[f'M3x45 {label} {i+1}'] for label in ['holder tie bolt','holder front washer','holder rear washer','holder locknut']) for i in range(4)]
    structural=_holder.inspect_load_path(holder,wall,HOLDER_FRONT,BEARING_FRONT,holder_columns,hardware)
    assert structural['passed'],structural
    return dict(passed=True,structural_load_path=structural,mounting_flanges={'count':4,'pattern_mm':[52,31],'continuous_column_length_mm':HOLDER_FRONT-4,'overall_width_mm':62,'bolt':'M3x45 through bolt with front/rear washers and DIN 985 locknut','bolt_insertion':insertion_checks},assembled_collisions=collisions,source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),existing_screw_removed_mm3=removed,addition_outside_bearing_ring_mm3=outside,full_rotation_envelope_clear=True,coupling_tool_access=True,motor_bolt_tool_access=True,bearing_axial_installation_clear=True,rear_loading_path_clear=True,bearing_mm=[25,37,7],bearing_x_mm=[BEARING_BACK,BEARING_FRONT],holder_projection_mm=30.3,holder_projection_reduction_mm=1.,recess_opening='motor-facing side',housing_bore_mm=37.2,seat_diameter_mm=24.9,inner_race_shoulder_od_mm=27,outer_race_abutment_bore_mm=35,forward_lip_retained_fraction=retained/lip.Volume(),forward_lip_clearance_mm=.1,load_case_static_n=4.44822,limitations=['Geometry checks only: no fatigue, PETG creep, vibration or load rating.','One-direction thrust support toward the screw tip; no independent reverse-direction axial retainer.','Bearing internal race/shield geometry is illustrative; verify the purchased bearing.','New ring occupies X22.3–31.3; this is a separate assembly, not a drop-in carriage retrofit.'])

if __name__=='__main__':
    report=validate();scene=[];checks=[]
    stls=OUT/'stl';stls.mkdir(exist_ok=True)
    for stale in stls.glob('*.stl*'):stale.unlink()
    for p in parts:
        print('Exporting',p['name'],flush=True)
        vs,ts=p['shape'].tessellate(.06,.16)
        row={k:v for k,v in p.items() if k!='shape'}
        row.update(vertices=[v.toTuple() for v in vs],triangles=ts)
        if p['printed']:
            slug=p['name'].lower().replace(' ','_')+'.stl'
            dest=stls/slug
            cq.exporters.export(p['shape'],str(dest),tolerance=.025,angularTolerance=.12)
            checks.append(verify_print_mesh(dest))
            row['stl']='stl/'+slug+'.gz'
            (stls/(slug+'.gz')).write_bytes(gzip.compress(dest.read_bytes(),mtime=0))
        scene.append(row)
    report['print_meshes']=checks
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    data=dict(revision=4,explosionStages=5,experiment='bearing-supported-screw',parts=scene,sourceRevision=hashlib.sha256(pathlib.Path(__file__).read_bytes()+pathlib.Path(__file__).with_name('holder_geometry.py').read_bytes()).hexdigest())
    (OUT/'assembly.json.gz').write_bytes(gzip.compress(json.dumps(data,separators=(',',':')).encode(),mtime=0))
    with zipfile.ZipFile(OUT/'bearing-supported-screw.zip','w',zipfile.ZIP_DEFLATED) as z:
        for f in stls.glob('*.stl'):z.write(f,'stl/'+f.name)
        z.write(__file__,'experiments/bearing-supported-screw/model.py');z.write(pathlib.Path(__file__).with_name('holder_geometry.py'),'experiments/bearing-supported-screw/holder_geometry.py');z.write(SOURCE,'experiments/t8-leadscrew/model.py')
        z.write(OUT/'validation.json','validation.json')
        if (OUT/'README.txt').exists():z.write(OUT/'README.txt','README.txt')
    for f in stls.glob('*.stl'):f.unlink()
    print(json.dumps(report,indent=2),flush=True)
