RACK ACTUATOR — REVISION 16
CadQuery 2.7.0, dimensions in mm. See configuration.json for this preset.

CHANGES / REPRINTING
M3 heat-set inserts replace all enclosure trapped nuts. The M5 bearing
through-bolts, nuts and washers are retained. Four top mounting inserts
are supported by full-height tray posts; lid removal clears these posts.
Lid screws are recessed 0.3 mm below the top mounting surface.
Five printed components: chassis, rack, pinion, tray and lid.
From revision 15, reprint chassis, tray and lid: front chassis holes are
now 3.4 mm for M3 screws. Reuse its matching 40 mm rack and pinion.
Other strokes require their own rack and enclosure. Do not mix motor
variants' racks and pinions: NEMA17 is 20 degrees, NEMA14 is 25 degrees.

PRESETS (MODULE 2; BOTH MOTORS)
Stroke       Housing length       Lid screws       Total M3 inserts
40           132                  4                10
100          247                  6                12
150          347                  6                12
200          447                  8                14
250          547                  10               16
400          848                  16               22
Housing length excludes the protruding rack. At 400 mm stroke the longest
printed part is about 860 mm. These are single-piece parts for a suitably
large printer; no segmentation or joining scheme is provided. Long-stroke
stiffness, sag, load rating and positional accuracy need physical testing.
The six-bearing guide station spacing remains 46 mm.

ENCLOSURE HARDWARE
M3 inserts: default 4.6 mm OD x 5 mm long; printed pilot diameter 4.2 mm,
with 0.4 mm extra pocket depth. Match your insert manufacturer's guidance;
OD, length and pilot are configurable. Nominal knurl-to-pilot overlap is
intentional: plastic is displaced by heat during installation.
M3x20 socket lid screws, quantity from the table; 2 x M3x10 socket chassis
screws. Maximum modeled M3 head diameter 5.5 mm, height 3 mm.
See bill-of-materials.json for the selected preset's quantities.

MOUNTING
Side: four 8 x 4.5 mm slots on the flat rear side face, for M4 fasteners.
Top: four M3 inserts, flush at Z=24.9, in full-height posts attached to the
tray. These transfer mounting loads directly to the tray, bypassing the
removable lid. Use application-length screws with 3–5 mm engagement;
do not bottom screws in the blind insert pockets.
Default 40 mm top pattern: 117 x 75.8 mm NEMA17; 117 x 69.8 mm NEMA14.
Longer presets: X spacing = housing length minus 15 mm. The Y spacing is
unchanged. Exact coordinates are in the STEP, viewer and validation.json.
A top-mounted module must be detached from its fixture before the lid can
be lifted. The service animation models the module after that detachment.
Two output mounting holes: diameter 3.4, pitch 9 mm.

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

Install inserts from above into the open tray before installing the
chassis or lid. Use the insert manufacturer's process and qualify the
pilot in your material. Do not force cold inserts into printed pockets.
Attach the open tray to a side fixture if used. Assemble lower guide
hardware, seat the chassis, and install its two M3x10 screws. Install the
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
housing length automatic minimum..1000; motor depth 32..60.
--insert-od 4.6 --insert-length 5 --insert-pilot 4.2
--spring-preload 2.3 --spring-thickness 1.4 --bearing-clearance .8
--hardware-clearance .5 --rack-backbone-width 16 --preload .10
Each preset has its own sampled collision report. Intentional elastic
rack/pinion contact and heat-set/host interference are recorded separately.
Insert installation approach, valid single solids, guide geometry and
hardware gaps are checked. Recheck custom parameters and print-test fits.
CAD is not a continuous collision proof, load rating, FEA or fatigue test.
Use controller travel limits; no axial hard stop is provided.
Inspiration: https://github.com/seveibar/compliant-spur-gear
