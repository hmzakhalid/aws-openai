# OpenAI API shared code

Common constants, validations and misc utility functions that are called by both the openai and langchain lambdas.

## Settings class

This shared class manages configuration settings for all uses cases, including: local development, test, QA, CI-CD, and production.

### Validations and strong data typing

The Settings class leverages [Pydantic](https://docs.pydantic.dev/latest/) to enforce strong data typing as well as to assist with common-sense validations of several of the configuration values. Additionally, it enables us to enforce a read-only state of the settings attributes in able to thwart potential side effects from erroneous CD-CD processes.

### Avoids ambiguous initialization scenarios

Sources of configuration data vary depending on the use case, which can invariably introduce ambiguities with regard to which source takes priority in varying scenarios. The Settings class resolves these potential ambiguities by consistently applying the following order of precedence by source:

1. Python constructor arguments passed from inside the source code
2. `.env` files which can be saved anywhere inside the repo, and nothing prevents multiple .env files from being created.
3. environment variables initialized in the form of `export VARIABLE_NAME=some-value`
4. `terraform.tfvars` if it exists
5. default values declared in SettingsDefaults class

Where possible, we use [Pydantic](https://docs.pydantic.dev/latest/) to seamlessly resolve some of these ambiguities.

### Protects sensitive data

The Settings class will not expose sensitive data under any circumstances, including logging and dumps.

#### AWS configuration

The Settings class contains instance variables for `aws_profile` and `aws_region`. If either of these is unset then standard behavior of [AWS CLI](https://aws.amazon.com/cli/) will take precedence.

#### OpenAI API configuration

The Settings class contains an instance variable for `openai_api_key` which will take precedence if it is set.

#### Pinecone API configuration

The Settings class contains an instance variable for `pinecone_api_key` which will take precedence if it is set.

### CloudWatch logging

The Settings class is also a provider to CloudWatch when both `DEBUG_MODE` and `DUMP_DEFAULTS` environment variables are set to `True`. The Settings property `dump` generates a context sensitive JSON dict of the state data for all settings as well as class instance meta data that can be helpful during development trouble shooting.

An example CloudWatch dump:

```json
{
  "aws": {
    "aws_profile": "lawrence",
    "aws_region": "us-east-1"
  },
  "aws_api_gateway": {
    "aws_apigateway_custom_domain_name": "api.openai.example.com",
    "aws_apigateway_custom_domain_name_create": false,
    "aws_apigateway_root_domain": "example.com"
  },
  "environment": {
    "boto3": "1.34.2",
    "debug_mode": true,
    "dotenv": [
      "AWS_REGION",
      "DEBUG_MODE",
      "AWS_DYNAMODB_TABLE_ID",
      "AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT",
      "AWS_REKOGNITION_FACE_DETECT_THRESHOLD",
      "AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES",
      "AWS_REKOGNITION_FACE_DETECT_QUALITY_FILTER",
      "AWS_REKOGNITION_COLLECTION_ID",
      "LANGCHAIN_MEMORY_KEY",
      "OPENAI_ENDPOINT_IMAGE_N",
      "OPENAI_ENDPOINT_IMAGE_SIZE"
    ],
    "dump_defaults": true,
    "is_using_dotenv_file": true,
    "is_using_tfvars_file": true,
    "os": "posix",
    "release": "23.2.0",
    "shared_resource_identifier": "openai",
    "system": "Darwin",
    "tfvars": [
      "aws_account_id",
      "tags",
      "aws_region",
      "openai_endpoint_image_n",
      "openai_endpoint_image_size",
      "lambda_python_runtime",
      "debug_mode",
      "lambda_memory_size",
      "lambda_timeout",
      "logging_level",
      "log_retention_days",
      "create_custom_domain",
      "root_domain",
      "shared_resource_identifier",
      "stage",
      "quota_settings_limit",
      "quota_settings_offset",
      "quota_settings_period",
      "throttle_settings_burst_limit",
      "throttle_settings_rate_limit"
    ],
    "version": "0.7.0"
  },
  "openai_api": {
    "langchain_memory_key": "chat_history",
    "openai_endpoint_image_n": 4,
    "openai_endpoint_image_size": "1024x768"
  },
  "secrets": {
    "openai_api_source": "environment variable",
    "pinecone_api_source": "environment variable"
  },
  "settings_defaults": {
    "AWS_APIGATEWAY_CUSTOM_DOMAIN_NAME_CREATE": false,
    "AWS_APIGATEWAY_ROOT_DOMAIN_NAME": "example.com",
    "AWS_DYNAMODB_TABLE_ID": "rekognition",
    "AWS_PROFILE": null,
    "AWS_REGION": "us-east-1",
    "AWS_REKOGNITION_COLLECTION_ID": "rekognition-collection",
    "AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES": "DEFAULT",
    "AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT": 10,
    "AWS_REKOGNITION_FACE_DETECT_QUALITY_FILTER": "AUTO",
    "AWS_REKOGNITION_FACE_DETECT_THRESHOLD": 10,
    "DEBUG_MODE": true,
    "DUMP_DEFAULTS": false,
    "LANGCHAIN_MEMORY_KEY": "chat_history",
    "OPENAI_API_KEY": null,
    "OPENAI_API_ORGANIZATION": null,
    "OPENAI_ENDPOINT_IMAGE_N": 4,
    "OPENAI_ENDPOINT_IMAGE_SIZE": "1024x768",
    "PINECONE_API_KEY": null,
    "SHARED_RESOURCE_IDENTIFIER": "openai",
    "VALID_AWS_REGIONS": [
      "ap-south-1",
      "eu-north-1",
      "eu-west-3",
      "eu-west-2",
      "eu-west-1",
      "ap-northeast-3",
      "ap-northeast-2",
      "ap-northeast-1",
      "ca-central-1",
      "sa-east-1",
      "ap-southeast-1",
      "ap-southeast-2",
      "eu-central-1",
      "us-east-1",
      "us-east-2",
      "us-west-1",
      "us-west-2"
    ],
    "VALID_DOMAIN_PATTERN": "^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$"
  }
}
```
