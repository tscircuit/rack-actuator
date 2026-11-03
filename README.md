# Rack actuator

CadQuery NEMA17/NEMA14 actuators with compliant rack teeth, six 625ZZ bearings and a printed enclosure.

[Viewer](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site) · [NEMA14 / 150 mm](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site/?motor=nema14&stroke=150)

## Revision 24

The **Variant** dropdown selects **Enclosed rack** or **Rear pass-through · shorter** for either motor and every stroke preset. The shorter housing has a rear opening for the rack and teeth. The motor, bearing stations, output pad and usable stroke retain their positions. Reserve the rear clearance shown below across the full stroke.

| Stroke | Enclosed housing | Pass-through housing | Reduction | Maximum rear rack projection |
| --- | --- | --- | --- | --- |
| 40 mm | 146 mm | 125 mm | 21 mm | 17 mm |
| 100 mm | 256 mm | 175 mm | 81 mm | 77 mm |
| 150 mm | 356 mm | 225 mm | 131 mm | 127 mm |

[Open the shorter variant](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site/?enclosure=pass-through). Dimensions are at module 2, for both motors. The rear opening spans Y=15…41, Z=−10…22 in CAD coordinates. The rack is exposed behind the case; a fixture must leave this travel envelope clear. Housing length can still be increased independently. Shortening the enclosure does not shorten the rack or its swept working space.

Use the selected variant's complete CAD bundle: tray, lid, mounting coordinates and chassis lid-post clearance slots depend on the enclosure. The default enclosed models retain revision 23 geometry. Both variants retain the floor-supported rear chassis posts, recessed M3 inserts and M3×16 rear screws; front screws are M3×10. The centered output pad is 18 × 18 mm with a 9 × 9 mm insert pattern.

### Retained bearing layout

One arrangement replaces the Standard/Short alternatives. The motor and rear bearing group stay where shown in the reference image: pinion at X=0, rear group at X=−32 mm. The exit group moves forward, with its centers **13 mm behind the opening** and its bearing rims 5 mm behind the face. The pinion is deliberately offset toward the rear group.

The earlier **single broad flexure floor** is restored, with its 14 mm free span and supported R1.2 wall blends. Thickness increases from **1.4 to 1.8 mm**; preload remains 2.3 mm. There is no stationary lower deck and no additional spring hardware. The narrower support allows a smaller enclosure. Local reliefs clear the existing axle/nut ends from the enclosure posts, and an internal lid fastener moves inboard. During service, each extracted angled axle lifts 20 mm before parking sideways; the lower axles first back out 10 mm, then the retained chassis/bearing subassembly lifts 6 mm and slides 10 mm rearward before the tray is lowered.

| Stroke | Bearing centers X | Bearing span | Housing length | Rack print length |
| --- | --- | --- | --- | --- |
| 40 mm | −32, 44 mm | 76 mm | 146 mm | 161.5 mm |
| 100 mm | −32, 94 mm | 126 mm | 256 mm | 271.5 mm |
| 150 mm | −32, 144 mm | 176 mm | 356 mm | 371.5 mm |

At module 2, housing width is **90.8 mm for NEMA17** and **84.8 mm for NEMA14**. The table above gives enclosed lengths; the pass-through reductions are listed at the top. The enclosed variant keeps all teeth inside; every guide retains at least 13 mm from the bearing center to either end over full travel. Parts are single-piece; check your printer's build volume.

Twelve presets cover 40, 100 and 150 mm strokes for each motor and enclosure. The viewer includes actuation, staged explosion, right-click hiding and CAD downloads. Legacy `layout=short` links use the current bearing layout.

## Hardware and printing

Five printed parts: chassis, rack, pinion, tray and lid. Use parts from the same motor, stroke and enclosure preset. NEMA17 rack/pinion use 20° pressure angle; NEMA14 use 25°.

NEMA17 defaults: 42 × 42 × 40 mm body, 31 mm mounting pitch, 18T pinion. NEMA14: 35.2 × 35.2 × 34 mm body, 26 mm pitch, 14T pinion. Both initially use module 2 and 40 mm stroke. The rear-mounted driver remains outside the case. Verify your motor's shaft, pilot and mounting dimensions.

M3 inserts default to 4.6 mm OD × 5 mm long, with a 4.2 mm printed pilot. Each preset's `bill-of-materials.json` gives quantities. Four inserts remain on each mounting face:

| Face | Pattern | Insert position |
| --- | --- | --- |
| Front / exit (+X) | Housing width − 18 mm by motor depth − 10 mm | 0.3 mm recessed |
| Side (+Y) | Housing length − 15 mm by motor depth − 10 mm | 0.3 mm recessed |
| Top (+Z) | Housing length − 15 mm by housing width − 15 mm | Flush, full-height tray posts |
| Moving output (+Z) | 9 × 9 mm in an 18 × 18 mm pad | 0.3 mm recessed |

Use 3–5 mm screw engagement: 3.3–5.3 mm penetration from recessed faces, or 3–5 mm from the top face. A front fixture must clear the full output pad at retraction: at module 2, the minimum opening spans Y=18.5…41 and Z=−10…22 in CAD coordinates. Mounting coordinates change with the narrower housing; use the new STEP/report. Remove external fixtures and load before full service.

Enclosure screws are M3×20 socket for the lid and M3×10 socket for the front chassis row and M3×16 for the rear row. Bearing hardware remains four M5×16 upper axles, two M5×25 lower axles, six thin M5 nuts and six inner-race washers. Clamp only the bearing inner races.

Print the chassis with **Y normal to the bed**, keeping flexure bending in the XZ plane within the layers. STL chassis is relaxed; STEP/viewer show installed deflection. Print tray floor-down, lid roof-down, rack tooth-face down and pinion gear-face down. See [printing and assembly instructions](README.txt) for insert installation and the service sequence.

## Generate CAD

Python 3.12 / CadQuery 2.7.0:

```sh
pip install -r requirements.txt
python build_presets.py --jobs 4
python check_flexure_service.py --jobs 4
python check_lid_screw_parking.py --all
python package_designs.py
python -m http.server 8000 --directory dist

python model.py --motor nema14 --stroke 100 --enclosure pass-through --out build/custom --check
python model.py --config configuration.json --out build/custom --check
```

Explicit CLI options override JSON. Build caching requires a matching source hash, motor, stroke and enclosure. The viewer's selectors load generated models; custom parameters export JSON/CLI and require regeneration.

| Parameter | Behavior |
| --- | --- |
| `--enclosure` | `enclosed` (default) or `pass-through` |
| `--stroke` | 20–150 mm; default 40 |
| `--tooth-module` | 1.5–2.5 mm; default 2 |
| `--actuator-length` | Calculated minimum when omitted; maximum 2000 mm |
| `--motor-depth` | 32–60 mm; defaults 40 / 34 |
| `--insert-od`, `--insert-length`, `--insert-pilot` | Defaults 4.6 / 5 / 4.2 mm |
| `--spring-preload` | Default 2.3 mm; range 0.1–2.5 |
| `--spring-thickness` | Default 1.8 mm; range 1.6–2.2 |
| `--bearing-clearance`, `--hardware-clearance` | Defaults 0.8 / 0.5 mm |
| `--rack-backbone-width` | Default 16 mm minimum |
| `--preload` | Tooth oversize per flank, default 0.10 mm |

Default NEMA17/NEMA14 commanded increments at 200 full steps/revolution: 0.565487 / 0.439823 mm per full step and 0.035343 / 0.027489 mm at 1/16. Stroke does not change the drive ratio. These are command increments, not measured positioning accuracy.

## Validation

All twelve presets are regenerated and checked against revision 24 source. Reports identify retained native collision scans when only the rear-containment validation rule changed; geometry and scan code remain identical, and subsequent checks are rerun.

Each preset includes `validation.json`: all assembled pairs; enclosure/fastener service poses at ≤0.5 mm spacing; mechanism poses at 1% slider intervals, stage boundaries/midpoints and 0.5 mm bearing-release transitions; 41 travel positions with all six guide contacts; nominal tooth mesh; insert installation access; blind-pocket backing; valid single solids; hardware and flexure travel clearances. Bounds used to skip empty regions are checked against the solids. Lid-screw removal uses continuous swept outer envelopes. Removed lid screws park 180 mm sideways; a separate continuous motion-envelope proof keeps them clear of all later stages (`python check_lid_screw_parking.py nema17 40 pass-through`). Heat-set knurl/host interference and elastic tooth preload are recorded separately.

`flexure-service-validation.json` additionally checks bearing hardware removal at ≤0.5 mm increments from 38–100% explosion. End-post clearance checks include the lower axle rising as the flexure relaxes. Release verification checks both housing lengths and unchanged bearing/motor positions.

The thicker restored flexure needs physical fit, insertion-force, recovery and fatigue testing. Its CAD deformation is prescribed and does not establish carrier angle or a load rating. Sampled checks are not a continuous collision proof or a physical tolerance test. Use controller travel limits; no axial hard stop is provided.

## License

MIT; see [LICENSE](LICENSE). Compliant tooth principle inspired by [seveibar/compliant-spur-gear](https://github.com/seveibar/compliant-spur-gear); its license is included in the bundles.
