RACK ACTUATOR — REVISION 24
CadQuery 2.7.0, dimensions in mm. See configuration.json for this preset.

ENCLOSURE VARIANTS / REPRINTING
Select Enclosed rack or Rear pass-through in the viewer's Variant dropdown.
The pass-through case removes the rear chamber and provides a rear opening
for the rack AND its teeth. Motor, bearing positions and stroke stay fixed.
Stroke    Enclosed length    Pass-through length    Maximum rear projection
40        146                125                    17
100       256                175                    77
150       356                225                    127
Dimensions in mm at module 2, for both motors. Keep the rear travel envelope
clear: opening Y=15..41, Z=-10..22 in CAD coordinates. The shorter housing
still needs the same rack length and swept working space.
Use the matching enclosure/motor/stroke bundle. The tray, lid, mounting
coordinates and chassis lid-post clearance slots vary with enclosure.
Default enclosed parts retain revision 23 geometry.
Both variants include wall-braced rear chassis posts with M3 inserts 6 mm
below their tops and M3x16 screws; front chassis screws remain M3x10.

RETAINED BEARING LAYOUT
One arrangement replaces the former Standard/Short alternatives. The motor
and rear bearing group stay at their pictured positions (pinion X=0,
rear group X=-32). Only the exit group moves: centers are 13 mm behind
the exit face; the bearing rim is 5 mm behind it. The gear is deliberately
not centered between the two bearing groups.
The earlier single broad flexure floor is restored, with its 14 mm free
span and supported R1.2 wall blends. Thickness increases from 1.4 to 1.8 mm.
Default preload remains 2.3 mm. No opposed leaves, extra spring parts or
stationary lower deck. CAD displacement is prescribed, not a measured
carrier angle, force, recovery, creep or fatigue rating.
Moving the exit group requires relief around the existing axle/nut ends
in the enclosure posts. An internal lid screw moves inboard. For service, the retained chassis and
bearing subassembly lifts 6 mm and slides 10 mm rearward after the lower
axles back out 10 mm, before the tray lowers. Four M3
inserts remain on the exit face, side face, top and moving output pad.
Use parts from the same enclosure/motor/stroke preset. NEMA17 rack/pinion use
20-degree pressure angle; NEMA14 use 25 degrees. Do not mix variants.

PRESETS (MODULE 2; BOTH MOTORS)
Stroke   Bearing centers X   Bearing span   Housing length   Rack print
40       -32, 44             76             146              161.5
100      -32, 94             126            256              271.5
150      -32, 144            176            356              371.5
Housing width: 90.8 mm NEMA17 / 84.8 mm NEMA14, at all three strokes.
The table lists enclosed housing lengths; pass-through lengths appear above.
Only 40, 100 and 150 mm presets are supplied. Maximum custom stroke: 150.
Enclosed variants keep all teeth inside. Bearing-to-guide-end margin is at least
13 mm throughout travel; at full retraction the exit margin is 14.5 mm.
Parts are single-piece; check your printer's build volume. Housing length
can be increased independently above the minimum for the selected stroke.
Physical fit, side-load and fatigue testing are required for the revision.

INSERTS / ENCLOSURE HARDWARE
M3 inserts: default 4.6 mm OD x 5 mm long; printed pilot diameter 4.2 mm,
with 0.4 mm extra pocket depth. OD, length and pilot are configurable.
Qualify the pilot/installation temperature for your insert and material.
Nominal knurl-to-pilot overlap is intentional; heat displaces the plastic.
M3x20 socket lid screws; M3x10 front / M3x16 rear socket chassis screws. Modeled M3 heads:
5.5 mm diameter x 3 mm high. Quantities vary by preset; use the included
bill-of-materials.json. Insert count includes four each for front, side,
top and moving output mounts, plus lid and chassis fastening inserts.

MOUNTING
Front (+X, face where rack exits): four M3 inserts in two columns outside
the rack opening. Y spacing = housing width minus 18 mm; Z spacing = motor
depth minus 10 mm. All four are in the tray, not the removable lid. Inserts
sit 0.3 mm below the flat face, with 2 mm backing behind each blind pocket.
Any attached front fixture must clear the entire moving output pad and
guide, including when fully retracted. Use frontFixtureOpeningYZ in the
assembly metadata or front_fixture_opening_yz_mm in validation.json for
the minimum rectangular opening with 1 mm margin. At module 2 it spans
Y=18.5..41 and Z=-10..22 (22.5 x 32 mm), referenced to the CAD coordinates.
Side (+Y): four M3 inserts, recessed 0.3 mm into a flat wall. X spacing =
housing length minus 15 mm; Z spacing = motor depth minus 10 mm. All
reinforcement is inside the tray; blind pockets have 2 mm backing.
Top (+Z): four flush M3 inserts at Z=24.9, in full-height tray posts that
bypass the removable lid. X/Y spacing = housing length/width minus 15 mm.
Output (+Z): four M3 inserts on a 9 x 9 mm pattern, recessed 0.3 mm into
an 18 x 18 mm face at Z=21. Each pocket continues as a 3.4 mm clearance
hole through the full 18 mm pad. Inserts are optional: use an M3 bolt,
washers and nut instead. Size bolt length for the pad, attachment,
washers and full nut engagement. Annular backing remains below the insert.
Use application-length M3 screws with 3..5 mm thread engagement. For
recessed front/side/output inserts, this means 3.3..5.3 mm penetration
from the mounting face. For flush top inserts it means 3..5 mm. Do not
bottom screws in the blind pockets. Coordinates are in STEP and reports.
Detach external fixtures/load before full service. A top fixture must
be removed before lifting the lid; a front fixture may block rack removal.

MOTOR / DRIVE
NEMA17: 42 x 42 x 40 mm body, 31 mm mounting pitch, 18T / 20-degree pinion.
NEMA14: 35.2 x 35.2 x 34 mm body, 26 mm mounting pitch, 14T / 25-degree pinion.
Verify actual motor shaft, pilot and mounting dimensions. Motor rear
projects 4 mm beyond the case. Rear-mounted controller is not modeled;
keep it behind the motor rear plane with cooling and connector clearance.
Motor and driver leave before the tray in the service sequence.
Default tooth module 2; 0.6 mm tooth walls; 8 mm tooth face; 0.10 mm oversize
per flank. Circular root reliefs, no internal fingers. All teeth remain
inside the front of the enclosure; a smooth tongue passes through its exit.
The pass-through variant exposes the rear rack/teeth during retraction.
5.30 mm D bore for 5 mm shaft with 0.5 mm-deep flat; 0.15 mm wall clearance.
Tap the 2.5 mm radial pilot M3. Use M3x4 flat-point screw normal to the flat.
4 x M3x12 countersunk motor screws; 5 mm mounting land integral to chassis.

GUIDE HARDWARE / CLEARANCE
6 x 625ZZ (5 x 16 x 5): four upper at 45 degrees, two lower on flexures.
4 x M5x16 upper and 2 x M5x25 lower socket axle screws.
6 x thin M5 nuts (2.7 mm); 6 x inner-race washers (0.3 mm, 7.5 mm OD).
Clamp only the inner races. Rotating faces have 0.8 mm radial/axial relief.
Rack/chassis nominal gap 1 mm; axle-head gap 0.5 mm around the conservative
9.5 x 5 mm head envelope. Actual print and hardware tolerances vary.
There is no axial hard stop or downward flexure stop; use controller limits.

PRINT / ASSEMBLE
Tray: outer floor down. Lid: roof down. Rack: tooth face down, output pad
on the same plane. Pinion: gear face down. Keep tooth relief cuts clear.
Chassis: orient Y normal to the bed so the XZ leaf length/bending plane
lies within the layers. Use local supports where required at passages;
remove them without damaging the supported floor blends.
Chassis STL is RELAXED. STEP and viewer show installed spring deflection.
Install front and side inserts from outside, 0.3 mm recessed. Install the
four optional output inserts from Z=21 before inserting the rack. Install vertical
tray inserts before chassis/lid. Use heat, not cold interference forcing.
Fit lower bearings with axles backed out 10 mm and hold the nuts loose.
Position the chassis 6 mm above and 10 mm behind its seated location;
slide forward 10 mm, lower 6 mm, then advance the axles and tighten nuts.
Install front M3x10 and rear M3x16 chassis screws. Install motor/screws BEFORE upper rollers
and axles. Fit pinion and set screw. Insert rack from the output side,
square insertion end first, with motor free to turn; support spring seats
by hand if necessary. Check all six bearings rotate without rubbing.
Fit lid over top mounting posts and install M3x20 screws. Attach load and
mounting fixture last. Test low-speed full travel before applying load.

SERVICE (REMOVE EXTERNAL FIXTURES AND LOAD FIRST)
Remove/park lid screws 180 mm sideways; lift lid. Withdraw rack;
leaves relax. Remove set screw, lift/clear pinion. Withdraw front angled
axles, lift them another 20 mm and park; repeat for rear axles. Lift upper
rollers. Remove and park motor screws; lower motor/driver. Remove/park chassis screws; back lower axles out 10 mm while holding
their nuts. Lift the chassis and remaining bearings 6 mm, then slide
10 mm rearward to clear the end posts, then lower the tray with its inserts.
Remove lower nuts rearward, withdraw lower axles forward, then park the
axles outward in X. Remove angled nuts down along their axes and lift
lower rollers. Reverse to assemble. The animation shows clearance paths,
not gravity/workholding.

RESOLUTION (200 FULL STEPS/REV, MODULE 2)
Setting       NEMA17 mm/command       NEMA14 mm/command
Full             0.565487                0.439823
Half             0.282743                0.219911
1/4              0.141372                0.109956
1/8              0.070686                0.054978
1/16             0.035343                0.027489
Stroke does not change drive ratio. These are commanded increments,
not measured accuracy. Match your motor's actual full-step angle.

SOURCE / CHECKS
pip install -r requirements.txt
python model.py --config configuration.json --out build/custom --check
python model.py --motor nema14 --stroke 100 --enclosure pass-through --out build/custom --check
python build_presets.py --jobs 4
python check_flexure_service.py --jobs 4
python check_lid_screw_parking.py --all
python package_designs.py
CLI options override JSON. Stroke 20..150;
tooth module 1.5..2.5; housing length calculated minimum..2000;
motor depth 32..60; insert defaults OD4.6 / length5 / pilot4.2.
Restored free flexure span: 14 mm. Thickness: 1.8 mm by default;
--spring-thickness accepts 1.6..2.2 mm. Thicker floors increase required
insertion force and need testing in the selected print material.
--spring-preload 2.3 --bearing-clearance .8 --hardware-clearance .5
--rack-backbone-width 16 --preload .10
All twelve presets are regenerated and checked against revision 24 source.
Reports identify retained native scans across the assertion-only correction
for rear containment; geometry and collision-scan code are unchanged.
--enclosure selects enclosed (default) or pass-through.
Each preset has a sampled collision report, including all six contacts at
41 travel positions. Enclosure/fastener paths use <=0.5 mm sampling;
core paths use 1% slider intervals, boundaries/midpoints and 0.5 mm
bearing-release transitions. Nominal tooth mesh is checked separately.
Intentional elastic tooth contact and heat-set/host overlap are recorded.
Insert approaches on all three axes, blind-pocket backing, single-solid
validity, guide/hardware gaps and flexure travel clearance are checked.
flexure-service-validation.json additionally checks bearing hardware
removal at <=0.5 mm increments from 38..100% explosion. Local enclosure
reliefs cover the lower axle rise as the rack leaves the flexure.
Recheck custom parameters. Print-test fit, side load, sag and fatigue.
Large standalone STEP files use gzip; ZIP bundles contain ordinary STEP.
Inspiration: https://github.com/seveibar/compliant-spur-gear
