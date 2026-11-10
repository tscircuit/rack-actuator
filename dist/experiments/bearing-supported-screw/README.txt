6805 bearing-supported screw — independent prototype, revision 2
Units: mm. Based on the existing 40 mm travel printed lead screw (tip X152).

LAYOUT
The bearing sits in the MOTOR-FACING recess of the holder. The screw is inserted
from the motor side: its threaded end passes through the bearing and holder,
until the added shoulder contacts the inner race. The holder's forward lip
supports the outer race. There is no bearing retaining cap, steel circlip,
inner-race spacer, cap screw or cap nut.

The holder projects 30.3 mm from the wall's front face, 1 mm less than revision 1.
The wall remains 52 x 52 x 4 mm, with a 31 x 31 mm NEMA17 hole pattern.
Motor and screw retain their original relative positions. Existing actuator
parts are unchanged; this is a separate assembly without a carriage.

PRINTED PARTS
1. 4 mm NEMA17 wall, with M3 clearance holes.
2. Bearing holder: motor-facing recess, forward lip and four open standoffs.
3. Existing printed screw plus additive bearing journal and shoulder.

HARDWARE
1 NEMA17 motor: 5 mm D shaft, 4.5 mm across flat, 24 mm shaft projection.
1 6805 bearing, 25 mm bore x 37 mm OD x 7 mm width.
4 M3x16 socket-head screws for holder + wall + motor (6 mm engagement).
1 M3x12 socket-head screw + M3 hex nut for the original shaft clamp.
Check actual motor thread depth before using 6 mm engagement. Tighten without
crushing PETG or forcing axial preload into the motor through the coupling.

FITS
Printed journal: diameter 24.9, X24.3..31.3.
Shoulder: diameter 27, X22.3..24.3; contacts only the inner race.
Original shaft bore, clamp split and bolt/nut pockets stay clear. The split
continues through the added ring to X26, preserving the coupling's opening.
Holder body: X24.2..34.3. Rear recess: diameter 37.2, ending at X31.4.
Bearing: X24.3..31.3; 0.1 mm nominal clearance to the forward retaining lip.
Front lip: 35 mm opening; contacts only the outer race.
The rear bearing-loading path is clear between the standoffs. Open radial
motor-bolt channels replace fragile strips between the recess and bolt bores.
All original screw material is retained. The ring covers the first 1.3 mm
of the original helical region. This is not a drop-in carriage retrofit.

ASSEMBLY
1. Seat the bearing in the holder's rear, motor-facing recess.
2. Feed the screw's threaded end through the bearing and holder FROM THE MOTOR
   SIDE until the shoulder rests against the bearing's inner race. Fit the
   original coupling nut and loose clamp bolt.
3. Fit the flat 4 mm wall and motor, engaging the D shaft in the coupling.
4. Attach the holder and wall using four M3x16 motor screws.
5. Tighten the shaft clamp through the open side of the holder. Check free
   rotation and bearing seating before applying load.

EXPLODED VIEW / DISASSEMBLY
Loosen the shaft clamp first. Remove the motor screws, motor and wall. Withdraw
THE SCREW toward the motor side through the stationary bearing. After the screw
clears it, remove the bearing from the rear recess. The bearing does not pass
through the front lip. The clamp hardware remains on the screw in the viewer.

PRINT / CHECK
Wall: broad face on bed. Holder: front face on bed, standoffs upward.
Screw: use the existing screw printing orientation/profile.
STLs have assembly coordinates; use the slicer's place-on-face/drop-to-bed tools.
No sliced print profile or printer upload is included.
CAD checks cover valid single solids, watertight oriented print meshes, assembled
intersections, full rotational envelopes, bolt/tool access, rear bearing passage,
original screw preservation and 41 sampled disassembly poses.

The shoulder/bearing/holder load path supports thrust TOWARD THE SCREW TIP.
There is no independent reverse-direction retainer; reverse retention relies
on the motor coupling. About 1 lb = 4.45 N static is the intended input, not a
physically tested load rating. PETG creep and vibration require testing.
This bearing does not prevent back-driving with motor power removed.

DIMENSION SOURCE
https://www.nsk.com/engineering/6805-dgbb-sr.html

REBUILD
Extract the bundle; install CadQuery 2.7; run:
python experiments/bearing-supported-screw/model.py
python experiments/bearing-supported-screw/check_assembly.py
The referenced legacy generator is read via AST, not executed or modified.
