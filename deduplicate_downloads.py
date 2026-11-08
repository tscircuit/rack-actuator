"""Reuse byte-identical STEP files already in the spur bundles.
The STEP button extracts that entry; STL and CAD geometry remain unchanged.
"""
import gzip,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
catalog=ROOT/'dist/presets.json';data=json.loads(catalog.read_text());saved=0
for preset in data['presets']:
 folder=ROOT/'dist'/preset['basePath'].removeprefix('./')/'downloads'
 with zipfile.ZipFile(folder/preset['bundleFile']) as z:
  entries=[name for name in z.namelist() if name.endswith('.step')];assert len(entries)==1
  standalone=folder/preset['stepFile'];entry=entries[0]
  if standalone.exists():
   raw=standalone.read_bytes();raw=gzip.decompress(raw) if standalone.suffix=='.gz' else raw
   assert raw==z.read(entry);saved+=standalone.stat().st_size;standalone.unlink()
  preset['stepEntry']=entry
catalog.write_text(json.dumps(data,indent=2)+'\n');print('Duplicate STEP payloads removed, MiB',saved/2**20)
