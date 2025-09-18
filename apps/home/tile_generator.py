"""
TIFF to XYZ Tile Generator
Converts geospatial TIFF files to XYZ tile sets for web mapping
"""

import os
import math
import shutil
from PIL import Image
import subprocess
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class TiffTileGenerator:
    """Generate XYZ tiles from TIFF files using GDAL and PIL"""
    
    def __init__(self, tiff_path, output_dir, max_zoom=18, min_zoom=0):
        self.tiff_path = tiff_path
        self.output_dir = output_dir
        self.max_zoom = max_zoom
        self.min_zoom = min_zoom
        self.tile_size = 256
        
    def generate_tiles(self):
        """
        Generate XYZ tiles from TIFF file
        Returns: (success: bool, tile_dir: str, bounds: dict)
        """
        try:
            logger.info(f"🔄 TILE GENERATION: Starting tile generation for {self.tiff_path}")
            
            # Ensure output directory exists
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Step 1: Check if GDAL is available
            if not self._check_gdal():
                logger.warning("⚠️ GDAL not available, using basic PIL approach")
                return self._generate_tiles_pil()
            
            # Step 2: Use GDAL to generate tiles (preferred method)
            return self._generate_tiles_gdal()
            
        except Exception as e:
            logger.error(f"❌ TILE GENERATION: Error generating tiles: {str(e)}")
            return False, None, None
    
    def _check_gdal(self):
        """Check if GDAL utilities are available"""
        try:
            result = subprocess.run(['gdal_translate', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _generate_tiles_gdal(self):
        """Generate tiles using GDAL (preferred method for georeferenced data)"""
        try:
            logger.info("🗺️ TILE GENERATION: Using GDAL for georeferenced tile generation")
            
            # Create temporary Web Mercator version
            temp_mercator = os.path.join(self.output_dir, 'temp_mercator.tif')
            
            # Reproject to Web Mercator (EPSG:3857) if needed
            reproject_cmd = [
                'gdalwarp',
                '-t_srs', 'EPSG:3857',
                '-r', 'bilinear',
                '-of', 'GTiff',
                self.tiff_path,
                temp_mercator
            ]
            
            logger.info(f"🔄 REPROJECTION: {' '.join(reproject_cmd)}")
            result = subprocess.run(reproject_cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                logger.error(f"❌ REPROJECTION FAILED: {result.stderr}")
                # Fall back to PIL method
                return self._generate_tiles_pil()
            
            # Generate tiles using gdal2tiles
            tiles_cmd = [
                'gdal2tiles.py',
                '-z', f'{self.min_zoom}-{self.max_zoom}',
                '-w', 'none',  # No web viewer
                '--processes=4',  # Use multiple processes
                temp_mercator,
                self.output_dir
            ]
            
            logger.info(f"🔄 TILE GENERATION: {' '.join(tiles_cmd)}")
            result = subprocess.run(tiles_cmd, capture_output=True, text=True, timeout=300)
            
            # Clean up temporary file
            if os.path.exists(temp_mercator):
                os.remove(temp_mercator)
            
            if result.returncode != 0:
                logger.error(f"❌ TILE GENERATION FAILED: {result.stderr}")
                return self._generate_tiles_pil()
            
            # Get bounds from the generated tilemapresource.xml or estimate
            bounds = self._extract_bounds_from_tiles()
            
            logger.info("✅ TILE GENERATION: GDAL tiles generated successfully")
            return True, self.output_dir, bounds
            
        except Exception as e:
            logger.error(f"❌ GDAL TILE GENERATION: {str(e)}")
            return self._generate_tiles_pil()
    
    def _generate_tiles_pil(self):
        """Fallback: Generate tiles using PIL (for non-georeferenced display)"""
        try:
            logger.info("🖼️ TILE GENERATION: Using PIL fallback for image tiles")
            
            # Open the TIFF image
            with Image.open(self.tiff_path) as img:
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                width, height = img.size
                logger.info(f"📐 IMAGE SIZE: {width}x{height}")
                
                # Calculate zoom levels based on image size
                max_dimension = max(width, height)
                actual_max_zoom = min(self.max_zoom, math.ceil(math.log2(max_dimension / self.tile_size)))
                
                logger.info(f"🔍 ZOOM RANGE: 0 to {actual_max_zoom}")
                
                # Generate tiles for each zoom level
                for zoom in range(actual_max_zoom + 1):
                    self._generate_zoom_level_pil(img, zoom, actual_max_zoom)
                
                # Create bounds (approximate for non-georeferenced)
                bounds = {
                    'north': 85.0511,
                    'south': -85.0511,
                    'east': 180.0,
                    'west': -180.0
                }
                
                logger.info("✅ TILE GENERATION: PIL tiles generated successfully")
                return True, self.output_dir, bounds
                
        except Exception as e:
            logger.error(f"❌ PIL TILE GENERATION: {str(e)}")
            return False, None, None
    
    def _generate_zoom_level_pil(self, img, zoom, max_zoom):
        """Generate tiles for a specific zoom level using PIL"""
        try:
            # Calculate scale factor
            scale = 2 ** (max_zoom - zoom)
            scaled_width = img.width // scale
            scaled_height = img.height // scale
            
            if scaled_width < self.tile_size and scaled_height < self.tile_size:
                # Image is smaller than tile size, create single tile
                zoom_dir = os.path.join(self.output_dir, str(zoom), '0')
                os.makedirs(zoom_dir, exist_ok=True)
                
                # Resize image to fit in tile
                resized = img.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
                
                # Create tile with padding if needed
                tile = Image.new('RGB', (self.tile_size, self.tile_size), (255, 255, 255))
                offset_x = (self.tile_size - scaled_width) // 2
                offset_y = (self.tile_size - scaled_height) // 2
                tile.paste(resized, (offset_x, offset_y))
                
                tile_path = os.path.join(zoom_dir, '0.png')
                tile.save(tile_path, 'PNG')
                
            else:
                # Scale image for this zoom level
                scaled_img = img.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
                
                # Calculate number of tiles needed
                tiles_x = math.ceil(scaled_width / self.tile_size)
                tiles_y = math.ceil(scaled_height / self.tile_size)
                
                logger.info(f"🧩 ZOOM {zoom}: Generating {tiles_x}x{tiles_y} tiles")
                
                # Generate tiles
                for y in range(tiles_y):
                    y_dir = os.path.join(self.output_dir, str(zoom), str(y))
                    os.makedirs(y_dir, exist_ok=True)
                    
                    for x in range(tiles_x):
                        # Calculate tile bounds
                        left = x * self.tile_size
                        top = y * self.tile_size
                        right = min(left + self.tile_size, scaled_width)
                        bottom = min(top + self.tile_size, scaled_height)
                        
                        # Extract tile
                        tile_img = scaled_img.crop((left, top, right, bottom))
                        
                        # Pad tile if necessary
                        if tile_img.size != (self.tile_size, self.tile_size):
                            padded_tile = Image.new('RGB', (self.tile_size, self.tile_size), (255, 255, 255))
                            padded_tile.paste(tile_img, (0, 0))
                            tile_img = padded_tile
                        
                        # Save tile
                        tile_path = os.path.join(y_dir, f'{x}.png')
                        tile_img.save(tile_path, 'PNG')
                        
        except Exception as e:
            logger.error(f"❌ ZOOM LEVEL {zoom}: Error generating tiles: {str(e)}")
    
    def _extract_bounds_from_tiles(self):
        """Extract bounds from generated tiles or estimate"""
        try:
            # Look for tilemapresource.xml or googlemaps.html
            xml_path = os.path.join(self.output_dir, 'tilemapresource.xml')
            if os.path.exists(xml_path):
                # Parse XML to extract bounds
                # This is a simplified version - could be enhanced
                return {
                    'north': 85.0511,
                    'south': -85.0511,
                    'east': 180.0,
                    'west': -180.0
                }
            
            # Default bounds (Web Mercator extent)
            return {
                'north': 85.0511,
                'south': -85.0511,
                'east': 180.0,
                'west': -180.0
            }
            
        except Exception as e:
            logger.warning(f"⚠️ BOUNDS EXTRACTION: Could not extract bounds: {str(e)}")
            return {
                'north': 85.0511,
                'south': -85.0511,
                'east': 180.0,
                'west': -180.0
            }


def generate_tiff_tiles(tiff_path, output_base_dir, file_id):
    """
    Convenience function to generate tiles for a TIFF file
    
    Args:
        tiff_path: Path to the TIFF file
        output_base_dir: Base directory for tile output
        file_id: Unique identifier for this file's tiles
    
    Returns:
        (success: bool, tile_url_template: str, bounds: dict)
    """
    try:
        # Create unique output directory for this file
        tile_dir = os.path.join(output_base_dir, file_id)
        
        # Generate tiles
        generator = TiffTileGenerator(tiff_path, tile_dir, max_zoom=15, min_zoom=0)
        success, tiles_path, bounds = generator.generate_tiles()
        
        if success:
            # Create URL template for Django tile serving
            tile_url_template = f"/tiles/{file_id}/{{z}}/{{x}}/{{y}}.png"
            return True, tile_url_template, bounds
        else:
            return False, None, None
            
    except Exception as e:
        logger.error(f"❌ TILE GENERATION WRAPPER: {str(e)}")
        return False, None, None
