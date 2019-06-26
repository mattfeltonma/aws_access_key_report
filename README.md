# AWS Access Key Report
This Lambda queries an AWS account for a listing of all AWS IAM User access keys, their ages, and information on their last usage.

## What problem does this solve?
AWS IAM User access keys and secret keys are used to provide 3rd party access to AWS resources when AWS IAM Roles are not an option.  Managing the lifecycle of the keys can difficult and often leads to stale keys which are never rotated or disabled which creates a security risk.  While [Credential Reports](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_getting-report.html) provide some of this information, it is often user centric verus key centric.  It also does not provide the key IDs which creates more work to determine which key needs to be rotated.

The script queries the AWS IAM API to pull a listing of AWS IAM Users from an account, queries for a listing of the access keys each account has provisioned, and then pulls metadata about each key including the creation date, the last date the key was used, and more.  The data is outputed to a variable in CSV format.

## Requirements

### Python Runtime and Modules
* [Python 3.6](https://www.python.org/downloads/release/python-360/)
* [AWS Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html?id=docs_gateway)

### AWS Permissions Requirement
* IAM:ListUsers
* IAM:ListAccessKeys
* IAM:GetAccessKeyLastUsed
* S3:PutObject (only required for user specific S3 prefix)

## Setup
The can be pushed using the provided CloudFormation template.  The code must be placed into a ZIP file and placed on an S3 bucket the user creating the CloudFormation stack.  

