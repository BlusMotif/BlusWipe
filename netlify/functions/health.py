import json
from datetime import datetime

def handler(event, context):
    """
    Health check endpoint for Netlify function.
    """
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'BlusWipe Background Remover',
            'version': '1.0.0',
            'developer': 'Eleblu Nunana'
        })
    }

# For Netlify Functions
def lambda_handler(event, context):
    return handler(event, context)
