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

def parse_multipart_form_data(body, boundary):
    """Parse multipart form data to extract file content."""
    try:
        if isinstance(body, str):
            body = body.encode('utf-8')
        
        # Split by boundary
        parts = body.split(f'--{boundary}'.encode())
        
        for part in parts:
            if b'Content-Type:' in part and b'filename=' in part:
                # Find the start of file data (after headers)
                header_end = part.find(b'\r\n\r\n')
                if header_end != -1:
                    file_data = part[header_end + 4:]
                    # Remove trailing boundary markers
                    if file_data.endswith(b'\r\n'):
                        file_data = file_data[:-2]
                    return file_data
        return None
    except Exception as e:
        print(f"❌ Error parsing multipart data: {str(e)}")
        return None

def handler(event, context):
    """
    Netlify function handler for background removal.
    Expects multipart/form-data with file upload.
    """
    try:
        print(f"🎨 Function called with method: {event.get('httpMethod')}")
        print(f"📋 Headers: {json.dumps(event.get('headers', {}), indent=2)}")
        
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
        
        # Get request body
        body = event.get('body', '')
        is_base64 = event.get('isBase64Encoded', False)
        
        if is_base64:
            try:
                body = base64.b64decode(body)
                print("✅ Decoded base64 body")
            except Exception as e:
                print(f"❌ Error decoding base64: {str(e)}")
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'Invalid base64 encoding'})
                }
        
        # Get content type and boundary
        content_type = event.get('headers', {}).get('content-type', '')
        print(f"📋 Content-Type: {content_type}")
        
        image_data = None
        
        if 'multipart/form-data' in content_type:
            # Extract boundary
            boundary_match = content_type.split('boundary=')
            if len(boundary_match) > 1:
                boundary = boundary_match[1].strip()
                print(f"🔍 Found boundary: {boundary}")
                image_data = parse_multipart_form_data(body, boundary)
            else:
                print("❌ No boundary found in content-type")
        else:
            # Try to handle as raw image data
            if isinstance(body, str):
                body = body.encode('utf-8')
            
            # Check if it's a common image format
            if body.startswith(b'\xff\xd8\xff') or body.startswith(b'\x89PNG') or body.startswith(b'RIFF'):
                image_data = body
                print("✅ Detected raw image data")
        
        if image_data is None or len(image_data) == 0:
            print("❌ No valid image data found")
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'No valid image data found',
                    'debug': {
                        'content_type': content_type,
                        'body_length': len(body) if body else 0,
                        'is_base64': is_base64
                    }
                })
            }
        
        print(f"📊 Image data size: {len(image_data)} bytes")
        
        # Process the image
        print("🖼️ Processing image...")
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            print(f"📏 Image size: {image.size}, format: {image.format}")
            
            # Remove background
            result_image = remover.remove_background(image)
            print("✅ Background removal completed")
            
            # Convert result to bytes
            output_buffer = io.BytesIO()
            result_image.save(output_buffer, format='PNG', optimize=True)
            result_bytes = output_buffer.getvalue()
            
            print(f"📤 Result image size: {len(result_bytes)} bytes")
            
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
            import traceback
            print(f"📋 Traceback: {traceback.format_exc()}")
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({
                    'error': f'Image processing failed: {str(e)}',
                    'type': 'processing_error'
                })
            }
        
    except Exception as e:
        print(f"❌ Function error: {str(e)}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': f'Server error: {str(e)}',
                'type': 'server_error'
            })
        }
