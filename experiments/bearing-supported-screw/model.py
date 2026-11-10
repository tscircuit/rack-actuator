"""Independent 6805 supported printed-screw experiment. Units: mm.

Extract the existing screw construction without executing or changing its generator.
Only an additive bearing seat/shoulder is fused to that screw. Hardware is reference
geometry, not a manufacturing drawing. Run with the project's CadQuery Python.
"""
import ast, collections, gzip, hashlib, json, math, pathlib, struct, zipfile
import cadquery as cq

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

def xhex(af, length, x, y, z):
    return hex_prism(af, length, (0, 0, 0)).rotate((0,0,0), (0,1,0), 90).translate((x,y,z))

# The shoulder starts beyond the original clamp slit (ends X26). No existing
# material is removed, including in the DIN 471 groove, which is wholly in the ring.
seat = xcyl(12.45, 11.1, 28.2).fuse(xcyl(13.5, 2., 26.2))
seat = seat.cut(annulus(13, 11.95, 36.3, 37.6))
seat = seat.cut(xcyl(7.9, 13.2, 26.15))
screw = original_screw.fuse(seat).clean()
holes = [(y, 42+z) for y in (-15.5,15.5) for z in (-15.5,15.5)]
cap_holes = [(y, 42+z) for y in (-21,21) for z in (-10,10)]
wall = rect(0,4,-26,26,16,68).cut(xcyl(11.3,4,0))
holder = rect(25.2,35.3,-26,26,16,68).cut(xcyl(17.5,10.1,25.2))
holder = holder.cut(xcyl(18.6,7.2,28.1))
for y,z in holes:
    wall = wall.cut(xcyl(1.7,4,0,y,z))
    holder = holder.fuse(xcyl(5.,21.2,4,y,z))
    holder = holder.cut(xcyl(1.7,6,4,y,z)).cut(xcyl(3.2,25.4,10,y,z))
cap = rect(35.3,38.3,-26,26,16,68).cut(xcyl(17.5,3,35.3))
for y,z in holes:
    cap = cap.cut(xcyl(3.2,3,35.3,y,z)) # Motor screw/hex-driver access.
for y,z in cap_holes:
    holder = holder.cut(xcyl(1.7,10.1,25.2,y,z)).cut(xhex(5.9,3.7,25.2,y,z))
    cap = cap.cut(xcyl(1.7,3,35.3,y,z))
holder, cap = holder.clean(), cap.clean()

# Separate race envelopes let the inspection view distinguish inner-only contact.
# Exact shield/race internals vary by manufacturer; only d/D/B are authoritative.
inner = annulus(13.5,12.5,28.2,35.2)
outer = annulus(18.5,17.5,28.2,35.2)
shield = annulus(17.4,13.6,28.35,35.05)
spacer = annulus(13.5,12.6,35.2,36.2)
# Installed, sprung DIN471-25 reference. Ears are conservatively within Ø34.2.
clip = annulus(15.,11.95,36.35,37.55).cut(rect(36.3,37.6,-4,4,42,61))
for y in (-5.,5.):
    clip = clip.fuse(xcyl(2.1,1.2,36.35,y,56.1)).cut(xcyl(1.,1.2,36.35,y,56.1))
clip = clip.clean()
motor = rect(-40,0,-21,21,21,63).fuse(xcyl(11,2,0)).cut(xcyl(2.6,2.2,-.1))
for y,z in holes:
    motor = motor.cut(xcyl(1.65,7,-6,y,z))
shaft = xcyl(2.5,4,0).fuse(d_shaft(2.5,2.,20,4))

parts=[]
def add(name, shape, color, printed=False, group='fixed', stage=0, vector=(0,0,0)):
    shape=shape.clean()
    assert shape.isValid() and len(shape.Solids())==1, (name,'invalid solid')
    parts.append(dict(name=name,shape=shape,color=color,printed=printed,group=group,stage=stage,vector=vector))

add('NEMA17 motor reference',motor,'#26394a',stage=6,vector=(-80,0,0))
add('NEMA17 D shaft reference',shaft,'#b7c8d5',group='motorRotor',stage=6,vector=(-80,0,0))
add('4 mm NEMA17 wall',wall,'#7195a0',True,stage=7,vector=(-40,0,0))
add('Bearing holder',holder,'#39556c',True)
add('Bearing retaining cap',cap,'#618395',True,stage=2,vector=(260,0,0))
add('Printed lead screw with bearing seat',screw,'#e8b84a',True,'rotor',stage=8,vector=(65,0,0))
add('6805 inner race reference',inner,'#c2ced7',group='bearingRotor',stage=4,vector=(180,0,0))
add('6805 outer race reference',outer,'#a2b1bd',stage=4,vector=(180,0,0))
add('6805 shield envelope reference',shield,'#718290',stage=4,vector=(180,0,0))
add('Inner race spacer',spacer,'#e3a34b',True,'bearingRotor',stage=4,vector=(182,0,0))
add('DIN 471-25 steel circlip reference',clip,'#505967',group='bearingRotor',stage=3,vector=(240,0,0))
add('M3x12 shaft clamp bolt',bolt(1.45,12,2.75,3,(17,5,33)),'#94a3b8',group='rotor',stage=8,vector=(65,0,0))
add('M3 shaft clamp nut',hex_prism(5.5,2.4,(17,5,34.5)).cut(cyl(1.55,2.6,(17,5,34.4))),'#b7c8d5',group='rotor',stage=8,vector=(65,0,0))
for i,(y,z) in enumerate(holes):
    add(f'M3x16 motor bolt {i+1}',bolt(1.45,16,2.75,3,(-6,y,z),AXIS),'#a5b7c5',stage=5,vector=(320,0,0))
for i,(y,z) in enumerate(cap_holes):
    add(f'M3x12 cap bolt {i+1}',bolt(1.45,12,2.75,3,(26.3,y,z),AXIS),'#a5b7c5',stage=1,vector=(320,0,0))
    add(f'M3 cap nut {i+1}',xhex(5.5,2.4,26.3,y,z).cut(xcyl(1.55,2.4,26.3,y,z)),'#bdcbd6')

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
    # Conservative full rotational envelopes of screw, clamp, races and circlip.
    sweep=xcyl(11,17.2,9).fuse(xcyl(13.5,10.15,26.2)).fuse(xcyl(17.1,1.2,36.35)).fuse(xcyl(12.45,1.75,37.55)).fuse(xcyl(10.1,112.7,39.3))
    # Clamp/nut extremes are inside the original Ø22 hub.
    for name,shape in [('wall',wall),('holder',holder),('cap',cap)]:
        assert overlap(sweep,shape)<1e-5,('rotation envelope',name)
    # Coupler's original split, D bore and screwdriver approach remain clear.
    tool=cyl(1.5,35,(17,5,48))
    assert overlap(tool,holder)+overlap(tool,wall)+overlap(tool,cap)<1e-5
    for y,z in holes:
        tool=xcyl(1.5,60,13,y,z)
        assert overlap(tool,holder)+overlap(tool,cap)<1e-5
    # Bearing + spacer can slide over all geometry in front of the shoulder.
    forward=screw.intersect(rect(28.2,153,-30,30,12,72))
    bearing_path=annulus(18.5,12.5,28.2,159.2)
    assert overlap(forward,bearing_path)<1e-5
    return dict(passed=True,assembled_collisions=collisions,source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),existing_screw_removed_mm3=removed,addition_outside_bearing_ring_mm3=outside,full_rotation_envelope_clear=True,coupling_tool_access=True,motor_bolt_tool_access=True,bearing_axial_installation_clear=True,bearing_mm=[25,37,7],seat_diameter_mm=24.9,housing_bore_mm=37.2,inner_race_shoulder_od_mm=27,outer_race_abutment_bore_mm=35,groove_diameter_mm=23.9,groove_width_mm=1.3,groove_end_margin_mm=1.7,axial_clearance_mm={'outer_race':.2,'inner_stack':.25},load_case_static_n=4.44822,limitations=['Geometry checks only: no fatigue, PETG creep, vibration or load rating.','Circlip reference shows installed envelope; plier expansion is not simulated.','Bearing internal race/shield geometry is illustrative; verify the purchased bearing.','New ring occupies X26.2–39.3; this is a separate assembly, not a drop-in carriage retrofit.'])

if __name__=='__main__':
    report=validate();scene=[];checks=[]
    stls=OUT/'stl';stls.mkdir(exist_ok=True)
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
    data=dict(revision=1,experiment='bearing-supported-screw',parts=scene,sourceRevision=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest())
    (OUT/'assembly.json.gz').write_bytes(gzip.compress(json.dumps(data,separators=(',',':')).encode(),mtime=0))
    with zipfile.ZipFile(OUT/'bearing-supported-screw.zip','w',zipfile.ZIP_DEFLATED) as z:
        for f in stls.glob('*.stl'):z.write(f,'stl/'+f.name)
        z.write(__file__,'experiments/bearing-supported-screw/model.py');z.write(SOURCE,'experiments/t8-leadscrew/model.py')
        z.write(OUT/'validation.json','validation.json')
        if (OUT/'README.txt').exists():z.write(OUT/'README.txt','README.txt')
    for f in stls.glob('*.stl'):f.unlink()
    print(json.dumps(report,indent=2),flush=True)
