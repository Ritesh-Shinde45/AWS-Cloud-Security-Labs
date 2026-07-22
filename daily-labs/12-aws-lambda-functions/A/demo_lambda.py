import json

def lambda_handler(context, event):
    print('Demo Zip ')
    return{
        'statusCode': 200,
        'body': json.dumps('Hello from code zip')
    }