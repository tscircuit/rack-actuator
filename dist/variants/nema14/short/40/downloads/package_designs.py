"""Package all checked presets, package stroke-specific spring meshes and write the viewer manifest."""
from pathlib import Path
import gzip,hashlib,json,shutil,zipfile
from build_presets import PRESETS,LAYOUTS,folder_for
root=Path(__file__).resolve().parent
source_hash=hashlib.sha256((root/'model.py').read_bytes()).hexdigest()
manifest=[]
for motor in ['nema17','nema14']:
 label='FLEX17' if motor=='nema17' else 'FLEX14';default=folder_for(motor,40)
 for stroke,layout in [(s,l) for s in PRESETS for l in LAYOUTS]:
  folder=folder_for(motor,stroke,layout);dest=folder/'downloads';report=json.loads((dest/'validation.json').read_text());mesh=folder/'assets/assembly.json';mesh_gz=folder/'assets/assembly.json.gz';data=json.loads(mesh.read_text() if mesh.exists() else gzip.decompress(mesh_gz.read_bytes()))
  assert report['revision']==20 and report['layout']==layout and report['source_sha256']==source_hash and report['stroke_mm']==stroke,(motor,stroke,'Run build_presets.py first')
  assert report['motion_samples']==41 and not report['explosion_failures'] and not report['motion_failures'],(motor,stroke,'Collision checks failed')
  service=json.loads((dest/'flexure-service-validation.json').read_text())
  assert (service['motor'],service['stroke_mm'],service['layout'])==(motor,stroke,layout)
  assert service['source_sha256']==source_hash and service['checker_sha256']==hashlib.sha256((root/'check_flexure_service.py').read_bytes()).hexdigest() and not service['failures'],'Run check_flexure_service.py first'
  assert data['layout']==layout and data['stroke']==stroke and data['motor'].lower()==motor
  if mesh.exists():
   with gzip.open(mesh_gz,'wb') as f:f.write(mesh.read_bytes())
   mesh.unlink()
  assert (folder/'assets/spring-states.json.gz').exists(),'Missing stroke-specific spring states'
  (folder/'assets/spring-states.json').unlink(missing_ok=True)
  for filename in ['model.py','README.txt','requirements.txt','package_designs.py','build_presets.py','check_flexure_service.py']:
   shutil.copyfile(root/filename,dest/filename)
  shutil.copyfile(root/'LICENSE',dest/'LICENSE.txt')
  for filename in ['reference-LICENSE.txt','check_guide_constraints.py']:
   src=root/'dist/downloads'/filename
   if src!=dest/filename:shutil.copyfile(src,dest/filename)
  (dest/'parameter-case-validation.json').unlink(missing_ok=True)
  config={'motor':motor,'layout':layout,'tooth_module':data['toothModule'],'stroke':stroke,'actuator_length':data['actuatorLength'],'motor_depth':data['motorDepth'],'insert_od':data['insertOD'],'insert_length':data['insertLength'],'insert_pilot':data['insertPilot']}
  (dest/'configuration.json').write_text(json.dumps(config,indent=2)+'\n')
  bom={'motor':motor,'layout':layout,'flexure':report['spring_carrier'],'front_mounting':{'thread':'M3','quantity':4,'pattern_yz_mm':data['frontMounts'],'mounting_plane_x_mm':data['frontMountX'],'thread_engagement_mm':[3,data['insertLength']],'insert_recess_mm':data['frontMountInsertRecess'],'maximum_screw_penetration_mm':data['insertLength']+data['frontMountInsertRecess'],'fixture_opening_yz_mm':data['frontFixtureOpeningYZ']},'stroke_mm':stroke,'printed_parts':[p['name'] for p in data['parts'] if p['printed']], 'heat_set_inserts':{'thread':'M3','quantity':data['insertCount'],'enclosure_quantity':data['enclosureInsertCount'],'output_quantity':data['outputInsertCount'],'outer_diameter_mm':data['insertOD'],'length_mm':data['insertLength'],'pilot_diameter_mm':data['insertPilot']},'lid_screws':{'type':'M3x20 socket','quantity':data['coverScrewCount']},'chassis_screws':{'type':'M3x10 socket','quantity':data['chassisScrewCount']},'bearings':{'type':'625ZZ','quantity':6},'bearing_axles':['4 x M5x16 socket','2 x M5x25 socket','6 x thin M5 nuts (2.7 mm)','6 x inner-race washers (0.3 mm / 7.5 mm OD)'],'output_mounting':{'thread':'M3','quantity':4,'pitch_xy_mm':[data['outputMountPitch']]*2,'pad_size_mm':data['outputPadSize'],'insert_recess_mm':data['outputInsertRecess'],'thread_engagement_mm':[3,data['insertLength']],'maximum_screw_penetration_from_pad_face_mm':data['insertLength']+data['outputInsertRecess']},'motor_screws':'4 x M3x12 countersunk','pinion_set_screw':'M3x4 flat point','top_mounting':'4 x application-length M3 screws; 3–5 mm insert engagement','side_mounting':{'thread':'M3','quantity':4,'insert_recess_mm':data['sideMountInsertRecess'],'thread_engagement_mm':[3,data['insertLength']],'maximum_screw_penetration_from_side_face_mm':data['insertLength']+data['sideMountInsertRecess'],'pattern_xz_mm':data['caseMounts']}}
  (dest/'bill-of-materials.json').write_text(json.dumps(bom,indent=2)+'\n')
  step=dest/(label+'.step');gz=dest/(label+'.step.gz')
  compressed=not step.exists() or step.stat().st_size>8*1024**2
  if compressed and step.exists():
   with step.open('rb') as src,gzip.open(gz,'wb') as target:shutil.copyfileobj(src,target)
  if not compressed:gz.unlink(missing_ok=True)
  bundle=label+('_short' if layout=='short' else '')+f'_{stroke}mm_bundle.zip'
  for old in dest.glob('*.zip'):
   if old.name!=bundle:old.unlink()
  with zipfile.ZipFile(dest/bundle,'w',zipfile.ZIP_DEFLATED) as z:
   for f in sorted(dest.iterdir()):
    if f.is_file() and f.suffix not in ['.zip','.gz']:z.write(f,f.name)
   if not step.exists():z.writestr(label+'.step',gzip.decompress(gz.read_bytes()))
  if compressed:step.unlink(missing_ok=True)
  manifest.append({'motor':motor,'layout':layout,'stroke':stroke,'basePath':('./' if folder==root/'dist' else './'+folder.relative_to(root/'dist').as_posix()+'/'),'housingLength':data['actuatorLength'],'assemblyFile':'assembly.json.gz','stationSpacing':data['stationSpacing'],'exitBearingOffset':data['exitBearingOffset'],'chassisScrewCount':data['chassisScrewCount'],'stepFile':gz.name if compressed else step.name,'bundleFile':bundle,'partCount':len(data['parts']),'insertCount':data['insertCount'],'coverScrewCount':data['coverScrewCount'],'sourceSha256':source_hash})
  print(motor,stroke,layout,'packaged; housing',data['actuatorLength'],'mm;',data['insertCount'],'inserts',flush=True)
(root/'dist/presets.json').write_text(json.dumps({'revision':20,'presets':manifest},indent=2)+'\n')
