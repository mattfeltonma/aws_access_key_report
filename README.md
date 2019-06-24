# AWS Access Key Report
This Python script queries an AWS account for a listing of all AWS IAM User access keys, their ages, and information on their last usage.

## What problem does this solve?
AWS IAM User access keys and secret keys are used to provide 3rd party access to AWS resources when AWS IAM Roles are not an option.  Managing the lifecycle of the keys can difficult and often leads to stale keys which are never rotated or disabled which creates a security risk.  While [Credential Reports](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_getting-report.html) provide some of this information, it is often user centric verus key centric.  It also does not provide the key IDs which creates more work to determine which key needs to be rotated.

The script queries the AWS IAM API to pull a listing of AWS IAM Users from an account, queries for a listing of the access keys each account has provisioned, and then pulls metadata about each key including the creation date, the last date the key was used, and more.  The data is outputed into a CSV file which can be consumed in your favorite logging or data platform.  Access keys are sanitized prior to writing to the CSV by keeping only the first and last four characters.

My plan is to use this script in a larger solution I'm creating that will run as an Azure Function.  Due to this long term plan, the script is setup to use an IAM User access key and secret key.  Minimum work would be required to switch this to an IAM Role if you plan to run this as an AWS Lambda.

## Requirements

### Python Runtime and Modules
* [Python 3.6](https://www.python.org/downloads/release/python-360/)
* [AWS Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html?id=docs_gateway)

### AWS IAM Permissions Requirement
I've included a CloudFormation template that will create the IAM Group and IAM Managed Policy with the required permissions.
* IAM:ListUsers
* IAM:ListAccessKeys
* IAM:GetAccessKeyLastUsed


## Execution

python3 aws_access_key_report.py -parameterfile parameters.json -exportfile report.csv
