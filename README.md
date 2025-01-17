# OpenAI Code Samples

[![FullStackWithLawrence](https://a11ybadges.com/badge?text=FullStackWithLawrence&badgeColor=orange&logo=youtube&logoColor=282828)](https://www.youtube.com/@FullStackWithLawrence)<br>
[![OpenAI](https://a11ybadges.com/badge?logo=openai)](https://platform.openai.com/)
[![LangChain](https://a11ybadges.com/badge?text=LangChain&badgeColor=0834ac)](https://www.langchain.com/)
[![Amazon AWS](https://a11ybadges.com/badge?logo=amazonaws)](https://aws.amazon.com/)
[![ReactJS](https://a11ybadges.com/badge?logo=react)](https://react.dev/)
[![Python](https://a11ybadges.com/badge?logo=python)](https://www.python.org/)
[![Terraform](https://a11ybadges.com/badge?logo=terraform)](https://www.terraform.io/)<br>
[![12-Factor](https://img.shields.io/badge/12--Factor-Compliant-green.svg)](./doc/Twelve_Factor_Methodology.md)
![Unit Tests](https://github.com/FullStackWithLawrence/aws-openai/actions/workflows/testsPython.yml/badge.svg?branch=main)
![GHA pushMain Status](https://img.shields.io/github/actions/workflow/status/FullStackWithLawrence/aws-openai/pushMain.yml?branch=main)
![Auto Assign](https://github.com/FullStackwithLawrence/aws-openai/actions/workflows/auto-assign.yml/badge.svg)
[![Release Notes](https://img.shields.io/github/release/FullStackWithLawrence/aws-openai)](https://github.com/FullStackWithLawrence/aws-openai/releases)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![hack.d Lawrence McDaniel](https://img.shields.io/badge/hack.d-Lawrence%20McDaniel-orange.svg)](https://lawrencemcdaniel.com)

A [React](https://react.dev/) + [AWS Serverless](https://aws.amazon.com/serverless/) full stack implementation of the [30 example applications](https://platform.openai.com/examples) found in the official OpenAI API documentation. This repository is used as an instructional tool for the YouTube channel "[Full Stack With Lawrence](https://youtube.com/@FullStackWithLawrence)" as well as for University of British Columbia course, "[Artificial Intelligence Cloud Technology Implementation](https://extendedlearning.ubc.ca/courses/artificial-intelligence-cloud-technology-implementation/mg202)" taught by Lawrence McDaniel.

![Marv](https://cdn.lawrencemcdaniel.com/marv.gif)

**IMPORTANT DISCLAIMER: AWS' Lambda service has a hard 29-second timeout. OpenAI API calls often take longer than this, in which case the AWS API Gateway endpoint will return a 504 "Gateway timeout error" response to the React client. This happens frequently with apps created using chatgpt-4. Each of the 30 OpenAI API example applications are nonetheless implemented exactly as they are specified in the official documentation.**

Code composition as of Dec-2023:

```console
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
Markdown                        50            739              6           2357
HCL                             23            296            574           1948
Python                          14            352            369           1306
YAML                            19            109            101           1077
JavaScript                      39            112            126           1074
JSX                              5             37             41            771
CSS                              5             31             14            172
make                             1             22             32             82
INI                              2             15              0             69
HTML                             2              1              0             65
Text                             3              3              0             56
Jupyter Notebook                 1              0            186             48
Bourne Shell                     4             10             44             32
TOML                             1              3              0             32
Dockerfile                       1              4              4              7
-------------------------------------------------------------------------------
SUM:                           170           1734           1497           9096
-------------------------------------------------------------------------------
```

## ReactJS chat application

Complete documentation is located [here](./client/).

React app that leverages [Vite.js](https://github.com/FullStackWithLawrence/aws-openai), [@chatscope/chat-ui-kit-react](https://www.npmjs.com/package/@chatscope/chat-ui-kit-react), and [react-pro-sidebar](https://www.npmjs.com/package/react-pro-sidebar).

### Webapp Key features

- robust, highly customizable chat features
- A component model for implementing your own highly personalized OpenAI apps
- Skinnable UI for each app
- Includes default assets for each app
- Small compact code base
- Robust error handling for non-200 response codes from the custom REST API
- Handles direct text input as well as file attachments
- Info link to the OpenAI API official code sample
- Build-deploy managed with Vite

## Custom OpenAI REST API Backend

Complete documentation is located [here](./api/).

A REST API implementing each of the [30 example applications](https://platform.openai.com/examples) from the official [OpenAI API Documentation](https://platform.openai.com/docs/api-reference/making-requests?lang=python) using a modularized Terraform approach. Leverages OpenAI's suite of AI models, including [GPT-3.5](https://platform.openai.com/docs/models/gpt-3-5), [GPT-4](https://platform.openai.com/docs/models/gpt-4), [DALL·E](https://platform.openai.com/docs/models/dall-e), [Whisper](https://platform.openai.com/docs/models/whisper), [Embeddings](https://platform.openai.com/docs/models/embeddings), and [Moderation](https://platform.openai.com/docs/models/moderation).

### API Key features

- [OpenAI API](https://pypi.org/project/openai/) library for Python. [LangChain](https://www.langchain.com/) enabled API endpoints where designated.
- [Pydantic](https://docs.pydantic.dev/latest/) based CI-CD friendly [Settings](./api/terraform/python/openai_api/common/README.md) configuration class that consistently and automatically manages Python Lambda initializations from multiple sources including bash environment variables, `.env` and `terraform.tfvars` files.
- [CloudWatch](https://aws.amazon.com/cloudwatch/) logging
- [Terraform](https://www.terraform.io/) fully automated and [parameterized](./api/terraform/terraform.tfvars) build. Usually builds your infrastructure in less than a minute.
- Secure: uses AWS role-based security and custom IAM policies. Best practice handling of secrets and sensitive data in all environments (dev, test, CI-CD, prod). Proxy-based API that hides your OpenAI API calls and credentials. Runs on https with AWS-managed SSL/TLS certificate.
- Excellent [documentation](./doc/)
- [AWS serverless](https://aws.amazon.com/serverless/) implementation. Free or nearly free in most cases
- Deploy to a custom domain name

## Requirements

- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git). _pre-installed on Linux and macOS_
- [make](https://gnuwin32.sourceforge.net/packages/make.htm). _pre-installed on Linux and macOS._
- [AWS account](https://aws.amazon.com/)
- [AWS Command Line Interface](https://aws.amazon.com/cli/)
- [Terraform](https://www.terraform.io/).
  _If you're new to Terraform then see [Getting Started With AWS and Terraform](./doc/TERRAFORM_GETTING_STARTED_GUIDE.md)_
- [OpenAI platform API key](https://platform.openai.com/).
  _If you're new to OpenAI API then see [How to Get an OpenAI API Key](./doc/OPENAI_API_GETTING_STARTED_GUIDE.md)_
- [Python 3.11](https://www.python.org/downloads/): for creating virtual environment used for building AWS Lambda Layer, and locally by pre-commit linters and code formatters.
- [NodeJS](https://nodejs.org/en/download): used with NPM for local ReactJS developer environment, and for configuring/testing Semantic Release.
- [Docker Compose](https://docs.docker.com/compose/install/): used by an automated Terraform process to create the AWS Lambda Layer for OpenAI and LangChain.

## Documentation

Detailed documentation for each endpoint is available here: [Documentation](./doc/examples/)

## Support

To get community support, go to the official [Issues Page](https://github.com/FullStackWithLawrence/aws-rekognition/issues) for this project.

## Good Coding Best Practices

This project demonstrates a wide variety of good coding best practices for managing mission-critical cloud-based micro services in a team environment, namely its adherence to [12-Factor Methodology](./doc/Twelve_Factor_Methodology.md). Please see this [Code Management Best Practices](./doc/GOOD_CODING_PRACTICE.md) for additional details.

We want to make this project more accessible to students and learners as an instructional tool while not adding undue code review workloads to anyone with merge authority for the project. To this end we've also added several pre-commit code linting and code style enforcement tools, as well as automated procedures for version maintenance of package dependencies, pull request evaluations, and semantic releases.

## Contributing

We welcome contributions! There are a variety of ways for you to get involved, regardless of your background. In addition to Pull requests, this project would benefit from contributors focused on documentation and how-to video content creation, testing, community engagement, and stewards to help us to ensure that we comply with evolving standards for the ethical use of AI.

For developers, please see:

- the [Developer Setup Guide](./doc/CONTRIBUTING.md)
- and these [commit comment guidelines](./doc/SEMANTIC_VERSIONING.md) 😬😬😬 for managing CI rules for automated semantic releases.

You can also contact [Lawrence McDaniel](https://lawrencemcdaniel.com/contact) directly.
