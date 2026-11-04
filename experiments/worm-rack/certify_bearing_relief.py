"""Certify a narrowly bounded chassis clearance update against a full checked model.

Usage (from the repository or extracted bundle):
 python experiments/worm-rack/certify_bearing_relief.py --motor nema17 --stroke 40 \
   --reference-model validation-reference/model.py --reference-report validation-reference.json

Only the Ø12 inner-race relief, and the already-checked long-preset mounting
clearances applied to 40 mm, are accepted. All nine chassis states are checked
as exact OCC solids. Other geometry and every animation track must have identical
source. No motion result is claimed to have been rerun by this script.
"""
import argparse,ast,copy,hashlib,json,pathlib,sys,zipfile
P=argparse.ArgumentParser();P.add_argument('--motor',choices=['nema17','nema14'],required=True);P.add_argument('--stroke',type=int,choices=[40,100,150],required=True);P.add_argument('--reference-model',required=True);P.add_argument('--reference-report',required=True);a=P.parse_args()
ROOT=pathlib.Path(__file__).resolve().parents[2];source_path=ROOT/'experiments/worm-rack/model.py';source=source_path.read_text();old=pathlib.Path(a.reference_model).read_text();reference=json.loads(pathlib.Path(a.reference_report).read_text())
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
assert reference['passed'] and reference['source_sha256']==sha(old)
assert (reference['motor'].lower(),reference['stroke_mm'])==(a.motor,a.stroke)
for key,name in [('validation_source_sha256','validate.py'),('enclosure_source_sha256','enclosure.py')]:assert reference[key]==hashlib.sha256((source_path.parent/name).read_bytes()).hexdigest(),name
before_relief=source.replace('xcyl(6.,2.1,16)','xcyl(4.25,2.1,16)');assert before_relief!=source
legacy=before_relief.replace('mount_clearances=[]\n','').replace(' mount_clearances.append(clearance)\n','').replace(' for clearance in mount_clearances:result=result.cut(clearance)\n','').replace('# Rack and cover print top-face down; the worm prints vertically.','# Rack prints tooth-face down, worm vertically, enclosure cover roof down.')
assert old==before_relief or (a.stroke==40 and old==legacy),'Unexpected source change; run the full validator'
sys.argv=[str(source_path),'--motor',a.motor,'--stroke',str(a.stroke)]
g={'__file__':str(source_path),'__name__':'clearance_export'}
head,tail=source.split("print('Assembly built'",1);exec(compile(head,str(source_path),'exec'),g)
assert g['source_hash']==reference['geometry_cache_sha256'],'Worm, rack or baseline geometry changed'
oldg=g.copy()
for node in ast.parse(old).body:
 if isinstance(node,ast.FunctionDef) and node.name in ['end_saddle','fixture']:exec(compile(ast.get_source_segment(old,node),'reference-'+node.name,'exec'),oldg)
oldg['end_block']=oldg['end_saddle']();oldg['rear_block']=oldg['end_block'].mirror('YZ').translate((g['WORM_START']+16,0,0))
# The accepted operations only enlarge these voids. They cannot create material
# at any spring deflection. Check every shape actually used by the viewer too.
front=g['xcyl'](6.,2.1,16);rear=front.mirror('YZ').translate((g['WORM_START']+16,0,0));allowed=front.fuse(rear)
if old==legacy:
 for cutter in g['mount_clearances']:allowed=allowed.fuse(cutter)
keys=[(0,0)]+[(j,0) for j in range(1,5)]+[(4,j) for j in range(1,5)];checks=[]
for key in keys:
 ns=g['ns'];base=ns['base'] if key==(0,0) else ns['base_print'] if key==(4,4) else ns['chassis'](tuple(ns['SPRING_PRELOAD']*(1-v/4) for v in key))
 previous=oldg['fixture'](base);current=g['spring_shapes'].get(key)
 if current is None:current=g['fixture'](base);g['spring_shapes'][key]=current
 assert previous.isValid() and current.isValid() and len(current.Solids())==1
 added=current.cut(previous).Volume();removed=previous.cut(current);unexpected=removed.cut(allowed).Volume()
 assert added<.01 and unexpected<.01,(key,added,unexpected)
 checks.append(dict(spring_state=list(key),added_material_mm3=added,removed_material_mm3=removed.Volume(),removed_outside_allowed_clearances_mm3=unexpected,valid_single_solid=True))
 print(a.motor,a.stroke,'clearance state',key,'verified',flush=True)
report=copy.deepcopy(reference);report['source_sha256']=sha(source)
report['reference_full_check_source_sha256']=reference['source_sha256'];report['clearance_certifier_sha256']=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
report['chassis_clearance_update']={'method':'Exact OCC material-removal certificate for all nine chassis states; source changes are restricted to larger voids. All other shapes and tracks are unchanged. Full motion/disassembly results are retained from the reference report, not rerun.','reference_report_sha256':hashlib.sha256(pathlib.Path(a.reference_report).read_bytes()).hexdigest(),'bearing_inner_race_relief_diameter_mm':12,'outer_race_shoulder_radial_overlap_mm':2,'short_preset_mount_clearances_applied':old==legacy,'states':checks,'maximum_added_material_mm3':max(q['added_material_mm3'] for q in checks)}
report['method']+=' Final chassis clearance update certified by exact material removal; see chassis_clearance_update and the included reference report.'
report['geared_drive']['bearing_inner_race_relief_diameter_mm']=12
out=g['OUT'];(out/'validation.json').write_text(json.dumps(report,indent=2))
# Export the certified geometry, reusing the states checked above.
exec(compile("print('Assembly built'"+tail,str(source_path),'exec'),g)
(out/'validation-reference.json').write_bytes(pathlib.Path(a.reference_report).read_bytes())
(out/'validation-reference-model.py').write_text(old)
bundle=out/'worm-rack-experiment.zip';tmp=ROOT/f'work/certified-{a.motor}-{a.stroke}.zip'
with zipfile.ZipFile(bundle) as src,zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as dst:
 for info in src.infolist():dst.writestr(info,src.read(info.filename))
 dst.write(__file__,'experiments/worm-rack/certify_bearing_relief.py')
 dst.write(out/'validation-reference.json','validation-reference.json')
 dst.writestr('validation-reference/model.py',old)
tmp.replace(bundle)
print('Certified clearance export complete',a.motor,a.stroke,flush=True)
