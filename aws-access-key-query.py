import json
import logging
import re
import csv
import boto3

from argparse import ArgumentParser
from datetime import datetime

# Parse the IAM User ARN to extract the AWS account number
def parse_arn(arn_string):
    acct_num = re.findall(r'(?<=:)[0-9]{12}',arn_string)
    return acct_num[0]

# Query for a list of AWS IAM Users
def query_iam_users(accesskey,secretkey):
    
    todaydate = (datetime.now()).strftime("%Y-%m-%d")
    users = []
    client = boto3.client(
        'iam',
        aws_access_key_id = accesskey,
        aws_secret_access_key = secretkey
    )

    paginator = client.get_paginator('list_users')
    response_iterator = paginator.paginate()
    for page in response_iterator:
        for user in page['Users']:
            user_rec = {'loggedDate':todaydate,'username':user['UserName'],'account_number':(parse_arn(user['Arn']))}
            users.append(user_rec)
    return users

# Query for a list of access keys and information on access keys for an AWS IAM User
def query_access_keys(accesskey,secretkey,user):
    keys = []
    client = boto3.client(
        'iam',
        aws_access_key_id = accesskey,
        aws_secret_access_key = secretkey
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

def main():

    # Enable logging to console
    logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    try:

        # Initialize empty list
        key_records = []

        # Process parameters file
        parser = ArgumentParser()
        parser.add_argument('-parameterfile', type=str, help='JSON file with parameters')
        parser.add_argument('-exportfile', type=str, default='azure_resources.json', help='Name of export file (default: azure_resources.json')
        args = parser.parse_args()

        with open(args.parameterfile) as json_data:
            config = json.load(json_data)

        # Retrieve list of IAM Users
        users = query_iam_users(config['accesskey'],config['secretkey'])

        # Retrieve list of access keys for each IAM User and add to record
        for user in users:
            key_records.extend(query_access_keys(config['accesskey'],config['secretkey'],user))
        print(key_records)
        # Convert to CSV and write to file
        dictkeys = key_records[0].keys()
        with open(args.exportfile, 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, dictkeys)
            dict_writer.writeheader()
            dict_writer.writerows(key_records)

    except Exception as e:
        logging.error("Execution error",exc_info=True)

if __name__ == "__main__":
    main()