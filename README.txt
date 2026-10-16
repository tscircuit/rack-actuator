FLEX17 revision 09 — integral motor mount, six-roller angled guide
CadQuery 2.7, millimetres. Mechanical prototype; load and life untested.

LAYOUT
Six 625ZZ bearings only: four upper rollers at 45 degrees, two lower
rollers with horizontal Y axes. All axes are perpendicular to X travel.
The upper rollers run on sloping faces and react downward/inward.
The lower rollers run on a flat underside and react upward.
Two stations at X=-23 and +23 mm give 46 mm longitudinal spacing.
At each station, two angled rollers and one lower roller surround the rail.
Lower contact centers are at Y=31 and 33 mm, staggered across the flat
underside to resist rocking while allowing balanced positive preload.
Nominal geometry is tangent; preload is set physically with eccentrics.
Angle alone does not generate preload.

RACK / DRIVE
40 mm stroke; editable source accepts --stroke 20..80.
112 mm guide length + 14 mm output pad; 166 mm swept length at 40 mm stroke.
68 x 81 mm chassis; complete centered envelope 126 x 81 x 52 mm.
Deeper solid beveled rail and 14.5 mm-wide upper body stiffen the rack.
Rounded tooth-root reliefs retained: R1.98072 inside, R0.56087 between.
0.60 mm tooth walls, 8 mm face, 0.10 mm oversize per flank.
18T module-2, 20-degree pinion; pitch radius 18 mm.
113.097336 mm travel/revolution; 0.035343 mm commanded at 1/16 step
with a 200-full-step/revolution motor. This is not measured accuracy.
D bore 5.30 mm with 0.15 mm wall clearance for a 5 mm shaft having
0.5 mm flat depth. M3x4 flat-point screw normal to the flat at Z=6.5.
Tap its 2.5 mm pilot M3; actual threads are not modeled.

ADJUSTMENT
Each lower axle is carried by a printed 0.5 mm eccentric bushing.
Nominal hole offset is 0.4 mm sideways and 0.3 mm upward from its body.
Rotation gives -0.8 to +0.2 mm vertical adjustment relative to nominal.
Loosen the M3 radial lock and M5 axle nut before turning the 12 mm hex.
Start with the lower rollers backed off for rack insertion. Turn the motor
freely while sliding the rack from the output/right side, plain end first.
Adjust each lower roller until all six outer races touch and roll over
the complete stroke. Use light contact, not a large forced deflection.
Tighten the M3 radial locks and M5 axle nuts, then recheck for binding.
Driver regulation, print tolerance and rail warp still need physical tests.

PARTS / HARDWARE
From revision 08, reprint only the chassis; reuse the rack, pinion and
eccentric bushings. The former 5 mm motor spacer is now part of the chassis.
Motor position, screws and overall dimensions remain the same.
Hardware is unchanged from revision 08.
Total: 6 bearings, 4 M5x16 + 2 M5x25 axles, 6 thin M5 nuts (2.7 mm),
6 inner-race washers (0.3 mm), 4 countersunk M3x12 motor screws,
M3x4 pinion screw, 2 M3x6 locks, application-specific M4 mounts.
Tap the eccentric-lock pilots M3. Threads use simplified core envelopes.
Chassis mounting holes X=+/-30, Y=-13/54: 60 x 67 mm pattern.
Output holes remain two diameter-3.4 holes, 9 mm apart; pad thickness 18 mm.

PRINT / ASSEMBLY
The deeper chassis requires supports beneath the motor-platform overhang
and in horizontal/angled holes. Keep bearing seats clean after removal.
The motor mounting land is printed with the chassis; there is no separate spacer.
Print the pinion broad gear face down. Print eccentrics hex-flange down.
Print the rack broad tooth-face down: its pad shares that flat print plane.
The rail expands below the neck on 45-degree faces; check the slicer preview.
Print a short guide/relief coupon before the complete rack. PETG/PA are
starting candidates; a 0.25 mm nozzle helps with the fine tooth walls.
Clamp bearing inner races only; shields and outer races must stay free.
Install captured upper nuts, four upper bearings/washers and angled axles.
Fit the lower eccentric bushes, bearings, washers, axles, nuts and locks.
Fit motor against the integral mounting land, then pinion and set screw; insert rack and set light preload.

SERVICE / CHECKS
Viewer stages share the exact CAD translation and rotation tracks.
Remove rack, pinion screw and pinion first. Withdraw front angled axles
along their axes and park clear, then repeat for rear axles. Lift upper
rollers, remove motor screws, lower motor from its integral seat, then remove upper nuts.
Remove lower nuts; withdraw each lower roller, washer and axle together
through the front opening. Withdraw radial locks, then pull the
eccentric bushes rearward. The chassis stays one piece.
validation.json records nominal mesh, all initial rigid-pair checks,
full travel, and staged-removal checks, including the new hardware.
Tests are sampled, not a continuous swept-volume or fatigue proof.
Controller travel limits are required; the rack insertion end is open.

SOURCE
python model.py --stroke 40 --preload 0.10 --check
Options: --shaft-diameter 5 --shaft-flat-depth 0.5 --shaft-clearance 0.15
Modified dimensions require fresh checks. No force or accuracy rating.
Inspiration: https://github.com/seveibar/compliant-spur-gear
