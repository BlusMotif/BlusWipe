import json
import base64
import io
from background_remover import BackgroundRemover
from PIL import Image

# Global background remover instance
background_remover = None

def init_background_remover():
    """Initialize the background remover if not already done."""
    global background_remover
    if background_remover is None:
        print("🚀 Initializing BlusWipe background remover...")
        background_remover = BackgroundRemover(model_name="u2net")
        print("✅ Background remover ready!")
    return background_remover

def handler(event, context):
    """
    Netlify function handler for background removal.
    Expects multipart/form-data with file upload.
    """
    try:
        print(f"🎨 Function called with method: {event.get('httpMethod')}")
        
        # Handle CORS preflight
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        }
        
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }
        
        # Only handle POST requests
        if event['httpMethod'] != 'POST':
            return {
                'statusCode': 405,
                'headers': headers,
                'body': json.dumps({'error': 'Method not allowed'})
            }
        
        # Initialize background remover
        print("🔧 Initializing background remover...")
        remover = init_background_remover()
        
        # Parse request body (assuming base64 encoded multipart data)
        body = event.get('body', '')
        if event.get('isBase64Encoded', False):
            body = base64.b64decode(body)
        
        # Simple approach: look for image data in the body
        # This is a simplified multipart parser
        if isinstance(body, str):
            body = body.encode('utf-8')
            
        # Find image content in multipart data
        # Look for common image headers
        image_data = None
        
        if b'Content-Type: image/' in body:
            # Find the start of actual image data
            data_start = body.find(b'\r\n\r\n')
            if data_start != -1:
                data_start += 4
                # Find the end (next boundary)
                data_end = body.find(b'\r\n--', data_start)
                if data_end != -1:
                    image_data = body[data_start:data_end]
        
        if image_data is None:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'No valid image data found'})
            }
        
        # Process the image
        print("🖼️ Processing image...")
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            print(f"📏 Image size: {image.size}")
            
            # Remove background
            result_image = remover.remove_background(image)
            print("✅ Background removal completed")
            
            # Convert result to bytes
            output_buffer = io.BytesIO()
            result_image.save(output_buffer, format='PNG', optimize=True)
            result_bytes = output_buffer.getvalue()
            
            # Return as binary data
            return {
                'statusCode': 200,
                'headers': {
                    **headers,
                    'Content-Type': 'image/png',
                    'Content-Length': str(len(result_bytes))
                },
                'body': base64.b64encode(result_bytes).decode('utf-8'),
                'isBase64Encoded': True
            }
            
        except Exception as e:
            print(f"❌ Error processing image: {str(e)}")
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'error': f'Image processing failed: {str(e)}'})
            }
        
    except Exception as e:
        print(f"❌ Function error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': f'Server error: {str(e)}'})
        }
