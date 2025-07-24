#!/usr/bin/env python3
"""
Data models and validation schemas for Claude Memory API.
Implements the memory document structure from the execution plan.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import re


class MemoryDocument(BaseModel):
    """Memory document schema according to execution plan"""
    id: Optional[str] = None
    content: str = Field(..., min_length=1, max_length=50000, description="Full conversation summary")
    title: str = Field(..., min_length=1, max_length=200, description="Extracted title")
    date: str = Field(..., description="Session date in YYYY-MM-DD format")
    source: str = Field(..., description="Source interface")
    technologies: List[str] = Field(default_factory=list, description="Technologies mentioned")
    file_paths: List[str] = Field(default_factory=list, description="File paths referenced")
    complexity: str = Field(..., description="Complexity level")
    project: Optional[str] = Field(None, max_length=100, description="Project name")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @validator('date')
    def validate_date(cls, v):
        """Validate date format YYYY-MM-DD"""
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', v):
            raise ValueError('Date must be in YYYY-MM-DD format')
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Invalid date')
        return v

    @validator('source')
    def validate_source(cls, v):
        """Validate source is either claude_code or claude_desktop"""
        allowed_sources = ['claude_code', 'claude_desktop']
        if v not in allowed_sources:
            raise ValueError(f'Source must be one of: {allowed_sources}')
        return v

    @validator('complexity')
    def validate_complexity(cls, v):
        """Validate complexity level"""
        allowed_complexity = ['low', 'medium', 'high']
        if v not in allowed_complexity:
            raise ValueError(f'Complexity must be one of: {allowed_complexity}')
        return v

    @validator('technologies')
    def validate_technologies(cls, v):
        """Validate technologies list"""
        if len(v) > 20:
            raise ValueError('Too many technologies (max 20)')
        return v

    @validator('file_paths')
    def validate_file_paths(cls, v):
        """Validate file paths list"""
        if len(v) > 50:
            raise ValueError('Too many file paths (max 50)')
        return v


class SearchRequest(BaseModel):
    """Search request schema"""
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    max_results: Optional[int] = Field(default=3, ge=1, le=10, description="Maximum results to return")
    similarity_threshold: Optional[float] = Field(default=0.3, ge=0.0, le=1.0, description="Minimum similarity score")
    source_filter: Optional[str] = Field(None, description="Filter by source")

    @validator('source_filter')
    def validate_source_filter(cls, v):
        """Validate source filter"""
        if v is not None:
            allowed_sources = ['claude_code', 'claude_desktop']
            if v not in allowed_sources:
                raise ValueError(f'Source filter must be one of: {allowed_sources}')
        return v


class SearchResult(BaseModel):
    """Search result schema"""
    id: str = Field(..., description="Unique memory ID")
    title: str = Field(..., description="Memory title")
    similarity: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Hybrid relevance score")
    preview: str = Field(..., max_length=500, description="Content preview")
    metadata: Dict[str, Any] = Field(..., description="Memory metadata")
    source: str = Field(..., description="Source interface")
    date: str = Field(..., description="Memory date")


class AddMemoryRequest(BaseModel):
    """Add memory request schema"""
    content: str = Field(..., min_length=1, max_length=50000, description="Memory content")
    title: Optional[str] = Field(default="Untitled Memory", max_length=200, description="Memory title")
    date: Optional[str] = Field(default=None, description="Memory date (YYYY-MM-DD)")
    source: Optional[str] = Field(default="claude_desktop", description="Source interface")
    technologies: Optional[List[str]] = Field(default_factory=list, description="Technologies")
    file_paths: Optional[List[str]] = Field(default_factory=list, description="File paths")
    complexity: Optional[str] = Field(default="medium", description="Complexity level")
    project: Optional[str] = Field(default="", description="Project name")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    id: Optional[str] = Field(None, description="Custom memory ID")

    @validator('date', pre=True, always=True)
    def set_default_date(cls, v):
        """Set default date if not provided"""
        if v is None:
            return datetime.now().strftime('%Y-%m-%d')
        return v

    @validator('source')
    def validate_source(cls, v):
        """Validate source"""
        allowed_sources = ['claude_code', 'claude_desktop']
        if v not in allowed_sources:
            raise ValueError(f'Source must be one of: {allowed_sources}')
        return v

    @validator('complexity')
    def validate_complexity(cls, v):
        """Validate complexity"""
        allowed_complexity = ['low', 'medium', 'high']
        if v not in allowed_complexity:
            raise ValueError(f'Complexity must be one of: {allowed_complexity}')
        return v


class PaginationRequest(BaseModel):
    """Pagination request schema"""
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=10, ge=1, le=50, description="Items per page")


class APIResponse(BaseModel):
    """Standard API response schema"""
    success: bool = Field(..., description="Request success status")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information")
    metadata: Dict[str, Any] = Field(..., description="Response metadata")


class ErrorDetail(BaseModel):
    """Error detail schema"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional error details")


class HealthStatus(BaseModel):
    """Health status schema"""
    status: str = Field(..., description="System status")
    database: Dict[str, Any] = Field(..., description="Database status")
    api: Dict[str, Any] = Field(..., description="API information")
    performance: Optional[Dict[str, Any]] = Field(None, description="Performance metrics")


class MemoryListResponse(BaseModel):
    """Memory list response schema"""
    memories: List[Dict[str, Any]] = Field(..., description="List of memories")
    pagination: Dict[str, Any] = Field(..., description="Pagination information")


class ReindexRequest(BaseModel):
    """Reindex request schema"""
    confirm: bool = Field(..., description="Confirmation flag")
    backup: Optional[bool] = Field(default=True, description="Create backup before reindex")


# Validation utility functions
def validate_memory_data(data: dict) -> MemoryDocument:
    """Validate and convert memory data to MemoryDocument"""
    return MemoryDocument(**data)


def validate_search_request(data: dict) -> SearchRequest:
    """Validate and convert search request data"""
    return SearchRequest(**data)


def validate_add_memory_request(data: dict) -> AddMemoryRequest:
    """Validate and convert add memory request data"""
    return AddMemoryRequest(**data)


# Constants for validation
ALLOWED_SOURCES = ['claude_code', 'claude_desktop']
ALLOWED_COMPLEXITY = ['low', 'medium', 'high']
MAX_SEARCH_RESULTS = 10
MAX_MEMORY_CONTENT_LENGTH = 50000
MAX_TECHNOLOGIES = 20
MAX_FILE_PATHS = 50