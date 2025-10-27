# Content Gap Analysis AI Agent - FastAPI

**An AI agent that identifies missing or weak content in product descriptions across multiple sources via a FastAPI web service.**

---

## Overview

**Content Gap Analysis AI Agent** helps e-commerce businesses, marketing teams, and content creators analyze product descriptions more intelligently.  
By comparing similar products from different sources, the agent automatically extracts:

- **Common features** shared among all products  
- **Unique features** specific to each source  
- **Customer content gaps** — features mentioned in reviews but missing from descriptions  

It then generates a **marketing insight summary** to guide content improvement and product positioning.

---

## How It Works

1. **Upload File**  
   Use the `/input` endpoint to upload a `.json` file containing product descriptions and reviews.

2. **Analyze Content**  
   Call the `/analyze` endpoint to process the uploaded text. The AI agent compares product features, identifies overlaps, and finds missing points.

3. **Output**  
   The result is returned as JSON containing:
   - `common_features`
   - `unique_features`
   - `customer_gaps`
   - `marketing_insight`

---

## API Endpoints

| Method | Endpoint     | Description |
|--------|-------------|-------------|
| POST   | `/input`    | Upload a `.json` file containing product data. Returns status |
| GET    | `/analyze`  | Analyze the uploaded text. Returns JSON with content gaps and marketing insights. |

---

## Technologies Used

- **Python 3.11+**
- **FastAPI** – serve API endpoints  
- **Pydantic** – data validation and structured output  
- **Regex (re)** – text normalization  
- **OpenAI GPT API** – semantic comparison and content analysis  

---

## Project Structure
```
content-gap-analyzer/
│
├── .env                          # Environment variables (API keys, configuration settings)
├── agent.py                      # Core logic that communicates with the API and performs content analysis
├── base_model.py                 # Pydantic models for data validation and structured responses
├── logger.py                     # Central logging system (saves logs with timestamps)
├── main.py                       # FastAPI application entry point (defines endpoints for upload & analysis)
├── requirements.txt              # List of Python dependencies
│
├── logs/                         # Automatically created folder for log files
│   └── log_YYYY-MM-DD_HH-MM-SS.log
│
├── I_O/                          # Input/Output data folder
│   ├── inputs/                   # Input files (e.g., product data)
│   │   └── input.json
│   └── outputs/                  # Output files (e.g., model analysis results)
│       └── output.json
│
└── unit_tests/                   # Unit tests for each module
    ├── test_agent.py             # Tests for agent logic
    ├── test_base_model.py        # Tests for Pydantic models
    ├── test_logger.py            # Tests for logging functionality
    └── test_main.py              # Tests for FastAPI endpoint

```

## How to use 

## 1. Setting up the Project Environment

First, you need to create a **Python virtual environment (venv)** and install all dependencies. Follow these steps:
### 1-1. Navigate to your project folder
```bash
cd path/to/your/project
```
### 1-2. Create a virtual environment (named myenv)
```bash
python -m venv myenv
```
### 1-3. Make sure the requirements.txt file is in the same folder

### 1-4. Activate the virtual environment

> [!IMPORTANT]
> note that every time you want to run the app you should activate the venv

### On Windows:
```bash
. Scripts\activate
```

### On Linux / macOS:
```bash
source myenv/bin/activate
```
### 1-5. Install all dependencies
```bash
pip install -r requirements.txt
```
## 2. Run the app
### in a terminal in your venv, run the app via uvicorn:
```bash
uvicorn yourfilename:app --reload
```
## 3. test the app
You can test your FastAPI app using one of these three methods:

### 3-1. Using `curl` (command line)
Upload a file:
```bash
curl -X POST "http://127.0.0.1:8000/input" -F "file=@yourfile.json"
```
Analyze the uploaded file:
```
curl -X GET "http://127.0.0.1:8000/analyze"
```
### 3-2. Using [Postman](https://www.postman.com/)(Recommended)

Open Postman.

To upload a file (/input endpoint):

Select POST method at the top.

Set URL:
```bash
http://127.0.0.1:8000/input
```
- Go to the Body tab and select form-data.

- Add a field named file and set type to File.
 
- Click Select Files and choose your .txt file.

- Click Send.

- The server response will show below (status).

- To analyze the uploaded text (/analyze endpoint):

- Open a new tab and select GET method.

Set URL:
```bash
http://127.0.0.1:8000/analyze
```

- Click Send.

- Then the result will save to your project Directory

### 3-3. Using Swagger UI

Open your browser and go to:
```bash
http://127.0.0.1:8000/docs
```

- You’ll see the Swagger UI page with all available endpoints.

- Upload a file (/input endpoint):

- Click on POST /input to expand it.

- Click the “Try it out” button (top-right of the endpoint box).

- In the file field, click “Choose File” and select your .txt file.

- Click Execute.

- The response section below will show the status and text length.

- Analyze uploaded text (/analyze endpoint):

- Click on GET /analyze to expand it.

- Click “Try it out”, then Execute.

## Examples

You can check an example input and output file here:  
[example_input.txt](example_input.txt) , [example_output.json](example_output.json)


## Found a Bug?

If you encounter an issue or want to suggest an improvement, please submit it via the **Issues** tab.




