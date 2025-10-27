#  connect to OpenAI gpt API
# To connect to the OpenAI GPT API, we utilized https://avalai.ir. After signing in, we generated an API key specifically for our project.

# Python standard libraries
import os
import json
# external libraries
from dotenv import load_dotenv
from pydantic import ValidationError
from langchain_openai import ChatOpenAI, OpenAI
from langchain_community.callbacks import get_openai_callback
# Internal project libraries
from base_model import ContentGapAnalysisResult, force_json_closure,normalize_mixed_text
from logger import get_logger

logger = get_logger()

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("API key not found in .env file!")
    raise ValueError("API key not found in .env file!")


llm = ChatOpenAI(
    model="gpt-4o-mini", # in this case we want to use gpt-4o-mini
    base_url="https://api.avalai.ir/v1",
    temperature=None,
    max_tokens=3800, #token limiter
    timeout=None,
    max_retries=0,
    api_key=OPENAI_API_KEY)


# testing the API connection and tracking token usage
try:
    logger.info("Testing OpenAI API connection...")
    with get_openai_callback() as cb:
        test_response = llm.invoke([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello world!"}
        ])
        logger.info(cb)
        logger.info("OpenAI API test successful")

except Exception as e:
    logger.error(f"OpenAI API test failed: {repr(e)}")
    raise

# Prompting The Model


def analyze_content_gaps(input_file: str, output_file: str ):
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    messages = [
    {
        "role": "system",
        "content": """
You are an AI assistant specialized in **Content Gap Analysis**.
Task:
- Compare product descriptions and customer reviews.
- Identify common features,unique features,customer gaps, and marketing insights.
Output Format:
{
"common_features": ["..."],
"unique_features": {
  "Product_Name_1": ["..."],
  "Product_Name_2": ["..."]
},
"customer_gaps": [
  {
    "product_name": "...",
    "review_mentions": ["..."],
    "missing_in_description": ["..."]
  }
],
"marketing_insight": "..."
}
Rules:
1. Analyze in English, but output must be in Persian(just values not field names).
2. Common features: Only those appearing in all products.
3. Unique features: Only features exclusive to a product; must match product names in 'customer_gaps'.
4. Customer gaps: List review topics; 'missing_in_description' shows what is absent from product description.
5. Marketing insight: 3-4 short sentences in Persian summarizing key points and what features/benefits should be highlighted.
6. The response must be a valid JSON.
7. Do not include any text outside the JSON.
8. use double quotes for all keys and string values."""},

         #using own data
         {"role": "user","content": content}
    ]

    response = None
    try:
        with get_openai_callback() as cb:
            response = llm.invoke(messages)
            logger.info(cb)

        logger.info("")
        cleaned_text = normalize_mixed_text(response.content.strip())
        cleaned_json = force_json_closure(cleaned_text)
        data = json.loads(cleaned_json)
        result = ContentGapAnalysisResult(**data)

        with open(output_file, 'w', encoding="utf-8") as f:
            json.dump(result.model_dump(by_alias=True), f, indent=2, ensure_ascii=False)


    except ValidationError as ve:
        logger.error("Model output does not match expected structure!")
        logger.error(ve.json())
        logger.error(f"Raw model output: {response.content if response else 'No response'}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error: {repr(e)}")
        logger.error(f"Raw model output: {response.content if response else 'No response'}")
        raise
