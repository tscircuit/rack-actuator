T8 screw length: 300 mm. Usable travel: 270 mm. Overall retracted length: 391 mm.
Width variant: 4x. Output plate: 168 x 42 mm. Base width: 206 mm. Upper bearing span: 167.569 mm.

# T8×8 — 100 and 300 mm screw lengths

Select the purchased rod length independently of 1×, 2× and 4× width. The 100 mm screw gives 70 mm usable travel; the 300 mm screw gives 270 mm. Both bearing stations stay 40 mm apart and support the carriage throughout travel. The rod engages a rigid 5-to-8 mm coupling by 8 mm, with a bolted brass flange nut in the hollow carriage.

| Screw length | Travel | Bearing X stations | Base length | Overall retracted | Overall extended |
|---|---|---|---|---|---|
| 100 mm | 70 mm | 93 / 133 mm | 159 mm | 191 mm | 261 mm |
| 300 mm | 270 mm | 293 / 333 mm | 359 mm | 391 mm | 661 mm |

The screw starts at X=26 mm. The 15 mm nut remains fully engaged, with 4.5 mm of screw beyond its front face at full extension. The tip stays 25 mm inside the retracted output face. T8 threads use smooth fit envelopes in the viewer; actual helical engagement, backlash and friction are not simulated. The 300 mm rod is the lab-stock length. Long components are single-piece STLs, so check print-bed dimensions.

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

Install `python -m pip install -r experiments/t8-leadscrew/requirements.txt`, then run `python experiments/t8-leadscrew/model.py --screw-length 300 --width 1 --check`. The site offers 100 and 300 mm screws, each at widths 1, 2 and 4.

The 100 mm, 1× assets stay at the experiment root; wider models use `widths/2x/` and `widths/4x/`. The 300 mm models use `lengths/300mm/` with the same width subdirectories. Each configuration has matching STL files, source and a validation report. `--quick` produces an unvalidated preview only.
