# Rack actuator

CadQuery NEMA17/NEMA14 actuators with compliant rack teeth, six 625ZZ bearings and a printed enclosure.

[Viewer](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site) · [NEMA14 / 150 mm](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site/?motor=nema14&stroke=150)

## Revision 22

The moving output pad and its four M3 inserts are centered on the rack’s flat backbone. The center is calculated as `(ROOT_Y + BACK_Y) / 2`; for all six default presets this shifts the pad 3 mm in +Y to Y=28.5 mm. The 18 × 18 mm pad and 9 × 9 mm insert pattern are preserved. Upgrading from revision 21 requires **only a new rack print**.

### Retained bearing layout

One arrangement replaces the Standard/Short alternatives. The motor and rear bearing group stay where shown in the reference image: pinion at X=0, rear group at X=−32 mm. The exit group moves forward, with its centers **13 mm behind the opening** and its bearing rims 5 mm behind the face. The pinion is deliberately offset toward the rear group.

The earlier **single broad flexure floor** is restored, with its 14 mm free span and supported R1.2 wall blends. Thickness increases from **1.4 to 1.8 mm**; preload remains 2.3 mm. There is no stationary lower deck and no additional spring hardware. The narrower support allows a smaller enclosure. Local reliefs clear the existing axle/nut ends from the enclosure posts, and an internal lid fastener moves inboard. During service, each extracted angled axle lifts 20 mm before parking sideways; the retained chassis/bearing subassembly slides 10 mm rearward before the tray is lowered.

| Stroke | Bearing centers X | Bearing span | Housing length | Rack print length |
| --- | --- | --- | --- | --- |
| 40 mm | −32, 44 mm | 76 mm | 146 mm | 161.5 mm |
| 100 mm | −32, 94 mm | 126 mm | 256 mm | 271.5 mm |
| 150 mm | −32, 144 mm | 176 mm | 356 mm | 371.5 mm |

At module 2, housing width is **90.8 mm for NEMA17** and **84.8 mm for NEMA14**. Lengths match the former pictured compact housings; widths shrink by 12.9–22.9 mm and 16.9–28.9 mm respectively, depending on stroke. All teeth remain enclosed, and every guide retains at least 13 mm from the bearing center to either end over full travel. Parts are single-piece; check your printer's build volume.

Six presets remain: 40, 100 and 150 mm strokes for each motor. The viewer includes actuation, staged explosion, right-click hiding and CAD downloads. Legacy `layout=short` links load the single current model.

## Hardware and printing

Five printed parts: chassis, rack, pinion, tray and lid. Use parts from the same motor/stroke preset. Revision 22 reuses the revision 21 chassis, pinion, tray, lid and bearing hardware. NEMA17 rack/pinion use 20° pressure angle; NEMA14 use 25°.

NEMA17 defaults: 42 × 42 × 40 mm body, 31 mm mounting pitch, 18T pinion. NEMA14: 35.2 × 35.2 × 34 mm body, 26 mm pitch, 14T pinion. Both initially use module 2 and 40 mm stroke. The rear-mounted driver remains outside the case. Verify your motor's shaft, pilot and mounting dimensions.

M3 inserts default to 4.6 mm OD × 5 mm long, with a 4.2 mm printed pilot. Each preset's `bill-of-materials.json` gives quantities. Four inserts remain on each mounting face:

| Face | Pattern | Insert position |
| --- | --- | --- |
| Front / exit (+X) | Housing width − 18 mm by motor depth − 10 mm | 0.3 mm recessed |
| Side (+Y) | Housing length − 15 mm by motor depth − 10 mm | 0.3 mm recessed |
| Top (+Z) | Housing length − 15 mm by housing width − 15 mm | Flush, full-height tray posts |
| Moving output (+Z) | 9 × 9 mm in an 18 × 18 mm pad | 0.3 mm recessed |

Use 3–5 mm screw engagement: 3.3–5.3 mm penetration from recessed faces, or 3–5 mm from the top face. A front fixture must clear the full output pad at retraction: at module 2, the minimum opening spans Y=18.5…41 and Z=−10…22 in CAD coordinates. Mounting coordinates change with the narrower housing; use the new STEP/report. Remove external fixtures and load before full service.

Enclosure screws are M3×20 socket for the lid and M3×10 socket for the chassis. Bearing hardware remains four M5×16 upper axles, two M5×25 lower axles, six thin M5 nuts and six inner-race washers. Clamp only the bearing inner races.

Print the chassis with **Y normal to the bed**, keeping flexure bending in the XZ plane within the layers. STL chassis is relaxed; STEP/viewer show installed deflection. Print tray floor-down, lid roof-down, rack tooth-face down and pinion gear-face down. See [printing and assembly instructions](README.txt) for insert installation and the service sequence.

## Generate CAD

Python 3.12 / CadQuery 2.7.0:

```sh
pip install -r requirements.txt
python build_presets.py --jobs 4
python check_flexure_service.py --jobs 4
python package_designs.py
python -m http.server 8000 --directory dist

python model.py --motor nema14 --stroke 100 --out build/custom --check
python model.py --config configuration.json --out build/custom --check
```

Explicit CLI options override JSON. Build caching requires a matching source hash, motor and stroke. The viewer's selectors load generated models; custom parameters export JSON/CLI and require regeneration.

| Parameter | Behavior |
| --- | --- |
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

Revision 22 rechecks output-insert fit/access/backing and valid rack geometry. An exact rack difference confines changed material to the output pad, and continuous X bounds keep the entire pad and inserts clear throughout travel and explosion. The source-bound revision 21 checks for unchanged mechanism geometry are retained; see `output_centering_validation` in each report.

Each preset includes `validation.json`: all assembled pairs; enclosure/fastener service poses at ≤0.5 mm spacing; mechanism poses at 1% slider intervals, stage boundaries/midpoints and 0.5 mm bearing-release transitions; 41 travel positions with all six guide contacts; nominal tooth mesh; insert installation access; blind-pocket backing; valid single solids; hardware and flexure travel clearances. Bounds used to skip empty regions are checked against the solids. Lid-screw removal uses continuous swept outer envelopes. Removed lid screws park 180 mm sideways; a separate continuous motion-envelope proof keeps them clear of all later stages (`python check_lid_screw_parking.py nema17 40`). Heat-set knurl/host interference and elastic tooth preload are recorded separately.

`flexure-service-validation.json` additionally checks bearing hardware removal at ≤0.5 mm increments from 38–100% explosion. End-post clearance checks include the lower axle rising as the flexure relaxes. Housing dimensions, motor position, rear bearing location and rack endpoints are compared against the pictured revision 20 arrangement during release verification.

The thicker restored flexure needs physical fit, insertion-force, recovery and fatigue testing. Its CAD deformation is prescribed and does not establish carrier angle or a load rating. Sampled checks are not a continuous collision proof or a physical tolerance test. Use controller travel limits; no axial hard stop is provided.

## License

MIT; see [LICENSE](LICENSE). Compliant tooth principle inspired by [seveibar/compliant-spur-gear](https://github.com/seveibar/compliant-spur-gear); its license is included in the bundles.
