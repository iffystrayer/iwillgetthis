"""Pydantic schemas for search API"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class SearchResult(BaseModel):
    """Individual search result"""
    id: int
    entity_type: str
    url: str
    relevance_score: float
    highlight: str
    # Additional fields will be added dynamically based on entity type

class GlobalSearchResponse(BaseModel):
    """Response schema for global search"""
    query: str
    total_results: int
    results_by_entity: Dict[str, List[Dict[str, Any]]]
    top_results: List[Dict[str, Any]]
    search_time_ms: int
    entities_searched: List[str]

class SearchSuggestionResponse(BaseModel):
    """Response schema for search suggestions"""
    query: str
    suggestions: List[str]

class AdvancedSearchRequest(BaseModel):
    """Request schema for advanced search"""
    entity_type: str = Field(..., description="Entity type to search")
    filters: Dict[str, Any] = Field(..., description="Search filters")

class AdvancedSearchResponse(BaseModel):
    """Response schema for advanced search"""
    entity_type: str
    filters: Dict[str, Any]
    total_results: int
    results: List[Dict[str, Any]]

class SearchStatsResponse(BaseModel):
    """Response schema for search statistics"""
    period_days: int
    total_searches: int
    searches_by_entity: Dict[str, int]
    popular_search_terms: List[Dict[str, Any]]
    average_daily_searches: float