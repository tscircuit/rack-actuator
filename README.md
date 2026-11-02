# Rack actuator

Revision 15: CadQuery NEMA17/NEMA14 rack actuators with compliant teeth, six 625ZZ bearings and a printable mounting enclosure.

[Interactive viewer](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site) · [NEMA14 viewer](https://flex17-compliant-linear-actuator.seveibar.chatgpt.site/?motor=nema14)

## Configurable enclosed module

- Tooth module controls both matched rack and pinion profiles (default 2 mm).
- Usable stroke and fixed housing length are separate parameters: defaults 40 mm and 132 mm. Omit housing length to calculate its minimum.
- Standard-depth motors: 40 mm NEMA17 and 34 mm NEMA14. Motor rear projects 4 mm outside the case; rear-mounted drivers remain exposed and are not assigned guessed dimensions.
- Two new printed enclosure parts: mounting tray and removable lid. Four reinforced M4 slots on a flat side face attach the module to a fixture.
- A shortened tooth segment and extended smooth output tongue keep all teeth covered throughout normal travel.
- Actuation, 16-stage service animation, enclosure visibility, mounting-face/driver views, resolution table and downloadable parameter JSON are available in the viewer. The parameter form generates CAD configuration; browser geometry remains the checked default.

The tested six-bearing chassis, integral spring floors, 2.3 mm preload, 0.8 mm bearing relief and 0.5 mm axle-head clearance are retained. At module 2, reuse the revision-14 chassis and matching pinion; print the new rack, tray and lid. Five printed parts total. The enclosure adds four M3×25 screws/nuts and two low-head M4×12 screws/nuts; see [printing and assembly instructions](README.txt).

| Default | NEMA17 | NEMA14 |
| --- | --- | --- |
| Motor body | 42 × 42 × 40 mm | 35.2 × 35.2 × 34 mm |
| Housing body | 132 × 88.8 × 68.9 mm | 132 × 82.8 × 62.9 mm |
| Pinion | 18T / 20° | 14T / 25° |
| Full-step increment, 200 steps/rev | 0.565487 mm | 0.439823 mm |
| 1/16 increment | 0.035343 mm | 0.027489 mm |

Housing dimensions exclude 3 mm mounting pads, moving output and exposed motor/driver. Increments are theoretical, not measured accuracy. Do not mix variant racks/pinions. Verify the actual motor shaft, pilot and hole dimensions.

## Generate CAD

Use Python 3.12 / CadQuery 2.7.0:

```sh
pip install -r requirements.txt
python model.py --motor nema17 --out dist --check
python model.py --motor nema14 --out dist/variants/nema14 --check
python package_designs.py
python -m http.server 8000 --directory dist
```

For a custom build:

```sh
python model.py --motor nema14 --tooth-module 1.8 --stroke 60 --actuator-length 180 --motor-depth 34 --out build/custom --check
# Or use a downloaded JSON; explicit CLI arguments override JSON values:
python model.py --config configuration.json --out build/custom --check
```

| Parameter | Range / behavior |
| --- | --- |
| `--tooth-module` | 1.5–2.5 mm; default 2, circular pitch = π × module |
| `--stroke` | 20–120 mm; default 40 |
| `--actuator-length` | Housing X length, automatic minimum when omitted; maximum 350 mm |
| `--motor-depth` | 32–60 mm; defaults 40 / 34 |
| `--spring-preload` | 0.1–2.5 mm; default 2.3 |
| `--spring-thickness` | 1.2–1.8 mm; default 1.4 |
| `--bearing-clearance` | Default 0.8 mm |
| `--hardware-clearance` | 0.5–1.2 mm; default 0.5 |
| `--rack-backbone-width` | 14.5–18 mm requested minimum; default 16 |
| `--preload` | Tooth oversize per flank, default 0.10 mm |

Short housing requests are rejected. Fine reliefs at smaller modules need printer qualification. Changed parameters need regenerated geometry, fresh checks and a fit test. Download bundles contain STEP, five STL files, configuration JSON, source and reports. Packaging verifies that both default reports match the current source.

## Assembly and checks

Fit captive nuts and attach the open tray to the fixture. The chassis sits on front supports and a broad rear ledge; two M4 screws retain the front, and the lid clamps the existing rear recesses. Install motor screws before the upper rollers. Insert the rack with the motor free to turn, check all six bearings rotate, then attach the lid.

For service, remove lid, rack, pinion and upper bearings; lower the motor with its driver attached before lowering the tray. The tray remains at least 4 mm ahead of the motor rear plane throughout the checked service sequence. Electronics/connectors must stay behind that plane. Complete hardware, print orientations and assembly order are in [README.txt](README.txt).

[Default NEMA17 report](dist/downloads/validation.json) and [NEMA14 report](dist/variants/nema14/downloads/validation.json) check all assembled pairs, dense sampled service/travel, nominal tooth mesh, captive-nut insertion and hardware gaps. Additional parameter cases are recorded separately with their smaller sample counts. Viewer and CAD share motion tracks.

The builder has physically tested the core mechanism. The new enclosure and new parameter combinations still need fit, thermal and load testing. Sampled intersections are not continuous swept-volume proof or a physical tolerance test. Prescribed spring displacement does not establish elastic recovery, creep or fatigue life. The chassis STL is relaxed; STEP/viewer show the installed deflection. Use controller travel limits; no axial hard stop is provided.

## License

MIT; see [LICENSE](LICENSE). Compliant tooth principle inspired by [seveibar/compliant-spur-gear](https://github.com/seveibar/compliant-spur-gear); its license is included in both bundles.
