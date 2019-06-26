import json
import logging
import re
import csv
import boto3
import os

from io import StringIO
from datetime import datetime

# Parse the IAM User ARN to extract the AWS account number
def parse_arn(arn_string):
    acct_num = re.findall(r'(?<=:)[0-9]{12}',arn_string)
    return acct_num[0]

# Query for a list of AWS IAM Users
def query_iam_users():
    
    todaydate = (datetime.now()).strftime("%Y-%m-%d")
    users = []
    client = boto3.client(
        'iam'
    )

    paginator = client.get_paginator('list_users')
    response_iterator = paginator.paginate()
    for page in response_iterator:
        for user in page['Users']:
            user_rec = {'loggedDate':todaydate,'username':user['UserName'],'account_number':(parse_arn(user['Arn']))}
            users.append(user_rec)
    return users

# Query for a list of access keys and information on access keys for an AWS IAM User
def query_access_keys(user):
    keys = []
    client = boto3.client(
        'iam'
    )
    paginator = client.get_paginator('list_access_keys')
    response_iterator = paginator.paginate(
        UserName = user['username']
    )

    # Get information on access key usage
    for page in response_iterator:
        for key in page['AccessKeyMetadata']:
            response = client.get_access_key_last_used(
                AccessKeyId = key['AccessKeyId']
            )

            # Santize key before sending it along for export

            sanitizedacctkey = key['AccessKeyId'][:4] + '...' + key['AccessKeyId'][-4:]
            # Create new dictonionary object with access key information
            if 'LastUsedDate' in response.get('AccessKeyLastUsed'):
                key_rec = {'loggedDate':user['loggedDate'],'user':user['username'],'account_number':user['account_number'],
                'AccessKeyId':sanitizedacctkey,'CreateDate':(key['CreateDate']).strftime("%m-%d-%Y %H:%M:%S"),
                'LastUsedDate':(response['AccessKeyLastUsed']['LastUsedDate']).strftime("%m-%d-%Y %H:%M:%S"),
                'Region':response['AccessKeyLastUsed']['Region'],'Status':key['Status'],
                'ServiceName':response['AccessKeyLastUsed']['ServiceName']}
                keys.append(key_rec)
    return keys

def export_report(data):
    todaydate = (datetime.now()).strftime("%Y-%m-%d")
    encoded_string = data.encode("utf-8")
    logging.info("Writing report to S3...")
    s3_path = os.environ['s3_prefix'] + "/" + todaydate + ".json"
    s3 = boto3.resource('s3')
    s3.Bucket(os.environ['bucket']).put_object(Key=s3_path, Body=encoded_string)
    
def lambda_handler(event, context):

    # Enable logging to console
    logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    try:

        # Initialize empty list
        key_records = []

        # Retrieve list of IAM Users
        logging.info("Retrieving a list of IAM Users...")
        users = query_iam_users()

        # Retrieve list of access keys for each IAM User and add to record
        logging.info("Retrieving a listing of access keys for each IAM User...")
        for user in users:
            key_records.extend(query_access_keys(user))

        # Convert to CSV and store contents in a StringIO
        output = StringIO()
        dictkeys = key_records[0].keys()
        dict_writer = csv.DictWriter(output,dictkeys)
        dict_writer.writeheader()
        dict_writer.writerows(key_records)

        # Export report to another format
        logging.info("Creating report...")
        export_report(output.getvalue())

    except Exception as e:
        logging.error("Execution error",exc_info=True)