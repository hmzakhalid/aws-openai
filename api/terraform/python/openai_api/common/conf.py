# -*- coding: utf-8 -*-
# pylint: disable=no-member
# pylint: disable=E0213,C0103
"""
Configuration for Lambda functions.

This module is used to configure the Lambda functions. It uses the pydantic_settings
library to validate the configuration values. The configuration values are read from
any of the following sources:
    - constructor arguments
    - environment variables
    - terraform.tfvars
    - default values
"""

import importlib.util
import os  # library for interacting with the operating system
import platform  # library to view information about the server host this Lambda runs on
import re
from typing import Any, Dict, List, Optional

import boto3  # AWS SDK for Python https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
from dotenv import load_dotenv
from openai_api.common.const import IS_USING_TFVARS, PROJECT_ROOT, TFVARS
from openai_api.common.exceptions import (
    OpenAIAPIConfigurationError,
    OpenAIAPIValueError,
)
from pydantic import Field, SecretStr, ValidationError, ValidationInfo, field_validator
from pydantic_settings import BaseSettings


TFVARS = TFVARS or {}
DOT_ENV_LOADED = load_dotenv()
ec2 = boto3.Session().client("ec2")
regions = ec2.describe_regions()


def load_version() -> Dict[str, str]:
    """Stringify the __version__ module."""
    version_file_path = os.path.join(PROJECT_ROOT, "__version__.py")
    spec = importlib.util.spec_from_file_location("__version__", version_file_path)
    version_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(version_module)
    return version_module.__dict__


VERSION = load_version()


def get_semantic_version() -> str:
    """
    Return the semantic version number.

    Example valid values of __version__.py are:
    0.1.17
    0.1.17-next.1
    0.1.17-next.2
    0.1.17-next.123456
    0.1.17-next-major.1
    0.1.17-next-major.2
    0.1.17-next-major.123456

    Note:
    - pypi does not allow semantic version numbers to contain a dash.
    - pypi does not allow semantic version numbers to contain a 'v' prefix.
    - pypi does not allow semantic version numbers to contain a 'next' suffix.
    """
    version = VERSION["__version__"]
    version = re.sub(r"-next\.\d+", "", version)
    return re.sub(r"-next-major\.\d+", "", version)


# pylint: disable=too-few-public-methods
class SettingsDefaults:
    """Default values for Settings"""

    DEBUG_MODE = TFVARS.get("debug_mode", False)
    DUMP_DEFAULTS = TFVARS.get("dump_defaults", False)
    AWS_PROFILE = TFVARS.get("aws_profile", None)
    AWS_REGION = TFVARS.get("aws_region", "us-east-1")
    AWS_DYNAMODB_TABLE_ID = "rekognition"
    AWS_REKOGNITION_COLLECTION_ID = AWS_DYNAMODB_TABLE_ID + "-collection"
    AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT = 10
    AWS_REKOGNITION_FACE_DETECT_THRESHOLD = 10
    AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES = "DEFAULT"
    AWS_REKOGNITION_FACE_DETECT_QUALITY_FILTER = "AUTO"
    AWS_APIGATEWAY_ROOT_DOMAIN_NAME = TFVARS.get("root_domain", None)
    AWS_APIGATEWAY_CUSTOM_DOMAIN_NAME_CREATE: bool = TFVARS.get("create_custom_domain", False)
    LANGCHAIN_MEMORY_KEY = "chat_history"
    OPENAI_API_ORGANIZATION: str = None
    OPENAI_API_KEY = SecretStr(None)
    OPENAI_ENDPOINT_IMAGE_N = 4
    OPENAI_ENDPOINT_IMAGE_SIZE = "1024x768"
    PINECONE_API_KEY = SecretStr(None)
    SHARED_RESOURCE_IDENTIFIER = TFVARS.get("shared_resource_identifier", "openai")
    VALID_DOMAIN_PATTERN = r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$"
    VALID_AWS_REGIONS = [region["RegionName"] for region in regions["Regions"]]

    @classmethod
    def to_dict(cls):
        """Convert SettingsDefaults to dict"""
        return {
            key: value
            for key, value in SettingsDefaults.__dict__.items()
            if not key.startswith("__") and not callable(key) and key != "to_dict"
        }


def empty_str_to_bool_default(v: str, default: bool) -> bool:
    """Convert empty string to default boolean value"""
    if v in [None, ""]:
        return default
    return v.lower() in ["true", "1", "t", "y", "yes"]


def empty_str_to_int_default(v: str, default: int) -> int:
    """Convert empty string to default integer value"""
    if v in [None, ""]:
        return default
    try:
        return int(v)
    except ValueError:
        return default


# pylint: disable=too-many-public-methods
# pylint: disable=too-many-instance-attributes
class Settings(BaseSettings):
    """Settings for Lambda functions"""

    _aws_session: boto3.Session = None
    _s3_client: boto3.client = None
    _api_client: boto3.client = None
    _dynamodb_client: boto3.client = None
    _rekognition_client: boto3.client = None
    _dynamodb_table: boto3.resource = None
    _dump: Dict[str, str] = None
    _pinecone_api_key_source: str = "unset"
    _openai_api_key_source: str = "unset"
    _initialized: bool = False

    def __init__(self, **data: Any):
        super().__init__(**data)
        if "PINECONE_API_KEY" in os.environ:
            self._pinecone_api_key_source = "environment variable"
        elif data.get("pinecone_api_key"):
            self._pinecone_api_key_source = "init argument"
        if "OPENAI_API_KEY" in os.environ:
            self._openai_api_key_source = "environment variable"
        elif data.get("openai_api_key"):
            self._openai_api_key_source = "init argument"
        self._initialized = True

    debug_mode: Optional[bool] = Field(
        SettingsDefaults.DEBUG_MODE,
        env="DEBUG_MODE",
        pre=True,
        getter=lambda v: empty_str_to_bool_default(v, SettingsDefaults.DEBUG_MODE),
    )
    dump_defaults: Optional[bool] = Field(
        SettingsDefaults.DUMP_DEFAULTS,
        env="DUMP_DEFAULTS",
        pre=True,
        getter=lambda v: empty_str_to_bool_default(v, SettingsDefaults.DUMP_DEFAULTS),
    )
    aws_profile: Optional[str] = Field(
        SettingsDefaults.AWS_PROFILE,
        env="AWS_PROFILE",
    )
    aws_regions: Optional[List[str]] = Field(SettingsDefaults.VALID_AWS_REGIONS, description="The list of AWS regions")
    aws_region: Optional[str] = Field(
        SettingsDefaults.AWS_REGION,
        env="AWS_REGION",
    )
    aws_apigateway_custom_domain_name_create: Optional[bool] = Field(
        SettingsDefaults.AWS_APIGATEWAY_CUSTOM_DOMAIN_NAME_CREATE,
        env="AWS_APIGATEWAY_CUSTOM_DOMAIN_NAME_CREATE",
        pre=True,
        getter=lambda v: empty_str_to_bool_default(v, SettingsDefaults.AWS_APIGATEWAY_CUSTOM_DOMAIN_NAME_CREATE),
    )
    aws_apigateway_root_domain: Optional[str] = Field(
        SettingsDefaults.AWS_APIGATEWAY_ROOT_DOMAIN_NAME, env="AWS_APIGATEWAY_ROOT_DOMAIN_NAME"
    )
    aws_apigateway_custom_domain_name: Optional[str] = Field(
        "api." + SettingsDefaults.SHARED_RESOURCE_IDENTIFIER + "." + SettingsDefaults.AWS_APIGATEWAY_ROOT_DOMAIN_NAME,
        env="AWS_APIGATEWAY_CUSTOM_DOMAIN_NAME",
    )
    aws_dynamodb_table_id: Optional[str] = Field(
        SettingsDefaults.AWS_DYNAMODB_TABLE_ID,
        env="AWS_DYNAMODB_TABLE_ID",
    )
    aws_rekognition_collection_id: Optional[str] = Field(
        SettingsDefaults.AWS_REKOGNITION_COLLECTION_ID,
        env="AWS_REKOGNITION_COLLECTION_ID",
    )

    aws_rekognition_face_detect_attributes: Optional[str] = Field(
        SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES,
        env="AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES",
    )
    aws_rekognition_face_detect_quality_filter: Optional[str] = Field(
        SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_QUALITY_FILTER,
        env="AWS_REKOGNITION_FACE_DETECT_QUALITY_FILTER",
    )
    aws_rekognition_face_detect_max_faces_count: Optional[int] = Field(
        SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT,
        gt=0,
        env="AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT",
        pre=True,
        getter=lambda v: empty_str_to_int_default(v, SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT),
    )
    aws_rekognition_face_detect_threshold: Optional[int] = Field(
        SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_THRESHOLD,
        gt=0,
        env="AWS_REKOGNITION_FACE_DETECT_THRESHOLD",
        pre=True,
        getter=lambda v: empty_str_to_int_default(v, SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_THRESHOLD),
    )
    langchain_memory_key: Optional[str] = Field(SettingsDefaults.LANGCHAIN_MEMORY_KEY, env="LANGCHAIN_MEMORY_KEY")
    openai_api_organization: Optional[str] = Field(
        SettingsDefaults.OPENAI_API_ORGANIZATION, env="OPENAI_API_ORGANIZATION"
    )
    openai_api_key: Optional[SecretStr] = Field(SettingsDefaults.OPENAI_API_KEY, env="OPENAI_API_KEY")
    openai_endpoint_image_n: Optional[int] = Field(
        SettingsDefaults.OPENAI_ENDPOINT_IMAGE_N, env="OPENAI_ENDPOINT_IMAGE_N"
    )
    openai_endpoint_image_size: Optional[str] = Field(
        SettingsDefaults.OPENAI_ENDPOINT_IMAGE_SIZE, env="OPENAI_ENDPOINT_IMAGE_SIZE"
    )
    pinecone_api_key: Optional[SecretStr] = Field(SettingsDefaults.PINECONE_API_KEY, env="PINECONE_API_KEY")
    shared_resource_identifier: Optional[str] = Field(
        SettingsDefaults.SHARED_RESOURCE_IDENTIFIER, env="SHARED_RESOURCE_IDENTIFIER"
    )

    @property
    def pinecone_api_key_source(self) -> str:
        """Pinecone API key source"""
        return self._pinecone_api_key_source

    @property
    def openai_api_key_source(self) -> str:
        """OpenAI API key source"""
        return self._openai_api_key_source

    @property
    def is_using_dotenv_file(self) -> bool:
        """Is the dotenv file being used?"""
        return DOT_ENV_LOADED

    @property
    def environment_variables(self) -> List[str]:
        """Environment variables"""
        return list(os.environ.keys())

    @property
    def is_using_tfvars_file(self) -> bool:
        """Is the tfvars file being used?"""
        return IS_USING_TFVARS

    @property
    def tfvars_variables(self) -> List[str]:
        """Terraform variables"""
        return list(TFVARS.keys())

    @property
    def is_using_aws_rekognition(self) -> bool:
        """Future: Is the AWS Rekognition service being used?"""
        return False

    @property
    def is_using_aws_dynamodb(self) -> bool:
        """Future: Is the AWS DynamoDB service being used?"""
        return False

    @property
    def version(self) -> str:
        """OpenAI API version"""
        return get_semantic_version()

    @property
    def aws_session(self):
        """AWS session"""
        if not self._aws_session:
            if self.aws_profile:
                self._aws_session = boto3.Session(profile_name=self.aws_profile, region_name=self.aws_region)
            else:
                self._aws_session = boto3.Session(region_name=self.aws_region)
        return self._aws_session

    @property
    def api_client(self):
        """API Gateway client"""
        if not self._api_client:
            self._api_client = self.aws_session.client("apigateway")
        return self._api_client

    @property
    def s3_client(self):
        """S3 client"""
        if not self._s3_client:
            self._s3_client = self.aws_session.client("s3")
        return self._s3_client

    @property
    def dynamodb_client(self):
        """DynamoDB client"""
        if not self._dynamodb_client:
            self._dynamodb_client = self.aws_session.client("dynamodb")
        return self._dynamodb_client

    @property
    def rekognition_client(self):
        """Rekognition client"""
        if not self._rekognition_client:
            self._rekognition_client = self.aws_session.client("rekognition")
        return self._rekognition_client

    @property
    def dynamodb_table(self):
        """DynamoDB table"""
        if not self._dynamodb_table:
            self._dynamodb_table = self.dynamodb_client.Table(self.aws_dynamodb_table_id)
        return self._dynamodb_table

    # use the boto3 library to initialize clients for the AWS services which we'll interact
    @property
    def dump(self) -> dict:
        """Dump settings to CloudWatch"""

        def recursive_sort_dict(d):
            return {k: recursive_sort_dict(v) if isinstance(v, dict) else v for k, v in sorted(d.items())}

        if self._dump and self._initialized:
            return self._dump

        self._dump = {
            "secrets": {
                "openai_api_source": self.openai_api_key_source,
                "pinecone_api_source": self.pinecone_api_key_source,
            },
            "environment": {
                "is_using_tfvars_file": self.is_using_tfvars_file,
                "is_using_dotenv_file": self.is_using_dotenv_file,
                "os": os.name,
                "system": platform.system(),
                "release": platform.release(),
                "boto3": boto3.__version__,
                "shared_resource_identifier": self.shared_resource_identifier,
                "debug_mode": self.debug_mode,
                "dump_defaults": self.dump_defaults,
                "version": self.version,
            },
            "aws": {
                "aws_profile": self.aws_profile,
                "aws_region": self.aws_region,
            },
            "aws_api_gateway": {
                "aws_apigateway_root_domain": self.aws_apigateway_root_domain,
                "aws_apigateway_custom_domain_name_create": self.aws_apigateway_custom_domain_name_create,
                "aws_apigateway_custom_domain_name": self.aws_apigateway_custom_domain_name,
            },
            "openai_api": {
                "langchain_memory_key": self.langchain_memory_key,
                "openai_endpoint_image_n": self.openai_endpoint_image_n,
                "openai_endpoint_image_size": self.openai_endpoint_image_size,
            },
        }
        if self.dump_defaults:
            settings_defaults = SettingsDefaults.to_dict()
            self._dump["settings_defaults"] = settings_defaults

        if self.is_using_aws_rekognition:
            aws_rekognition = {
                "aws_rekognition_collection_id": self.aws_rekognition_collection_id,
                "aws_rekognition_face_detect_max_faces_count": self.aws_rekognition_face_detect_max_faces_count,
                "aws_rekognition_face_detect_attributes": self.aws_rekognition_face_detect_attributes,
                "aws_rekognition_face_detect_quality_filter": self.aws_rekognition_face_detect_quality_filter,
            }
            self._dump["aws_rekognition"] = aws_rekognition

        if self.is_using_aws_dynamodb:
            aws_dynamodb = {
                "aws_dynamodb_table_id": self.aws_dynamodb_table_id,
            }
            self._dump["aws_dynamodb"] = aws_dynamodb

        if self.is_using_dotenv_file:
            self._dump["environment"]["dotenv"] = self.environment_variables

        if self.is_using_tfvars_file:
            self._dump["environment"]["tfvars"] = self.tfvars_variables

        self._dump = recursive_sort_dict(self._dump)
        return self._dump

    # pylint: disable=too-few-public-methods
    class Config:
        """Pydantic configuration"""

        frozen = True

    @field_validator("aws_profile")
    # pylint: disable=no-self-argument,unused-argument
    def validate_aws_profile(cls, v, values, **kwargs) -> str:
        """Validate aws_profile"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_PROFILE
        return v

    @field_validator("aws_region")
    # pylint: disable=no-self-argument,unused-argument
    def validate_aws_region(cls, v, values: ValidationInfo, **kwargs) -> str:
        """Validate aws_region"""
        valid_regions = values.data.get("aws_regions", [])
        if v in [None, ""]:
            return SettingsDefaults.AWS_REGION
        if v not in valid_regions:
            raise OpenAIAPIValueError(f"aws_region {v} not in aws_regions")
        return v

    @field_validator("aws_apigateway_root_domain")
    def validate_aws_apigateway_root_domain(cls, v) -> str:
        """Validate aws_apigateway_root_domain"""
        if v in [None, ""]:
            v = SettingsDefaults.AWS_APIGATEWAY_ROOT_DOMAIN_NAME
        if not re.match(SettingsDefaults.VALID_DOMAIN_PATTERN, v):
            raise OpenAIAPIValueError("Invalid root domain name")
        return v

    @field_validator("aws_apigateway_custom_domain_name")
    def validate_aws_apigateway_custom_domain_name(cls, v) -> str:
        """Validate aws_apigateway_custom_domain_name"""
        if v in [None, ""]:
            v = SettingsDefaults.AWS_APIGATEWAY_CUSTOM_DOMAIN_NAME_CREATE
        if not re.match(SettingsDefaults.VALID_DOMAIN_PATTERN, v):
            raise OpenAIAPIValueError("Invalid custom domain name")
        return v

    @field_validator("aws_apigateway_custom_domain_name")
    def validate_aws_apigateway_custom_domain_name_create(cls, v) -> bool:
        """Validate aws_apigateway_custom_domain_name_create"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_APIGATEWAY_CUSTOM_DOMAIN_NAME_CREATE
        return v

    @field_validator("shared_resource_identifier")
    def validate_shared_resource_identifier(cls, v) -> str:
        """Validate shared_resource_identifier"""
        if v in [None, ""]:
            return SettingsDefaults.SHARED_RESOURCE_IDENTIFIER
        return v

    @field_validator("aws_dynamodb_table_id")
    def validate_table_id(cls, v) -> str:
        """Validate aws_dynamodb_table_id"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_DYNAMODB_TABLE_ID
        return v

    @field_validator("aws_rekognition_collection_id")
    def validate_collection_id(cls, v) -> str:
        """Validate aws_rekognition_collection_id"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_REKOGNITION_COLLECTION_ID
        return v

    @field_validator("aws_rekognition_face_detect_attributes")
    def validate_face_detect_attributes(cls, v) -> str:
        """Validate aws_rekognition_face_detect_attributes"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES
        return v

    @field_validator("debug_mode")
    def parse_debug_mode(cls, v) -> bool:
        """Parse debug_mode"""
        if isinstance(v, bool):
            return v
        if v in [None, ""]:
            return SettingsDefaults.DEBUG_MODE
        return v.lower() in ["true", "1", "t", "y", "yes"]

    @field_validator("dump_defaults")
    def parse_dump_defaults(cls, v) -> bool:
        """Parse dump_defaults"""
        if isinstance(v, bool):
            return v
        if v in [None, ""]:
            return SettingsDefaults.DUMP_DEFAULTS
        return v.lower() in ["true", "1", "t", "y", "yes"]

    @field_validator("aws_rekognition_face_detect_max_faces_count")
    def check_face_detect_max_faces_count(cls, v) -> int:
        """Check aws_rekognition_face_detect_max_faces_count"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT
        return int(v)

    @field_validator("aws_rekognition_face_detect_threshold")
    def check_face_detect_threshold(cls, v) -> int:
        """Check aws_rekognition_face_detect_threshold"""
        if isinstance(v, int):
            return v
        if v in [None, ""]:
            return SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_THRESHOLD
        return int(v)

    @field_validator("aws_rekognition_face_detect_quality_filter")
    def check_face_detect_quality_filter(cls, v) -> str:
        """Check aws_rekognition_face_detect_quality_filter"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_QUALITY_FILTER
        return v

    @field_validator("langchain_memory_key")
    def check_langchain_memory_key(cls, v) -> str:
        """Check langchain_memory_key"""
        if isinstance(v, int):
            return v
        if v in [None, ""]:
            return SettingsDefaults.LANGCHAIN_MEMORY_KEY
        return v

    @field_validator("openai_api_organization")
    def check_openai_api_organization(cls, v) -> str:
        """Check openai_api_organization"""
        if v in [None, ""]:
            return SettingsDefaults.OPENAI_API_ORGANIZATION
        return v

    @field_validator("openai_api_key")
    def check_openai_api_key(cls, v) -> SecretStr:
        """Check openai_api_key"""
        if v in [None, ""]:
            return SettingsDefaults.OPENAI_API_KEY
        return v

    @field_validator("openai_endpoint_image_n")
    def check_openai_endpoint_image_n(cls, v) -> int:
        """Check openai_endpoint_image_n"""
        if isinstance(v, int):
            return v
        if v in [None, ""]:
            return SettingsDefaults.OPENAI_ENDPOINT_IMAGE_N
        return int(v)

    @field_validator("openai_endpoint_image_size")
    def check_openai_endpoint_image_size(cls, v) -> str:
        """Check openai_endpoint_image_size"""
        if v in [None, ""]:
            return SettingsDefaults.OPENAI_ENDPOINT_IMAGE_SIZE
        return v

    @field_validator("pinecone_api_key")
    def check_pinecone_api_key(cls, v) -> SecretStr:
        """Check pinecone_api_key"""
        if v in [None, ""]:
            return SettingsDefaults.PINECONE_API_KEY
        return v


settings = None
try:
    settings = Settings()
except (ValidationError, ValueError, OpenAIAPIConfigurationError, OpenAIAPIValueError) as e:
    raise OpenAIAPIConfigurationError("Invalid configuration: " + str(e)) from e
