# Base support study

The published example is the 40 mm travel, 1x printed lead-screw **base only**, floor on the build plate (CAD Z up). It compares the original base, the preceding printability revision, and the current base with angled motor-side lid gussets. The current base also retains the filled motor foot, pitched side windows and four support-removal openings. Other variants receive the shared CAD change; this slice does not represent their toolpaths.

Bambu Studio 2.9.1.70 uses the supplied P2S 0.4 mm, Generic PETG and process profiles: 0.20 mm layers, four walls, 25% gyroid, automatic tree supports everywhere, 0.20 mm top/bottom support gaps. No support blockers or build-plate-only setting hide the problem areas. Profiles are local copies of the installed Bambu presets and the existing project settings.

For a decompressed base STL at `/absolute/study/after/base.stl`, run from the repository root:

```sh
bambu-studio --datadir /absolute/study/cli-data \
  --load-settings 'experiments/printed-leadscrew/slicing/machine.json;experiments/printed-leadscrew/slicing/process.json' \
  --load-filaments experiments/printed-leadscrew/slicing/filament.json \
  --orient 0 --arrange 1 --slice 0 \
  --outputdir /absolute/study/after --export-3mf after.gcode.3mf \
  /absolute/study/after/base.stl
python experiments/printed-leadscrew/slicing/parse_slice.py \
  /absolute/study/after dist/experiments/printed-leadscrew/slice/after.paths.json.gz
```

The slicer must return success in `result.json`. `parse_slice.py` extracts every non-custom extrusion centerline, excluding travel and stationary unretractions. Support totals use support/interface extrusion length, 1.75 mm filament and the profile's 1.27 g/cm3 PETG density. The model is translated back from its arranged plate position into CAD coordinates. The parser explicitly rejects extruding arcs and relative XYZ instead of approximating them. The preview groups walls/surfaces, infill, supports and interfaces; it does not model bead width.

The downloadable 3MF contains the revised base STL, profiles and exact sliced G-code. The preview's STL/G-code SHA-256 values identify its source. `check_access.py` checks the support paths through the four floor openings in the published before/after data. The published `summary.json` includes profiles, estimates and access evidence.

Support-region weights classify path positions, not the feature that caused each branch. In particular, shelf-region support can increase because it now extends down through the floor to the bed. Bed access and the open tool path do not certify physical removability, snap-axle strength or print tolerances. Confirm printer/material settings before using the sliced 3MF. No print is sent by these scripts.

Run `python experiments/printed-leadscrew/slicing/check_lid_braces.py` after parsing the revised slice. The `before-lid-braces` paths retain the preceding slice; the check clips support and interface segments against both motor-side mount regions and requires zero in the current slice. The published example is only the 40 mm 1× base, not a sliced verification of all six configurations.
