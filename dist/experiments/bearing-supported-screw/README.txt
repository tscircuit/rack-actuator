6805 bearing-supported screw — outward through-bolt holder, revision 4
Units: mm. Independent assembly using the original 40 mm printed screw.

WHAT CHANGED
The old inward feet, thin ribs and access slots are removed. Four full-depth
mounting columns project outside the 43 mm bearing-seat body. Their through
holes form a 52 x 31 mm rectangle, separate from the motor's 31 x 31 mm pattern.
The front plate has an uninterrupted 360-degree outer-race shoulder. Long steel
bolts, front and rear washers and front-facing locknuts tie it to the wall.
The holder is 62 mm wide and still projects 30.3 mm. The wall is now 64 x 52 x
4 mm, with both the original NEMA17 holes and four external support holes.
The original screw, bearing journal, shaft clamp and axial positions are retained.

LOAD PATH
For load pulling the screw AWAY FROM THE MOTOR:
screw shoulder -> inner race -> 6805 -> continuous outer-race lip -> front
plate/washer -> front locknut -> steel through-bolt -> rear washer -> wall.
The bolted columns replace the thin cantilever ribs. The bearing journal is
24.9 mm diameter; the shoulder OD is 27 mm; the housing abutment bore is 35 mm.
Those shoulder dimensions follow the NSK 6805 mounting recommendations.
This remains a ONE-DIRECTION thrust support. There is no reverse retaining cap
or circlip. Mount it so gravity pulls the screw toward its tip. Reverse axial
retention still depends on the coupling. A bearing does not prevent back-driving.

HARDWARE
1 NEMA17 motor, 5 mm D shaft / 4.5 mm flat-to-opposite-side.
1 6805 bearing: 25 x 37 x 7 mm.
4 M3x45 socket-head steel holder bolts, loaded from behind the wall.
8 M3 flat washers: nominal OD 7 mm / ID 3.2 mm / thickness 0.5 mm.
4 M3 DIN 985 nylon-insert locknuts on the FRONT of the holder.
4 M3x10 socket-head motor screws (6 mm engagement into the motor).
Original M3x12 shaft-clamp screw and M3 hex nut.
Use the actual motor's permitted screw engagement. Locknuts resist loosening;
this is not a substitute for checking PETG creep and clamp relaxation.
The same holder geometry fits the revised T8 Z variants, translated by 2 mm in
assembly coordinates. Their 6 mm base wall uses M3x12 motor screws.

ASSEMBLY
1. Mount the motor to the 4 mm wall with its four separate M3x10 screws.
2. Seat the 6805 in the holder's motor-facing recess, then feed the screw's
   threaded end through it from the motor side until the shoulder meets the
   inner race. Fit the coupling bolt and nut loosely.
3. Slide this module onto the D shaft, against the wall.
4. Insert the four M3x45 bolts with rear washers from the motor side of the
   wall. Add the front washers and locknuts. The nuts are entirely outside
   the bearing-seat body and can be reached with a straight socket.
5. Tighten evenly without crushing PETG. Gently seat the screw toward its tip
   so the outer race touches the housing lip, then tighten the shaft clamp
   in this seated position without preloading the motor shaft. Check rotation.
Loosen the coupling before disassembly. Remove front nuts/washers and withdraw
bolts rearward, slide the module 30 mm off the shaft, and lift it clear. Motor
screws are then accessible. The screw and bearing leave the holder from its rear.

PRINTING
Print the holder with its FRONT bearing face on the bed, columns pointing up.
The vertical through holes and open recess avoid internal support pockets.
Print the wall flat. STLs retain assembly coordinates; orient and drop to bed.
The screw keeps its original print orientation/profile.

VALIDATION AND LIMITS
Checks cover valid solids/meshes, rotation, bearing loading, complete columns,
continuous outer-race shoulder, bolt loading, the abutments along the axial load
path, and 41 sampled rigid disassembly poses. The earlier 1 lb (4.448 N) load is
an input, not a tested rating. Average seat pressure is about 0.039 MPa; that is
not a stress analysis of the flange, wall or printed layer interfaces. Physical
proof-load, creep and vibration testing are still required before assigning a
working-load rating. Bearing internal geometry is a reference envelope.

REFERENCES
NSK 6805 dimensions and mounting shoulders:
https://www.nsk.com/engineering/6805-dgbb-sr.html
Four-bolt outward flange arrangement reference (not a rating for this print):
https://www.skf.com/si/productinfo/productid-UCF%20206%2FH
DIN 985 locknut dimensions:
https://www.westfieldfasteners.co.uk/Standards/Nut-HexNy-M.html

REBUILD
With CadQuery 2.7, run experiments/bearing-supported-screw/model.py then
experiments/bearing-supported-screw/check_assembly.py. holder_geometry.py is
shared with the optional T8 Z support. The original screw is extracted from
its generator via AST and preserved exactly apart from its existing added ring.
