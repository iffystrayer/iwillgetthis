"""Advanced search service for full-text search across platform data"""

import logging
from typing import List, Dict, Any, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import text, or_, and_, func, desc, asc
from datetime import datetime

from models.risk import Risk
from models.asset import Asset
from models.assessment import Assessment
from models.evidence import Evidence
from models.task import Task
from models.framework import Framework, Control
from models.user import User

logger = logging.getLogger(__name__)

class SearchService:
    """Advanced search service with full-text search capabilities"""
    
    def __init__(self):
        # Define searchable entities and their fields
        self.searchable_entities = {
            'risks': {
                'model': Risk,
                'fields': ['title', 'description', 'category', 'mitigation_strategy', 'owner'],
                'display_fields': ['id', 'title', 'description', 'category', 'level', 'status', 'owner'],
                'url_pattern': '/risks/{id}'
            },
            'assets': {
                'model': Asset,
                'fields': ['name', 'description', 'asset_type', 'location', 'owner'],
                'display_fields': ['id', 'name', 'description', 'asset_type', 'criticality', 'owner'],
                'url_pattern': '/assets/{id}'
            },
            'assessments': {
                'model': Assessment,
                'fields': ['name', 'description', 'scope', 'methodology'],
                'display_fields': ['id', 'name', 'description', 'status', 'assessment_type'],
                'url_pattern': '/assessments/{id}'
            },
            'evidence': {
                'model': Evidence,
                'fields': ['name', 'description', 'file_name', 'content_summary'],
                'display_fields': ['id', 'name', 'description', 'evidence_type', 'file_name'],
                'url_pattern': '/evidence/{id}'
            },
            'tasks': {
                'model': Task,
                'fields': ['title', 'description', 'assigned_to'],
                'display_fields': ['id', 'title', 'description', 'status', 'priority', 'assigned_to'],
                'url_pattern': '/tasks/{id}'
            },
            'frameworks': {
                'model': Framework,
                'fields': ['name', 'description', 'version'],
                'display_fields': ['id', 'name', 'description', 'version', 'framework_type'],
                'url_pattern': '/frameworks/{id}'
            },
            'controls': {
                'model': Control,
                'fields': ['control_id', 'name', 'description', 'guidance'],
                'display_fields': ['id', 'control_id', 'name', 'description', 'category'],
                'url_pattern': '/controls/{id}'
            }
        }
        
        # Search result relevance scoring weights
        self.relevance_weights = {
            'exact_match': 10.0,
            'title_match': 8.0,
            'description_match': 5.0,
            'field_match': 3.0,
            'partial_match': 1.0
        }
    
    def global_search(
        self, 
        db: Session, 
        query: str, 
        entities: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0,
        user: Optional[User] = None
    ) -> Dict[str, Any]:
        """Perform global search across all searchable entities"""
        
        if not query or len(query.strip()) < 2:
            return {
                'query': query,
                'total_results': 0,
                'results_by_entity': {},
                'top_results': [],
                'search_time_ms': 0
            }
        
        start_time = datetime.now()
        
        # Sanitize query
        clean_query = query.strip()
        search_terms = clean_query.lower().split()
        
        # Filter entities to search
        entities_to_search = entities if entities else list(self.searchable_entities.keys())
        entities_to_search = [e for e in entities_to_search if e in self.searchable_entities]
        
        results_by_entity = {}
        all_results = []
        total_results = 0
        
        for entity_type in entities_to_search:
            try:
                entity_results = self._search_entity(
                    db, entity_type, clean_query, search_terms, limit, user
                )
                
                if entity_results:
                    results_by_entity[entity_type] = entity_results
                    all_results.extend([{**r, 'entity_type': entity_type} for r in entity_results])
                    total_results += len(entity_results)
                    
            except Exception as e:
                logger.error(f"Error searching {entity_type}: {e}")
                continue
        
        # Sort all results by relevance score
        all_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Apply global pagination
        top_results = all_results[offset:offset + limit]
        
        search_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return {
            'query': clean_query,
            'total_results': total_results,
            'results_by_entity': results_by_entity,
            'top_results': top_results,
            'search_time_ms': search_time_ms,
            'entities_searched': entities_to_search
        }
    
    def _search_entity(
        self, 
        db: Session, 
        entity_type: str, 
        query: str, 
        search_terms: List[str],
        limit: int,
        user: Optional[User] = None
    ) -> List[Dict[str, Any]]:
        """Search within a specific entity type"""
        
        entity_config = self.searchable_entities[entity_type]
        model = entity_config['model']
        fields = entity_config['fields']
        display_fields = entity_config['display_fields']
        
        # Build search query
        base_query = db.query(model)
        
        # Add user-based filtering if needed (for security)
        if user and hasattr(model, 'created_by'):
            # For now, allow all users to search all data
            # In the future, you might want to add role-based filtering
            pass
        
        # Build WHERE conditions for full-text search
        conditions = []
        
        for field in fields:
            if hasattr(model, field):
                field_attr = getattr(model, field)
                
                # Exact match condition (highest score)
                conditions.append(field_attr.ilike(f'%{query}%'))
                
                # Individual term matching
                for term in search_terms:
                    if len(term) > 2:  # Avoid very short terms
                        conditions.append(field_attr.ilike(f'%{term}%'))
        
        if not conditions:
            return []
        
        # Apply WHERE clause with OR conditions
        search_query = base_query.filter(or_(*conditions))
        
        # Execute query with limit
        try:
            results = search_query.limit(limit * 2).all()  # Get more for scoring
        except Exception as e:
            logger.error(f"Database query error for {entity_type}: {e}")
            return []
        
        # Score and format results
        formatted_results = []
        for result in results:
            try:
                score = self._calculate_relevance_score(result, query, search_terms, fields)
                
                # Build result dictionary
                result_dict = {
                    'relevance_score': score,
                    'url': entity_config['url_pattern'].format(id=result.id),
                    'entity_type': entity_type,
                    'highlight': self._generate_highlight(result, query, search_terms, fields)
                }
                
                # Add display fields
                for field in display_fields:
                    if hasattr(result, field):
                        value = getattr(result, field)
                        # Handle datetime objects
                        if isinstance(value, datetime):
                            value = value.isoformat()
                        result_dict[field] = value
                
                formatted_results.append(result_dict)
                
            except Exception as e:
                logger.error(f"Error formatting result for {entity_type}: {e}")
                continue
        
        # Sort by relevance and limit
        formatted_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return formatted_results[:limit]
    
    def _calculate_relevance_score(
        self, 
        result: Any, 
        query: str, 
        search_terms: List[str], 
        fields: List[str]
    ) -> float:
        """Calculate relevance score for search result"""
        
        score = 0.0
        query_lower = query.lower()
        
        for field in fields:
            if not hasattr(result, field):
                continue
                
            field_value = getattr(result, field)
            if not field_value:
                continue
                
            field_lower = str(field_value).lower()
            
            # Exact match bonus
            if query_lower == field_lower:
                score += self.relevance_weights['exact_match']
            elif query_lower in field_lower:
                # Full query match
                if field == 'title' or field == 'name':
                    score += self.relevance_weights['title_match']
                elif field == 'description':
                    score += self.relevance_weights['description_match']
                else:
                    score += self.relevance_weights['field_match']
            
            # Individual term matching
            term_matches = 0
            for term in search_terms:
                if len(term) > 2 and term in field_lower:
                    term_matches += 1
            
            if term_matches > 0:
                score += (term_matches / len(search_terms)) * self.relevance_weights['partial_match']
        
        return round(score, 2)
    
    def _generate_highlight(
        self, 
        result: Any, 
        query: str, 
        search_terms: List[str], 
        fields: List[str]
    ) -> str:
        """Generate highlighted snippet for search result"""
        
        query_lower = query.lower()
        
        # Try to find the best field with matches
        best_match = ""
        best_score = 0
        
        for field in fields:
            if not hasattr(result, field):
                continue
                
            field_value = getattr(result, field)
            if not field_value:
                continue
                
            field_str = str(field_value)
            field_lower = field_str.lower()
            
            # Count matches in this field
            matches = 0
            if query_lower in field_lower:
                matches += 10  # Full query match
            
            for term in search_terms:
                if len(term) > 2 and term in field_lower:
                    matches += 1
            
            if matches > best_score:
                best_score = matches
                best_match = field_str
        
        if not best_match:
            # Fallback to first available field
            for field in fields:
                if hasattr(result, field) and getattr(result, field):
                    best_match = str(getattr(result, field))
                    break
        
        # Truncate and return highlight
        if len(best_match) > 200:
            # Try to find a good truncation point near query matches
            truncated = best_match[:200]
            if query_lower in truncated.lower():
                return truncated + "..."
            else:
                # Find first term match
                for term in search_terms:
                    term_pos = best_match.lower().find(term)
                    if term_pos > 0:
                        start = max(0, term_pos - 100)
                        end = min(len(best_match), term_pos + 100)
                        return "..." + best_match[start:end] + "..."
                
                # No matches found, just truncate
                return truncated + "..."
        
        return best_match
    
    def search_suggestions(
        self, 
        db: Session, 
        partial_query: str, 
        limit: int = 10
    ) -> List[str]:
        """Get search suggestions based on partial query"""
        
        if not partial_query or len(partial_query) < 2:
            return []
        
        suggestions = set()
        partial_lower = partial_query.lower()
        
        # Search in common fields across entities
        suggestion_queries = [
            # Risk titles and categories
            db.query(Risk.title).filter(Risk.title.ilike(f'%{partial_query}%')).limit(5),
            db.query(Risk.category).filter(Risk.category.ilike(f'%{partial_query}%')).distinct().limit(3),
            
            # Asset names and types
            db.query(Asset.name).filter(Asset.name.ilike(f'%{partial_query}%')).limit(5),
            db.query(Asset.asset_type).filter(Asset.asset_type.ilike(f'%{partial_query}%')).distinct().limit(3),
            
            # Assessment names
            db.query(Assessment.name).filter(Assessment.name.ilike(f'%{partial_query}%')).limit(5),
            
            # Evidence names
            db.query(Evidence.name).filter(Evidence.name.ilike(f'%{partial_query}%')).limit(5),
            
            # Framework names
            db.query(Framework.name).filter(Framework.name.ilike(f'%{partial_query}%')).limit(3),
        ]
        
        for query in suggestion_queries:
            try:
                results = query.all()
                for result in results:
                    if result and result[0]:
                        suggestion = str(result[0]).strip()
                        if suggestion.lower().startswith(partial_lower):
                            suggestions.add(suggestion)
            except Exception as e:
                logger.error(f"Error getting suggestions: {e}")
                continue
        
        # Convert to sorted list
        suggestion_list = sorted(list(suggestions))[:limit]
        return suggestion_list
    
    def advanced_search(
        self, 
        db: Session,
        entity_type: str,
        filters: Dict[str, Any],
        user: Optional[User] = None
    ) -> List[Dict[str, Any]]:
        """Perform advanced search with specific filters"""
        
        if entity_type not in self.searchable_entities:
            return []
        
        entity_config = self.searchable_entities[entity_type]
        model = entity_config['model']
        display_fields = entity_config['display_fields']
        
        query = db.query(model)
        
        # Apply filters
        for field, value in filters.items():
            if hasattr(model, field) and value is not None:
                field_attr = getattr(model, field)
                
                if isinstance(value, str):
                    # Text search
                    query = query.filter(field_attr.ilike(f'%{value}%'))
                elif isinstance(value, list):
                    # Multiple values (IN clause)
                    query = query.filter(field_attr.in_(value))
                elif isinstance(value, dict):
                    # Range queries
                    if 'min' in value:
                        query = query.filter(field_attr >= value['min'])
                    if 'max' in value:
                        query = query.filter(field_attr <= value['max'])
                else:
                    # Exact match
                    query = query.filter(field_attr == value)
        
        # Execute query
        try:
            results = query.limit(100).all()
        except Exception as e:
            logger.error(f"Advanced search query error: {e}")
            return []
        
        # Format results
        formatted_results = []
        for result in results:
            result_dict = {
                'entity_type': entity_type,
                'url': entity_config['url_pattern'].format(id=result.id)
            }
            
            for field in display_fields:
                if hasattr(result, field):
                    value = getattr(result, field)
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    result_dict[field] = value
            
            formatted_results.append(result_dict)
        
        return formatted_results

# Global search service instance
search_service = SearchService()