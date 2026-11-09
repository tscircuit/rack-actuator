T8 screw length: 100 mm. Usable travel: 70 mm. Overall retracted length: 191 mm.
Width variant: 1x. Output plate: 42 x 42 mm. Base width: 80 mm. Upper bearing span: 41.569 mm.

# T8×8 — 100 and 300 mm screw lengths

Select a 100 or 300 mm purchased rod. Both T8 designs are 1× width only; wide variants are reserved for the printed-screw 40 mm stroke. The 100 mm screw gives 70 mm usable travel; the 300 mm screw gives 270 mm. Both bearing stations stay 40 mm apart and support the carriage throughout travel. The rod engages a rigid 5-to-8 mm coupling by 8 mm, with a bolted brass flange nut in the hollow carriage.

| Screw length | Travel | Bearing X stations | Base length | Overall retracted | Overall extended |
|---|---|---|---|---|---|
| 100 mm | 70 mm | 93 / 133 mm | 159 mm | 191 mm | 261 mm |
| 300 mm | 270 mm | 293 / 333 mm | 359 mm | 391 mm | 661 mm |

The screw starts at X=26 mm. The 15 mm nut remains fully engaged, with 4.5 mm of screw beyond its front face at full extension. The tip stays 25 mm inside the retracted output face. T8 threads use smooth fit envelopes in the viewer; actual helical engagement, backlash and friction are not simulated. The 300 mm rod is the lab-stock length. Long components are single-piece STLs, so check print-bed dimensions.

## Width and external mounting patterns

T8 uses a 42 mm output plate and an 80 mm base. Its six bearings include two lower bearings tightened together by one carrier and four M5 adjustment bolts. The carrier's ruthex RX-M5x9.5 inserts use Ø6.4 mm printed pilots, 10.5 mm deep. Heat-set these before assembly.

T8 output plates remain 42 mm wide with the centered four-hole pattern. Compatible 40 mm printed-screw plates are described below. All external mounting interfaces use a **31 mm square hole grid**. Every adjacent pair of columns and rows forms a complete NEMA17 pattern. The 1×, 2× and 4× output plates are **42, 104 and 168 mm wide**, respectively. The 2× plate was widened from 84 mm to keep a centered NEMA17 pattern while adding columns at the same 31 mm pitch; the carriage running section, bearings and base widths are unchanged.

The output plate has two rows 31 mm apart and 2, 4 or 6 columns: Y=±15.5 mm for 1×; add ±46.5 mm for 2×; add ±77.5 mm for 4×. This gives 4, 8 or 12 M3 three-ridge holes. All three retain the centered 31×31 mm NEMA17 square.

The base and lid extend the existing grid toward their exit edges in 31 mm steps from X=10.5 mm, measured forward from the motor front. Each adds every row with at least 4 mm of material radius around the hole center. Continuous floor and lid ribs connect the insert seats around the cutouts. The first NEMA17 square remains centered at X=26, Y=0 mm.

| Configuration | Base insert seats | Lid insert seats | Last base / lid row X | Distance to base / lid exit edge |
|---|---:|---:|---|---|
| Printed 40 mm, 1× / 2× / 4× | 10 / 20 / 30 | 10 / 20 / 30 | 134.5 / 134.5 mm | 20.5 / 11.5 mm |
| Printed 120 mm, 1× | 16 | 14 | 227.5 / 196.5 mm | 7.5 / 29.5 mm |
| T8 100 mm screw, 1× | 10 | 10 | 134.5 / 134.5 mm | 16.5 / 7.5 mm |
| T8 300 mm screw, 1× | 22 | 22 | 320.5 / 320.5 mm | 30.5 / 21.5 mm |

The next 31 mm row would fall outside the relevant face or its required edge margin. The 120 mm printed-screw base extends farther than its lid and supports one additional row.

A wider actuator plate can also be mounted with its width along the host length (X), including on a narrow 1× host. The original five rows support these positions; the longer grids additionally support the forward outer pair:

| Mounted plate | Center X | Supported X rows (at Y=±15.5) | Bolts |
|---|---|---|---|
| 1× | 26 mm | 10.5, 41.5 | 4 |
| 2× | 57 or 88 mm | First four or last four grid rows | All 8 |
| 4×, rear overhang | 57 mm | All five grid rows | 10 of 12 |
| 4×, front overhang | 88 mm | All five grid rows | 10 of 12 |

On a short base or lid, the unused 4× outer pair is at X=−20.5 mm or X=165.5 mm, outside the original five-row grid. Longer bases and lids also support X=165.5 mm, allowing all 12 holes of a 4× plate in the forward position. These are alternative mounting positions, not a simultaneous two-actuator arrangement. An overhanging plate and its attached mechanism still require a load and clearance check for the actual application. The CAD report verifies matching holes and screw access, not attached-actuator strength.

Use [ruthex RX-M3Sx4.0 short inserts](https://www.ruthex.de/en/collections/gewindeeinsatze/products/ruthex-gewindeeinsatz-m3s-100stuck-rx-m3x4-0-short-messing-gewindebuchsen-fur-3d-druck), nominal Ø4.6×4 mm. Printed pilots are Ø4 mm with a Ø4.8 mm entry taper; the pilot diameter is a prototype fit to calibrate on the actual PETG print. Install lid inserts from above and base inserts from below. Lid seats are open-bottomed. Base pilots are 5 mm deep, leaving 1 mm beyond the 4 mm insert; where a grid hole lies below a structural foot, backing is retained above the pilot instead of drilling through the foot. Other base seats pass through the floor. Limit external screw entry to 4 mm from the lid top or 5 mm from the base underside. External mounting screws are not included because their length depends on the attached structure. The viewer shows installed Ø4.64 mm cavities around the insert references; STLs retain undersized pilots.

External side mounting bosses and side holes are removed. The former perimeter M5 floor pads and external M5 lid receivers are replaced by the matched M3 patterns. These mounts do not preserve the previous external hole locations.

## Windowed base and structural lid

Volume-reduction cutouts are applied as a final post-processing pass after every printed feature, mounting hole, installed insert cavity, bearing relief and axle has been placed. The base uses one coordinated floor-window pattern, replacing the overlapping old and new patterns. Whole rounded windows are laid out between complete protected bands, with at least 6 mm between neighboring windows; narrow leftover openings are omitted rather than clipped into fragments. Lid windows use the same planning method. Carriage and motor-brace cutouts are also deferred to this final pass.

Rounded floor windows and side windows with 45-degree pitched roofs reduce base volume. The motor face is filled down to the floor beneath its central opening. Four rounded 23 x 11 mm floor openings below the fixed bearing supports and adjustment shelves give support trees a path to the bed and provide access from underneath for removal. Other floor windows reserve 6 mm around these access openings. Side guide walls, bearing seats, shelves and insert seats remain intact. A continuous floor perimeter and side rails connect the supports. The validation report checks protected regions, window spacing, empty cutouts and a single connected solid; it does not establish stiffness under load.

The lid stays at Z=64–68 mm and does not increase the 68 mm assembly height. Rounded through-windows remove material between a continuous 8 mm perimeter and transverse fixing/mounting ribs. Longitudinal ribs preserve every insert seat; transverse fixing bands and intermediate ribs connect them to the perimeter. The geometry report records the exact CAD volume reduction for the selected configuration, not printed mass or a stiffness rating.

Six recessed M3×12 button-head screws fasten the lid into the base's 12 mm-deep three-ridge pilots. These structural fasteners are separate from the external M3 insert patterns. Driver access remains for the four carrier-adjustment bolts and motor bolts; extend the carriage to reach the motor bolts.

## Bearings and running faces

All four fixed upper-bearing supports extend 4 mm downward. Their undersides are at Z=28 mm, flush with the underside of the adjacent carrier-adjustment bolt shelves. This fills the former Z=28–32 mm recess beside each bolt. The shared carrier, bearing seats, bolt bores and adjustment travel remain unchanged. CAD checks verify the filled regions, underside level and carrier/assembly clearance. Slicer support requirements elsewhere still depend on print orientation and settings.

The carriage runs on smooth flats with no raised side rails. The CAD checks include nominal bearing alignment and ±1 mm axial displacement relative to the carriage. The base and carrier retain their existing clearance channels. Split Ø4.8 mm axles keep the 6.4 mm-wide retaining shoulders and extended 30° bent tips. Restored through-slots taper from 2.2 mm at the tip through 2.0 mm at the head to 1.2 mm near the root, ending in a 0.6 mm radius. A Ø5.4 mm clearance behind the inner-race seat frees the prongs to flex inward. The Ø7.4 mm inner-race lands and surrounding Ø17 mm face relief keep the outer rings and shields clear.

Pinch the split retaining head and slide the bearing on while supporting its inner race. The assembly report records these head/bore contacts separately; it does not validate insertion force, PETG strain or the snap-fit durability. The viewer does not simulate bending. Tilt, preload, friction, wear and print fit need physical testing.

## Assembly and downloads

Individual STL downloads and each configuration's ZIP contain the matching printable geometry. The bundle includes CAD source, configuration, bill of materials and validation report. Heat-set the mounting inserts while the lid and base are accessible; mount the base from below. Install the adjustable carrier, bearings and drive before closing the lid. The exploded view removes lid screws, lid (with its inserts), carriage, drive and bearing packs, then the carrier. M5 inserts remain attached to the carrier. The printed screw rotates during carriage withdrawal.

This is a geometry prototype, not a strength, stiffness or fatigue rating. No external screw-support bearings are fitted. Bought motor and hardware meshes are fit references. Printed threads, insert pilots and three-ridge holes require calibration for the actual print process.

## Rebuilding

Install `python -m pip install -r experiments/t8-leadscrew/requirements.txt`, then run `python experiments/t8-leadscrew/model.py --screw-length 300 --width 1 --check`. The site offers 100 and 300 mm screws, both at width 1 only.

The 100 mm assets stay at the experiment root; the 300 mm assets use `lengths/300mm/`. Each has matching STL files, source and a validation report. `--quick` produces an unvalidated preview only.

Print the base with its floor on the bed (CAD Z up). A before/after Bambu Studio slice for the 40 mm, 1x printed-screw base is available in the site’s slice preview. It uses P2S 0.4 mm, Generic PETG, 0.20 mm layers, four walls, 25% gyroid and automatic tree supports everywhere. Remaining axle and shelf supports still need removal; the preview is not a physical removal or strength test.

The 1x output plate has two underside access openings behind its lower mounting holes (7 mm wide, 20 mm long, rounded at the rear with a 45-degree roof). Extend the carriage fully before fitting M3 socket-head bolts from the inside. Clearance is checked for M3x12 bolts with 5.5 mm diameter, 3 mm high heads and a 3 mm envelope for a short hex key. The upper pair loads from above. The 31 mm pattern, 8 mm flange and three-ridge pilots remain unchanged. The 2x/4x plates retain their existing geometry.
