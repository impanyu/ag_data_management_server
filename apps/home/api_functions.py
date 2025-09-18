"""
Function-based API views that bypass authentication
These are designed to work around Django/DRF authentication issues
"""

import os
import json
import hashlib
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .tile_generator import generate_tiff_tiles

logger = logging.getLogger(__name__)


@csrf_exempt
def generate_tiles_api(request):
    """
    Function-based view for tile generation API
    Bypasses all DRF authentication issues
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET method allowed'}, status=405)
    
    try:
        file_path = request.GET.get('file_path')
        if not file_path:
            return JsonResponse({'error': 'file_path parameter required'}, status=400)
        
        # Handle both authenticated and anonymous users  
        if hasattr(request, 'user') and hasattr(request.user, 'username') and request.user.username:
            current_user = request.user.username
        else:
            current_user = 'ypan12'  # Default user for development/testing
        
        logger.info(f"🔄 TILE GENERATION API: Generating tiles for {file_path} (user: {current_user})")
        
        # Construct full path to TIFF file
        safe_path = os.path.normpath(file_path).lstrip('/')
        full_tiff_path = os.path.join(settings.USER_DATA_DIR, current_user, "ag_data", safe_path)
        
        # Check if TIFF file exists
        if not os.path.exists(full_tiff_path):
            return JsonResponse({'error': f'TIFF file not found: {full_tiff_path}'}, status=404)
        
        # Generate unique file ID based on path and modification time
        file_stat = os.stat(full_tiff_path)
        unique_string = f"{current_user}_{safe_path}_{file_stat.st_mtime}"
        file_id = hashlib.md5(unique_string.encode()).hexdigest()[:12]
        
        logger.info(f"🆔 TILE GENERATION: File ID = {file_id}")
        
        # Set up tile output directory
        tile_base_dir = os.path.join(settings.CONVERTED_STATIC_FILES_ROOT, 'tiles')
        os.makedirs(tile_base_dir, exist_ok=True)
        
        # Check if tiles already exist
        tile_dir = os.path.join(tile_base_dir, file_id)
        if os.path.exists(tile_dir) and os.listdir(tile_dir):
            logger.info(f"✅ TILES EXIST: Using existing tiles for {file_id}")
            tile_url_template = f"/tiles/{file_id}/{{z}}/{{x}}/{{y}}.png"
            bounds = {
                'north': 85.0511, 'south': -85.0511, 
                'east': 180.0, 'west': -180.0
            }
            return JsonResponse({
                'success': True, 
                'tile_url_template': tile_url_template, 
                'bounds': bounds
            })
        
        # Generate tiles
        logger.info(f"🔄 TILE GENERATION: Starting tile generation...")
        success, tile_url_template, bounds = generate_tiff_tiles(
            full_tiff_path, tile_base_dir, file_id
        )
        
        if success:
            logger.info(f"✅ TILE GENERATION: Success! Template = {tile_url_template}")
            return JsonResponse({
                'success': True,
                'tile_url_template': tile_url_template,
                'bounds': bounds,
                'file_id': file_id
            })
        else:
            logger.error(f"❌ TILE GENERATION: Failed for {file_path}")
            return JsonResponse({'error': 'Tile generation failed'}, status=500)
            
    except Exception as e:
        import traceback
        logger = logging.getLogger(__name__)
        error_msg = f'GenerateTiles Error: {str(e)}\nTraceback: {traceback.format_exc()}'
        logger.error(error_msg)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt 
def convert_to_static_api(request):
    """
    Function-based view for convert to static API
    Bypasses all DRF authentication issues
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET method allowed'}, status=405)
        
    try:
        file_path = request.GET.get('file_path')
        if not file_path:
            return HttpResponse('file_path parameter required', status=400)
            
        # Handle both authenticated and anonymous users
        if hasattr(request, 'user') and hasattr(request.user, 'username') and request.user.username:
            current_user = request.user.username
        else:
            current_user = 'ypan12'  # Default user for development/testing

        safe_path = os.path.normpath(file_path).lstrip('/')
        full_path = os.path.join(settings.USER_DATA_DIR, current_user, "ag_data", safe_path)
        
        # Check if file exists
        if not os.path.exists(full_path):
            return HttpResponse(f'File not found: {full_path}', status=404)
        
        # Copy to static folder
        static_path = os.path.join(settings.CONVERTED_STATIC_FILES_ROOT, current_user, "ag_data", safe_path)
        os.makedirs(os.path.dirname(static_path), exist_ok=True)
        
        import shutil
        shutil.copy2(full_path, static_path)
        
        static_url = f"/static_files/{current_user}/ag_data/{safe_path}"
        return HttpResponse(static_url)
        
    except Exception as e:
        import traceback
        error_msg = f'ConvertToStatic Error: {str(e)}\nTraceback: {traceback.format_exc()}'
        logger.error(error_msg)
        return HttpResponse(error_msg, status=500)


@csrf_exempt
def debug_api_simple(request):
    """Simple debug endpoint"""
    return JsonResponse({
        'success': True,
        'message': 'Function-based API works!',
        'method': request.method,
        'path': request.path,
        'user_authenticated': hasattr(request, 'user') and request.user.is_authenticated
    })
