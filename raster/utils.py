import os
import json
import numpy as np
import rasterio
from shapely.geometry import shape, mapping
from rasterio.features import shapes
from rasterio.warp import transform_geom
from django.conf import settings

def classify_and_vectorize_raster(file_path):
    with rasterio.open(file_path) as src:
        raster = src.read(1)
        profile = src.profile  # Get the raster profile for metadata
        transform = src.transform

        # Mask out pixels below or equal to 0 meters
        raster = np.where(raster <= 0, np.nan, raster)

        # Example classification (adjust as per your classification logic)
        shallow_threshold = 0.5
        moderate_threshold = 1.5
        deep_threshold = 3.0

        # Create an empty mask with the same shape as the raster
        classification = np.zeros_like(raster, dtype=np.uint8)

        # Assign classification values based on flood depth thresholds
        classification[raster > deep_threshold] = 3  # Deep flood zones
        classification[(raster > moderate_threshold) & (raster <= deep_threshold)] = 2  # Moderate risk zones
        classification[(raster > shallow_threshold) & (raster <= moderate_threshold)] = 1  # Low risk zones
        classification[np.isnan(raster)] = 0  # No flood zone for NaN values

        # Define classification mapping
        class_mapping = {
            1: 'shallow',
            2: 'moderate',
            3: 'deep'
        }

        # Extract polygons for each class
        geometries = []
        for class_value, class_name in class_mapping.items():
            mask = classification == class_value
            shapes_generator = shapes(mask.astype(np.int16), mask=mask, transform=transform)
            
            for geom, val in shapes_generator:
                geom_transformed = transform_geom(src.crs, 'EPSG:4326', geom)
                geometries.append({
                    'type': 'Feature',
                    'geometry': geom_transformed,
                    'properties': {
                        'classification': class_name
                    }
                })

    min_value = np.nanmin(raster)
    max_value = np.nanmax(raster)
    
    return geometries, profile, min_value, max_value

def save_vector_data(geometries, profile):
    vector_dir = os.path.join(settings.MEDIA_ROOT, 'vector_data')
    os.makedirs(vector_dir, exist_ok=True)

    output_path = os.path.join(vector_dir, 'classified_zones.geojson')
    with open(output_path, 'w') as f:
        geojson = {
            'type': 'FeatureCollection',
            'features': geometries
        }
        json.dump(geojson, f)

    relative_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
    return relative_path