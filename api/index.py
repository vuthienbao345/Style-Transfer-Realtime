from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import base64
from urllib.parse import urlparse, parse_qs

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_html_template():
    """Load the HTML template for the web interface"""
    try:
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Style Transfer App</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .upload { border: 2px dashed #ccc; padding: 20px; text-align: center; margin: 20px 0; }
                .result { margin-top: 20px; }
                img { max-width: 100%; height: auto; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎨 Style Transfer App</h1>
                <p>This is a simplified version. For full functionality, please use Streamlit Cloud.</p>
                <div class="upload">
                    <h3>Upload Image</h3>
                    <p>Due to Vercel limitations, this is a demo version.</p>
                    <p>For the full app with image processing, deploy to Streamlit Cloud.</p>
                </div>
                <div class="result">
                    <h3>Available Styles:</h3>
                    <ul>
                        <li>Post Impressionism</li>
                        <li>Cubism</li>
                        <li>Abstract Expressionism</li>
                        <li>Digital Painting</li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """

def handle_static_files(path):
    """Handle static file requests"""
    try:
        if path.startswith('/static/'):
            file_path = path[1:]  # Remove leading slash
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Determine content type
            if file_path.endswith('.css'):
                content_type = 'text/css'
            elif file_path.endswith('.js'):
                content_type = 'application/javascript'
            elif file_path.endswith('.png'):
                content_type = 'image/png'
            elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
                content_type = 'image/jpeg'
            else:
                content_type = 'application/octet-stream'
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': content_type,
                    'Access-Control-Allow-Origin': '*'
                },
                'body': base64.b64encode(content).decode('utf-8'),
                'isBase64Encoded': True
            }
    except FileNotFoundError:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'File not found'
        }

def handle_api_request(path, method, body):
    """Handle API requests"""
    if path == '/api/stylize' and method == 'POST':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': 'Image processing is not available in this demo version. Please deploy to Streamlit Cloud for full functionality.'
            })
        }
    
    return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'error': 'API endpoint not found'})
    }

def handler(request):
    """Main handler function for Vercel serverless function"""
    try:
        # Parse the request
        path = request.get('path', '/')
        method = request.get('method', 'GET')
        body = request.get('body', '')
        
        # Handle static files
        if path.startswith('/static/'):
            return handle_static_files(path)
        
        # Handle API requests
        if path.startswith('/api/'):
            return handle_api_request(path, method, body)
        
        # Handle main page
        if path == '/' or path == '':
            html_content = load_html_template()
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/html; charset=utf-8',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': html_content
            }
        
        # Default response
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'Page not found'
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
