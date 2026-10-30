FLEX17 revision 12 — full-width wall-blended spring floors, open underside
CadQuery 2.7, millimetres. Mechanical prototype; force and life untested.

WHAT CHANGED
The lower bearing seats remain integral with the chassis. The floors now
extend to the full front/rear chassis boundaries and meet the axle-block
walls. Rounded blends exist only along actual wall-to-floor joints; the
unsupported floor has no raised curved ridge. The rigid lower deck is
removed, leaving the underside open.
No separate flexure frames, eccentric bushes, mounting bolts or mounting
nuts are used. There are only three printed parts: chassis, rack and pinion.
The bearing bolts/nuts clamp the inner races directly to the integral seats.
No bearing-preload locking set screw remains. The drive pinion retains its
M3x4 screw against the D-shaft flat.

GUIDANCE / SPRINGS
Six 625ZZ bearings (5 x 16 x 5 mm). Four upper rollers at 45 degrees react
downward/inward; two lower rollers react upward. Stations X=-23/+23 mm
are 46 mm apart, with lower contact Y=31/33 mm to resist rocking.
Nominal spring deflection is 0.30 mm. Floors are 22.1 mm wide and 1.4 mm
thick, with 1.2 mm blends at the central spine and the axle-block walls.
The open underside has no mechanical downward stop. Geometry is also
checked at 0.8 mm deflection; that is a check condition, not a load rating
or a physical travel limit.
A 4 mm-long, 0.8 mm-high ramp at the rack's insertion end depresses the
lower bearings. They rise independently as the rack is withdrawn.
The broad floors support solid axle blocks; compliance is confined to the
relieved floor regions. Spring force, axle shift, creep and fatigue still
require a physical test. The prescribed CAD deflection is not an FEA result.

IMPORTANT: Chassis STL is RELAXED for printing. STEP and viewer show the
assembled deflection. PETG/PA are starting materials; PLA is a poor choice
for sustained preload. If contact is lost or motion binds, revisit the fit,
material or source dimensions. Do not force insertion or overbend the floors.

PARTS / HARDWARE
From revision 11: reprint only the chassis; reuse the rack, pinion, motor,
six bearings, M5 axles, thin M5 nuts, washers and motor screws.
From revision 09: the rack also needs the new insertion ramp.
Total hardware: 6 x 625ZZ; 4 x M5x16 upper + 2 x M5x25 lower axles;
6 thin M5 nuts (2.7 mm), 6 inner-race washers (0.3 mm);
4 countersunk M3x12 motor screws; M3x4 flat-point pinion screw;
application-specific M4 chassis mounts. No new hardware is required.
Only inner races should be clamped; outer races and shields stay free.
Chassis mounts X=+/-30, Y=-13/54 mm: 60 x 67 mm pattern.
Output has two diameter-3.4 holes, 9 mm apart, through an 18 mm-thick pad.

PRINT / ASSEMBLY
Print the one-piece chassis so floor length and bending direction lie
within the layer plane (Y-normal print orientation). The chassis already
needs support under the motor overhang; use accessible local support under
the spring floors/axle seats as required by the slicer. Clear supports
through the open underside without gouging the wall-to-floor blends.
Test spring return by hand before installing bearings.
Print the pinion gear-face down and rack tooth-face down; the output pad
shares that flat print plane. Keep the fine tooth slots and rounded roots clear.
Fit the lower bearings and front inner-race washers to their integral
seats using the existing M5 axles and rear nuts. Install upper rollers,
angled axle hardware, motor and pinion. Insert the rack from the output/
right side, plain end first, with the motor free to turn. The ramp should
slightly depress each lower seat. Verify all six rollers turn through the
full stroke. Check material, fit and source preload if contact is missing
or insertion is hard. Driver travel limits are required; the rack end is open.

SERVICE
Withdraw rack; remove pinion screw and gear. Withdraw front angled axles,
park clear, then rear axles. Lift upper rollers. Remove motor screws,
lower motor, then remove angled nuts. Remove the lower M5 nuts, withdraw
lower axle bolts and lift bearings/washers through the open top windows.
The spring floors stay with the one-piece chassis; no rigid deck is below them.

RACK / DRIVE
40 mm initial stroke; source accepts 20..80 mm.
112 mm guide + 14 mm output pad; 166 mm swept length at 40 mm stroke.
68 x 81 mm footprint; centered envelope 126 x 81 x 52 mm.
Motor spacer remains integral. Removing the rigid deck leaves the reference
motor as the lowest component, so the overall envelope is unchanged.
Continuous beveled rail, 14.5 mm upper backbone, 0.60 mm tooth walls,
8 mm face and 0.10 mm oversize per flank. Smooth reliefs R1.98072 / R0.56087;
no internal tooth fingers. 18T module-2, 20-degree pinion, pitch radius 18 mm.
113.097336 mm/rev; 0.035343 mm commanded per 1/16 step with 200 steps/rev.
Commanded increments are not measured accuracy.
D bore 5.30 mm for a 5 mm shaft having a 0.5 mm-deep flat; 0.15 mm clearance.
Tap the 2.5 mm radial pilot M3; set screw is normal to the flat at Z=6.5 mm.

CHECKS / SOURCE
python model.py --stroke 40 --preload 0.10 --spring-preload 0.30 --spring-thickness 1.4 --check
--preload is tooth oversize; --spring-preload is nominal chassis deflection.
Spring preload range 0.10..0.40 mm; thickness range 1.2..1.8 mm.
validation.json records assembled pairs, travel, staged service, free
single-solid chassis, wall-local blends and open-underside checks. Viewer uses the same paths.
Sampled geometry checks are not continuous swept-volume or physical fit
proof. No load, stiffness, life, backlash or accuracy rating is implied.
Changed dimensions and materials require fresh geometry and print tests.
Inspiration: https://github.com/seveibar/compliant-spur-gear
