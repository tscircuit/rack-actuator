"""Refresh downloads only after both default variants pass checks with current source."""
from pathlib import Path
import hashlib,json,shutil,zipfile
root=Path(__file__).resolve().parent
source_hash=hashlib.sha256((root/'model.py').read_bytes()).hexdigest()
for motor,folder in [('FLEX17',root/'dist'),('FLEX14',root/'dist/variants/nema14')]:
 dest=folder/'downloads';report=json.loads((dest/'validation.json').read_text())
 assert report['revision']==14 and report['source_sha256']==source_hash,(motor,'Run current model.py --check first')
 assert not report['explosion_failures'] and not report['motion_failures'],(motor,'Collision checks failed')
 for filename in ['model.py','README.txt','requirements.txt','package_designs.py']:
  shutil.copyfile(root/filename,dest/filename)
 shutil.copyfile(root/'LICENSE',dest/'LICENSE.txt')
 if motor=='FLEX14':
  for filename in ['reference-LICENSE.txt','check_guide_constraints.py']:
   shutil.copyfile(root/'dist/downloads'/filename,dest/filename)
 with zipfile.ZipFile(dest/(motor+'_bundle.zip'),'w',zipfile.ZIP_DEFLATED) as z:
  for f in sorted(dest.iterdir()):
   if f.is_file() and f.suffix!='.zip':z.write(f,f.name)
 print(motor,'packaged',source_hash)
