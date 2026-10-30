FLEX17 revision 10 — passive parallel-leaf bearing preload
CadQuery 2.7, millimetres. Mechanical prototype; force and fatigue untested.

LAYOUT
Six 625ZZ bearings only (5 x 16 x 5 mm). Four upper rollers at 45 degrees
react downward/inward; two lower rollers react upward on a flat underside.
Stations at X=-23/+23 mm are 46 mm apart. Lower contact Y=31/33 mm is
staggered to resist rocking. All bearing axes are perpendicular to travel.
Two replaceable spring cartridges support the lower axle blocks.
Each block has four rounded leaves: one upper/lower pair on each side; no eccentric or preload
locking set screw remains. Two M3 through-bolts retain each fixed root (four total).
The pinion's separate D-shaft set screw remains necessary for the drive.

SPRING CARRIER
Nominal unloaded bearing centers are 0.30 mm above the assembled centers.
Inserting the rack deflects the leaves down and supplies passive preload.
Leaf thickness 1.0 mm; width 2.4 mm; flexible span 13.4 mm;
root flare radius 0.8 mm. Both ends have rounded transitions.
Stops limit downward block motion to 0.8 mm from its unloaded position,
leaving 0.5 mm additional travel from the nominal assembled position.
The rack's plain insertion end has a 4 mm-long, 0.8 mm-high lead-in.
The viewer and CAD checks let each lower roller follow that ramp and
relax upward as the rack is withdrawn. The root stays fixed.

IMPORTANT: STL is the unloaded spring carrier, ready to print.
STEP/viewer show the assembled, prescribed 0.30 mm deflection.
The deformation shape is a geometric model, not a finite element result.
Force, creep and fatigue require a physical test. PETG/PA are starting
materials; PLA is a poor choice for sustained spring preload.
If contact is lost over time, replace the carrier and revisit the material
or source dimensions. Do not compensate by forcing excessive deflection.

PARTS / HARDWARE
From revision 09: print a new chassis, ramped rack and spring carrier.
Reuse the pinion, motor, six bearings, M5 axle hardware and motor screws.
Remove the two eccentric bushes and two M3x6 locking screws.
Add four M3x20 socket-head through-bolts and four M3 nuts for the spring root.
Total: 6 x 625ZZ; 4 x M5x16 upper + 2 x M5x25 lower axles;
6 thin M5 nuts (2.7 mm), 6 inner-race washers (0.3 mm),
4 x M3x20 cartridge mounts + 4 captive M3 nuts; 4 countersunk M3x12 motor screws;
M3x4 flat-point pinion screw; application-specific M4 chassis mounts.
Ordinary mount bolts clamp the fixed root; they do not adjust preload.
Clamp only the bearing inner races. Verify actual hardware dimensions.
Chassis mounts X=+/-30, Y=-13/54 mm (60 x 67 mm pattern).
Output: two diameter-3.4 holes, 9 mm apart, through an 18 mm-thick pad.

RACK / DRIVE
40 mm stroke; source accepts --stroke 20..80.
112 mm guide + 14 mm output pad; 166 mm swept length at 40 mm stroke.
68 x 81 mm chassis; centered envelope 126 x 81 x 52 mm.
Continuous beveled guide, 14.5 mm-wide upper backbone, rounded tooth reliefs.
Root radii R1.98072 inside, R0.56087 between; 0.60 mm tooth walls,
8 mm face, 0.10 mm oversize per flank. No internal tooth fingers.
18T module-2, 20-degree pinion; pitch radius 18 mm.
113.097336 mm/revolution; 0.035343 mm commanded per 1/16 step
with a 200-full-step/rev motor. Commanded increments are not accuracy.
D bore 5.30 mm for a 5 mm shaft with 0.5 mm-deep flat;
0.15 mm wall clearance. Tap the 2.5 mm radial pilot M3 for an M3x4
flat-point screw normal to the shaft flat at Z=6.5 mm.
The motor mounting land remains integral with the chassis.

PRINT / ASSEMBLY
Print each cartridge with its broad SIDE face on the bed (minimum-X face).
Leaf length and bending then lie in the layer plane. Check the upper-leaf
bridges and axle collars in the slicer; use local support where needed,
keeping support off the thin leaves and gaps. Confirm bridges remain clear.
Test this small carrier before committing to a complete printed module.
The chassis needs supports under the motor overhang and in angled bores.
Keep seats clean. Print the pinion gear-face down and rack tooth-face down;
the output pad shares that flat print plane. Check ramp/rail in the slicer.
Place the M3 nuts in each cartridge root, slide cartridges in from behind,
and attach each fixed root with two M3x20 bolts from the underside.
Fit lower bearings, inner-race washers, M5 axles and rear nuts to its blocks.
Fit the four upper rollers and angled axle hardware, then the motor and
pinion. Insert the rack from the output/right side, plain end first, with
the motor free to turn. The lead-in should gently depress the lower rollers.
Verify all six rollers turn across the whole stroke and the rack does not
bind. If insertion is hard or contact is missing, check print fit and spring
parameters; do not force it. Controller travel limits are required.

SERVICE / CHECKS
Rack withdrawal lets the two spring ends relax independently.
Remove pinion screw and gear; withdraw front angled axles, park clear,
then rear axles. Lift upper rollers, remove motor screws and lower motor.
Remove angled nuts, then withdraw the four cartridge mounting bolts
downward. Slide both complete lower-bearing cartridges rearward with
their axle hardware and captive mounting nuts. Once clear of the chassis,
remove the M5 nuts, withdraw the axle bolts and lift out the lower bearings
and washers. This staged subassembly path avoids the fixed cartridge roots. Chassis stays one piece.
validation.json records assembled pairs, full travel, staged removal,
rounded roots, nominal gear mesh, spring stop and free-print geometry.
Checks are sampled, not a continuous swept-volume or physical fit proof.
No load, life, backlash or stiffness rating is implied.

SOURCE
python model.py --stroke 40 --preload 0.10 --spring-preload 0.30 --spring-thickness 1.0 --check
--preload changes tooth oversize; --spring-preload changes leaf deflection.
Spring preload range 0.10..0.40 mm; thickness range 0.8..1.3 mm.
Changed dimensions/materials need new geometry and physical tests.
Inspiration: https://github.com/seveibar/compliant-spur-gear
