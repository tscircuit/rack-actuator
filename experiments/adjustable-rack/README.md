# Screw-adjusted rack variants

Scope: NEMA17, 40 mm, separate worm and spur chassis. A shared rigid lower guide carrier replaces both spring floors. Four top-access M3×20 screws and four M3 heat-set inserts set preload. Six 625ZZ guides use integral split PETG axles; outer races are relieved from printed faces.

Build from the repository root with the CadQuery environment:

```
python experiments/adjustable-rack/model.py --drive spur
python experiments/adjustable-rack/finish.py spur
python experiments/adjustable-rack/model.py --drive worm
python experiments/adjustable-rack/finish.py worm
```

The pinned baseline source is intentional: it preserves the previously checked mechanism while replacing the guide support. The generator applies the current axial output plate and derives the existing reinforced and solid worm tooth recipes by content hash. Local BREP caches are rebuildable and ignored. `finish.py` uses the same staged tracks for exact-solid collision confirmation and the browser animation. Failed geometry checks prevent STL bundle export.

A displaced cover-screw post, relieved enclosure ribs, and open-ended carrier guides provide actual assembly paths. Use the chassis, carrier, tray and cover from this variant together. These are geometric prototypes, not measured PETG load or fatigue ratings.
