6805 bearing-supported screw — shared NEMA17 bolts, revision 5
Units: mm. Independent assembly using the original 40 mm printed screw.

HOLDER AND HARDWARE
Four M3x40 socket-head screws pass through the holder and wall directly into
NEMA17's existing 31 x 31 mm mounting pattern. No separate holder screws,
washers, locknuts or extra motor screws are required. Left and right shells
connect the four corner columns to the continuous outer-race lip. Top and
bottom openings preserve access to the coupling clamp. Overall holder width
is 43 mm, projection 30.3 mm; the standalone wall is 52 x 52 x 4 mm.
The original printed screw, bearing journal and coupling are unchanged.

Other hardware: one NEMA17 motor (5 mm D shaft, 4.5 mm flat-to-opposite-side),
one 6805 bearing (25 x 37 x 7 mm), original M3x12 clamp bolt and M3 hex nut.
The shared M3x40 screws have 5.7 mm nominal engagement in the motor. Verify
actual motor thread depth before assembly; screws must not bottom out.
The T8 Z version uses the same four M3x40 bolts with 2 mm recessed head seats
to account for its thicker 6 mm base wall. Use the matching holder STL.

LOAD PATH
For load pulling the screw AWAY FROM THE MOTOR:
screw shoulder -> inner race -> 6805 -> continuous housing lip / side shells
-> four shared screw heads -> motor front threads / clamped wall.
The bearing journal is 24.9 mm diameter; shoulder OD 27 mm; housing abutment
bore 35 mm. The original 0.1 mm unloaded lip clearance is retained.
This remains one-direction support without a reverse retaining cap or circlip.
Reverse retention depends on the coupling; the bearing does not prevent screw
back-driving. The earlier 1 lb input is not a physically tested load rating.

ASSEMBLY
1. Seat the 6805 in the motor-facing recess. Feed the threaded screw end
   through the bearing/holder from the motor side until its shoulder reaches
   the inner race. Fit the original shaft-clamp bolt and nut loosely.
2. Place the motor against the wall. Slide the supported screw onto the shaft
   and seat the holder against the other face of the wall.
3. Insert four M3x40 screws from the holder front, through the wall into the
   motor. Start all four before tightening evenly, without crushing PETG.
4. Gently seat the screw toward its tip until the outer race touches the lip,
   then tighten the coupling without preloading the motor shaft. Check rotation.
For disassembly, loosen the coupling, back the four shared screws out 6 mm
while they remain captured in the holder, slide the whole module 30 mm off
the shaft and lift it clear. Then fully withdraw the bolts. The motor is no
longer attached once these four screws are undone: support it during service.
The screw and bearing leave the housing from the motor-facing side.
On T8 versions remove the lid and withdraw the carriage first; an L-shaped
hex key reaches all four shared screws from above with the lid removed.

PRINTING AND CHECKS
Print the holder front-face down, side shells upward. Print the wall flat.
STLs retain assembly coordinates; orient and drop to bed before slicing.
The separate holder sliced with zero supports. The T8 holder generated 0.07 g
only inside its four shallow head recesses, open to the bed; no bearing-tunnel
support was generated. Results use P2S/Generic PETG/0.20 mm/4 walls/25% gyroid
with automatic supports everywhere. Physical support removal is not tested.
Reprint wall and holder for this separate assembly, base and holder for T8 Z.
Other printed parts and the T8 travel are unchanged.
Checks cover solids, meshes, rotational clearances, coupling/bolt access,
continuous lip/columns, nominal motor engagement and sampled assembly poses.
They do not establish PETG creep/fatigue, motor thread strength or load capacity.
Bearing internals are illustrative fit envelopes. Test actual print fits.

REFERENCE
NSK 6805 dimensions and mounting shoulders:
https://www.nsk.com/engineering/6805-dgbb-sr.html

REBUILD
Run experiments/bearing-supported-screw/model.py and check_assembly.py with
CadQuery. holder_geometry.py is shared with the optional T8 Z support.
