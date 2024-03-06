import awsgi
import boto3
from flask_cors import CORS
from flask import Flask, request, jsonify
from uuid import uuid4

BASE_ROUTE = "/news"
APPROVE_ROUTE = "/approve"
TABLE = "nbnweditorpendingfinal-dev"
APPROVED_TABLE = "approvedarticles-dev"


client = boto3.client("dynamodb")
app = Flask(__name__)
CORS(app)

def postItem(client, event):
    item_data = event
    # Create a dictionary to hold the formatted item
    formatted_item = {}
    # Iterate through the keys and values in item_data
    for key, value in item_data.items():
        # Determine the data type based on the Python type of the value
        if isinstance(value, str):
            formatted_item[key] = {'S': value}
        elif isinstance(value, int):
            formatted_item[key] = {'N': str(value)}
        elif isinstance(value, list):
            formatted_item[key] = {'L': [{'S': str(item)} for item in value]}
        # Add more data type checks as needed
    response = client.put_item(
            TableName=TABLE,
            Item=formatted_item
    )

    return response


def postItemToApprovedTable(client, event):
    news_id = event['id']

    # Get the item from the pending table
    response = client.get_item(
        TableName=TABLE,
        Key={
            'id': {'S': str(news_id)}
        }
    )

    # Put the item in the approved table
    item = response['Item']
    response = client.put_item(
        TableName=APPROVED_TABLE,
        Item=item
    )

    return response
    

@app.route(BASE_ROUTE, methods=["POST"])
def create_news():
    request_json = request.get_json(force=True)
    response = postItem(client, request_json)
    return jsonify({"message": "News created successfully", "response": response})
    

def getNewsById(dynamodb, event):
    """
    ID and Date are required. (Remove need for date)
    """
    newsId = event['id']
    print(newsId)
    response = dynamodb.get_item(
        TableName='doshabdh_content',
        Key={
            'id': {'S': str(newsId)},
            'date': {'N': str(event['date'])}  # Convert integer to string
        }
    )
    return response['Item']


@app.route(BASE_ROUTE, methods=["GET"])
def list_news_for_review():
    request_json = request.get_json(force=True)
    response = getNewsById(client, request_json)
    return jsonify({"message": "News article retrieved successfully", "response": response})


@app.route(APPROVE_ROUTE, methods=["POST"])
def approve_news():
    request_json = request.get_json(force=True)
    response = postItemToApprovedTable(client, request_json)
    return jsonify({"message": "News approved successfully", "response": response})



def handler(event, context):
    return awsgi.response(app, event, context)