from pydantic import BaseModel, Field
from typing import List


class Structure(BaseModel):
    tldr: str = Field(description="generate a too long; didn't read summary")
    motivation: str = Field(description="describe the motivation in this paper")
    method: str = Field(description="method of this paper")
    result: str = Field(description="result of this paper")
    conclusion: str = Field(description="conclusion of this paper")


class ResearchProfile(BaseModel):
    """Research profile structure for paper relevance scoring"""
    field: str = Field(description="Main research field (in English)")
    field_keywords: List[str] = Field(description="Related keywords for the research field")
    pain_points: List[str] = Field(description="Current research pain points/challenges")
    methods: List[str] = Field(description="Research methods and techniques used")
    keywords: List[str] = Field(description="Extended technical keywords")