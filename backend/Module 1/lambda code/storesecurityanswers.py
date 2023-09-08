import boto3

dynamodb = boto3.client('dynamodb')


def lambda_handler(event, context):
    # Retrieve the request body
    request_data = event['body']

    # Extract the user ID and security questions from the request
    uid = request_data['uid']
    security_questions = request_data['security_questions']

    try:

        # Save security questions in DynamoDB
        dynamodb.put_item(
            TableName='securityanswer',
            Item={
                'uid': {'S': uid},
                'security_questions': {'L': security_questions}
            }
        )

        return {"status": True, "response": 'User registered successfully.'}

    except Exception as e:
        return {'statusCode': 400, 'body': str(e)}
