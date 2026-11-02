# Rack actuator

CadQuery NEMA17/NEMA14 linear actuators with compliant rack teeth, six 625ZZ bearings and a printed enclosure.

[Open the viewer](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site) · [NEMA14 / 400 mm](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site/?motor=nema14&stroke=400)

## Revision 16

- **M3 heat-set inserts** replace the enclosure's trapped nuts. Default insert: 4.6 mm outside diameter × 5 mm long, with a 4.2 mm printed pilot. These dimensions are configurable; match the insert manufacturer's specification.
- **Top or side mounting.** Four M3 top inserts sit in full-height posts connected to the tray. Mounting loads bypass the removable lid. Four M4 side slots remain available. Lid screw heads are recessed below the top face.
- **Six actual stroke presets** for each motor: 40, 100, 150, 200, 250 and 400 mm. Selecting a preset loads its CadQuery geometry, motion, staged explosion, measurements and downloads. Longer housings receive additional lid fasteners.
- White viewer, right-click hiding, Show all, transparent enclosure and dedicated side/top mounting views.

| Stroke | Housing length | M3×20 lid screws | M3 inserts, total |
| --- | --- | --- | --- |
| 40 mm | 132 mm | 4 | 10 |
| 100 mm | 247 mm | 6 | 12 |
| 150 mm | 347 mm | 6 | 12 |
| 200 mm | 447 mm | 8 | 14 |
| 250 mm | 547 mm | 10 | 16 |
| 400 mm | 848 mm | 16 | 22 |

Lengths are for module 2 and apply to both motors. Housing length is separate from usable stroke. The rack extends beyond the housing; the longest printed part in the 400 mm preset is about 860 mm. Long presets require a sufficiently large printer; they are not split into short-bed segments. Stiffness and load capacity at long extension have not been physically established.

Default NEMA17 motor: 42 × 42 × 40 mm body, 31 mm mounting pitch, 18T / 20° pinion. NEMA14: 35.2 × 35.2 × 34 mm body, 26 mm mounting pitch, 14T / 25° pinion. Both use module 2 and 40 mm stroke initially. The motor rear projects 4 mm outside the housing; a back-mounted driver stays exposed. Verify actual motor shaft, pilot and hole dimensions.

At 200 full steps/revolution, default NEMA17/NEMA14 increments are 0.565487 / 0.439823 mm per full step and 0.035343 / 0.027489 mm at 1/16. These are commanded increments, not measured accuracy. Stroke does not change the drive ratio. Do not mix the two variants' racks and pinions.

## Hardware and printing

Five printed parts: chassis, rack, pinion, tray and lid. The front chassis mounting holes now fit M3 screws. From revision 15, **reprint the chassis, tray and lid**; reuse the matching 40 mm rack and pinion. A different stroke needs its own rack and enclosure.

Enclosure hardware: M3 inserts as listed above, M3×20 socket lid screws, and two M3×10 socket chassis screws. The tested M5 bearing through-bolts, thin nuts and inner-race washers remain. Each preset includes a bill of materials and configuration JSON. Large standalone STEP downloads are gzip-compressed; ZIP bundles contain ordinary STEP files.

Top mounting uses four application-length M3 screws with 3–5 mm thread engagement. For the default 40 mm model, the top pattern is 117 × 75.8 mm (NEMA17) or 117 × 69.8 mm (NEMA14). Side mounting uses four M4 slots. Top-mounted modules must be detached from their fixture before lid removal; the service animation excludes the fixture.

Install inserts vertically into the open tray before installing the chassis or lid. Use the insert maker's pilot/temperature guidance and test fit in your print material. Print tray floor-down, lid roof-down, rack tooth-face down and pinion gear-face down. Preserve the successful chassis orientation/material; the chassis STL is relaxed, while STEP and viewer show installed spring deflection. See [README.txt](README.txt) for assembly and full hardware details.

## Generate CAD

Python 3.12 / CadQuery 2.7.0:

```sh
pip install -r requirements.txt
# All 12 checked presets, then downloadable bundles and viewer manifest:
python build_presets.py --jobs 4
python package_designs.py
python -m http.server 8000 --directory dist

# One custom configuration:
python model.py --motor nema14 --stroke 150 --tooth-module 2 --out build/custom --check
python model.py --config configuration.json --out build/custom --check
```

Explicit CLI options override JSON values. `build_presets.py` reuses passing reports only when their source hash and preset match.

| Parameter | Behavior |
| --- | --- |
| `--stroke` | 20–400 mm; default 40 |
| `--tooth-module` | 1.5–2.5 mm; default 2 |
| `--actuator-length` | Fixed housing length, calculated minimum when omitted; maximum 1000 mm |
| `--motor-depth` | 32–60 mm; defaults 40 / 34 |
| `--insert-od` | M3 insert outside diameter, default 4.6 mm |
| `--insert-length` | M3 insert length, default 5 mm |
| `--insert-pilot` | Printed pilot diameter, default 4.2 mm |
| `--spring-preload` | Default 2.3 mm; range 0.1–2.5 |
| `--spring-thickness` | Default 1.4 mm; range 1.2–1.8 |
| `--bearing-clearance` | Default 0.8 mm |
| `--hardware-clearance` | Default 0.5 mm |
| `--rack-backbone-width` | Default 16 mm minimum |
| `--preload` | Tooth oversize per flank, default 0.10 mm |

Custom parameters need regenerated geometry, fresh checks and physical fit testing. The parameter form exports JSON/CLI; the stroke selector loads the generated preset models.

## Validation

Each preset has its own `validation.json`: all assembled pairs, enclosure/fastener service poses at ≤0.5 mm spacing, core mechanism poses at 1% slider intervals plus stage boundaries/midpoints and bearing-release positions, 41 travel positions, nominal tooth mesh, insert installation access, spring geometry and hardware clearances. Heat-set knurls intentionally overlap their own printed pilot before installation; that specific host/insert overlap is recorded separately from unintended intersections. All parts are valid single solids. Conservative enclosure bounds are verified against the solids, lid-screw removal uses continuous swept outer envelopes, and repeated tooth phases are reused only after exact periodicity checks.

The core mechanism has been tested by the builder. New enclosure details and long-stroke models still require fit and load testing. Sampled intersections are not a continuous swept-volume proof or a physical tolerance test. Prescribed spring displacement does not establish force, creep or fatigue life. Use controller travel limits; no axial hard stop is provided.

## License

MIT; see [LICENSE](LICENSE). Compliant tooth principle inspired by [seveibar/compliant-spur-gear](https://github.com/seveibar/compliant-spur-gear); its license is included in the bundles.
