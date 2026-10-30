# Rack actuator

A compact, 3D-printable NEMA17 rack actuator with compliant teeth and six 625ZZ guide bearings. This is the FLEX17 revision 10 design, with an integral motor mount and passive parallel-leaf preload for the two lower bearings.

[Open the interactive 3D viewer](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site) to actuate the rack, inspect bearing contacts, and explore the staged assembly explosion.

## Design

- Configurable stroke; 40 mm initially.
- Four upper bearings at 45° react downward/inward; two lower bearings support upward.
- Bearing stations spaced 46 mm apart; lower contacts staggered ±1 mm to resist rocking.
- A pair of replaceable four-leaf spring cartridges pushes the lower bearings upward, with 0.30 mm nominal deflection, rounded roots and 0.8 mm overtravel stops. Two ordinary through-bolts retain each fixed cartridge root; there are no preload locking screws.
- A ramp at the rack insertion end gently depresses the spring-supported rollers.
- One-piece chassis with integral 5 mm motor mounting land.
- Rounded compliant-tooth reliefs, oversized tooth flanks, and an oversized D-shaped pinion bore with a set screw normal to the shaft flat.
- Mounting holes on both the chassis and moving output pad.

See [printing, hardware, assembly and adjustment instructions](README.txt) before printing. From revision 09, reprint the chassis and rack and replace the eccentrics with the spring cartridges. Reuse the bearings, pinion, M5 axles and motor hardware; add four M3×20 through-bolts and four M3 nuts.

## Files

- [model.py](model.py): parametric CadQuery source.
- [dist/downloads](dist/downloads): STEP assembly, five printable STL files, CAD bundle, and validation report.
- [dist](dist): standalone Three.js viewer with actuation and staged explosion controls.
- [validation.json](dist/downloads/validation.json): sampled solid-intersection checks and CAD/viewer reference poses.

## Generate and check the CAD

Use Python 3.12 and CadQuery 2.7.0:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python model.py --stroke 40 --preload 0.10 --check
```

This regenerates STEP, STL, viewer geometry and the validation report under `dist/`. It does not rebuild the bundled ZIP or copy modified source into the downloads directory. Geometry checks can take several minutes. A changed stroke or other dimensions require fresh checks.

Spring parameters are `--spring-preload 0.30 --spring-thickness 1.0` (mm). The spring STL is unloaded for printing; the STEP/viewer show the assembled deflection. Print each cartridge on its broad side face so bending stays within the layer plane. Spring force, creep and fatigue must be tested physically.

Optional shaft parameters are `--shaft-diameter 5 --shaft-flat-depth 0.5 --shaft-clearance 0.15`. Use `--out PATH` for a separate export directory.

## Run the viewer locally

```sh
python -m http.server 8000 --directory dist
```

Open <http://localhost:8000>. The viewer is static and needs no API keys or backend.

## Validation and limitations

The generated report records assembled-pair, travel, staged-removal, unloaded-print and spring-stop checks. Each lower bearing follows the rack lead-in during insertion/removal; the carrier deforms with it. Only intentional elastic tooth contact is allowed. Spring deformation is prescribed geometry, not a finite element prediction. The viewer uses the same CAD motion tracks; actuation, all six bearing rotations, mobile layout and reference explosion poses were also checked.

These are sampled geometry checks, not a continuous swept-volume proof or physical load test. Backlash, stiffness, preload force, fatigue life and positioning accuracy remain unmeasured. Use controller travel limits; the rack insertion end is open. The motor is a dimensional reference, and electronics, driver, wiring and limit switches are not included.

## License and inspiration

MIT; see [LICENSE](LICENSE). The compliant rack adapts the spring-wall principle from [seveibar/compliant-spur-gear](https://github.com/seveibar/compliant-spur-gear). Its reference license is included in [dist/downloads/reference-LICENSE.txt](dist/downloads/reference-LICENSE.txt).
