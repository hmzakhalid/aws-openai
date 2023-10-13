// see https://github.com/FullStackWithLawrence/aws-openai/blob/main/api/terraform/apigateway_endpoints.tf#L19

import { BACKEND_API_URL, AWS_API_GATEWAY_KEY } from "../config";

const ProductNameGenerator = {
  api_url: BACKEND_API_URL + 'default-product-name-gen',
  api_key: AWS_API_GATEWAY_KEY,
  app_name: "Product Name Generator",
  assistant_name: "Pierson",
  avatar_url: '/applications/ProductNameGenerator/Pierson.svg',
  background_image_url: '/applications/ProductNameGenerator/ProductNameGenerator-bg.avif',
  welcome_message: `Hello, I'm Pierson, and I create a list of potential product names based on your input.`,
  example_prompts: [
    'We make everlasting gobstoppers',
    'a time travel machine',
  ],
  placeholder_text: `tell Pierson about your product`,
};

export default ProductNameGenerator;
