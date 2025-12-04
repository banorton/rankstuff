"""
Pydantic models for chart visualization data.
"""

from pydantic import BaseModel


class AlgorithmScore(BaseModel):
    """Scores for each candidate under one algorithm."""
    algorithm: str
    winner: str
    scores: dict[str, float]


class AlgorithmComparisonChart(BaseModel):
    """Chart showing how different algorithms produce different winners."""
    title: str
    description: str
    source_url: str
    data: list[AlgorithmScore]


class OptionDistribution(BaseModel):
    """Distribution of rankings for one option."""
    option: str
    first: int
    second: int
    third: int


class VoteDistributionChart(BaseModel):
    """Chart showing how often each option is ranked 1st, 2nd, 3rd."""
    title: str
    description: str
    source_url: str
    data: list[OptionDistribution]
