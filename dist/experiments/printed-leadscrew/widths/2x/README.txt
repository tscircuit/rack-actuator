Printed screw travel: 40 mm. Screw tip X=152 mm. Overall retracted length: 195 mm.
Width variant: 2x. Output plate: 84 x 42 mm. Base width: 122 mm. Upper bearing span: 83.569 mm.

# Printed Ø20 mm lead screw — 40 and 120 mm travel

Select 40 or 120 mm of extension beyond the base exit, independently of 1×, 2× and 4× width. The screw and hollow nose extend with travel; both 12 mm threaded bands stay fully engaged and the screw stays inside the retracted carriage.

| Travel | Bearing X stations | Screw tip X | Overall retracted length | Overall extended length | Base length |
|---|---|---|---|---|---|
| 40 mm | 63 / 137 mm | 152 mm | 195 mm | 235 mm | 191 mm |
| 120 mm | 143 / 217 mm | 232 mm | 275 mm | 395 mm | 271 mm |

All variants keep 74 mm station spacing, 68 mm total height, and a 3 mm screw-tip recess at home. The base-length figure includes the rear motor braces. Parts are single-piece STLs; check print-bed fit for the selected length and width.

## Printed screw and motor coupling

The screw has a single-start Ø20 mm trapezoidal helix, 8 mm lead, Ø16 mm root, 2 mm radial depth, 2 mm crest width and 5 mm root width. Its working thread runs from X=30 mm to the selected tip. Female bands remain at home X=36–48 and X=96–108 mm, with shared helix phase, 0.35 mm radial relief and 0.25 mm axial relief per flank. The intermediate bore and longer nose are smooth Ø21.2 mm. At full travel the front threaded band ends 4 mm before the screw tip.

An integral Ø22 mm split clamp fits a nominal 5 mm D shaft measuring 4.5 mm from flat to opposite side. The D bore is Ø5.3 mm and 4.8 mm across the flat, with 15 mm shaft engagement. An M3×12 bolt tightens into a captive M3 hex nut (5.5 mm across flats, 2.4 mm thick) in a 5.9 mm pocket. Insert the nut from below before coupling the motor. With the carriage extended, rotate the bolt into alignment with the lid access hole and tighten from above. Do not smooth out the carriage's two threaded bands.

The rear motor braces remain 42 mm long and 12 mm wide, with 1.5 mm nominal motor-side clearance. Base and carriage pockets retain the contact strips, mounting material and threaded bands.

## Width and external mounting patterns

Widths 1×, 2× and 4× use output plates 42, 84 and 168 mm wide and bases 80, 122 and 206 mm wide. The motor and screw remain centered. Four upper bearings move outward; 1× has two lower bearings, while 2× and 4× have four. One carrier and four M5 adjustment bolts tighten the lower bearings together. Its ruthex RX-M5x9.5 inserts use Ø6.4 mm printed pilots, 10.5 mm deep. Heat-set these before assembly.

The lid and base have identical XY mounting patterns centered at X=26, Y=0 mm, just ahead of the motor face at X=0. The X rows are 10.5 and 41.5 mm. The 1× pattern uses Y=±15.5 mm; 2× adds ±36.5 mm; 4× adds ±78.5 mm. This gives 31×31, 31×73 and 31×157 mm patterns, with 4, 8 or 12 insert seats on each face. These external patterns use M3 threads. The output plate retains its separate central 31×31 mm M3 three-ridge pattern and outer width-dependent holes.

Use [ruthex RX-M3Sx4.0 short inserts](https://www.ruthex.de/en/collections/gewindeeinsatze/products/ruthex-gewindeeinsatz-m3s-100stuck-rx-m3x4-0-short-messing-gewindebuchsen-fur-3d-druck), nominal Ø4.6×4 mm. Printed pilots are Ø4 mm with a Ø4.8 mm entry taper; the pilot diameter is a prototype fit to calibrate on the actual PETG print. Install lid inserts from above and base inserts from below. Both seats are open-bottomed. Limit external screw entry to 4 mm from the lid top or 5 mm from the base underside. External mounting screws are not included because their length depends on the attached structure. The viewer shows installed Ø4.64 mm cavities around the insert references; STLs retain undersized pilots.

External side mounting bosses and side holes are removed. The former perimeter M5 floor pads and external M5 lid receivers are replaced by the matched M3 patterns. These mounts do not preserve the previous external hole locations.

## Windowed structural lid

The lid stays at Z=64–68 mm and does not increase the 68 mm assembly height. Rounded through-windows remove material between a continuous 8 mm perimeter and transverse fixing/mounting ribs. Mounting rows retain full-width bands of material; intermediate ribs divide long windows. The geometry report records the exact CAD volume reduction for the selected configuration, not printed mass or a stiffness rating.

Six recessed M3×12 button-head screws fasten the lid into the base's 12 mm-deep three-ridge pilots. These structural fasteners are separate from the external M3 insert patterns. Driver access remains for the four carrier-adjustment bolts and motor bolts; extend the carriage to reach the motor bolts.

## Bearings and running faces

The carriage runs on smooth flats with no raised side rails. The CAD checks include nominal bearing alignment and ±1 mm axial displacement relative to the carriage. The base and carrier retain their existing clearance channels. Solid Ø4.8 mm axles keep the 6.4 mm-wide retaining shoulders and extended 30° bent tips, without relief slots. The Ø7.4 mm inner-race lands and surrounding Ø17 mm face relief keep the outer rings and shields clear.

The bearings must be forced over the solid heads. The assembly report records these head/bore contacts separately; it does not validate insertion force, PETG strain or the ability to force the bearing on without damage. The viewer does not simulate bending. Tilt, preload, friction, wear and print fit need physical testing.

## Assembly and downloads

Individual STL downloads and each configuration's ZIP contain the matching printable geometry. The bundle includes CAD source, configuration, bill of materials and validation report. Heat-set the mounting inserts while the lid and base are accessible; mount the base from below. Install the adjustable carrier, bearings and drive before closing the lid. The exploded view removes lid screws, lid (with its inserts), carriage, drive and bearing packs, then the carrier. M5 inserts remain attached to the carrier. The printed screw rotates during carriage withdrawal.

This is a geometry prototype, not a strength, stiffness or fatigue rating. No external screw-support bearings are fitted. Bought motor and hardware meshes are fit references. Printed threads, insert pilots and three-ridge holes require calibration for the actual print process.

## Rebuilding

Install `python -m pip install -r experiments/printed-leadscrew/requirements.txt`, then run `python experiments/printed-leadscrew/model.py --travel 120 --width 1 --check`. Width choices are 1, 2 and 4; travel choices are 40 and 120 mm. Keep the extracted experiments directory structure because the generator and validator are shared with T8.

The 40 mm, 1× assets stay at the experiment root; other widths use `widths/2x/` and `widths/4x/`. The longer design uses `travel/120mm/` with the same width subdirectories. `--quick` produces an unvalidated preview only.
