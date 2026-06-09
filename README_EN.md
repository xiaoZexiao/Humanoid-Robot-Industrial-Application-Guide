# Humanoid Robot Industrial Application Guide

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

An open-source implementation guide for humanoid robot industrial applications. This project systematically organizes industrial scenarios and standardized primitive action taxonomies, providing comprehensive reference solutions from technology selection to deployment.

---

## Project Statistics

| Metric | Count | Description |
|--------|-------|-------------|
| Industrial Scenarios | 973 | Covering 41 major industrial categories |
| L1 Action Categories | 9 | Locomotion, posture, manipulation, etc. |
| L2 Action Subcategories | 65 | Walking, bending, precision grasping, etc. |
| L3 Action Instances | 122+ | Continuously expanding |
| Scene Building Guides | 34 | Completed, continuously expanding |

---

## Quick Navigation

| Your Role | Question | Go To |
|-----------|----------|-------|
| Robot Company Executive | Which scenarios are easiest to deploy? | [analysis/quick-win-scenes.md](analysis/quick-win-scenes.md) |
| Data Collection Team | Which actions should we prioritize? | [analysis/high-reuse-actions.md](analysis/high-reuse-actions.md) |
| Manufacturing Enterprise | What scenarios exist in my industry? | [scenes/](scenes/) |
| Algorithm Researcher | How are primitive actions classified? | [framework/action-taxonomy.md](framework/action-taxonomy.md) |
| System Integrator | How is implementation difficulty assessed? | [analysis/difficulty-ranking.md](analysis/difficulty-ranking.md) |

---

## Directory Structure

```
├── framework/                  # Classification Framework
│   ├── scene-taxonomy.md       # Scene classification system
│   ├── action-taxonomy.md      # Primitive action taxonomy
│   └── field-definitions.md    # Standard field definitions
│
├── scenes/                     # Scene Building Guides (by industry)
│   ├── automotive/
│   ├── electronics-3c/
│   └── ...
│
├── actions/                    # Primitive Action Library
│   ├── action-library.json     # Complete library (machine-readable)
│   ├── action-overview.md      # Overview and statistics
│   └── by-category/            # L3 actions by scene
│
├── analysis/                   # Analysis & Insights
│   ├── quick-win-scenes.md     # Quick-win scenario recommendations
│   ├── high-reuse-actions.md   # High-reuse action analysis
│   └── difficulty-ranking.md   # Scenario difficulty ranking
│
├── data/                       # Structured Data
│   ├── scene-matrix-work.csv   # Scene classification matrix
│   └── statistics.json         # Project statistics
│
└── docs/                       # Additional Documentation
    ├── methodology.md          # Research methodology
    └── references.md           # References and standards
```

---

## Core Concepts

### Primitive Action Taxonomy

Three-level hierarchical structure:

- **L1 Categories (9)**: Based on kinematic essence - locomotion, grasping, rotation, etc.
- **L2 Subcategories (65)**: Based on operational characteristics - level walking, precision pinch, axis rotation, etc.
- **L3 Instances**: Atomic actions from specific scenarios with parameter ranges and constraints

### Scenario Assessment Dimensions

Each scenario is evaluated across seven dimensions:

1. **Labor Replacement Urgency**: Pain points of current manual operation
2. **Scale Potential**: Number of replicable workstations
3. **Superhuman Value**: Additional value robots can provide
4. **Operation Complexity**: Precision, force control, contact state requirements
5. **Structure Level**: Environmental predictability
6. **Fault Tolerance**: Consequences of single failure
7. **Takt Pressure**: Output speed requirements

---

## Data Formats

### Scene Data (CSV)

```csv
scene_name_zh,scene_name_en,industry_code,process_step,scores...
搬运码垛-精矿成品-25kg袋装,Palletizing-ConcentrateProduct-25kgBagged,09-91-00,...
```

### Primitive Action Data (JSON)

```json
{
  "l3_id": "L3-04-01-001",
  "l3_name_zh": "抓取-袋装物料-双手对握",
  "l3_name_en": "Grasp-BaggedMaterial-TwoHandSymmetric",
  "parent_l2_id": "L2-04-01",
  "description": "Symmetric two-hand grasping of bagged materials from both sides",
  "parameter_ranges": {
    "weight_range": "20-30kg",
    "size_range": "400x300x200mm"
  }
}
```

---

## Contributing

We welcome contributions in the following areas:

- **Practical Experience**: Real-world problems and solutions from actual projects
- **Parameter Calibration**: Corrections based on measured data
- **New Scenarios**: Additional industrial scenarios not yet covered
- **Action Extensions**: Expanding L3 primitive action definitions

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## License

This project is licensed under [CC BY-SA 4.0](LICENSE).

You are free to share and adapt this work, provided you:
- **Attribute**: Give appropriate credit
- **ShareAlike**: Distribute derivatives under the same license

---

## Contact

For questions or suggestions, please submit an Issue or Pull Request.
