# Worm-to-compliant-rack experiment

**[Open the experimental viewer](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site/experiments/worm-rack/)** · [Production spur actuator](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site/?motor=nema17&stroke=40)

An isolated **NEMA17 / 40 mm stroke** feasibility prototype. This is a direct worm engaging a compliant linear rack. It does not introduce a worm wheel or replace any of the twelve production spur presets. Select **Drive type → Worm rack · experimental** on the 40 mm NEMA17 page.

The prototype is an open bench fixture with a removable motor/shaft cartridge. Its motor axis is parallel to rack travel; the 42 × 42 × 40 mm motor sits beyond the retracted rack. This costs space compared with the production enclosure. The rear-mounted controller remains outside the fixture and is not modeled.

[![Matched worm and compliant rack flanks](https://raw.githubusercontent.com/tscircuit/rack-actuator/main/docs/images/worm-contact.png)](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site/experiments/worm-rack/)

## Tooth geometry

| Parameter | Value |
| --- | --- |
| Axial module / pitch | 2 mm / 6.283185 mm |
| Center-section pressure angle | 20° |
| Worm starts / lead | 1 / 6.283185 mm per revolution |
| Worm pitch / outside diameter | 24 / 28 mm |
| Threaded length | 24 mm |
| Rack tooth face | 8 mm |
| Rack oversize | 0.10 mm per flank |
| Worm flank allowance | 0.03 mm per flank |
| Nominal net elastic engagement | 0.07 mm per flank, before printing tolerances |
| Shaft / printed D bore | 5 / 5.30 mm |

The original straight rack cannot simply be reused: its profile does not follow the worm through the tooth thickness. The experiment preserves the **module, 20° axial tooth profile and smooth compliant reliefs at the center plane**, then curves the tooth flanks to match the worm. It retains the lower six-bearing guide rail and original output mount, including its four M3 insert pockets.

For a point `(x, y)` in the original rack profile, and worm axis `(Y, Z) = (6, 17)` mm:

```text
r = y − Y
θ = asin((z − Z) / r)
x′ = x + lead / (2π) × θ
y′ = Y + sqrt(r² − (z − Z)²)
```

The mapping is blended back into the rigid backbone above the tooth roots and into the plain rack beyond the tooth field. CAD splines approximate this surface; collision checks evaluate the resulting solids/meshes, not just the formula. Positive rack travel requires negative rotation about the worm's +X axis.

## Resolution

For a 1.8° motor with 200 full steps per revolution:

| Setting | mm per command | µm per command |
| --- | ---: | ---: |
| Full step | 0.031416 | 31.416 |
| Half step | 0.015708 | 15.708 |
| 1/4 step | 0.007854 | 7.854 |
| 1/8 step | 0.003927 | 3.927 |
| 1/16 step | 0.001963 | 1.963 |

These are **command increments**, 18× finer than the 18T spur version. They do not establish positioning accuracy, repeatability, holding force or self-locking. A worm introduces substantial sliding contact; heating, friction, wear and the ability to drive the preloaded teeth are open questions.

## Hardware and assembly

Retain the six 625ZZ guide bearings and their M5 axle hardware from the production 40 mm NEMA17 guide. Add:

- Two 625ZZ bearings (5 × 16 × 5 mm) supporting the worm shaft.
- A 5 mm steel D shaft, nominally 96.5 mm long; confirm the motor's actual shaft length before cutting. The reference motor has a 24 mm projection from its mounting face.
- Two 1.5 mm inner-race spacers, Ø7.5 mm outside / Ø5.3 mm inside, and two 0.3 mm washers of the same diameters.
- Two adjustable 5 mm shaft collars. The reference collars are Ø10 × 5 mm with radial M3 screws. Position them to take up axial play without preloading the 625ZZ bearings excessively. Axial load capacity is not established.
- One M3×8 flat-point worm set screw, two M3×3 coupling set screws and two M3×3 collar set screws. They bear on the D-shaft flat. Tap printed Ø2.5 mm radial pilots M3. The worm pilot opens through the thread crest; its set screw is recessed so a hex key can reach it without the screw projecting into the tooth contact.
- Four M3×8 keeper screws; tap the carrier's Ø2.5 mm pilots M3.
- Four M3×10 motor screws; confirm engagement against the chosen motor's datasheet.
- Two M3×10 cartridge mounting screws and two M3 heat-set inserts, Ø4.6 × 5 mm, for the base. The rack uses its existing four M3 inserts of the same size.

The bundle includes separate printed STLs, an assembled STEP file, source, and the check report. The guide fixture STL contains the **unloaded flexure floors**; the assembly view contains their installed, deflected state. The rack STL is placed on its flat top face. Check all other orientations in your slicer; this experimental worm/support geometry is not claimed to print without supports.

Start with the **worm and `rack_mesh_coupon.stl`** to check tooth fit by hand before printing the full fixture. The coupon uses the same generated tooth shape and is not an additional assembly component. Test with the motor disconnected first. Check sliding force across a full turn, tooth recovery and shaft end play before powered travel.

Insert the rack into the six-bearing guide while the drive cartridge is removed. Install the support bearings, spacers, worm, shaft, collars and bearing keepers on the cartridge; connect the motor using the D coupling. Set rack position to mid-stroke and phase the worm into the matching gaps. Slide the cartridge into place and fasten its two base screws. Set controller travel limits to the 40 mm stroke.

The viewer's **Separate module** slider removes those two mounting screws and moves the complete drive cartridge sideways. It intentionally leaves the rack guide and cartridge's internal hardware assembled; it is not a full hardware teardown simulation.

[![Drive cartridge separated from the rack guide fixture](https://raw.githubusercontent.com/tscircuit/rack-actuator/main/docs/images/worm-separated.png)](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site/experiments/worm-rack/)

## Reproduce the CAD and checks

From the repository root, using Python 3.12:

```sh
pip install -r experiments/worm-rack/requirements.txt
python experiments/worm-rack/model.py --check
python -m http.server 8000 --directory dist
```

Open `http://localhost:8000/experiments/worm-rack/`. Geometry builds only into `dist/experiments/worm-rack/`; the production `model.py`, presets and downloads are not regenerated. Local B-rep caches live under ignored `work/worm-cache/` and are invalidated when the tooth geometry source changes.

The [validation report](validation.json) records assembled solid intersections, full-stroke motion checks, relative tooth phases, and staged module separation. FCL uses fine CAD tessellation to find moving collision candidates; OCC measures their solid overlap. Selected mesh poses are also checked directly with OCC, including the incompatible straight rack for comparison. Mating insert/host interference and compliant tooth preload are recorded separately. These are sampled geometric checks, not continuous-motion proof, elastic simulation or physical testing.

Before integrating this drive into an enclosure, measure printed fit, available drive force, backlash under load reversals, spring fatigue, wear/temperature and shaft thrust restraint. No performance or self-locking claim is made for this prototype.
