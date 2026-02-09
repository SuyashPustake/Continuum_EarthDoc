"""
Bulletproof Methodology Matcher
Simple, reliable keyword-based matching - no API calls, never fails
"""

from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class MethodologyRecommendation:
    """Methodology recommendation result"""
    methodology_id: str
    title: str
    category: str
    confidence: float
    reasons: List[str]


class MethodologyMatcher:
    """Ultra-reliable methodology matcher using keywords only"""
    
    # Comprehensive keyword mappings for all 10 Verra methodologies
    METHODOLOGY_KEYWORDS = {
        'VM0038': {
            'keywords': ['ev', 'electric vehicle', 'charging', 'charger', 'evse', 'mobility', 'transport electrification', 'charge point'],
            'confidence_base': 95
        },
        'VM0047': {
            'keywords': ['afforestation', 'tree planting', 'forest restoration', 'reforestation', 'plantation', 'forestry', 'tree'],
            'confidence_base': 95
        },
        'VM0048': {
            'keywords': ['redd', 'deforestation', 'forest conservation', 'avoided deforestation', 'forest protection', 'degradation'],
            'confidence_base': 95
        },
        'VM0042': {
            'keywords': ['agriculture', 'soil', 'cropland', 'grassland', 'improved land management', 'carbon sequestration', 'farming'],
            'confidence_base': 90
        },
        'VM0033': {
            'keywords': ['livestock', 'manure', 'animal waste', 'methane', 'enteric fermentation', 'cattle', 'dairy'],
            'confidence_base': 90
        },
        'AMS-III.E': {
            'keywords': ['cookstove', 'cooking', 'clean cooking', 'biomass', 'efficient stove', 'household energy', 'kitchen'],
            'confidence_base': 95
        },
        'VMR0006': {
            'keywords': ['wetland', 'mangrove', 'seagrass', 'blue carbon', 'coastal', 'tidal', 'marine', 'marsh'],
            'confidence_base': 95
        },
        'VM0043': {
            'keywords': ['concrete', 'cement', 'co2 utilization', 'mineralization', 'carbon cure', 'building material'],
            'confidence_base': 95
        },
        'AMS-I.D': {
            'keywords': ['solar', 'wind', 'renewable', 'grid', 'electricity generation', 'photovoltaic', 'pv', 'turbine'],
            'confidence_base': 90
        },
        'VM0044': {
            'keywords': ['biochar', 'pyrolysis', 'biomass conversion', 'carbon removal', 'charcoal'],
            'confidence_base': 90
        }
    }
    
    def __init__(self, methodology_database: Dict):
        """Initialize matcher with methodology database"""
        self.methodology_db = methodology_database
    
    def recommend(self, project_description: str, top_k: int = 3) -> List[MethodologyRecommendation]:
        """
        Recommend methodologies based on project description
        ALWAYS returns results - never fails
        """
        if not project_description or len(project_description.strip()) < 10:
            return self._get_defaults(top_k)
        
        desc_lower = project_description.lower()
        scores = {}
        match_details = {}
        
        # Score each methodology
        for method_id, config in self.METHODOLOGY_KEYWORDS.items():
            matched_keywords = []
            score = 0
            
            for keyword in config['keywords']:
                if keyword in desc_lower:
                    matched_keywords.append(keyword)
                    # Weight: longer keywords = higher confidence
                    score += config['confidence_base'] / len(config['keywords'])
            
            if matched_keywords:
                scores[method_id] = min(score, 100)  # Cap at 100
                match_details[method_id] = matched_keywords
        
        # If no matches, return defaults
        if not scores:
            return self._get_defaults(top_k)
        
        # Sort by score
        sorted_methods = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Build recommendations
        recommendations = []
        for method_id, score in sorted_methods[:top_k]:
            if method_id in self.methodology_db:
                method = self.methodology_db[method_id]
                keywords_matched = match_details.get(method_id, [])
                reasons = [f"Matched: '{kw}'" for kw in keywords_matched[:3]]
                
                recommendations.append(MethodologyRecommendation(
                    methodology_id=method_id,
                    title=method['title'],
                    category=method.get('category', 'Unknown'),
                    confidence=score,
                    reasons=reasons if reasons else ['Keyword match']
                ))
        
        # Fill remaining slots with defaults
        while len(recommendations) < top_k:
            defaults = self._get_defaults(top_k - len(recommendations))
            for default in defaults:
                if default.methodology_id not in [r.methodology_id for r in recommendations]:
                    recommendations.append(default)
            break
        
        return recommendations[:top_k]
    
    def _get_defaults(self, count: int) -> List[MethodologyRecommendation]:
        """Return default popular methodologies"""
        defaults = ['VM0038', 'VM0047', 'AMS-I.D', 'VM0048', 'VM0042']
        recommendations = []
        
        for method_id in defaults[:count]:
            if method_id in self.methodology_db:
                method = self.methodology_db[method_id]
                recommendations.append(MethodologyRecommendation(
                    methodology_id=method_id,
                    title=method['title'],
                    category=method.get('category', 'Unknown'),
                    confidence=50.0,
                    reasons=['Popular methodology']
                ))
        
        return recommendations
