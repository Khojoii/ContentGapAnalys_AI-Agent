"""## connect to OpenAI gpt API
To connect to the OpenAI GPT API, we utilized [AvalAi](https://avalai.ir/). After signing in, we generated an API key specifically for our project.
"""

from langchain_openai import ChatOpenAI,OpenAI
from langchain_community.callbacks import get_openai_callback

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello world!"},
]
model_name = "gpt-4o-mini" # in this case we want to use gpt-4o-mini


llm = ChatOpenAI(
    model=model_name,
    base_url="https://api.avalai.ir/v1",
    temperature=None,
    max_tokens=3800, #token limiter
    timeout=None,
    max_retries=0,



    api_key="aa-***"
)
# this is testing the API connection and tracking token usage
print("Testing OpenAI API connection...")
with get_openai_callback() as cb:
  response = llm.invoke(messages)
  print(cb)
  print("----------------------")

"""## Creating a pydantic class for better output format"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Dict


class ProductReviewGap(BaseModel):
    """Represents gaps and review mentions for a single product."""
    product_name: str = Field(description="Name of the product")
    review_mentions: List[str] = Field(..., description="Features or topics mentioned by customers in reviews")
    missing_in_description: List[str] = Field(..., description="Features mentioned in reviews but missing from product description (content gaps)")
    # product name must not be empty
    @field_validator("product_name")
    def validate_product_name(cls, v):
        """Ensure product name is not empty or only whitespace."""
        if not v.strip():
            raise ValueError("product_name cannot be empty or whitespace")
        return v


class ContentGapAnalysisResult(BaseModel):
    """Main model for the content gap analysis result."""
    common_features: List[str] = Field(..., description="Features common to all products")
    unique_features: Dict[str, List[str]] = Field(..., description="Unique features for each product; dictionary key = product name")
    customer_gaps: List[ProductReviewGap] = Field(..., description="List of gaps and review mentions for each product")
    marketing_insight: str = Field(description="A simple, business-oriented summary for the marketing team")
    #key feild must not be empty
    @field_validator("marketing_insight")
    def validate_not_empty(cls, v, info):
        """Ensure marketing insight is not empty."""
        if not v or not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty")
        return v
    #Checking the compatibility of product names between different parts
    @model_validator(mode="after")
    def validate_product_consistency(self):
        """Ensure all products in customer_gaps exist in unique_features."""
        if self.unique_features and self.customer_gaps:
            product_names_from_unique = set(self.unique_features.keys())
            product_names_from_gaps = {gap.product_name for gap in self.customer_gaps}
            missing = product_names_from_gaps - product_names_from_unique
            if missing:
                raise ValueError(
                    f"Products in customer_gaps not found in unique_features: {', '.join(missing)}"
                )
        return self

"""## Translating the key words for Farsi output (if needed)"""

# KEY_MAP = {
#     "نام_محصول": "product_name",
#     "اشارات_در_نقد": "review_mentions",
#     "مفقود_در_توضیحات": "missing_in_description",
#     "ویژگی‌های_مشترک": "common_features",
#     "ویژگی‌های_منحصر_به_فرد": "unique_features",
#     "شکاف‌های_مشتری": "customer_gaps",
#     "بینش_بازاریابی": "marketing_insight",
#     "between_marketing_insights": "marketing_insight"
# }

# def translate_keys(data):
#     if isinstance(data, dict):
#         return {KEY_MAP.get(k, k): translate_keys(v) for k, v in data.items()}
#     elif isinstance(data, list):
#         return [translate_keys(item) for item in data]
#     return data

import re

def force_json_closure(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.S)
    if match:
        return match.group()
    return "{}"
# better output format with EN-FA sentences
def normalize_mixed_text(text: str) -> str:
    text = re.sub(r'[\u200c\s]+', ' ', text)
    text = re.sub(r'\s+([,.!?;:])', r'\1', text)
    text = re.sub(r'([،؛؟])\s*', r'\1 ', text)
    text = re.sub(r'([آ-ی])([A-Za-z0-9])', r'\1 \2', text)
    text = re.sub(r'([A-Za-z0-9])([آ-ی])', r'\1 \2', text)
    text = re.sub(r'\(\s+', '(', text)
    text = re.sub(r'\s+\)', ')', text)
    return text.strip()

"""# Prompting The Model"""

import json
from pydantic import ValidationError

def analyze_content_gaps(input_file: str, output_file: str ):
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    messages = [
    {
        "role": "system",
        "content": """
You are an AI assistant specialized in **Content Gap Analysis**.

Your task is to compare **product descriptions** and **customer reviews**, and then identify **common features**, **unique features**, **customer gaps**, and **marketing insights**.

You will analyze and reason in English, but your **final output JSON must be entirely in Persian (Farsi)** — including all field names and text values.

### Output Format (follow this schema exactly, but translated into Persian)

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

### Strict Rules

1. **Common Features**
   - Identify **core characteristics** that appear in *every* product description.
   - These are the most **fundamental and shared qualities** across all products.
   - If even one product does **not** mention a feature, **exclude** it — only keep features that are *universally consistent*.
   - Think of this section as what defines the “common identity” of the product line.

2. **Unique Features**
   - Identify **exclusive attributes** that belong *only* to a specific product and are **not mentioned in any others**.
   - These are the points that **differentiate** one product from another and make it stand out.
   - Exclude anything shared between two or more products — this section must highlight **true uniqueness**.
   - **Crucially, every product name listed in 'customer_gaps' must also appear as a key in this 'unique_features' dictionary.**

3. **Customer Gaps**
   - For each product, analyze customer reviews to find **topics, features, or expectations** customers talk about.
   - List those topics in `"review_mentions"`.
   - In `"missing_in_description"`, include **only** the items that appear in reviews but are **absent from that product’s description**.
   - These represent **unmet informational needs** — what customers wanted to know or expected to see but didn’t find in the official product description.

4. **Missing In Description**
   - In this section, explain only the topics or details that were found in customer reviews but missing from the product description.

5. **Marketing Insight**
   - Write **3–4 concise sentences (in Persian)** summarizing the main findings.
   - Highlight what aspects of the product could be **better communicated**, **emphasized**, or **clarified** in marketing materials.
   - Suggest how emphasizing certain **features**, **keywords**, or **benefits** could make the product descriptions more **useful**, **appealing**, and **customer-focused**.

### Output Requirements

- The response must be a **valid JSON object** (parsable with `json.loads()`).
- Do **not** include any explanations, comments, or text outside the JSON.
- Always use **double quotes** for all keys and string values.
- Make sure arrays `[]` and objects `{}` are properly closed.
- The number of products is not always constant.
- If a product has no reviews, set its customer_gaps list to empty.
- Double-check that no feature is missing, even if it's not strongly emphasized in the text.
- The input file language may be Persian or English.
- Remember: even though you think in English, the final JSON output file and its contents must be written in **Persian (Farsi)**.
"""
    },

          #Example for better performance

         {
  "role": "user",
  "content": """
Products:

Western Digital My Passport External Hard Drive, 1TB Capacity (digikala):

Description:
The My Passport external hard drive by Western Digital connects to your computer via a USB 3.0 interface and helps you store data at high speed. The capacity of this drive is 1 terabyte, making it a great option for users with large storage needs. The My Passport external hard drive is compatible with all common operating systems, including various versions of Windows. It comes in multiple colors, offering suitable choices for every taste. The fourth generation of My Passport drives entered the market in 2019 with a beautiful design. Data transfer speed reaches up to 5 gigabits per second. Notably, the lightweight design makes it easy to carry, and its rotation speed is 5400 RPM.

Reviews:
- "Friends, can this hard drive connect to a mobile phone? Android?"
- "Hi, does it support Xbox Series S?"
- "Hello, which company provides the warranty, and is it valid?"

Western Digital My Passport External Hard Drive, 1TB Capacity (technolife):

Description:
Weight: 122.4 grams
Dimensions: 107.2 × 75 × 11.2 mm
Interface: USB 3.0
Capacity: 1 TB
Head Size: 2.5 inches
Data Transfer Speed: 5 Gbps
LED Indicator: No
Other Features: Automatic backup via software, password protection for security, AES 256-bit encryption support

Reviews:
- "Excuse me, can it be used with Windows 11?"
- "Hi, I wanted to know if it can connect to a MacBook?"
- "Good morning, I’m a videographer — do you think a 1TB external hard drive is enough for Instagram videos?"

Western Digital My Passport External Hard Drive, 1TB Capacity (arbabashop):

Description:
Review of WD My Passport 1TB External Hard Drive
The Western Digital My Passport 1TB is one of the most popular and best-selling portable hard drives on the market. With its compact and lightweight design, it’s an ideal choice for those looking for a secure space to store personal, work, or backup data. WD has long been recognized as one of the most reputable storage device manufacturers, and the My Passport series is among its flagship products.

Design and Build:
Compact and lightweight body, perfect for daily carrying
Available in various colors for different preferences
Uses Micro-B port (compatible with USB 3.2 Gen 1 and USB 2.0)
Good build quality with anti-slip design to prevent sliding on surfaces

Technical Specifications:
Storage Capacity: 1 TB
Connection Interface: USB 3.2 Gen 1 (up to 5 Gbps)
Security: Hardware AES 256-bit encryption + password protection
Software: WD Backup, WD Discovery, WD Security for management and backup
Dimensions: 107 × 75 × 11 mm
Weight: ~120 g
Warranty: 3 years

Performance and Speed:
According to tests, data transfer speed:
Read: around 120–135 MB/s
Write: around 110–125 MB/s
This speed is excellent for a hard drive of this type and allows easy storage of videos, photos, music, and large files.

Advantages:
- Affordable and economical price for its capacity
- Lightweight and portable design
- Hardware encryption support for data security
- WD management and backup software
- Compatible with both Windows and macOS
"""
},
         #using own data
         {"role": "user","content": content}
    ]

    response = None
    try:
        with get_openai_callback() as cb:
            response = llm.invoke(messages)

        print(cb)  # token usage stats

        cleaned = force_json_closure(response.content.strip())
        data = json.loads(cleaned)
        result = ContentGapAnalysisResult(**data)

        with open(output_file, 'w', encoding="utf-8") as f:
            json.dump(result.model_dump(by_alias=True), f, indent=2, ensure_ascii=False)

        print("---------")
        print(f"✅ Result successfully saved to {output_file}")

    except ValidationError as e:
        print("\n Model output does not match expected structure!")
        print("-" * 40)
        print(" Error details:")
        print(e.errors())
        print("-" * 40)
        print(" Raw model output:\n", response.content)

    except Exception as e:
        print("\n An unexpected error occurred!")
        print("-" * 40)
        print(" Error details:", repr(e))
        print("-" * 40)
        print(" Raw model output:\n", response.content)

#----# FastAPI server to handle file uploads and analysis requests----
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import os
import json
app = FastAPI()

input_file = None
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE_PATH = os.path.join(BASE_PATH, "input.json")

# post request to upload input file
@app.post("/input")
async def upload_text(file: UploadFile = File(...)):
    """Upload a .txt file and store its content as input.json"""
    try:
        contents = await file.read()
        text = contents.decode("utf-8").strip()

        if not text:
            return JSONResponse(
                content={"error": "The uploaded file is empty ❌"}, status_code=400
            )

        with open(INPUT_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(text)

        return {"status": "ok", "filename": file.filename}

    except Exception as e:
        return JSONResponse(
            content={"error": f"Failed to save file: {str(e)} ❌"},
            status_code=500
        )
#get request to analyze the uploaded file
@app.get("/analyze")
async def analyze_text():
    """Analyze the uploaded text"""
    try:
        if not os.path.exists(INPUT_FILE_PATH):
            return JSONResponse(
                content={"error": "No file has been uploaded yet ❌"}, status_code=400
            )

        # calling the analysis function
        result = analyze_content_gaps(INPUT_FILE_PATH, "output.json")

        return {"status": "ok", "result": result}

    except Exception as e:
        return JSONResponse(
            content={"error": f"Internal error during analysis: {str(e)} ❌"},
            status_code=500
        )
