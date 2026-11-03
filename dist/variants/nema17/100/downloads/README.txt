RACK ACTUATOR — REVISION 19
CadQuery 2.7.0, dimensions in mm. See configuration.json for this preset.

CHANGES / REPRINTING
The moving output pad is now 18 x 18 mm with four M3 heat-set inserts on
a 9 x 9 mm pattern, replacing the two through-holes. Inserts enter from
the same Z=21 mounting face and sit 0.3 mm below it. Default blind-pocket
backing is 12.3 mm. The pad remains on the rack's printing plane.
The side face is flat, with four recessed M3 heat-set inserts replacing
the projecting slotted pads. Reinforcement is inside the tray and joins
the floor/corner structure; blind pockets retain 2 mm of backing.
Two three-bearing stations: each has two upper 45-degree 625ZZ bearings
and one lower 625ZZ on an integral spring floor. The output station is
25 mm behind the enclosure exit. The other station mirrors it around the
motor/pinion at X=0. Longer strokes increase the station spacing.
Rack length preserves at least 13 mm from either station center to the
guide end throughout travel, 5 mm beyond the bearing radius. Longer
chassis have attachments near the bearing stations and the centered motor.
Local spring floors retain the prior dimensions, preload and wall blends.
M3 heat-set enclosure inserts and reinforced top/side mounting are retained.
Five printed components: chassis, rack, pinion, tray and lid.
From revision 18, reprint only the rack and add four M3 inserts.
Reuse the matching chassis, pinion, tray, lid and bearing hardware. Each stroke has its own chassis;
do not mix preset components. NEMA17 pinion/rack: 20 degrees; NEMA14: 25.

PRESETS (MODULE 2; BOTH MOTORS)
Stroke   Bearing span   Housing   Rack print   Lid screws   M3 inserts
40       54             136       151.5        4            18
100      164            306       321.5        6            22
150      264            456       471.5        8            24
200      364            606       621.5        12           28
250      464            756       771.5        14           30
400      766            1208      1223.5       22           38
Centering the gear while covering the teeth and maintaining full-stroke
bearing engagement requires longer racks and housings. At 400 mm stroke,
allow about 1224 mm of print length. These are single-piece parts; no
segmentation is provided. Revised layouts require fit, sag and load tests.

INSERTS / ENCLOSURE HARDWARE
The table includes enclosure inserts plus four output-pad inserts.
M3 inserts: default 4.6 mm OD x 5 mm long; printed pilot diameter 4.2 mm,
with 0.4 mm extra pocket depth. Match your insert manufacturer's guidance;
OD, length and pilot are configurable. Nominal knurl-to-pilot overlap is
intentional: plastic is displaced by heat during installation.
M3x20 socket lid screws, quantity from the table; M3x10 socket chassis
screws (two for 40 mm stroke, four for the longer presets). Maximum modeled M3 head diameter 5.5 mm, height 3 mm.
See bill-of-materials.json for the selected preset's quantities.

MOUNTING
Side: four M3 inserts, recessed 0.3 mm into the flat rear side face.
X spacing = housing length minus 15 mm; Z spacing = motor depth minus
10 mm (default 30 mm NEMA17 / 24 mm NEMA14). Use 3–5 mm thread engagement,
which means 3.3–5.3 mm screw penetration measured from the outer wall.
Top: four M3 inserts, flush at Z=24.9, in full-height posts attached to the
tray. These transfer mounting loads directly to the tray, bypassing the
removable lid. Use application-length screws with 3–5 mm engagement;
do not bottom screws in the blind insert pockets.
Default 40 mm top pattern: 121 x 75.8 mm NEMA17; 121 x 69.8 mm NEMA14.
Longer presets: X spacing = housing length minus 15 mm. The Y spacing is
unchanged. Exact coordinates are in the STEP, viewer and validation.json.
A top-mounted module must be detached from its fixture before the lid can
be lifted. For the full service animation, detach the module from any
external mounting fixture before lowering the tray.
Output: four M3 inserts on a 9 x 9 mm pattern in an 18 x 18 mm face.
Use 3–5 mm thread engagement, or 3.3–5.3 mm penetration from the pad face.
Remove the attached load before withdrawing the rack for service.

MOTOR / DRIVE
NEMA17: 42 x 42 x 40 mm body, 31 mm mounting pitch, 18T / 20-degree pinion.
NEMA14: 35.2 x 35.2 x 34 mm body, 26 mm mounting pitch, 14T / 25-degree pinion.
Verify actual motor shaft, pilot and mounting dimensions. The motor rear
projects 4 mm beyond the case; its rear-mounted controller is not modeled.
Keep electronics/connectors behind the motor's rear plane and provide
cooling/cable space. The motor plus driver leave before the tray during
service, so the tray need not pass over an assumed controller outline.
Default module 2; 0.6 mm tooth walls; 8 mm tooth face; 0.10 mm oversize per
flank. Circular tooth-root reliefs; no internal fingers. All teeth stay
inside the enclosure over the preset travel, with a smooth output tongue.
5.30 mm D bore for 5 mm shaft with a 0.5 mm-deep flat, 0.15 mm wall clearance.
Tap the 2.5 mm radial pilot M3; M3x4 flat-point screw normal to the shaft flat.
4 x M3x12 countersunk motor screws. Motor mounting land is integral.

GUIDE HARDWARE / CLEARANCE
6 x 625ZZ (5 x 16 x 5); four upper at 45 degrees, two lower.
4 x M5x16 upper and 2 x M5x25 lower socket axle screws.
6 x thin M5 nuts (2.7 mm); 6 x inner-race washers (0.3 mm, 7.5 mm OD).
Clamp only inner races. Clear rotating faces with 0.8 mm radial/axial
relief. Rack/chassis gap is 1 mm; axle-head clearance is 0.5 mm around
the conservative 9.5 x 5 mm head envelope. Actual print/hardware sizes vary.
The square insertion end has no ramp. Spring floors are integral, 1.4 mm
thick, with wall-local R1.2 root blends and 2.3 mm nominal deflection.
There is no rigid lower deck or downward stop. Prescribed CAD deflection
is not a force, recovery, creep or fatigue measurement.

PRINT / ASSEMBLE
Print tray on its outer floor, lid roof-down. Local supports may be needed
at horizontal passages and mounting counterbores. Print rack tooth-face
down, output pad sharing that plane; pinion gear-face down. Keep fine tooth
reliefs clear. Preserve the successful chassis orientation/material; for
a new chassis, keep floor length and bending in the layer plane (Y-normal
print). Remove local supports without damaging the floor root blends.
IMPORTANT: chassis STL is RELAXED; STEP and viewer show installed deflection.

Install the four output inserts from the Z=21 pad face, recessed 0.3 mm,
before inserting the rack. Install the four side inserts horizontally from outside to 0.3 mm below
the outer face. Install the other enclosure inserts from above into the open tray
before installing the chassis or lid. Use the insert manufacturer's process and qualify the
pilot in your material. Do not force cold inserts into printed pockets.
Attach the open tray to a side fixture if used. Assemble lower guide
hardware, seat the chassis, and install its M3x10 screws. Install the
motor and screws BEFORE the upper rollers/axles. Fit the pinion and set
screw. Insert rack from the output/right side, square end first, with the
motor free to turn. Support spring seats by hand if needed. Check all six
bearings rotate and nothing rubs. Fit the lid over the four tall mounting
posts and install its M3x20 screws. Attach a top fixture last, if used.

SERVICE (AFTER DETACHING ANY TOP FIXTURE)
Remove and park lid screws; lift lid and its rear chassis clamps. Withdraw
rack; floors relax. Remove set screw, lift and clear pinion. Withdraw/park
front angled axles, then rear axles; lift upper rollers. Remove motor
screws and lower motor/driver. Remove/park chassis screws; lower tray with
installed inserts. Remove lower nuts, withdraw/park lower axles sideways,
then remove angled nuts and lift lower rollers. Support loose components.
The animation shows clearance paths, not gravity or workholding.

RESOLUTION (200 FULL STEPS/REV, MODULE 2)
Setting       NEMA17 mm/command       NEMA14 mm/command
Full             0.565487                0.439823
Half             0.282743                0.219911
1/4              0.141372                0.109956
1/8              0.070686                0.054978
1/16             0.035343                0.027489
Stroke does not change resolution. These are commanded increments, not
measured positioning accuracy. Match the actual motor full-step angle.

Large standalone STEP downloads use gzip (.step.gz); every ZIP bundle
contains an ordinary STEP file.

SOURCE / CHECKS
pip install -r requirements.txt
python model.py --config configuration.json --out build/custom --check
python build_presets.py --jobs 4
python package_designs.py
CLI options override JSON. Stroke 20..400; tooth module 1.5..2.5;
housing length automatic minimum..2000; motor depth 32..60.
--insert-od 4.6 --insert-length 5 --insert-pilot 4.2
--spring-preload 2.3 --spring-thickness 1.4 --bearing-clearance .8
--hardware-clearance .5 --rack-backbone-width 16 --preload .10
Each preset has its own sampled collision report. All six bearing
contacts are checked at 41 travel positions, with 0.5 mm samples through
the bearing-release transitions during assembly. Intentional elastic
rack/pinion contact and heat-set/host interference are recorded separately.
Insert installation approach, valid single solids, guide geometry and
hardware gaps are checked. Recheck custom parameters and print-test fits.
CAD is not a continuous collision proof, load rating, FEA or fatigue test.
Use controller travel limits; no axial hard stop is provided.
Inspiration: https://github.com/seveibar/compliant-spur-gear
