# Rack actuator

CadQuery NEMA17/NEMA14 actuators with compliant rack teeth, six 625ZZ bearings and a printed enclosure.

[Viewer](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site) · [Short NEMA14 / 100 mm](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site/?motor=nema14&stroke=100&layout=short)

## Revision 20

- Four M3 heat-set inserts on the enclosure's exit face, carried by reinforced columns inside the tray. Front, side and output inserts are recessed 0.3 mm; top inserts are flush.
- Two opposed flexure leaves per lower bearing carrier reduce pitch under centered load. Each leaf is 12 mm wide, with supported rounded roots. Length grows from 22 to 28 mm and thickness from 2 to 2.67 mm over the 40–150 mm stroke range. The moving cradle is 4 mm thick; no stationary deck or extra spring parts are added.
- Default preload remains 2.3 mm. Maximum nominal leaf slope is 8.9° at 40 mm and 7.0° at 150 mm, versus 13.8° for the previous 14 mm leaf. The symmetric linear beam proxy predicts zero carrier pitch under centered load; this is an ideal estimate, not a measured print result or FEA.
- **Standard** keeps the exit bearing center 25 mm behind the front face, with the pinion midway between the two stations. **Short** keeps the stations at X=±32 mm, reducing housing length while retaining full tooth coverage. It has more unsupported output length and less leverage against tilt.
- Only **40, 100 and 150 mm** stroke presets remain, for both motors and both layouts: 12 models with actuation, staged explosion, right-click hiding, STEP/STL downloads and collision reports.

| Stroke | Layout | Bearing span | Housing length | Rack print length |
| --- | --- | --- | --- | --- |
| 40 mm | Standard | 84 mm | 166 mm | 181.5 mm |
| 40 mm | Short | 64 mm | 146 mm | 161.5 mm |
| 100 mm | Standard | 164 mm | 306 mm | 321.5 mm |
| 100 mm | Short | 64 mm | 256 mm | 271.5 mm |
| 150 mm | Standard | 264 mm | 456 mm | 471.5 mm |
| 150 mm | Short | 64 mm | 356 mm | 371.5 mm |

Module 2 dimensions apply to both motors. Each guide retains at least 13 mm from the bearing center to either end throughout travel. Parts are single-piece; check your printer's build volume. Housing length can be increased independently. Standard is preferable for larger side/moment loads, but neither layout has a rated load capacity.

NEMA17 defaults: 42 × 42 × 40 mm body, 31 mm mounting pitch, 18T / 20° pinion. NEMA14: 35.2 × 35.2 × 34 mm body, 26 mm pitch, 14T / 25° pinion. Both initially use module 2 and 40 mm stroke. The rear-mounted driver remains outside the case. Verify your motor's shaft, pilot and mounting dimensions.

## Hardware and mounting

Five printed parts: chassis, rack, pinion, tray and lid. **Reprint chassis, tray and lid**, and use the matching rack for the selected layout/stroke. The 40 mm standard and all short layouts change rack length. Matching pinion, motor and bearing hardware remain reusable. Do not mix preset components or NEMA14/NEMA17 rack and pinion profiles.

M3 inserts default to 4.6 mm OD × 5 mm long, with a 4.2 mm printed pilot. Each preset's `bill-of-materials.json` gives quantities, including four inserts each for front, side, top and moving output mounts, plus chassis and lid fasteners. Enclosure screws are M3×20 socket for the lid and M3×10 socket for the chassis. Bearing hardware remains four M5×16 upper axles, two M5×25 lower axles, six thin M5 nuts and six inner-race washers.

| Face | Four-insert pattern | Insert position |
| --- | --- | --- |
| Front / exit (+X) | Housing width − 18 mm by motor depth − 10 mm | 0.3 mm recessed |
| Side (+Y) | Housing length − 15 mm by motor depth − 10 mm | 0.3 mm recessed |
| Top (+Z) | Housing length − 15 mm by housing width − 15 mm | Flush, full-height tray posts |
| Moving output (+Z) | 9 × 9 mm in an 18 × 18 mm pad | 0.3 mm recessed |

Use 3–5 mm screw engagement: 3.3–5.3 mm penetration from recessed mounting faces, or 3–5 mm from the top face. Front and side blind pockets retain 2 mm backing. A front fixture must clear the full output pad at retraction: at module 2, provide a minimum opening Y=15.5…41 and Z=−10…22 in CAD coordinates (25.5 × 32 mm). Exact coordinates and configuration-specific opening bounds are in the report and STEP. Detach external fixtures and load before full service.

Print the chassis with X normal to the bed so flexure bending in the YZ plane lies within the layers; remove local supports carefully. STL chassis is relaxed; STEP/viewer show installed deflection. Print tray floor-down, lid roof-down, rack tooth-face down and pinion gear-face down. See [printing and assembly instructions](README.txt) for insert installation, service-window paths and full hardware details.

## Generate CAD

Python 3.12 / CadQuery 2.7.0:

```sh
pip install -r requirements.txt
python build_presets.py --jobs 4
python check_flexure_service.py --jobs 4
python package_designs.py
python -m http.server 8000 --directory dist

python model.py --motor nema14 --stroke 100 --layout short --out build/custom --check
python model.py --config configuration.json --out build/custom --check
```

Explicit CLI options override JSON. Build caching requires matching source hash, motor, stroke and layout. The viewer's selectors load generated models; custom parameters export JSON/CLI and require regeneration.

| Parameter | Behavior |
| --- | --- |
| `--stroke` | 20–150 mm; default 40 |
| `--layout` | `standard` (default) or `short` |
| `--tooth-module` | 1.5–2.5 mm; default 2 |
| `--actuator-length` | Calculated minimum when omitted; maximum 2000 mm |
| `--motor-depth` | 32–60 mm; defaults 40 / 34 |
| `--insert-od`, `--insert-length`, `--insert-pilot` | Defaults 4.6 / 5 / 4.2 mm |
| `--spring-preload` | Default 2.3 mm; range 0.1–2.5 |
| `--spring-thickness` | Automatic: `2*(leaf_length/22)^1.2`; override 1.6–3.2 mm |
| `--bearing-clearance`, `--hardware-clearance` | Defaults 0.8 / 0.5 mm |
| `--rack-backbone-width` | Default 16 mm minimum |
| `--preload` | Tooth oversize per flank, default 0.10 mm |

Leaf length is `22 + 6*max(0,(stroke-40)/110)` mm. The length/thickness scaling increases the ideal vertical stiffness per material modulus while reducing leaf angle and nominal bending strain.

Default NEMA17/NEMA14 commanded increments at 200 full steps/revolution: 0.565487 / 0.439823 mm per full step and 0.035343 / 0.027489 mm at 1/16. Stroke and layout do not change the drive ratio. These increments are not measured positioning accuracy.

## Validation

Each preset includes `validation.json`: all assembled pairs; enclosure/fastener service poses at ≤0.5 mm spacing; mechanism poses at 1% slider intervals, stage boundaries/midpoints and 0.5 mm bearing-release transitions; 41 travel positions with all six guide contacts; nominal tooth mesh; insert installation access on all three axes; blind-pocket backing; valid single solids; hardware and flexure travel clearances. Bounds used to skip empty regions are verified against the exact solids. Lid-screw removal uses continuous swept outer envelopes. Heat-set knurl/host interference and elastic tooth preload are recorded separately.

`flexure-service-validation.json` additionally checks every changed root-window hardware path at ≤0.5 mm increments from 82–100% explosion.

The flexure report includes nominal leaf slope, estimated strain and ideal stiffness per material modulus. Symmetry cancels translation/pitch coupling under centered load in the linear proxy. Printed tolerances, load eccentricity and creep can still cause tilt. Physical fit, side-load, recovery and fatigue testing remain necessary; CAD sampling is not continuous collision proof or a load rating. Use controller travel limits; no axial hard stop is provided.

## License

MIT; see [LICENSE](LICENSE). Compliant tooth principle inspired by [seveibar/compliant-spur-gear](https://github.com/seveibar/compliant-spur-gear); its license is included in the bundles.
