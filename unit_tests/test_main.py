import os
import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app, INPUTS_FOLDER, OUTPUTS_FOLDER, get_next_index_file

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup_folders(tmp_path):
    """Use tmp_path for inputs and outputs to avoid touching real folders."""
    os.makedirs(INPUTS_FOLDER, exist_ok=True)
    os.makedirs(OUTPUTS_FOLDER, exist_ok=True)
    yield
    # Clean up after test
    for folder in [INPUTS_FOLDER, OUTPUTS_FOLDER]:
        for f in os.listdir(folder):
            os.remove(os.path.join(folder, f))

def test_upload_text_success():
    """Test uploading a valid text file."""
    test_text = "This is a test file."
    files = {"file": ("test.txt", test_text, "text/plain")}
    response = client.post("/input", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert os.path.exists(data["saved_path"])


@patch("main.analyze_content_gaps")
def test_analyze_text_success(mock_analyze):
    """Test analysis endpoint with a valid input file."""
    # Create a dummy input file
    input_file_path = get_next_index_file(INPUTS_FOLDER, "input")
    with open(input_file_path, "w", encoding="utf-8") as f:
        f.write("Dummy product data")
    
    # Make mock create the output file
    def mock_func(input_file, output_file):
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("{}")  # empty JSON
    mock_analyze.side_effect = mock_func

    response = client.get("/analyze")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert os.path.exists(data["output_file"])
    # === To run the tests, navigate to the "tests" directory or specify a test file, then run: pytest ===