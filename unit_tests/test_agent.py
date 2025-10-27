import json
import pytest
from unittest.mock import patch, MagicMock
from agent import analyze_content_gaps

@pytest.fixture
def sample_input_file(tmp_path):
    content = """
Products:
Product A:
Description:
- Lightweight design
- Long battery life
Reviews:
- "Battery lasts long but charges slowly."
- "Comfortable to use."

Product B:
Description:
- Fast charging
- Sturdy build
Reviews:
- "Very durable."
- "Charges quickly, battery drains faster."
"""
    file_path = tmp_path / "input.txt"
    file_path.write_text(content, encoding="utf-8")
    return file_path

@pytest.fixture
def output_file(tmp_path):
    return tmp_path / "output.json"

@patch("agent.llm.__call__")
def test_analyze_content_gaps_success(mock_call, sample_input_file, output_file):
    """Test analyze_content_gaps with mocked ChatOpenAI __call__."""
    # Mock API response
    mock_response = MagicMock()
    mock_response.content = json.dumps({
        "common_features": ["Battery"],
        "unique_features": {
            "Product A": ["Lightweight design"],
            "Product B": ["Fast charging"]
        },
        "customer_gaps": [
            {
                "product_name": "Product A",
                "review_mentions": ["Battery"],
                "missing_in_description": ["Charging"]
            }
        ],
        "marketing_insight": "Focus on battery life and design improvements."
    })
    mock_call.return_value = mock_response

    # Run the function
    analyze_content_gaps(str(sample_input_file), str(output_file))

    # Verify output file was created
    assert output_file.exists(), "Output file should be created"

    # Verify JSON structure
    data = json.loads(output_file.read_text(encoding="utf-8"))
    assert "common_features" in data
    assert "unique_features" in data
    assert "customer_gaps" in data
    assert "marketing_insight" in data
    assert isinstance(data["customer_gaps"], list)
# === To run the tests, navigate to the "tests" directory or specify a test file, then run: pytest ===