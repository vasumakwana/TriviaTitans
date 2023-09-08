import boto3

dynamodb = boto3.client('dynamodb')

def lambda_handler(event, context):
    # Retrieve the request body
    request_data = event['body']

    # Get user ID, security question, and answer from the request
    uid = request_data.get('uid')
    question = request_data.get('question')
    answer = request_data.get('answer')

    try:
        # Retrieve security questions and answers from DynamoDB
        response = dynamodb.get_item(
            TableName='securityanswer',
            Key={'uid': {'S': uid}}
        )
        security_answers = response.get('Item', {}).get('security_questions', {}).get('L', [])

        # Check if the answer matches any of the stored answers
        for sq in security_answers:
            stored_question = sq['M']['question']['S']
            stored_answer = sq['M']['answer']['S']
            if question == stored_question and answer == stored_answer:
                return {'statusCode': 200, 'status': True, 'response': 'Answer is correct.'}

        return {'statusCode': 200, 'body': {'status': False, 'response': 'Answer is incorrect.'}}

    except Exception as e:
        return {'statusCode': 400, 'body': {'status': False, 'response': str(e)}}

"""{
  "body": $input.json('$')
}"""