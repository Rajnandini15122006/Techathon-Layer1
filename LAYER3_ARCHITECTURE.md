# 🏗️ Layer 3 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         LAYER 3: HRVC RISK ENGINE                    │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          INPUT (Layer 1 Data)                        │
├─────────────────────────────────────────────────────────────────────┤
│  Grid Cell Attributes (11,377 cells × 8 attributes)                 │
│  ├── elevation_mean          (terrain height)                       │
│  ├── drain_distance          (proximity to water)                   │
│  ├── flood_depth_avg         (historical flooding)                  │
│  ├── population_density      (people per m²)                        │
│  ├── slum_density           (vulnerable settlements %)              │
│  ├── land_use               (urban/residential/etc)                 │
│  ├── infra_count            (hospitals, shelters)                   │
│  └── complaint_density      (historical complaints)                 │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    RISK COMPUTATION ENGINE                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────┐  ┌────────────────────┐  ┌───────────────┐ │
│  │   HAZARD SCORE     │  │ VULNERABILITY SCORE│  │ CAPACITY SCORE│ │
│  │      (H)           │  │        (V)         │  │      (C)      │ │
│  ├────────────────────┤  ├────────────────────┤  ├───────────────┤ │
│  │ • Flood depth 40%  │  │ • Population  50%  │  │ • Infra   60% │ │
│  │ • Elevation   30%  │  │ • Slums       40%  │  │ • Response 40%│ │
│  │ • Drainage    30%  │  │ • Land use    10%  │  │               │ │
│  └────────────────────┘  └────────────────────┘  └───────────────┘ │
│           ↓                       ↓                      ↓          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              RISK FORMULA: (H × V) / C                       │  │
│  │              Normalized to 0-100 scale                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                ↓                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              RISK CATEGORIZATION                             │  │
│  │  • Low (0-25)      🟢 Green                                  │  │
│  │  • Medium (25-50)  🟠 Orange                                 │  │
│  │  • High (50-75)    🔴 Red                                    │  │
│  │  • Critical (75+)  🔴 Dark Red                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    OUTPUT (Database + API)                           │
├─────────────────────────────────────────────────────────────────────┤
│  Updated Grid Cells with Risk Scores:                               │
│  ├── hazard_score          (0-100)                                  │
│  ├── vulnerability_score   (0-100)                                  │
│  ├── capacity_score        (0-100)                                  │
│  ├── risk_score           (0-100)                                   │
│  └── risk_level           (Low/Medium/High/Critical)                │
│                                                                      │
│  API Endpoints:                                                      │
│  ├── POST /risk/compute-hrvc        (compute all scores)            │
│  └── GET  /risk/high-risk-cells     (query high-risk areas)         │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    VISUALIZATION (Web UI)                            │
├─────────────────────────────────────────────────────────────────────┤
│  Interactive Map:                                                    │
│  ├── Color-coded cells by risk score                                │
│  ├── Click for detailed breakdown                                   │
│  ├── H/V/C component display                                        │
│  └── Risk level legend                                              │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    NEXT LAYERS (Future)                              │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 4: Resource Prepositioning                                   │
│  └── Use risk_score to prioritize resource allocation               │
│                                                                      │
│  Layer 5: Alert Scheduling                                          │
│  └── Monitor high-risk areas for real-time alerts                   │
│                                                                      │
│  Layer 6: Risk Memory & Evolution                                   │
│  └── Track risk changes over time                                   │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
1. Layer 1 Grid Data
   ↓
2. Normalize attributes (0-100)
   ↓
3. Compute H, V, C scores
   ↓
4. Calculate Risk = (H × V) / C
   ↓
5. Assign risk level
   ↓
6. Save to database
   ↓
7. Serve via API
   ↓
8. Visualize on map
```

## Component Breakdown

### Hazard Score (H)
```
Input:
├── flood_depth_avg    → Higher depth = Higher hazard
├── elevation_mean     → Lower elevation = Higher hazard
└── drain_distance     → Closer to drain = Higher hazard

Output: 0-100 (normalized)
```

### Vulnerability Score (V)
```
Input:
├── population_density → More people = Higher vulnerability
├── slum_density      → More slums = Higher vulnerability
└── land_use          → Residential > Commercial > Others

Output: 0-100 (normalized)
```

### Capacity Score (C)
```
Input:
├── infra_count        → More infrastructure = Higher capacity
└── complaint_density  → More complaints = Lower capacity

Output: 0-100 (normalized, min 10)
```

## Example Calculation

```
Cell #5432:
├── flood_depth_avg = 2.1m      → Hazard component
├── elevation_mean = 545m       → Hazard component
├── drain_distance = 450m       → Hazard component
├── population_density = 0.012  → Vulnerability component
├── slum_density = 8.5%         → Vulnerability component
├── land_use = Residential      → Vulnerability component
├── infra_count = 1             → Capacity component
└── complaint_density = 12.3    → Capacity component

Computation:
├── H = 72.5  (high flood depth, low elevation, close to drain)
├── V = 68.3  (high population, moderate slums, residential)
├── C = 35.2  (low infrastructure, high complaints)
└── Risk = (72.5 × 68.3) / 35.2 = 140.6 → capped at 100

Result:
├── risk_score = 100.0
└── risk_level = Critical 🔴
```

## Performance Metrics

```
Processing:
├── Total cells: 11,377
├── Computation time: ~3 seconds
├── Database updates: Bulk commit
└── Memory usage: < 100MB

API Response:
├── /risk/compute-hrvc: ~3s
├── /risk/high-risk-cells: < 100ms
└── Map rendering: < 500ms
```

## Integration Architecture

```
┌──────────────┐
│   Layer 1    │  Grid Foundation (✅ Complete)
│  Grid Data   │  └── 8 spatial attributes
└──────┬───────┘
       │
       ↓
┌──────────────┐
│   Layer 3    │  HRVC Risk Engine (✅ Complete)
│ Risk Scoring │  └── H × V / C computation
└──────┬───────┘
       │
       ↓
┌──────────────┐
│   Layer 4    │  Resource Prepositioning (🔄 Next)
│  Resources   │  └── Use risk scores
└──────┬───────┘
       │
       ↓
┌──────────────┐
│   Layer 5    │  Alert Scheduling (🔄 Future)
│   Alerts     │  └── Monitor high-risk
└──────────────┘
```
