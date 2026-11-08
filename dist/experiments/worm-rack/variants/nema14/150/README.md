# Direct-shaft worm actuator

**[Open the worm viewer](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site/experiments/worm-rack/)** · [Standard spur actuator](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site/)

NEMA17 and NEMA14 presets at **40, 100 and 150 mm stroke** retain the enclosure dimensions, external mounting-hole coordinates and mounting planes of their matching fully enclosed spur models. The motor stays at the previous geared prototype’s position, with its back exposed for the controller.

[![Direct-shaft worm actuator](https://raw.githubusercontent.com/tscircuit/rack-actuator/main/docs/images/worm-overview.png)](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site/experiments/worm-rack/)

The one-piece worm fits directly onto the motor D shaft. Both spur gears and the rear worm bearing are removed. The matched compliant tooth strip moves down **21 mm for NEMA17 / 19 mm for NEMA14**, joined to the original guide backbone by a deep web and triangular rib. The six guide bearings retain their positions. The output is now a 42 × 42 × 8 mm end plate with the NEMA17 31 × 31 mm four-hole M3 pattern. Hole axes are parallel to travel (+X); insert seats are 0.3 mm recessed with 3.4 mm through-holes. No motor pilot or shaft bore is added. Smooth tooth reliefs and 0.10 mm oversize per flank remain.

[![Integral D-shaft socket](https://raw.githubusercontent.com/tscircuit/rack-actuator/main/docs/images/worm-direct-socket.png)](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site/experiments/worm-rack/)

[![Lowered compliant teeth engaging the worm](https://raw.githubusercontent.com/tscircuit/rack-actuator/main/docs/images/worm-contact.png)](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site/experiments/worm-rack/)

## Drive and resolution

| Parameter | NEMA17 | NEMA14 |
| --- | ---: | ---: |
| Motor body default | 42 × 42 × 40 mm | 35.2 × 35.2 × 34 mm |
| Motor / worm speed ratio | 1:1 | 1:1 |
| Worm pitch / outside diameter | 22 / 26 mm | 22 / 26 mm |
| Worm axial module / pressure angle | 2 mm / 20° | 2 mm / 25° |
| Single-start lead | 6.283185 mm/rev | 6.283185 mm/rev |
| Motor and worm center Z | −20 mm | −18 mm |

For either 1.8° motor, with 200 full steps per revolution:

| Setting | mm / command | µm / command |
| --- | ---: | ---: |
| Full step | 0.031416 | 31.416 |
| Half step | 0.015708 | 15.708 |
| 1/4 step | 0.007854 | 7.854 |
| 1/8 step | 0.003927 | 3.927 |
| 1/16 step | 0.001963 | 1.963 |

These are command increments, not measured accuracy. Removing the reduction increases travel per motor revolution and removes its extra gear backlash. Drive force, axial stiffness, motor bearing loading, wear and heat still require physical testing. Do not assume self-locking.

## Enclosure and mounting

| Stroke | NEMA17 shell (L × W × H) | NEMA14 shell (L × W × H) |
| --- | --- | --- |
| 40 mm | 146 × 90.8 × 68.9 mm | 146 × 84.8 × 62.9 mm |
| 100 mm | 256 × 90.8 × 68.9 mm | 256 × 84.8 × 62.9 mm |
| 150 mm | 356 × 90.8 × 68.9 mm | 356 × 84.8 × 62.9 mm |

Dimensions exclude the protruding motor, controller and moving output. The reference is the **fully enclosed spur preset**, not the pass-through variant. The lid remains flat. The front aperture clears the lowered rack; an axial service port reaches the end bolt. External M3 mounts stay in place. Rear-mounted controller dimensions are not modeled.

[![Exposed motor back face](https://raw.githubusercontent.com/tscircuit/rack-actuator/main/docs/images/worm-motor-rear.png)](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site/experiments/worm-rack/)

## Hardware

**Five printed assembly parts:** chassis, rack, direct-shaft worm, enclosure tray and flat cover. A tooth-fit coupon is supplied separately.

- **Seven 625ZZ bearings**, 5 × 16 × 5 mm: six guides and one worm end support.
- **One M5 insert**, Ø7 × 8 mm, in a Ø6.6 mm axial pilot, installed flush with the worm end.
- **One M5×16 socket bolt**, with 8 mm insert engagement and 0.6 mm blind-pilot tip clearance.
- One **2 mm metal inner-race spacer** and one **0.3 mm washer**, both Ø7.5 outside / Ø5.3 inside.
- One **M3×6 flat-point set screw**. Tap the worm’s Ø2.5 mm radial pilot M3. The screw faces the flat of the Ø5.30 mm D socket; reference shaft diameter is 5 mm with a 0.5 mm flat. Verify your actual shaft length and flat.
- Four M3×10 motor screws; two recessed M3×8 rear chassis-support screws with Ø4.6 × 5 mm M3 inserts.
- Existing guide axle hardware, enclosure inserts and chassis/lid screws are listed in each BOM.
- Four optional M3 output inserts. Ø3.4 mm holes pass through the output pad for alternative through-bolts.

The end bearing’s outer race is captured between a chassis shoulder and a front stop integral to the enclosure tray. The nominal axial fit allowance is **0.3 mm**. The central openings clear the inner race; the bolt, washer and spacer clamp that race to the worm. The spacer seats directly against the flush metal insert face (16.42 mm² contact area), avoiding a thin printed seating lip. There are no keeper screws or additional printed parts. Check printed endplay, free rotation and your motor’s axial-load rating before applying load; this is not a zero-backlash thrust bearing arrangement.

[![Captured end bearing](https://raw.githubusercontent.com/tscircuit/rack-actuator/main/docs/images/worm-end-bearing.png)](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site/experiments/worm-rack/)

## Assembly

1. Install enclosure/chassis inserts and the worm’s M5 insert. Tap the M3 set-screw pilot.
2. Insert the worm end bearing into the bare chassis from +X, outside the enclosure, then assemble the six guide bearings and their axle hardware. Install this subassembly into the tray using the checked service path; the tray stop then captures the end bearing. Secure chassis screws.
3. Align the worm D socket and motor shaft, position the worm face 2.8 mm ahead of the motor face, and tighten the set screw while outside the enclosure.
4. Insert motor and worm together through the rear. Tighten the four motor screws.
5. Lower the 2 mm inner-race spacer through its chassis slot. Fit the end washer and M5 bolt through the front service port. Verify free rotation and endplay.
6. Insert the rack from the front, turning the worm to draw the teeth into engagement. Check the full stroke by hand before installing the cover.

The **Explode drive** slider reverses this sequence: remove the lid, turn the worm while winding the rack clear, slide the rack out, remove the end bolt/washer, lift the spacer, release motor screws, and withdraw motor and worm together. The bearing stays captured in the base. The final insert motion shows its installation path; removal of an installed heat-set insert requires heat. Guide floors relax through sampled CAD states as the rack leaves.

[![Staged disassembly](https://raw.githubusercontent.com/tscircuit/rack-actuator/main/docs/images/worm-separated.png)](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site/experiments/worm-rack/)

## Printing and validation

Chassis STL flexures are unloaded. The nominal leaf span is now **18 mm**, increased from 14 mm. The fixed-root and inner axle-carrier transitions have **5 mm unloaded radii**, increased from 2 mm, while retaining the broad **1.8 mm leaf thickness**. The bearing-facing transition remains **2 mm** to preserve roller clearance. The rounded profiles are part of the unloaded spring geometry and deform with its prescribed bend; they are not regenerated as constant-radius fillets on every loaded pose. The spring bays extend 4 mm toward their roots, retaining the bearing positions.

These changes need print testing for spring force, elastic recovery and fatigue. The viewer uses prescribed displacement, not an elastic simulation.

Both spring bays reserve **0.8 mm clearance from the added worm supports** throughout **0–2.6 mm prescribed deflection**, including the bearing bridge and the material beneath it. Independent checks include the rounded spring transitions and detect interference inside the integral chassis, which ordinary separate-part collision checks cannot detect.

The motor mount now has **two 5 mm side webs**, joining the faceplate to the rear bridge and forming a deep U-section with the existing support floor. Their **2 mm tangent floor roots** and 3 mm rounded upper corners avoid abrupt projecting transitions. This adds a second load path around the thin upright while retaining the shaft-withdrawal bore, motor screw pockets, guide hardware access and spring envelopes. Validation records the added material and before/after section areas; these geometric comparisons are not stiffness or load ratings.

For the **NEMA17 / 40 mm worm preset**, the two indicated regions are joined by one **face-aligned U-shaped upper flange**. Its full-width motor-plate cap and both side shoulders share the chassis platform's **Z = 4 mm** top plane. The nominal section is **8 mm deep**, with **5.7 mm nominal neck widths**, **4 mm inside corner radii**, **1 mm edge rounds**, and smoothly flared joins into the fixed chassis. The marked points identify connection regions; they do not define individual beam axes or heights. Fastener and motion envelopes trim the final shape. A tapered 5 mm wide outer brace continues to reinforce the upright at **(−43, −19.818, −4.103) mm**, with a checked solid ligament extending 7 mm behind that face. Other motor/stroke presets retain their existing motor supports.

Motor-bolt service openings provide access to the upper bolts from above and the lower bolts through underside ports, with Ø8 mm head pockets. This preserves the deep side webs. With the lid and rack removed and space underneath the tray, the geometric access check uses a **compact 2.5 mm hex key with an 8 mm short-leg reach and a 40 mm long leg**, sweeping outward through 60° and following the first 5.5 mm of screw release (until the motor threads are disengaged); then withdraw the loose bolts by hand to 11 mm. Check your actual tool against these dimensions. The two internal tray support screws move 27 mm forward, into the fixed chassis region, to keep their inserts clear of the service openings and their access holes clear of the upper bridges. **Use the updated chassis and matching enclosure tray together**; their external enclosure bounds and mounting datums are preserved. Print/load testing is still required to establish stiffness or strength.

The rack and cover are oriented top-face down; the rack rib tapers inward in that orientation. The worm prints vertically. Inspect helical flanks, motor aperture and rear opening in your slicer for support requirements. Print the tooth coupon first. Longer worms need care with straightness and torsional stiffness.

Each ZIP includes ready-to-print STLs, CadQuery source, configuration, mounting coordinates, BOM and a fresh validation report. The viewer serves the revised chassis and matching tray STLs directly from the current Site version. STEP export is optional with `--step`; these published bundles prioritize STL downloads and do not include STEP files. Other standalone compressed CAD files live in [`downloads/worm`](https://github.com/tscircuit/rack-actuator/tree/main/downloads/worm). Production spur geometry is unchanged.

Checks cover valid single solids, assembled solid pairs, insert fit, bearing capture, worm/rack engagement, full-stroke motion, enclosure and mounting equality, tool access, guide installation and staged drive separation. FCL screens fine CAD tessellations; OCC confirms candidate interference volumes. Insert interference and compliant tooth preload are intentional. Explosion translations are sampled at no more than 0.5 mm increments, with separate dense worm phase checks. These are sampled geometric checks, not continuous-motion proof, elastic simulation or physical testing.

Run these commands from a full repository checkout; validation compares against the published spur preset references.

```sh
pip install -r experiments/worm-rack/requirements.txt
python experiments/worm-rack/model.py --motor nema17 --stroke 40 --check
python experiments/worm-rack/build_presets.py --motor nema17 --stroke 40 --skip-valid
# Omit --motor and --stroke to rebuild the entire worm family.
# Optional full STEP export: add --step to either build command.
python -m http.server 8000 --directory dist
```

Open `http://localhost:8000/experiments/worm-rack/`. This experiment remains separate from the standard spur models.

The upper flange rails move toward the motor centerline, leaving 5 mm from each upper bolt axis to the nominal outer neck edge. Rack clearance trims the inner edge. All four M3×10 bolts now withdraw 11 mm to clear the faceplate completely, then the upper pair lifts 60 mm and the lower pair drops 50 mm through the tray ports. The viewer can replay either removal or insertion; insertion reverses the same path. Validation checks continuous swept shaft/head solids against the staged assembly, plus the full sampled explosion sequence. These revised underside ports require the matching updated tray.

## Reinforced compliant and solid rack options

The Rack teeth selector offers two replacement racks for every NEMA17 / NEMA14 and 40 / 100 / 150 mm preset. Both retain the original bearing guide and actuator mounting interface. The selected rack STL and coupon are served directly by the site; the full bundle contains both rack STLs and both check reports.

- Reinforced compliant: nominal axial wall thickness increases from 0.6 to 0.9 mm. A rounded closed tip joins the two walls. The outside mating profile and 0.1 mm geometric preload per flank are retained. The thicker walls and closed tip are intended to improve strength; stiffness, fit and durability still need physical testing.
- Solid: removes the internal tooth slots and between-tooth root reliefs. The tooth root is continuous. The mating flanks are relieved by 0.1 mm relative to the nominal profile instead of applying interference preload; backlash can result.

Print the matching tooth-fit coupon first to check engagement with the existing worm. There is no load, fatigue or wear rating for either new tooth design.

Rebuild the baseline chassis with the existing model/build-presets command, then run `python experiments/worm-rack/teeth_variants.py --motor nema17 --stroke 40`, substituting the selected motor and stroke. The generator verifies matching baseline provenance, reuses unchanged assembly checks, and checks the entire changed tooth band against other parts through motion and disassembly. A solid difference check verifies that the rest of the rack matches the baseline. It separately checks the nominal compliant or actual solid teeth against the worm, with additional full-rack solid checks.

For a complete hosted-site rebuild, first run `python deduplicate_downloads.py` to share the unchanged spur STEP files already contained in their ZIP bundles. After generating all six worm presets, run `python experiments/worm-rack/package_teeth.py` to update the build notes and deduplicate hosted downloads. The site extracts the selected rack or coupon from the matching ZIP and checks its CRC32; the download is an ordinary STL.

## Axial output plate

Both reinforced and solid racks have the same NEMA17 end interface. The plate stays 1.5 mm outside the enclosure at full retraction. Exact solid differences preserve the tooth and guide geometry; continuous conservative swept-bound checks cover the new plate through travel and staged assembly. Use supports under the rack if printing on its long face, since the plate extends past both long faces. STEP files are omitted; STL downloads and the CAD source are updated.
