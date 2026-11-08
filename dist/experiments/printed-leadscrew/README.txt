Width variant: 1x. Output plate: 42 x 42 mm. Base width: 80 mm. Upper bearing span: 41.569 mm.

# Printed Ø20 mm screw — adjustable wide actuator

40 mm output extension. Two bearing stations guide the carriage. The 1× has six 625ZZ bearings; 2× and 4× have eight (four upper and four lower). Bearing stations are 63 and 137 mm (74 mm apart). The lower bearings are supported on one side by one shared rigid printed carrier with two side rails and cross-braces. There are no flexures or external motor/screw support bearings.

## Bearing adjustment

Four M5×25 adjustment bolts enter from above, bear on washers and fixed shelves, and engage four M5 heat-set inserts in the shared carrier. The rear row is X=51 mm and the front row is the front bearing station minus 12 mm. Y=±26 mm at 1×, ±47 mm at 2× and ±89 mm at 4×. Tighten evenly to take up the 1 mm adjustment range. Preload force and carrier tilt are not simulated.

Use four ruthex RX-M5x9.5 inserts (Ø7.1 mm × 9.5 mm). Printed seats have Ø6.4 mm pilots, 10.5 mm depth, a tapered entry and a through passage for the bolt. At least 2.6 mm radial material is retained around the seat. See the [manufacturer’s dimension sheet](https://www.igo3d.com/mediafiles/Sonstiges/Ruthex/ruthex_Datenblatt_RX-Serie.pdf). Heat-set the inserts into the loose carrier before installing bearings and assembling it. The assembly viewer represents displaced plastic around the seated insert; the STL retains the smaller pilot. Inserts stay bonded to the carrier during adjustment and explosion. Test installation on the actual print; heating and pull-out strength are not simulated.

The carrier slides in one base channel and withdraws through the exit. Integral solid PETG axles hold the bearings with retained heads. Lid bolts and external receiving holes retain their existing three-ridge seats; outer base mounts remain plain M5 clearance through-holes. Motor bolts enter the motor’s metal threads.

## Bearing-face relief

All bearing supports have an integral Ø7.4 mm inner-race land. A Ø17 mm relief around each land recesses the surrounding face by 2 mm relative to the bearing face, keeping the outer ring and shield clear. No bearing axle bolts, washers or loose support spacers are needed. The full bearing insertion corridor is relieved to remove the former thin plastic lip above each bearing.

The land diameter is a prototype choice within the 7.4–8.3 mm shaft-abutment range in the [SKF 625-Z drawing](https://assets.alliedelec.com/v1644492269/Datasheets/c5ad7fad1c9a5f6a3c382f0ca640fe6a.pdf). Confirm the inner-race face width on the purchased bearing and remove print burrs before assembly. Validation checks the land material and the surrounding clearance on both bearing faces against every printed part.

## Solid PETG bearing axles

The relief slots are filled while retaining the existing Ø4.8 mm coaxial journal, 6.4 mm-wide retaining shoulder and extended 30° bent tip. The widest shoulder remains nearest the bearing face. The deep clearance around the axle root is also filled, joining it directly to the Ø7.4 mm inner-race land. The surrounding Ø17 mm face relief remains to keep the bearing outer ring and shields clear.

The bearing must be forced over the solid retaining head. Support the inner race and the axle root during installation. The CAD report records head/bore interference separately from unexpected assembly collisions; it does not establish that PETG can deform enough without damage. No prong bending is animated. The STL and viewer have identical axle geometry. The carriage has smooth bearing faces without raised side rails; axial bearing retention comes from the solid axle heads.

## Structural lid

The 4 mm lid sits at Z=64–68 mm, within the original motor plate's 68 mm height. Short flanges beside the motor replace the tall posts. Six M3×12 button-head bolts clamp the lid to 12 mm-deep three-ridge base pilots; their heads are recessed below Z=68 mm. Lid bolt pass-throughs and head recesses remain clearance features so the bolts can clamp the lid to the threaded base. The four carrier-adjustment bolts remain reachable through Ø6 mm driver holes. The original floor mounting wells remain accessible through edge reliefs in the lid.

The four outer base mounting holes are plain Ø5.5 mm through-holes for M5 bolts, without self-threading ridges. Their raised pads are 10 mm thick, with clear access from above. The four lid mounts and six mounts on each side retain blind M5 three-ridge self-forming pilots, 9 mm deep. The output face retains its four central M3 three-ridge pilots; 2× and 4× add four outer pilots. Local bosses extend inward or upward into existing free space; the lid stays within the selected variant’s base width and the 68 mm assembly height. Limit screw penetration into the blind M5 pilots to 8.4 mm so the screw does not bottom out. External attachment screws are not included in the model; choose their length for the attached structure. The outer base bolts fasten into the supporting structure or use nuts beneath it; the blind receiving pilots need no nuts or inserts.

The large horizontal lower-bearing access holes and the cutouts in the shared carrier's opposite rail are closed. Bearings are installed from inside with the lid and carriage removed, using the existing bearing assembly sequence. The lid is translucent by default in the viewer; use Show lid or Transparent lid to inspect it.

## Dimensions and mounting

NEMA17 42×42×40 mm motor; 31×31 mm bolt pattern. The 1× carriage has a 16 mm guide inradius and 12 mm radial corner chamfers; wider variants translate the two angled running faces outward. Output face at X=155 mm when retracted, exactly 40 mm beyond the base at full extension. Carriage tail X=10 mm at home; 4 mm tapered entry. Base length including rear brace feet is 191 mm, width 80 / 122 / 206 mm; overall retracted length 195 mm including motor.

Four plain Ø5.5 mm through-holes accept M5 base bolts from above through 10 mm-high local pads. Open Ø12 mm wells leave room for Ø10 mm washers and an Ø11 mm driver. The output flange is 42 / 84 / 168 mm wide, 42 mm tall and 8 mm thick. All variants retain the central NEMA17 31×31 mm M3 three-ridge pattern. The 2× and 4× plates add four outer M3 three-ridge pilots on 73×31 and 157×31 mm centers, respectively; maximum output screw entry is 8 mm.

## Printed direct drive

The one-piece printed screw has a nominal Ø20 mm single-start trapezoidal helix: 8 mm lead, Ø16 mm root, 2 mm radial thread depth, 2 mm crest width and 5 mm root width. An integral Ø22 mm split clamp fits a nominal Ø5 mm D shaft measuring 4.5 mm from the flat to the opposite side. Its D bore is Ø5.3 mm with a 4.8 mm flat-to-opposite measurement, providing 0.15 mm radial and flat clearance before tightening. Shaft engagement is 15 mm. An M3×12 socket-head bolt crosses the 1 mm split and threads into an M3 hex nut (5.5 mm across flats, 2.4 mm thick), held against rotation in a 5.9 mm hex pocket. The clamp bolt uses clearance holes, not self-forming plastic threads. No separate shaft coupling is fitted. Confirm the actual motor's shaft diameter, flat depth and flat length before printing; the clamp fit needs checking with the actual PETG print.

Two 12 mm female threaded bands are integral to the carriage at X=36–48 and X=96–108 mm in its home position. They share a continuous helix phase. Female relief is 0.35 mm radial and 0.25 mm axial per flank relative to the prototype male profile. The middle and nose bores are smooth Ø21.2 mm; the rear clamp relief is Ø27 mm. The screw's working thread runs X=30–152 mm. Both bands remain fully engaged throughout the 40 mm stroke. The longer hollow nose keeps the screw tip 3 mm inside the retracted output face.

Print the screw and carriage as actual threaded parts, not smooth hardware references. Fit, friction, wear, print shrinkage and the split clamp need physical testing; the CAD clearance is not a calibrated printer tolerance. Do not drill the threaded bands smooth. Threaded motion is synchronized in the viewer and exploded withdrawal.

## Assembly and files

Use the exploded assembly slider to inspect lid removal, bearing removal and the shared carrier. Extend the carriage to reach the motor bolts. The outer base mounts and all four carrier adjustment bolts are reached from above while assembled. Inherited inner base holes must be fastened before carrier and carriage assembly. Printed screw versions require screwing the carriage onto the helix; the exploded path rotates the screw during withdrawal. With the carriage removed, support the inner race to press the bearings onto or off the solid axles. The exploded view illustrates forced axial removal and retains visible head/bore interference. After adjustment-fastener removal, lift the carrier clear of the raised floor mounting pads and slide it out through the exit. The drive withdraws as a subassembly; its clamp bolt then lifts out and its hex nut drops out of the underside pocket. Insert the nut from underneath before fitting the printed screw to the motor. Start the bolt loosely, align the D flat and slide onto the shaft, then tighten through the lid access hole with the carriage fully extended. Rotate the drive to align the clamp bolt with the access hole before tightening. The 2.4 mm nut engages the bolt fully, with 1.5 mm of bolt projecting past it.

All printable parts are in the STL bundle. Source rebuild: install `python -m pip install -r experiments/printed-leadscrew/requirements.txt`, then run `python experiments/printed-leadscrew/model.py --check`. Keep the extracted `experiments` directory structure; the printed variant shares the T8 generator and validator. `--quick` creates an unvalidated preview only.

This is a geometry prototype, not a load/stiffness/fatigue rating. The bearing contacts provide two-station guidance; the print material, bearing preload and unsupported screw still require testing. Three-ridge pilots are prototype values, not preformed helical machine threads.

## Width variants

Use the Width variant selector for 1×, 2× or 4×. Multipliers apply to output-plate width: 42, 84 and 168 mm. The four upper 625ZZ bearings translate outward by 0, 21 or 63 mm on each side; their diameter, axle dimensions and contact angles stay unchanged. The carriage running faces, base walls, lid and carrier rails follow them. The motor and screw remain centered. At 1× the lower contacts retain their original Y=−1 / +1 mm stagger. At 2× both stations have lower bearings at Y=±21 mm; at 4× they are at Y=±42 mm. All four lower bearings share the same adjustable carrier. Base widths are 80, 122 and 206 mm. Travel stays 40 mm, total retracted length 195 mm and height 68 mm. The larger bearing lever arm is intended to improve torsional stability about the travel axis; no stiffness or load rating is established.

Regenerate with `python experiments/printed-leadscrew/model.py --width 2 --check` (or `--width 1` / `--width 4`). Each width has its own assembly mesh, checked STL files, configuration, validation report and source bundle. The default output remains at the experiment root; 2× and 4× are in `widths/2x/` and `widths/4x/`.

## Longer motor braces and weight reduction

Two gussets extend from X=−36 to +6 mm beside the motor. Each is 12 mm wide, with its inner face at Y=±22.5 mm, leaving 1.5 mm to the nominal 42 mm motor body. Rounded triangular openings retain the diagonal load path. The feet remain within the existing total assembly length.

Rounded base-floor openings preserve perimeter rails, a central spine and cross ribs. The carriage has top access windows between its threaded bands; wider variants also have pockets on either side of the screw, with 4 mm floors and transverse ribs. All bearing contact strips remain continuous. The threaded bands and output mounting holes remain intact. The validation report records removed CAD volume relative to the same revised geometry before cutouts; this is not a strength or printed-material mass claim.

## Smooth bearing running faces

The raised 4 × 4 mm side rails are removed from every carriage width. Bearings run on the original flat faces, with no rails to catch small axial misalignment. The solid axle heads remain the axial bearing retainers. Existing support clearance channels are preserved so only the carriage needs reprinting; the base and shared bearing carrier geometry is unchanged.

Validation checks that the former rail regions are empty, the running skins remain continuous, and the bearing envelopes clear the carriage at nominal alignment and ±1 mm axial displacement. Tilt, preload force and print-surface friction still require physical testing. Travel, screw engagement, mounting patterns and threaded sections are unchanged.

## Cumulative base-floor mounting patterns

The 2× base retains the 1× pattern and its own outer pattern (8 holes). The 4× base retains the 1×, 2× and 4× patterns (12 holes). All patterns have X = -3 and 149 mm; their Y positions are ±34, ±55 and ±97 mm respectively, measured from the motor/screw centerline. This compatibility is between widths of the printed-screw design; the T8 base retains its own longitudinal spacing.

All floor bores are unthreaded Ø5.5 mm through-holes. The current width's four outer holes retain the original 10 mm-high washer pads and assembled top access. Inherited inner holes have Ø10.5 mm, 90° countersinks, 2.5 mm deep, in slightly wider pads. Use M5 countersunk screws with heads at most Ø10 mm and seat them flush; do not add washers under these heads. Select screw length for the supporting structure.

Fasten the base through the inherited holes from above before installing the bearing carrier and carriage. The installed flush-head envelopes are checked through the complete 40 mm stroke and staged assembly path, including carrier insertion. The lid and output-plate attachment patterns are unchanged.
