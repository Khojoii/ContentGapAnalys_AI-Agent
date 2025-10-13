# Content Gap Analysis AI Agent

**An AI-powered agent that identifies missing or weak content in product descriptions across multiple sources.**

---

## Overview

**Content Gap Analysis AI Agent** is designed to help e-commerce businesses, marketing teams, and content creators analyze product descriptions more intelligently.  
By comparing similar products from different sources, the agent automatically extracts:

- **Common features** shared among all products  
- **Unique features** specific to each source  
- **Customer content gaps** — features mentioned in reviews but missing from descriptions  

It then generates a **marketing insight summary** to guide content improvement and product positioning.

---

## How It Works

1. **Input**  
   Provide multiple product descriptions and reviews (in English or Persian) in a structured formated named "input.txt" file.

2. **Processing**  
   The AI model analyzes product features, compares descriptions, and identifies overlaps or missing points.

3. **Output**  
   The result is a validated json file name "output.json" containing:
   - `common_features`
   - `unique_features`
   - `customer_gaps`
   - `marketing_insight`

---

## Technologies Used

- **Python 3.11+**
- **Pydantic** – for data validation and structured output  
- **Regex (re)** – for text normalization  
- **OpenAI GPT API** – provides advanced natural language understanding and semantic comparison capabilities


---

## Examples

You can check an example input and output file here:  
[example_input.txt](example_input.txt) , [example_output.json](example_output.json)


## Found a Bug?

If you encounter an issue or want to suggest an improvement, please submit it via the **Issues** tab.

#

