# XYZ Tile serving for TIFF files
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse, Http404, HttpResponse
from django.conf import settings
import os


@csrf_exempt
def serve_tiles(request, file_id, z, x, y):
    """
    Serve XYZ tiles for TIFF files with CORS headers
    URL pattern: /tiles/{file_id}/{z}/{x}/{y}.png
    """
    try:
        # Construct tile path
        tile_path = os.path.join(settings.CONVERTED_STATIC_FILES_ROOT, 'tiles', file_id, str(z), str(x), f'{y}.png')
        
        # Security check
        if not os.path.commonpath([tile_path, settings.CONVERTED_STATIC_FILES_ROOT]) == settings.CONVERTED_STATIC_FILES_ROOT:
            raise Http404("Invalid tile path")
        
        # Check if tile exists
        if not os.path.exists(tile_path):
            # Return empty/transparent tile for missing tiles
            from PIL import Image
            import io
            
            # Create transparent tile
            tile = Image.new('RGBA', (256, 256), (255, 255, 255, 0))
            buffer = io.BytesIO()
            tile.save(buffer, format='PNG')
            buffer.seek(0)
            
            response = HttpResponse(buffer.getvalue(), content_type='image/png')
        else:
            # Serve existing tile
            response = FileResponse(
                open(tile_path, 'rb'),
                content_type='image/png'
            )
        
        # Add CORS headers for ArcGIS Online
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Accept, Accept-Language, Content-Language, Content-Type'
        response['Access-Control-Max-Age'] = '86400'
        response['Cache-Control'] = 'public, max-age=3600'  # Cache tiles for 1 hour
        
        return response
        
    except Exception as e:
        # Return error tile
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        tile = Image.new('RGB', (256, 256), (240, 240, 240))
        draw = ImageDraw.Draw(tile)
        
        try:
            # Try to use default font
            font = ImageFont.load_default()
        except:
            font = None
        
        # Draw error message
        draw.text((10, 120), f"Tile Error\n{z}/{x}/{y}", fill=(200, 0, 0), font=font)
        
        buffer = io.BytesIO()
        tile.save(buffer, format='PNG')
        buffer.seek(0)
        
        response = HttpResponse(buffer.getvalue(), content_type='image/png')
        response['Access-Control-Allow-Origin'] = '*'
        response['Cache-Control'] = 'public, max-age=60'  # Short cache for error tiles
        
        return response
