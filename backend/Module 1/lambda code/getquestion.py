import random
import boto3

dynamodb = boto3.client('dynamodb')


def lambda_handler(event, context):
    # Retrieve the request body
    request_data = event['body']

    # Get user ID and security question from the request
    user_details = request_data.get('user_details')

    # Retrieve security questions and answers from DynamoDB
    response = dynamodb.get_item(
        TableName='securityanswer',
        Key={'uid': {'S': user_details['user_id']}}
    )
    security_answers = response.get('Item', {}).get('security_questions', {}).get('L', [])

    # Get a random security question
    if security_answers:
        random_question = random.choice(security_answers)
        question = random_question['M']['question']['S']
        return {'statusCode': 200, 'status': True, 'response': question}
    else:
        return {'statusCode': 404, 'status': False, 'response': 'No security questions found.'}


"""{
  "body": $input.json('$')
}"""
