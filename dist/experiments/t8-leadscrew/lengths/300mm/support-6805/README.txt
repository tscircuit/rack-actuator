T8 screw length: 300 mm. Usable travel: 204 mm. Overall retracted length: 401 mm.
Width variant: 1x. Output plate: 42 x 42 mm. Base width: 80 mm. Upper bearing span: 41.569 mm.

# T8×8 — 100 and 300 mm screw lengths

Select a 100 or 300 mm purchased T8×8 rod, then choose **Standard drive** or the separate **6805 bearing support · Z axis** variant. The 100 mm rod supports 1×, 2× and 4× widths. The 300 mm rod is 1× and now has **80 mm** between guide-bearing stations, twice its previous spacing. Its longer spacing reduces usable travel by 40 mm without increasing its base length.

| Rod | Drive | Widths | Usable extension | Guide station spacing |
|---|---|---|---|---|
| 100 mm | Standard | 1× / 2× / 4× | 70 mm | 40 mm |
| 100 mm | 6805 Z support | 1× / 2× / 4× | 44 mm | 40 mm |
| 300 mm | Standard | 1× | 230 mm | 80 mm |
| 300 mm | 6805 Z support | 1× | 204 mm | 80 mm |

Travel is extension beyond the base exit. It is limited by both complete moving-nut engagement and full bearing coverage, not the purchased rod length. Standard rods start at X=26 mm; Z rods at X=26.5 mm. Wide 100 mm versions have a 14 mm longer nose for inside output-bolt access while retaining the full guide spacing and travel. Long components are single-piece STLs; check your print-bed dimensions.

### Optional Z support

The Z variant uses a 6805 bearing (25×37×7 mm) in a holder with **outward-facing mounting bosses on a 52×31 mm pattern**, separate from the central NEMA17 pattern. Four full-depth columns tie an uninterrupted outer-race shoulder to the wall. Four M3×45 steel bolts load from behind the wall, with 0.5 mm-thick M3 washers (7 mm OD) on both sides and exposed M3 DIN 985 locknuts on the front. The motor uses four separate M3×12 screws with 6 mm engagement; verify the motor's thread depth. The holder is 62 mm wide and fits below the existing lid. The motor-facing recess remains Ø37.2 mm; its continuous lip has a Ø35 mm opening, matching NSK's maximum housing-abutment diameter. The hub retains its Ø24.9 mm journal and Ø27 mm inner-race shoulder. Only the Z base and holder need reprinting for this change; the lid, carrier, carriage and hub stay unchanged. The same physical holder is used in the standalone 6805 experiment (its assembly coordinates differ by 2 mm along X).

Use a **second T8 brass flange nut**, Ø22 mm flange / Ø10 mm body / 15 mm total length / four holes on Ø16 mm PCD. It is captured in the hub with four M3×12 screws and three-ridge pilots. Fit these four screws through the straight front access passages on the loose hub **before installing the T8 locking-clamp bolt**; that cross-bolt crosses one access passage after assembly. The retaining nut is oriented with its holes at the top, bottom, left and right. Its thread transfers axial load from the rod into the hub; the second split clamp prevents the rod winding out of this nut. The motor clamp fits a 5 mm D shaft, 4.5 mm flat-to-opposite side. Both clamps use M3×12 bolts and M3 hex nuts. Fit and clamp the T8 rod with its rear end at X=26.5 mm. The 100/300 mm rod is unchanged.

Load path toward the screw tip: rod → captured nut → hub → inner-race shoulder → 6805 → continuous housing lip → front washers/locknuts → steel tie bolts → rear washers → motor wall/base. **This is one-direction thrust support; there is no independent reverse-direction bearing retainer.** Orient the Z axis for this load direction. No cap, circlip or loose inner-race spacer is introduced. Geometry checks do not establish fatigue life, PETG creep, thread pull-out strength or vibration endurance.

The 2× Z carrier shifts its front adjustment-bolt pair 6 mm rearward to keep the lid tool openings clear of the 31 mm insert grid. The Z variant needs its matching base/lid/carriage/carrier plus hub and holder; it is a selectable assembly, not a retrofit of the standard carriage. The standalone 6805 experiment and printed-lead-screw family remain separate. Before tightening the motor coupling, gently seat the screw toward its tip so the outer race rests against the housing lip; clamp in that seated position without axially preloading the motor. Loosen the coupling before disassembly. Remove the front locknuts/washers and withdraw the four holder bolts rearward, then slide the supported drive module 30 mm off the shaft and lift it clear. The separate motor bolts are now accessible. The exploded view follows this order before separating the housing and rear-loaded bearing. The retaining nut and clamps remain assembled to the hub.

## Width and external mounting patterns

The 1× T8 uses a 42 mm output plate and an 80 mm base. Its six bearings include two lower bearings tightened together by one carrier and four M5 adjustment bolts. The carrier's ruthex RX-M5x9.5 inserts use Ø6.4 mm printed pilots, 10.5 mm deep. Heat-set these before assembly.

The 100 mm T8 offers 42/104/168 mm output plates, matching the 40 mm printed-screw width convention. Wider T8 versions move the four upper bearings outward and use four lower bearings on the shared carrier. All external mounting interfaces use a **31 mm square hole grid**. Every adjacent pair of columns and rows forms a complete NEMA17 pattern. The 1×, 2× and 4× output plates are **42, 104 and 168 mm wide**, respectively. The 2× plate was widened from 84 mm to keep a centered NEMA17 pattern while adding columns at the same 31 mm pitch; the carriage running section, bearings and base widths are unchanged.

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

All four upper-bearing blocks and adjacent adjustment shelves rise from the sidewalls on 45° undersides. The axle-root bosses are trimmed to the same slope so their lower arcs cannot seed trapped supports. The raised bolt seats use M5×40 socket-head adjustment bolts; carrier position and adjustment travel are unchanged.

The carriage runs on smooth flats with no raised side rails. The CAD checks include nominal bearing alignment and ±1 mm axial displacement relative to the carriage. The base and carrier retain their existing clearance channels. Split Ø4.8 mm axles keep the 6.4 mm-wide retaining shoulders and extended 30° bent tips. Restored through-slots taper from 2.2 mm at the tip through 2.0 mm at the head to 1.2 mm near the root, ending in a 0.6 mm radius. A Ø5.4 mm clearance behind the inner-race seat frees the prongs to flex inward. The Ø7.4 mm inner-race lands and surrounding Ø17 mm face relief keep the outer rings and shields clear.

Pinch the split retaining head and slide the bearing on while supporting its inner race. The assembly report records these head/bore contacts separately; it does not validate insertion force, PETG strain or the snap-fit durability. The viewer does not simulate bending. Tilt, preload, friction, wear and print fit need physical testing.

## Assembly and downloads

Individual STL downloads and each configuration's ZIP contain the matching printable geometry. The bundle includes CAD source, configuration, bill of materials and validation report. Heat-set the mounting inserts while the lid and base are accessible; mount the base from below. Install the adjustable carrier, bearings and drive before closing the lid. The exploded view removes lid screws, lid (with its inserts), carriage, drive and bearing packs, then the carrier. M5 inserts remain attached to the carrier. The printed screw rotates during carriage withdrawal.

This is a geometry prototype, not a strength, stiffness or fatigue rating. The standard drive has no external screw-support bearing; the selectable Z variant adds one 6805. Bought motor and hardware meshes are fit references. Printed threads, insert pilots and three-ridge holes require calibration for the actual print process.

## Rebuilding

Install `python -m pip install -r experiments/t8-leadscrew/requirements.txt`, then run `python experiments/t8-leadscrew/model.py --screw-length 300 --width 1 --check`. The site offers 100 and 300 mm screws, both at width 1 only.

The 100 mm assets stay at the experiment root; the 300 mm assets use `lengths/300mm/`. Each has matching STL files, source and a validation report. `--quick` produces an unvalidated preview only.

Print the base with its floor on the bed (CAD Z up). A before/after Bambu Studio slice for the 40 mm, 1x printed-screw base is available in the site’s slice preview. It uses P2S 0.4 mm, Generic PETG, 0.20 mm layers, four walls, 25% gyroid and automatic tree supports everywhere. Remaining axle and shelf supports still need removal; the preview is not a physical removal or strength test.

The 1x output plate has two underside access openings behind its lower mounting holes (7 mm wide, 20 mm long, rounded at the rear with a 45-degree roof). Extend the carriage fully before fitting M3 socket-head bolts from the inside. Clearance is checked for M3x12 bolts with 5.5 mm diameter, 3 mm high heads and a 3 mm envelope for a short hex key. The upper pair loads from above. The 31 mm pattern, 8 mm flange and three-ridge pilots remain unchanged. The 2x/4x printed-screw plates also provide upper and lower 7 × 16 mm access pockets for their repeated mounting patterns. Use a short hex key with a 14 mm reach at the wide plates. The printed-screw front bearing station moves inward by 14 mm (60 mm station spacing) to keep the pockets outside the running surfaces without increasing the 40 mm actuator envelope. Reprint the matching wide base, carrier, lid and carriage together; these revised wide carriages are not compatible with the old front bearing location. Wide T8 noses extend by 14 mm instead, retaining 40 mm station spacing. All output holes are checked for bolt loading, driver access and installed clearance through travel.

The two lid mounts beside the motor now grow from continuous gussets, rooted 2 mm into the motor wall. Their undersides slope at least 45° above horizontal in both the forward and outward directions, replacing the hanging blocks and thin tabs. The existing lid holes and 68 mm assembly height are retained; only the base STL changes for this revision. Print with the base floor on the bed. The public slice preview uses the updated 40 mm, 1× printed-screw base.

## Lower carrier clearance

The blocks behind the lower bearings rise just 1 mm above the Z=20 mm side rails, with 1 mm, 45-degree chamfers around their tops. At Z=21 mm they remain 3.5 mm lower than the original tall blocks, adding local support behind the bearing seats without restoring the tall bumps. The circular inner-race seats, split axles, bearing centers and four M5 insert mounts are unchanged. Clearance to the base is checked throughout the 0–1 mm adjustment range. Only the carrier needs reprinting; the existing base and hardware remain compatible.

### Support-free bearing adjustment bays

The base bearing blocks, axle-root bosses and adjustment shelves now have continuous 45° undersides rising from the sidewalls. The bolt seats are at Z=47 mm: use four M5×40 ISO 4762 socket-head screws (8.5 mm head diameter), with the existing washers and M5 inserts. The carrier, bearings, lid, moving carriage and mounting grid are unchanged. Remove the bolts before the bearings, then lift the washers after the upper bearings are withdrawn. Print the base floor-down. The published 40 mm, 1× printed-screw Bambu slice has no support extrusion in any of the four bearing-adjustment bays with automatic supports everywhere; the motor aperture still has accessible support. Other configurations receive CAD checks, not a claim of identical slicer output.

The intended static input remains 1 lb (4.448 N), not a tested rating. Geometry checks verify all four complete columns and the positive abutments along the load path. They do not establish plate bending strength, bolt preload or PETG creep life. Print the holder with its front face on the bed and columns upward. See [NSK's mounting dimensions](https://www.nsk.com/engineering/6805-dgbb-sr.html) and [DIN 985 locknuts](https://www.westfieldfasteners.co.uk/Standards/Nut-HexNy-M.html).
