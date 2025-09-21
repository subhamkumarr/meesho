"""Database models for CatalogAI."""

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import json


class Scan(SQLModel, table=True):
    """Model for storing image scan results."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(index=True)
    size: int = Field(description="File size in bytes")
    mime_type: str = Field(description="MIME type of the uploaded file")
    score: float = Field(description="Synthetic probability score (0-1)")
    label: str = Field(description="Classification label: authentic/suspicious/synthetic")
    reasons: str = Field(description="JSON array of reasoning explanations")
    features_hash: str = Field(description="Hash of extracted features for reproducibility")
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    def get_reasons_list(self) -> list[str]:
        """Parse reasons JSON string to list."""
        try:
            return json.loads(self.reasons)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_reasons_list(self, reasons_list: list[str]):
        """Set reasons from list to JSON string."""
        self.reasons = json.dumps(reasons_list)


class ThresholdConfig(SQLModel, table=True):
    """Model for storing threshold configuration."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    thresh_auth: float = Field(description="Threshold for authentic classification")
    thresh_syn: float = Field(description="Threshold for synthetic classification")
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: str = Field(default="system", description="Who updated the thresholds")
    
    __tablename__ = "threshold_config"