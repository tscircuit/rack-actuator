"""Check the viewer's staged removal poses using exact CAD intersections.

The circlip expansion is a clearance envelope only, not an elastic solution.
Run after model.py. Checks 35 poses, with additional samples during clip opening.
"""
import importlib.util, json, pathlib, zipfile
import cadquery as cq

path=pathlib.Path(__file__).with_name('model.py')
spec=importlib.util.spec_from_file_location('bearing_model',path)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
clamp=lambda v:max(0.,min(1.,v))
poses=sorted(set([i/32 for i in range(33)]+[2.1/8,2.2/8]))
checks=[];collisions=[]
for t in poses:
    shapes=[]
    for p in m.parts:
        progress=clamp(t*8-(p['stage']-1)) if p['stage'] else 0
        shape=p['shape']
        if p['name'].startswith('DIN 471'):
            scale=1+.06*clamp(progress*5)
            shape=shape.transformGeometry(cq.Matrix([[1,0,0,0],[0,scale,0,0],[0,0,scale,42*(1-scale)],[0,0,0,1]]))
            progress=clamp((progress-.2)/.8)
        shape=shape.translate(tuple(v*progress for v in p['vector']))
        shapes.append((p['name'],shape,shape.BoundingBox()))
    pairs=0
    for i,(an,a,ab) in enumerate(shapes):
        for bn,b,bb in shapes[i+1:]:
            if any(min(getattr(ab,k+'max'),getattr(bb,k+'max'))-max(getattr(ab,k+'min'),getattr(bb,k+'min'))<1e-6 for k in 'xyz'):continue
            pairs+=1;volume=m.overlap(a,b)
            if volume>1e-4:collisions.append(dict(pose=t,a=an,b=bn,volume_mm3=volume))
    checks.append(dict(explosion_percent=100*t,exact_intersection_pairs=pairs))
    print(f'{100*t:.2f}%: {pairs} exact pair checks; {len(collisions)} collisions',flush=True)
report=dict(passed=not collisions,poses=checks,collisions=collisions,circlip_expansion='Illustrative radial 6% expansion before axial withdrawal; not a stress/force simulation.',scope='Sampled rigid disassembly poses, not a continuous swept-volume proof.')
(m.OUT/'assembly-checks.json').write_text(json.dumps(report,indent=2)+'\n')
assert not collisions,collisions
with zipfile.ZipFile(m.OUT/'bearing-supported-screw.zip','a',zipfile.ZIP_DEFLATED) as z:
    z.write(__file__,'experiments/bearing-supported-screw/check_assembly.py')
    z.write(m.OUT/'assembly-checks.json','assembly-checks.json')
print('PASS staged assembly poses',flush=True)
