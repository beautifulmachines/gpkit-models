# gpkit-models

[![CI Status](https://github.com/beautifulmachines/gpkit-models/actions/workflows/tests.yml/badge.svg)](https://github.com/beautifulmachines/gpkit-models/actions/workflows/tests.yml)
[![CI Status](https://github.com/beautifulmachines/gpkit-models/actions/workflows/lint.yml/badge.svg)](https://github.com/beautifulmachines/gpkit-models/actions/workflows/lint.yml)

This repository contains those GP-/SP-compatible models that we consider well documented and general enough to be useful to multiple projects.

* **Simple models with in-depth explanations** (good for learning GPkit)
  * [SimPleAC](https://github.com/beautifulmachines/gpkit-models/tree/main/gpkitmodels/SP/SimPleAC/): a basic aircraft model that captures the fundamental design tradeoffs
  * [Economic Order Quantity](https://github.com/beautifulmachines/gpkit-models/tree/main/gpkitmodels/misc/Economic%20Order%20Quantity/): tradeoff between setup and holding costs
  * [Cylindrical Beam Moment of Inertia](https://github.com/beautifulmachines/gpkit-models/tree/main/gpkitmodels/misc/Moment%20of%20Inertia%20(cylindrical%20beam)): GP approximation of cylindrical beam MOI
  * [Net Present Value](https://github.com/beautifulmachines/gpkit-models/tree/main/gpkitmodels/misc/Net%20Present%20Value): financial tradeoff between cash and equipment
  * [Raymer Weights](https://github.com/beautifulmachines/gpkit-models/tree/main/gpkitmodels/misc/Raymer%20Weights): rule-of-thumb weight relations for aircraft design
* **GP models**
  * Aircraft
    * [Wing Structural and Aero Models](https://github.com/beautifulmachines/gpkit-models/tree/main/gpkitmodels/GP/aircraft/wing)
    * [Empennage](https://github.com/beautifulmachines/gpkit-models/tree/main/gpkitmodels/GP/aircraft/tail): TailBoom, HorizontalTail, and VerticalTail inherit from the Wing model
    * [Mission](https://github.com/beautifulmachines/gpkit-models/tree/main/gpkitmodels/GP/aircraft/mission): models that unify subsystems and flight profiles
    * [Fuselage](https://github.com/beautifulmachines/gpkit-models/tree/main/gpkitmodels/GP/aircraft/fuselage): elliptical and cylindrical fuselage models
    * [IC Gas Engine Model](https://github.com/beautifulmachines/gpkit-models/tree/main/gpkitmodels/GP/aircraft/engine)
  * [Bending Beam](https://github.com/beautifulmachines/gpkit-models/tree/main/gpkitmodels/GP/beam): discretized beam for distributed loads
* **SP models**
  * Aircraft
    * [Tail Boom Flexibility](https://github.com/beautifulmachines/gpkit-models/tree/main/gpkitmodels/SP/aircraft/tail/tail_boom_flex.py)
    * [Wing Spanwise Effectiveness](https://github.com/beautifulmachines/gpkit-models/blob/main/gpkitmodels/SP/aircraft/wing/wing.py)
  * Atmosphere
    * [Tony Tao's fits as (efficient) signomial equalities](https://github.com/beautifulmachines/gpkit-models/blob/main/gpkitmodels/SP/atmosphere/atmosphere.py). Valid until 10,000m of altitude. 

## Releasing

Versions are derived automatically from git tags (via `hatch-vcs`) — there is no
`__version__` to hand-edit and no version-bump PR to remember. `gpkitmodels.__version__`
reflects whatever tag is checked out:

- On a commit exactly at tag `v0.2.0`, with no local changes: `0.2.0`.
- On any other commit: `0.2.1.devN+g<hash>`, where `N` is commits since the last tag.
- With uncommitted local changes: the version always carries a dev/dirty suffix, even
  if `HEAD` is itself tagged — so a clean `X.Y.Z` version only ever comes from a
  committed, exactly-tagged commit.

To cut a release:

```bash
make release V=0.2.0
```

or directly:

```bash
gh release create v0.2.0 --generate-notes
```

Publishing the release triggers `.github/workflows/publish.yml`, which builds the
package (version read straight from the new tag) and uploads it to PyPI.

Use plain `vMAJOR.MINOR.PATCH` tags. Bump PATCH for fixes, MINOR for backwards-compatible
additions, MAJOR for breaking changes.

