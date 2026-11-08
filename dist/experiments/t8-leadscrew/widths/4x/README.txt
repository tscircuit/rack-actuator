T8 screw length: 100 mm. Usable travel: 70 mm. Overall retracted length: 191 mm.
Width variant: 4x. Output plate: 168 x 42 mm. Base width: 206 mm. Upper bearing span: 167.569 mm.

# T8×8 — screw-length and width variants

Sized by overall T8×8 rod length, including its portion inside the coupling. The 100 mm version provides 70 mm usable extension (8.75 revolutions). Two stationary bearing stations guide the hollow carriage, 40 mm apart. The 1× has six 625ZZ bearings; 2× and 4× have eight, with two lower bearings per station. All lower bearings share one rigid printed carrier with four adjustment bolts. There are no flexures or external motor/screw support bearings.

## Bearing adjustment

Four M5×25 adjustment bolts enter from above, bear on washers and fixed shelves, and engage four M5 heat-set inserts in the shared carrier. The rear adjustment row is at X = travel + 11 mm (81 mm for the 100 mm screw), and the front row is 40 mm farther forward. Y=±26 mm at 1×, ±47 mm at 2× and ±89 mm at 4×. Tighten evenly to take up the 1 mm adjustment range. Preload force and carrier tilt are not simulated.

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

The four outer base mounting holes are plain Ø5.5 mm through-holes for M5 bolts, without self-threading ridges. Their raised pads are 10 mm thick, with clear access from above. The four lid mounts and six mounts on each side retain blind M5 three-ridge self-forming pilots, 9 mm deep. The output face retains its four M3 three-ridge pilots. Local bosses extend inward or upward into existing free space; overall length, width and height do not increase. Limit screw penetration into the blind M5 pilots to 8.4 mm so the screw does not bottom out. External attachment screws are not included in the model; choose their length for the attached structure. The outer base bolts fasten into the supporting structure or use nuts beneath it; the blind receiving pilots need no nuts or inserts.

The large horizontal lower-bearing access holes and the cutouts in the shared carrier's opposite rail are closed. Bearings are installed from inside with the lid and carriage removed, using the existing bearing assembly sequence. The lid is translucent by default in the viewer; use Show lid or Transparent lid to inspect it.

## 100 mm screw reference dimensions and mounting

NEMA17 42×42×40 mm motor; 31×31 mm bolt pattern. Carriage guide inradius 16 mm, with 12 mm radial corner chamfers. Output face at X=151 mm when retracted, exactly 70 mm beyond the base at full extension. Carriage tail X=10 mm at home; 4 mm tapered entry. Base 159×80 mm; overall retracted length 191 mm including motor.

Four plain Ø5.5 mm through-holes accept M5 base bolts from above through 10 mm-high local pads. Open Ø12 mm wells leave room for Ø10 mm washers and an Ø11 mm driver. Output flange remains 42×42×8 mm with four M3 three-ridge pilots on 31×31 mm centers; maximum output screw entry 8 mm.

## T8 drive

T8×8 rod, Ø8×100 mm at X=26–126 mm; rigid Ø19×25 mm 5-to-8 mm coupling. The purchased brass flange nut bolts to the carriage bulkhead with four M3×12 screws in three-ridge pilots. The screw axis passes through the center of both bearing triangles. The motor/coupling carries screw thrust; no external shaft bearings are fitted. Hardware meshes are reference envelopes, not manufacturing threads.

## Assembly and files

Use the exploded assembly slider to inspect lid removal, bearing removal and the shared carrier. Extend the carriage to reach the motor bolts. Base mounting and all four carrier adjustment bolts are reached from above. Printed screw versions require screwing the carriage onto the helix; the exploded path rotates the screw during withdrawal. With the carriage removed, support the inner race to press the bearings onto or off the solid axles. The exploded view illustrates forced axial removal and retains visible head/bore interference. After adjustment-fastener removal, lift the carrier clear of the raised floor mounting pads and slide it out through the exit. The drive remains a subassembly in the exploded view.

All printable parts are in the STL bundle. Source rebuild: install `python -m pip install -r experiments/t8-leadscrew/requirements.txt`, then run `python experiments/t8-leadscrew/model.py --check --screw-length 100`. Keep the extracted `experiments` directory structure; the printed variant shares the T8 generator and validator. `--quick` creates an unvalidated preview only.

This is a geometry prototype, not a load/stiffness/fatigue rating. The six bearing contacts restore two-station guidance; the print material, bearing preload and unsupported screw still require testing. Three-ridge pilots are prototype values, not preformed helical machine threads.

## Smooth bearing running faces

The raised 4 × 4 mm side rails are removed from every carriage width. Bearings run on the original flat faces, with no rails to catch small axial misalignment. The solid axle heads remain the axial bearing retainers. Existing support clearance channels are preserved so only the carriage needs reprinting; the base and shared bearing carrier geometry is unchanged.

Validation checks that the former rail regions are empty, the running skins remain continuous, and the bearing envelopes clear the carriage at nominal alignment and ±1 mm axial displacement. Tilt, preload force and print-surface friction still require physical testing. Travel, screw engagement, mounting patterns and threaded sections are unchanged.

## Screw-length sizing

100 mm names the purchased rod length, not actuator travel. The rod occupies X=26–126 mm, with 8 mm inside the coupling. The 15 mm-long nut occupies X=36.5–51.5 mm at home and X=106.5–121.5 mm at full extension, retaining full engagement and 4.5 mm of screw beyond its front face. The screw tip stays 25 mm inside the output face when retracted. The base is 159 × 80 mm; total retracted length including the motor is 191 mm, or 261 mm fully extended. Both bearing stations move forward to preserve their complete running flats throughout 70 mm travel; spacing remains 40 mm.

## Width variants

Select 1×, 2× or 4× at each supported screw length. Output-plate widths are 42, 84 and 168 mm; base widths are 80, 122 and 206 mm. The motor and screw remain centered. Upper bearings and guide faces move outward by 0, 21 or 63 mm per side. At 1×, lower bearing centers remain Y=−1/+1 mm. At 2× and 4×, each station has two lower bearings at Y=±21 and ±42 mm, respectively. One four-bolt carrier holds them all. Wide T8 bases retain central motor braces in addition to the outer supports.

All output plates retain the central NEMA17 31×31 mm pattern. Wider plates add outer M3 three-ridge mounting patterns on 73×31 or 157×31 mm centers. Base-floor patterns are cumulative: 4 holes at 1×, 8 at 2×, 12 at 4×. For a given screw length, X rows are −3 mm and 6 mm before the base exit; nested Y offsets are ±34, ±55 and ±97 mm. All floor holes are plain Ø5.5 mm through bores. Inherited inner holes use Ø10.5 mm, 90° countersinks for flush M5 heads. Install these inner mounting screws before the bearing carrier and carriage. The outer four holes retain assembled access from above.

Regenerate with `python experiments/t8-leadscrew/model.py --screw-length 100 --width 2 --check`. The 100 mm, 1× assets remain at the experiment root; other widths use `widths/2x/` and `widths/4x/`. Additional screw lengths use `lengths/<length>mm/`, with the same width subdirectories. Each configuration has its own checked STL bundle, dimensions and report.

## 300 mm lab screw

The additional 300 mm T8×8 screw option is available at 1×, 2× and 4× widths. It provides 270 mm travel, retains full 15 mm nut engagement and 4.5 mm tip margin at full extension, and keeps the screw inside the retracted carriage. The base is 359 mm long; overall length including motor is 391 mm retracted and 661 mm extended. The long base, lid and carriage need a print bed that accommodates their dimensions; the STLs are single parts. Bearing stations are X=293 and 333 mm. Widths and nested base-floor patterns follow the same rules as the 100 mm version.

Rebuild with `python experiments/t8-leadscrew/model.py --screw-length 300 --width 1 --check` (or width 2 / 4).
