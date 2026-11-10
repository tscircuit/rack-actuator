6805 bearing-supported screw — independent prototype, revision 1
Units: mm. Based on the existing 40 mm travel printed lead screw (tip X152).

PURPOSE
Transfer screw thrust into the 4 mm wall through an independently captured 6805
bearing. The original D-shaft coupling transmits torque. This assembly has no
carriage and is not a drop-in replacement for an existing actuator.

PRINTED PARTS
1. 52 x 52 x 4 mm flat NEMA17 wall; 31 x 31 mm pattern, M3 clearance holes.
2. Bearing holder with four open standoffs; attaches to the opposite wall face.
3. Bearing retaining cap, M3 clearance holes and access to the motor bolts.
4. Existing printed screw plus an additive bearing seat and shoulder ONLY.
5. Inner race spacer, 25.2 ID x 27 OD x 1 mm, contacting only the inner race.

HARDWARE
1 NEMA17 motor: 5 mm D shaft, 4.5 mm across flat, 24 mm shaft projection.
1 6805 bearing, 25 mm bore x 37 mm OD x 7 mm width (sealed preferred).
1 DIN 471 external circlip for 25 mm shaft, 1.2 mm thick, SPRING STEEL.
4 M3x16 socket-head screws for holder + wall + motor (6 mm engagement).
4 M3x12 socket-head screws and 4 M3 hex nuts for the bearing cap.
1 M3x12 socket-head screw + M3 hex nut for the original shaft clamp.
Check actual motor thread depth before using 6 mm engagement. Use vibration-
resistant fastening appropriate to the actual hardware; tighten without crushing
PETG or preloading the motor shaft through the coupling.

FITS / POSITIVE RETENTION
6805: d25 / D37 / B7. Printed journal is 24.9 diameter; holder bore is 37.2.
Shoulder OD27 contacts the inner ring. Holder and cap have 35 mm openings,
contacting only the outer ring. Housing depth 7.2 leaves 0.2 mm axial allowance.
Circlip groove: diameter 23.9, width 1.3; end margin 1.7. Ring X26.2..39.3.
The printed shoulder, inner race, spacer and steel circlip capture the screw.
Circlip + spacer nominal endplay: about 0.25 mm maximum before print variation.
Shim only against the inner ring if needed; do not crush or clamp the shields.
The groove is in ADDED material: the existing screw and shaft-clamp cuts are
unchanged. The ring covers the first 9.3 mm of the original helical region.

ASSEMBLY
1. Print-fit bearing journal, recess and circlip groove with the actual hardware.
   Remove burrs; verify the circlip seats completely around the groove.
2. Load the four cap hex nuts from the rear of the holder before mounting it.
3. Pass the four M3x16 screws through the holder and 4 mm wall into the motor.
4. Load the original coupling nut and loose bolt into the screw. Slide its D bore
   onto the shaft; leave the clamp loose until the bearing is seated.
5. Slide the bearing over the screw from the threaded end into the holder and
   against the printed shoulder. Press only the appropriate race during fitting.
6. Fit the inner-race spacer and expand/install the steel circlip using circlip
   pliers. Ensure the clip is fully seated, then fit the outer-race retaining cap.
7. Tighten the coupling through the open side of the holder. Rotate by hand and
   check free motion, axial play, clip engagement and bolt tightness before load.

PRINT / CHECK
Wall and cap: broad face on bed. Holder: bearing-cap face on bed, posts upward.
Spacer: flat. Screw: use the existing screw printing orientation/profile.
STLs have assembly coordinates; use the slicer's place-on-face/drop-to-bed tools.
No sliced print profile or printer upload is included in this experiment.
CAD checks cover valid single solids, watertight oriented print meshes, assembled
intersections, full rotational envelopes, bolt/tool access, bearing axial passage,
and exact preservation of original screw material outside the additive ring.
Hardware race/shield internals and the installed circlip are fit references.
Exploded view illustrates a sequence; clip expansion is illustrative, not a
simulation of steel deformation or installation forces.

~1 lb = 4.45 N static load is the intended prototype input, NOT a tested rating.
Printed groove/shoulder creep and vibration retention need physical testing.
This support does not prevent lead-screw back-driving with motor power removed.

DIMENSION SOURCES
https://www.nsk.com/engineering/6805-dgbb-sr.html
https://www.pgb-europe.com/en-gb/262160/retaining-ring-for-shafts-din-471-25

REBUILD
Extract the bundle; install CadQuery 2.7; run:
python experiments/bearing-supported-screw/model.py
The referenced legacy generator is read via AST, not executed or modified.
