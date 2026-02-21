"""
Liquid Galaxy Integration API
Exports USPS data in KML format for immersive visualization
"""
from fastapi import APIRouter, Query, Response
from app.services.usps_engine import USPSEngine
from app.services.usps_data_generator import USPSDataGenerator
import xml.etree.ElementTree as ET

router = APIRouter(prefix="/api/liquid-galaxy", tags=["liquid-galaxy"])
usps_engine = USPSEngine()


@router.get("/usps-kml")
async def export_usps_kml(
    lat_min: float = Query(18.45),
    lat_max: float = Query(18.55),
    lon_min: float = Query(73.80),
    lon_max: float = Query(73.90)
):
    """Export USPS data as KML for Liquid Galaxy"""
    
    # Generate data
    generator = USPSDataGenerator()
    grid_cells = generator.generate_grid_with_usps_data(lat_min, lat_max, lon_min, lon_max, 1.0)
    results = usps_engine.calculate_grid_usps(grid_cells)
    
    # Create KML
    kml = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
    document = ET.SubElement(kml, 'Document')
    ET.SubElement(document, 'name').text = 'USPS Heatmap - Pune'
    
    # Add styles
    for level, color in [
        ('critical', 'ff0000dc'),
        ('severe', 'ff0b9ef5'),
        ('high', 'fff6823b'),
        ('moderate', 'ff81b910'),
        ('low', 'ff808080')
    ]:
        style = ET.SubElement(document, 'Style', id=level)
        poly_style = ET.SubElement(style, 'PolyStyle')
        ET.SubElement(poly_style, 'color').text = color
        ET.SubElement(poly_style, 'fill').text = '1'
        ET.SubElement(poly_style, 'outline').text = '1'
    
    # Add placemarks
    for cell in results:
        placemark = ET.SubElement(document, 'Placemark')
        ET.SubElement(placemark, 'name').text = f"Cell {cell['cell_id']}"
        
        description = f"""
        <![CDATA[
        <h3>USPS: {cell['usps_score']}</h3>
        <p><b>Level:</b> {cell['pressure_level']}</p>
        <p><b>Ward:</b> {cell['ward_name']}</p>
        <hr/>
        <p>🌧️ Rain: {cell['subsystem_pressures']['rain_accumulation']}%</p>
        <p>🌊 Drain: {cell['subsystem_pressures']['drain_capacity_load']}%</p>
        <p>🚗 Road: {cell['subsystem_pressures']['road_congestion']}%</p>
        <p>🏥 Hospital: {cell['subsystem_pressures']['hospital_occupancy']}%</p>
        <p>⚡ Power: {cell['subsystem_pressures']['power_stress']}%</p>
        ]]>
        """
        ET.SubElement(placemark, 'description').text = description
        
        style_level = cell['pressure_level'].lower()
        ET.SubElement(placemark, 'styleUrl').text = f'#{style_level}'
        
        # Create polygon
        polygon = ET.SubElement(placemark, 'Polygon')
        ET.SubElement(polygon, 'extrude').text = '1'
        ET.SubElement(polygon, 'altitudeMode').text = 'relativeToGround'
        outer = ET.SubElement(polygon, 'outerBoundaryIs')
        linear_ring = ET.SubElement(outer, 'LinearRing')
        
        # Calculate cell bounds
        cell_size = 0.009
        lat, lon = cell['latitude'], cell['longitude']
        coords = f"{lon-cell_size/2},{lat-cell_size/2},{cell['usps_score']*10} "
        coords += f"{lon+cell_size/2},{lat-cell_size/2},{cell['usps_score']*10} "
        coords += f"{lon+cell_size/2},{lat+cell_size/2},{cell['usps_score']*10} "
        coords += f"{lon-cell_size/2},{lat+cell_size/2},{cell['usps_score']*10} "
        coords += f"{lon-cell_size/2},{lat-cell_size/2},{cell['usps_score']*10}"
        
        ET.SubElement(linear_ring, 'coordinates').text = coords
    
    kml_str = ET.tostring(kml, encoding='unicode', method='xml')
    kml_str = '<?xml version="1.0" encoding="UTF-8"?>\n' + kml_str
    
    return Response(content=kml_str, media_type="application/vnd.google-earth.kml+xml",
                   headers={"Content-Disposition": "attachment; filename=usps_pune.kml"})
