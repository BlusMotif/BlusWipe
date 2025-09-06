import json
import sys
from datetime import datetime

def handler(event, context):
    """
    Health check endpoint for Netlify function.
    """
    try:
        health_info = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'BlusWipe Background Remover',
            'version': '2.0.0',
            'developer': 'Eleblu Nunana',
            'python_version': sys.version,
            'environment': 'netlify-functions'
        }
        
        # Test critical imports
        try:
            import rembg
            health_info['rembg_available'] = True
        except ImportError as e:
            health_info['rembg_available'] = False
            health_info['rembg_error'] = str(e)
        
        try:
            from PIL import Image
            health_info['pillow_available'] = True
        except ImportError as e:
            health_info['pillow_available'] = False
            health_info['pillow_error'] = str(e)
        
        try:
            from background_remover import BackgroundRemover
            health_info['background_remover_available'] = True
        except ImportError as e:
            health_info['background_remover_available'] = False
            health_info['background_remover_error'] = str(e)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(health_info, indent=2)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'status': 'error',
                'error': str(e),
                'service': 'BlusWipe Background Remover'
            })
        }

# For Netlify Functions
def lambda_handler(event, context):
    return handler(event, context)
