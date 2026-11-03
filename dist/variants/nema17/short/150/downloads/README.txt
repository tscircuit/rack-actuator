RACK ACTUATOR — REVISION 20
CadQuery 2.7.0, dimensions in mm. See configuration.json for this preset.

CHANGES / REPRINTING
Four M3 heat-set inserts now mount the enclosure from its exit (+X) face.
The moving output pad retains its four M3 inserts on a 9 x 9 mm pattern.
Each lower bearing carrier now has two opposed leaves connected to fixed
walls. Their symmetry reduces carrier pitch under centered bearing load.
The central moving cradle is 4 mm thick; there is no stationary lower deck.
Rounded roots sit on supported flat lands. No extra printed parts or
spring hardware are added: five printed parts remain.
Leaves grow with stroke: length 22 to 28 mm; thickness 2 to 2.67 mm;
width 12 mm. Default installed deflection remains 2.3 mm. The nominal
maximum leaf slope falls from 8.9 to 7.0 degrees (previous 14 mm leaf:
13.8 degrees). The ideal symmetric linear model has zero carrier pitch;
actual print tilt, stiffness, recovery, creep and fatigue are unmeasured.
The CAD prescribes the deformed shape; it is not FEA or a load rating.

Reprint chassis, tray and lid. Use the matching rack for the selected
stroke/layout (40 mm standard and all short layouts change rack length).
Do not mix preset parts. The existing matching motor/pinion and bearing
hardware are reusable. NEMA17 rack/pinion: 20 degrees; NEMA14: 25 degrees.

PRESETS (MODULE 2; BOTH MOTORS)
Stroke   Layout      Bearing span   Housing length   Rack print length
40       Standard    84             166              181.5
40       Short       64             146              161.5
100      Standard    164            306              321.5
100      Short       64             256              271.5
150      Standard    264            456              471.5
150      Short       64             356              371.5
Only 40, 100 and 150 mm presets are supplied. Maximum custom stroke: 150.
Standard: exit bearing center 25 mm behind the front face. The other
station mirrors it around the centered pinion. Span grows with stroke.
Short: stations stay at X=-32/+32; the exit overhang grows with stroke.
Short saves length but reduces leverage against rack tilt and increases
unsupported output length. Prefer standard for larger side/moment loads;
no load capacity is rated for either layout.
Both layouts keep all teeth covered and maintain at least 13 mm from each
bearing center to the guide end throughout travel. Parts are single-piece;
select a printer that fits the actual STL. Housing length is independently
configurable above the minimum needed for the chosen layout and stroke.

INSERTS / ENCLOSURE HARDWARE
M3 inserts: default 4.6 mm OD x 5 mm long; printed pilot diameter 4.2 mm,
with 0.4 mm extra pocket depth. OD, length and pilot are configurable.
Qualify the pilot/installation temperature for your insert and material.
Nominal knurl-to-pilot overlap is intentional; heat displaces the plastic.
M3x20 socket lid screws; M3x10 socket chassis screws. Modeled M3 heads:
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
Y=15.5..41 and Z=-10..22 (25.5 x 32 mm), referenced to the CAD coordinates.
Side (+Y): four M3 inserts, recessed 0.3 mm into a flat wall. X spacing =
housing length minus 15 mm; Z spacing = motor depth minus 10 mm. All
reinforcement is inside the tray; blind pockets have 2 mm backing.
Top (+Z): four flush M3 inserts at Z=24.9, in full-height tray posts that
bypass the removable lid. X/Y spacing = housing length/width minus 15 mm.
Output (+Z): four M3 inserts on a 9 x 9 mm pattern, recessed 0.3 mm into
an 18 x 18 mm face at Z=21. Default blind-pocket backing is 12.3 mm.
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
inside the enclosure; a smooth tongue passes through its exit.
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
New chassis: orient X normal to the bed so the YZ leaf length/bending plane
lies within the layers. Use local supports where required at passages;
remove them without damaging leaf roots or blocking service windows.
Chassis STL is RELAXED. STEP and viewer show installed spring deflection.
Install front and side inserts from outside, 0.3 mm recessed. Install the
four output inserts from Z=21 before inserting the rack. Install vertical
tray inserts before chassis/lid. Use heat, not cold interference forcing.
Assemble lower bearing hardware through the root service windows. Seat
chassis and install M3x10 screws. Install motor/screws BEFORE upper rollers
and axles. Fit pinion and set screw. Insert rack from the output side,
square insertion end first, with motor free to turn; support spring seats
by hand if necessary. Check all six bearings rotate without rubbing.
Fit lid over top mounting posts and install M3x20 screws. Attach load and
mounting fixture last. Test low-speed full travel before applying load.

SERVICE (REMOVE EXTERNAL FIXTURES AND LOAD FIRST)
Remove/park lid screws, lift lid and rear chassis clamps. Withdraw rack;
leaves relax. Remove set screw, lift/clear pinion. Withdraw front angled
axles, then rear axles; lift upper rollers. Remove motor screws and lower
motor/driver. Remove/park chassis screws; lower tray with installed inserts.
Remove lower nuts through rear root windows, then park them outward in X.
Withdraw lower axles through front windows until fully clear, then park
outward in X. Angled nuts first move 12 mm along their axes, then 45 mm
in Y through the root windows. Finally lift lower rollers. Reverse to
assemble. The animation shows clearance paths, not gravity/workholding.

RESOLUTION (200 FULL STEPS/REV, MODULE 2)
Setting       NEMA17 mm/command       NEMA14 mm/command
Full             0.565487                0.439823
Half             0.282743                0.219911
1/4              0.141372                0.109956
1/8              0.070686                0.054978
1/16             0.035343                0.027489
Stroke/layout do not change drive ratio. These are commanded increments,
not measured accuracy. Match your motor's actual full-step angle.

SOURCE / CHECKS
pip install -r requirements.txt
python model.py --config configuration.json --out build/custom --check
python model.py --motor nema14 --stroke 100 --layout short --out build/custom --check
python build_presets.py --jobs 4
python check_flexure_service.py --jobs 4
python package_designs.py
CLI options override JSON. Stroke 20..150; layout standard|short;
tooth module 1.5..2.5; housing length calculated minimum..2000;
motor depth 32..60; insert defaults OD4.6 / length5 / pilot4.2.
Default leaf length: 22 + 6*max(0,(stroke-40)/110).
Default thickness: 2*(leaf_length/22)^1.2, override --spring-thickness 1.6..3.2.
--spring-preload 2.3 --bearing-clearance .8 --hardware-clearance .5
--rack-backbone-width 16 --preload .10
Each preset has a sampled collision report, including all six contacts at
41 travel positions. Enclosure/fastener paths use <=0.5 mm sampling;
core paths use 1% slider intervals, boundaries/midpoints and 0.5 mm
bearing-release transitions. Nominal tooth mesh is checked separately.
Intentional elastic tooth contact and heat-set/host overlap are recorded.
Insert approaches on all three axes, blind-pocket backing, single-solid
validity, guide/hardware gaps and flexure travel clearance are checked.
flexure-service-validation.json additionally checks changed root-window
hardware paths at <=0.5 mm increments from 82..100% explosion.
The symmetric beam proxy predicts zero carrier pitch under centered load;
max leaf slope, stiffness per material modulus and estimated strain are
reported. These are ideal small-deflection estimates, not physical ratings.
Recheck custom parameters. Print-test fit, side load, sag and fatigue.
Large standalone STEP files use gzip; ZIP bundles contain ordinary STEP.
Inspiration: https://github.com/seveibar/compliant-spur-gear
