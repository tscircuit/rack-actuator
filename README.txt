FLEX revision 15 — configurable teeth and travel, enclosed mounting module
CadQuery 2.7.0, millimetres. Builder-tested core; new enclosure needs fit testing.

CHANGES / REPRINTING
Five printed parts: integral spring chassis, rack, pinion, tray and lid.
At default module 2, reuse the revision-14 chassis and matching pinion;
print the revised rack and both enclosure halves. Replace pancake motors
with the reference 40 mm NEMA17 or 34 mm NEMA14 body (depth configurable).
The rack has a shorter toothed segment and a longer smooth output tongue.
All teeth remain inside the case over the specified usable stroke.
Default fixed housing length is 132 mm, separate from the 40 mm stroke.
Housing body: NEMA17 132 x 88.8 x 68.9 mm; NEMA14 132 x 82.8 x 62.9 mm.
Mount reinforcement pads extend another 3 mm out of the mounting face.
These dimensions exclude the moving output and exposed motor/driver.
Motor rear projects 4 mm beyond the floor. The controller is not modeled;
its electronics and connectors must lie behind the motor's rear plane.
The tray leaves after the motor/driver, so no guessed controller outline
needs to fit through the motor-body opening. Leave cooling/cable space.

GUIDANCE / SPRINGS / CLEARANCE
Six 625ZZ (5 x 16 x 5 mm), four upper at 45 degrees and two lower.
Bearing stations X=-23/+23 mm; lower contacts Y=31/33 mm resist rocking.
Spring floors are 1.4 mm thick, 22.1 mm wide for NEMA17 and 20.9 mm wide
for NEMA14 to clear the reference motor. Wall-local root blends R1.2 mm.
No rigid lower deck or downward stop. Geometry is checked at 2.6 mm
prescribed deflection; this is not a safe travel or load rating.
The square rack end engages the curved rims of the lower bearings; no
underside ramp or end chamfer is cut into the rack.
Bearing recesses give 0.8 mm radial and axial relief around rotating faces.
Only inner races clamp against the integral shoulders. The rack/chassis
nominal gap is 1 mm. Bounded head channels give 0.5 mm clearance to the
conservative full-height axle head envelope (diameter 9.5, height 5 mm).
These are CAD gaps; actual print accuracy and hardware dimensions vary.
Clear bores and seats after printing. Do not sand the raceways unevenly.

IMPORTANT: Chassis STL is RELAXED. STEP/viewer are assembled and deflected.
2.3 mm is an aggressive prototype. Force, elastic recovery, creep and
fatigue are not established by the prescribed CAD shape. Test one floor
in the intended material/orientation first. PETG/PA are starting materials,
not a validated material specification. Do not force a binding rack.

HARDWARE
6 x 625ZZ; 4 x M5x16 upper + 2 x M5x25 lower socket axle screws;
6 thin M5 nuts (2.7 mm); 6 inner-race washers (0.3 mm, 7.5 mm OD);
4 countersunk M3x12 motor screws; M3x4 flat-point pinion set screw;
application-specific M4 mounts. No new spring hardware.
Check head dimensions and use nuts/washers matching the CAD, not bulky
full-height nuts. Clamp inner races only; shields and outer races stay free.
Chassis mount holes: diameter 4.4 at X=+/-30, Y=-13/54 (60 x 67 pattern).
Use heads at most diameter 7.6 x 2.2 mm in the recessed mount seats.
Output pad: two diameter-3.4 holes, 9 mm pitch, 18 mm through thickness.


ENCLOSURE HARDWARE / MOUNTING
4 x M3x25 socket screws; 4 x M3 nuts, 5.5 mm AF x 2.4 mm thick.
2 x M4x12 low-head chassis screws, maximum head diameter 7.6 x 2.2 mm;
2 x M4 nuts, 7 mm AF x 3.2 mm thick. Nuts enter side-access pockets with flats that prevent rotation.
Application-specific M4 fasteners fit four 8 x 4.5 mm mounting slots on
the flat rear side face (normal +Y), clear of the axial motor rear (-Z).
Default slot centers: X=-64/+36 mm; NEMA17 Z=-35/-12 mm,
NEMA14 Z=-29/-12 mm. Select fixture fastener length for your application.
Front M4 screws retain the chassis; broad rear ledge supports it. Lid
posts clamp the existing rear recessed seats; rear chassis holes are unused.

PRINT / ASSEMBLY
Print tray on outer floor, lid roof-down. Horizontal captive nut passages
and mounting counterbores may need local supports; clean them afterward.
Preserve the chassis orientation/material used in your successful test.
For a new chassis, orient floor length and bending in the layer plane
(Y-normal print). Local supports are required at overhangs and bores.
Print rack tooth-face down, output pad on the same plane; pinion gear-face
down. Keep fine rounded relief slots and 0.6 mm tooth walls open.
Fit captive nuts and attach the open tray to the fixture. Assemble lower
bearing hardware on the chassis. Seat chassis on supports/rear ledge and
install front M4 screws. Install motor and its four screws before the
upper rollers/axles; fit pinion and flat-point screw. Insert rack from the
output/right side, square end first, with motor free to turn. Support
spring seats by hand if needed; do not force insertion. Check all six
bearings turn and no heads rub. Fit lid and four screws without crushing
printed clamps. Use controller travel limits; no axial stop is provided.

SERVICE (VIEWER ORDER)
Remove/park four cover screws; lift lid and its rear clamps. Slide rack
out and let floors relax. Remove set screw, lift pinion and park it clear.
Withdraw/park front upper axles, then rear upper axles; lift upper rollers.
Remove motor screws, lower motor AND attached driver. Remove/park front
chassis screws; lower tray with its captive nuts. Remove lower axle nuts,
withdraw/park lower axles sideways, then remove angled nuts. Lift lower
rollers last. Support loose subassemblies; the animation shows clearance
paths, not gravity or a required workholding fixture.

DRIVE VARIANTS
NEMA17: 42 x 42 x 40 mm reference body, 31 mm mounting pitch,
18T module-2 pinion, 20 degrees, OD40/pitch36 mm.
NEMA14: 35.2 x 35.2 x 34 mm body, 26 mm mounting pitch,
14T module-2 pinion, 25 degrees, OD32/pitch28 mm.
Do not mix their racks/pinions; verify actual motor drawing/shaft/pilot.
Default rack guide 129.5 mm plus 14 mm output pad, stroke 40 mm.
Integral 5 mm motor land; 0.10 mm tooth oversize per flank; smooth circular
reliefs, no internal fingers. D bore diameter 5.30 for 5 mm shaft with
0.5 mm-deep flat, 0.15 mm wall clearance. Tap diameter-2.5 pilot M3;
M3x4 flat-point screw normal to flat. Tooth module changes both profiles.

RESOLUTION (200 full steps/rev; commanded increments, not accuracy)
Setting       NEMA17 mm/command       NEMA14 mm/command
Full             0.565487                0.439823
Half             0.282743                0.219911
1/4              0.141372                0.109956
1/8              0.070686                0.054978
1/16             0.035343                0.027489
NEMA14 gives 22.2% finer nominal increments. Smaller gear does not itself
establish better physical accuracy. Torque, material, backlash and load matter.

SOURCE / PARAMETERS
pip install -r requirements.txt
python model.py --motor nema17 --out dist --check
python model.py --motor nema14 --out dist/variants/nema14 --check
python package_designs.py
python model.py --config configuration.json --out build/custom --check
Explicit CLI options override JSON. JSON contains physical parameters only.
--tooth-module 2: 1.5..2.5 mm; circular pitch = pi x module.
--stroke 40: 20..120 mm usable travel.
--actuator-length 132: fixed housing length along travel, excludes output.
Omit for automatic minimum; too-short housing rejected; maximum 350 mm.
--motor-depth 40: NEMA17 default40, NEMA14 default34; range32..60 mm.
--spring-preload 2.3; --spring-thickness 1.4; --bearing-clearance .8;
--hardware-clearance .5; --rack-backbone-width 16; --preload .10 is tooth
oversize, not spring travel. Spring deflection range .1..2.5 mm.
The site configurator exports JSON/CLI; its 3D view remains the checked
module-2, 40 mm-stroke default. Regenerate CAD for changed parameters.

VALIDATION
Reports check assembled pairs, sampled travel and staged service, wall
blends, relaxed chassis solids, nominal mesh and hardware clearances.
Only intended elastic tooth contact is allowed. Default reports cover
all sampled poses; additional parameter-case reports use stage boundaries
and midpoints (33 explosion poses / 9 travel positions), not dense sweeps.
All parameter changes require fresh checks and print-fit testing. The
builder tested the core; the new enclosure and parameter combinations
remain untested physically. CAD does not establish force, fatigue, thermal
behavior, load capacity, accuracy or continuous collision-free motion.
The ventilated case is not sealed. See reports for detailed exclusions.
Inspiration: https://github.com/seveibar/compliant-spur-gear
