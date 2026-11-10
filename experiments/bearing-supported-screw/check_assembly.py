"""Check the viewer's staged removal poses using exact CAD intersections.

Run after model.py. Checks 41 poses of the rear-loading assembly sequence.
"""
import importlib.util, json, pathlib, zipfile
import cadquery as cq

path=pathlib.Path(__file__).with_name('model.py')
spec=importlib.util.spec_from_file_location('bearing_model',path)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
clamp=lambda v:max(0.,min(1.,v))
poses=[i/40 for i in range(41)]
checks=[];collisions=[]
for t in poses:
    shapes=[]
    for p in m.parts:
        shape=p['shape']
        delta=m.explosion_offset(p,t)
        shape=shape.translate(tuple(delta))
        shapes.append((p['name'],shape,shape.BoundingBox()))
    pairs=0
    for i,(an,a,ab) in enumerate(shapes):
        for bn,b,bb in shapes[i+1:]:
            if any(min(getattr(ab,k+'max'),getattr(bb,k+'max'))-max(getattr(ab,k+'min'),getattr(bb,k+'min'))<1e-6 for k in 'xyz'):continue
            pairs+=1;volume=m.overlap(a,b)
            if volume>1e-4:collisions.append(dict(pose=t,a=an,b=bn,volume_mm3=volume))
    checks.append(dict(explosion_percent=100*t,exact_intersection_pairs=pairs))
    print(f'{100*t:.2f}%: {pairs} exact pair checks; {len(collisions)} collisions',flush=True)
report=dict(passed=not collisions,poses=checks,collisions=collisions,sequence='Unthread the four shared M3x40 bolts 6 mm, keeping them captured in the holder. Slide the support module off the shaft and lift it clear, finish withdrawing the bolts, remove motor/wall, then withdraw the screw and bearing from the rear of the holder.',scope='Sampled rigid disassembly poses, not a continuous swept-volume proof.')
(m.OUT/'assembly-checks.json').write_text(json.dumps(report,indent=2)+'\n')
assert not collisions,collisions
with zipfile.ZipFile(m.OUT/'bearing-supported-screw.zip','a',zipfile.ZIP_DEFLATED) as z:
    z.write(__file__,'experiments/bearing-supported-screw/check_assembly.py')
    z.write(m.OUT/'assembly-checks.json','assembly-checks.json')
print('PASS staged assembly poses',flush=True)
