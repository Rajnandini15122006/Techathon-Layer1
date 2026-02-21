# Liquid Galaxy Integration Guide

## Overview

PuneRakshak now supports Liquid Galaxy for immersive 3D visualization of USPS data!

## What is Liquid Galaxy?

Liquid Galaxy is an immersive visualization platform using multiple synchronized displays to create panoramic Google Earth experiences. Perfect for command centers and emergency operations.

## Features

- 3D visualization of USPS pressure scores
- Height-based representation (higher = more pressure)
- Color-coded risk levels
- Interactive cell information
- Real-time data export

## Quick Start

### 1. Export KML Data

```bash
curl "http://localhost:8000/api/liquid-galaxy/usps-kml?lat_min=18.45&lat_max=18.55&lon_min=73.80&lon_max=73.90" -o usps_pune.kml
```

### 2. Load in Google Earth

1. Open Google Earth Pro
2. File → Open → Select `usps_pune.kml`
3. Navigate to Pune, India
4. View 3D pressure visualization

### 3. Deploy to Liquid Galaxy

1. Copy KML to Liquid Galaxy master node
2. Use Liquid Galaxy control panel to load KML
3. Enjoy immersive visualization across multiple screens

## KML Features

- **3D Extrusion**: Cell height represents USPS score
- **Color Coding**: 
  - Red: Critical (90-100)
  - Orange: Severe (75-89)
  - Blue: High (60-74)
  - Green: Moderate (40-59)
  - Gray: Low (0-39)
- **Interactive Popups**: Click cells for detailed info
- **Real-time Updates**: Re-export KML for latest data

## API Endpoint

```
GET /api/liquid-galaxy/usps-kml
```

Parameters:
- `lat_min`, `lat_max`: Latitude bounds
- `lon_min`, `lon_max`: Longitude bounds

Returns: KML file for Google Earth/Liquid Galaxy

## Use Cases

1. **Emergency Operations Center**: Display on Liquid Galaxy for command decisions
2. **Public Demonstrations**: Immersive visualization for stakeholders
3. **Training**: Simulate disaster scenarios in 3D
4. **Presentations**: Impressive visualization for judges/officials

## Liquid Galaxy Setup

### Hardware Requirements
- 3-7 displays
- Master computer + slave computers
- Network switch
- Google Earth Pro on all machines

### Software Setup
1. Install Liquid Galaxy software
2. Configure master/slave relationship
3. Sync displays
4. Load KML from master

### Resources
- Liquid Galaxy Project: https://www.liquidgalaxy.eu/
- Setup Guide: https://github.com/LiquidGalaxyLAB

## Integration with PuneRakshak

The heatmap automatically updates every refresh. To keep Liquid Galaxy synchronized:

1. Set up automated KML export (cron job)
2. Configure Liquid Galaxy to auto-reload KML
3. Real-time visualization of system pressure

## Demo Script

```bash
# Export current USPS data
curl "http://localhost:8000/api/liquid-galaxy/usps-kml" -o usps_current.kml

# Open in Google Earth
google-earth-pro usps_current.kml

# Or deploy to Liquid Galaxy
scp usps_current.kml lg@liquidgalaxy:/var/www/html/
```

## Benefits for Judges

- **Impressive Visualization**: 3D immersive display
- **Scalability**: Works on single screen or Liquid Galaxy
- **Innovation**: Cutting-edge visualization technology
- **Practical**: Real command center deployment ready

Your USPS innovation now has world-class visualization! 🚀
