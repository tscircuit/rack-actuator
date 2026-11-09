"""Keep spur STLs in their download bundles without duplicate loose files.
Run after regenerating spur presets and before packaging the static site.
The viewer extracts individual STLs with the shared ZIP download helper.
"""
import json
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[1] / 'dist'
remove = []
for preset in json.loads((root / 'presets.json').read_text())['presets']:
    folder = root / preset['basePath'] / 'downloads'
    with zipfile.ZipFile(folder / preset['bundleFile']) as bundle:
        for path in folder.glob('*.stl'):
            if bundle.read(path.name) != path.read_bytes():
                raise ValueError(f'Bundled STL differs from loose file: {path}')
            remove.append(path)
# Validate all bundles before removing any redundant copies.
saved = sum(path.stat().st_size for path in remove)
for path in remove:
    path.unlink()
print(f'Removed {len(remove)} duplicate STL files; saved {saved / 1024**2:.2f} MiB.')
