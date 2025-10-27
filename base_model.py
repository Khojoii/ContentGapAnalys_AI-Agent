# Python standard libraries
import re
from typing import List, Dict
# external libraries
from pydantic import BaseModel, Field, field_validator, model_validator
# internal modules
from logger import get_logger

logger = get_logger()

class ProductReviewGap(BaseModel):
    """Represents gaps and review mentions for a single product."""
    product_name: str = Field(description="Name of the product")
    review_mentions: List[str] = Field(..., description="Features or topics mentioned by customers in reviews")
    missing_in_description: List[str] = Field(..., description="Features mentioned in reviews but missing from product description (content gaps)")

    @field_validator("product_name")
    def validate_product_name(cls, v):
        """Ensure product name is not empty or only whitespace."""
        if not v.strip():
            logger.warning("Empty product_name detected in ProductReviewGap")
            raise ValueError("product_name cannot be empty or whitespace")
        logger.info(f"Validated product_name: {v}")
        return v


class ContentGapAnalysisResult(BaseModel):
    """Main model for the content gap analysis result."""
    common_features: List[str] = Field(..., description="Features common to all products")
    unique_features: Dict[str, List[str]] = Field(..., description="Unique features for each product; dictionary key = product name")
    customer_gaps: List[ProductReviewGap] = Field(..., description="List of gaps and review mentions for each product")
    marketing_insight: str = Field(description="A simple, business-oriented summary for the marketing team")

    @field_validator("marketing_insight")
    def validate_not_empty(cls, v, info):
        """Ensure marketing insight is not empty."""
        if not v or not v.strip():
            logger.warning("Empty marketing_insight detected in ContentGapAnalysisResult")
            raise ValueError(f"{info.field_name} cannot be empty")
        logger.info("Validated marketing_insight")
        return v

    @model_validator(mode="after")
    def validate_product_consistency(self):
        """Ensure all products in customer_gaps exist in unique_features."""
        if self.unique_features and self.customer_gaps:
            product_names_from_unique = set(self.unique_features.keys())
            product_names_from_gaps = {gap.product_name for gap in self.customer_gaps}
            missing = product_names_from_gaps - product_names_from_unique
            if missing:
                logger.error(f"Products in customer_gaps not found in unique_features: {', '.join(missing)}")
                raise ValueError(
                    f"Products in customer_gaps not found in unique_features: {', '.join(missing)}"
                )
            logger.info("Product consistency validated successfully")
        return self
    

def force_json_closure(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.S)
    if match:
        logger.debug("JSON closure detected in text")
        return match.group()
    logger.warning("No JSON object found in text, returning empty dict")
    return "{}"


def normalize_mixed_text(text: str) -> str:
    """Normalize text mixing English and Persian for better formatting."""
    text = re.sub(r'[\u200c\s]+', ' ', text)
    text = re.sub(r'\s+([,.!?;:])', r'\1', text)
    text = re.sub(r'([،؛؟])\s*', r'\1 ', text)
    text = re.sub(r'([آ-ی])([A-Za-z0-9])', r'\1 \2', text)
    text = re.sub(r'([A-Za-z0-9])([آ-ی])', r'\1 \2', text)
    text = re.sub(r'\(\s+', '(', text)
    text = re.sub(r'\s+\)', ')', text)
    logger.debug("Text normalized using normalize_mixed_text")
    return text.strip()
