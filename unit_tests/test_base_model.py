import pytest
from base_model import (
    normalize_mixed_text,
    force_json_closure,
    ProductReviewGap,
    ContentGapAnalysisResult
)
from pydantic import ValidationError


#  Test normalize_mixed_text
def test_normalize_mixed_text_spaces():
    text = "Hello   world!"
    assert normalize_mixed_text(text) == "Hello world!"


def test_normalize_mixed_text_mixed_lang():
    text = "hello world"
    assert normalize_mixed_text(text) == "World"


#  Test force_json_closure
def test_force_json_closure_valid_json():
    text = "some text {\"key\": \"value\"} some more"
    result = force_json_closure(text)
    assert result == '{"key": "value"}'


def test_force_json_closure_no_json():
    text = "no json here"
    result = force_json_closure(text)
    assert result == "{}"


#  Test ProductReviewGap
def test_product_review_gap_valid():
    gap = ProductReviewGap(
        product_name="Test Product",
        review_mentions=["Good sound"],
        missing_in_description=["Battery life"]
    )
    assert gap.product_name == "Test Product"


def test_product_review_gap_empty_name():
    with pytest.raises(ValidationError):
        ProductReviewGap(
            product_name="   ",
            review_mentions=["Something"],
            missing_in_description=["Missing"]
        )


#  Test ContentGapAnalysisResult
def test_content_gap_analysis_valid():
    data = {
        "common_features": ["Shared feature"],
        "unique_features": {
            "Product A": ["Unique feature"]
        },
        "customer_gaps": [
            {
                "product_name": "Product A",
                "review_mentions": ["Good thing"],
                "missing_in_description": ["Missing detail"]
            }
        ],
        "marketing_insight": "Focus marketing on sound quality"
    }
    result = ContentGapAnalysisResult(**data)
    assert result.marketing_insight.startswith("Focus")


def test_content_gap_analysis_inconsistent_product():
    data = {
        "common_features": ["Shared feature"],
        "unique_features": {
            "Product A": ["Unique feature"]
        },
        "customer_gaps": [
            {
                "product_name": "Product B",
                "review_mentions": ["Good thing"],
                "missing_in_description": ["Missing detail"]
            }
        ],
        "marketing_insight": "Focus marketing on sound quality"
    }
    with pytest.raises(ValidationError):
        ContentGapAnalysisResult(**data)

# === To run the tests, navigate to the "tests" directory or specify a test file, then run: pytest ===

