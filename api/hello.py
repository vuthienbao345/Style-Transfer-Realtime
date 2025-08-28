from http.server import BaseHTTPRequestHandler

def handler(request):
    return {
        'statusCode': 200,
        'body': 'Hello from Vercel!'
    }
