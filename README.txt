FLEX revision 13 — NEMA17 and NEMA14; increased preload and print clearances
CadQuery 2.7, millimetres. Mechanical prototypes; force and life untested.

CHANGES / REPRINTING
Spring deflection is now 2.30 mm, 2 mm more than revision 12.
Reprint the chassis AND rack for NEMA17; reuse its 18T pinion and hardware.
For NEMA14 print the matching chassis, 25-degree rack and 14T pinion.
Do not mix tooth profiles between variants.
Three printed parts per variant. No added flexure parts, eccentric bushes
or bearing-preload set screws. The pinion retains its M3 drive set screw.

GUIDANCE / SPRINGS / CLEARANCE
Six 625ZZ (5 x 16 x 5 mm), four upper at 45 degrees and two lower.
Bearing stations X=-23/+23 mm; lower contacts Y=31/33 mm resist rocking.
Spring floors are 1.4 mm thick, 22.1 mm wide for NEMA17 and 20.9 mm wide
for NEMA14 to clear the reference motor. Wall-local root blends R1.2 mm.
No rigid lower deck or downward stop. Geometry is checked at 2.6 mm
prescribed deflection; this is not a safe travel or load rating.
A 10 mm-long, 2.8 mm-high rack lead-in depresses the lower bearings.
Bearing recesses give 0.8 mm radial and axial relief around rotating faces.
Only inner races clamp against the integral shoulders. The rack/chassis
nominal gap is 1 mm. Full-length channels give 0.8 mm clearance to the
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

PRINT / ASSEMBLY
Orient the chassis so floor length and bending are in the layer plane
(Y-normal printing). Local support is needed beneath the motor overhang,
floors/axle seats and horizontal bores as indicated by the slicer.
Remove supports through the open underside without gouging blends.
Check the floors recover freely before adding hardware.
Print rack tooth-face down; its output pad shares that face and needs no
under-pad support. Print pinion gear-face down. Keep 0.6 mm tooth walls
and fine circular relief slots open; qualify nozzle/material on a coupon.
Install lower rollers with front washers, through-axles and rear nuts.
Install upper rollers, motor and pinion. Insert the rack from the output/
right side, plain end first, with the motor free to turn. The ramp brings
the lower floors to 2.3 mm deflection. Check that all six bearings turn
through the whole stroke and that heads do not scrape the relief channels.
Use controller travel limits. No axial stop is provided at the plain end.

SERVICE
Slide rack out; spring floors relax independently. Remove pinion set screw,
lift and clear pinion. Withdraw front angled axles, park clear, then rear
axles. Lift upper rollers. Remove motor screws and lower the motor. Remove
lower nuts, withdraw lower axles and park them sideways BEFORE removing
the angled nuts; this
clears the raised axle ends from the rear nut path. Then lift lower rollers.
Floors remain integral with the chassis.

DRIVE VARIANTS
NEMA17 reference: 42 x 42 x 23 mm body, 31 mm mounting pitch.
Chassis 68 x 81 mm. Pinion 18T, module 2, 20 degrees, OD40/pitch36 mm.
NEMA14 reference: 35.2 x 35.2 x 20 mm body, 26 mm mounting pitch.
Chassis 68 x 75 mm. Pinion 14T, module 2, 25 degrees, OD32/pitch28 mm.
Use the matching 25-degree rack; verify the actual motor drawing.
40 mm default stroke; 112 mm rack guide plus 14 mm output pad.
Both: integral 5 mm motor land, 0.60 mm tooth walls, 8 mm tooth face,
0.10 mm oversize per flank, smooth circular reliefs, no internal fingers.
5.30 mm D bore for 5 mm shaft with 0.5 mm-deep flat. Clearance 0.15 mm.
Tap diameter-2.5 radial pilot M3. Flat-point set screw normal to shaft flat.

RESOLUTION (200 full steps/rev; commanded increments, not accuracy)
Setting       NEMA17 mm/command       NEMA14 mm/command
Full             0.565487                0.439823
Half             0.282743                0.219911
1/4              0.141372                0.109956
1/8              0.070686                0.054978
1/16             0.035343                0.027489
NEMA14 gives 22.2% finer nominal increments. Smaller gear does not itself
establish better physical accuracy. Torque, material, backlash and load matter.

SOURCE / CHECKS
python model.py --motor nema17 --out dist --check
python model.py --motor nema14 --out dist/variants/nema14 --check
python package_designs.py
--spring-preload 2.3; --spring-thickness 1.4; --bearing-clearance .8;
--hardware-clearance .8; --preload .10 is tooth oversize, not spring travel.
Spring deflection range .1..2.5; stroke range 20..80 mm.
All parameter changes require fresh collision checks and a physical fit test.
Validation reports cover assembled pairs, sampled travel/staged service,
wall blends, relaxed chassis solids, contact geometry and hardware gaps.
Only the intentional elastic rack/pinion contact is allowed.
Checks are not continuous collision proof, FEA or load/fatigue qualification.
Inspiration: https://github.com/seveibar/compliant-spur-gear
