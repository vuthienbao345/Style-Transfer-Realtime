def handler(request):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': '{"message": "Vercel deployment is working!", "status": "success"}'
    }
