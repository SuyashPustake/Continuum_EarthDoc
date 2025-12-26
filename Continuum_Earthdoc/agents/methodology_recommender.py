"""
Enhanced Methodology Recommendation System
Uses semantic embeddings, LLM-based matching, and domain-specific analysis
to provide accurate methodology recommendations based on project descriptions
"""

import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Gemini integration for embeddings and LLM
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Import METHODOLOGY_DATABASE - will be passed in or imported dynamically
METHODOLOGY_DATABASE = None


@dataclass
class MethodologyMatch:
    """Represents a methodology match with scoring"""
    methodology_id: str
    title: str
    category: str
    confidence_score: float
    match_reasons: List[str]
    applicability_score: float
    domain_alignment: float
    detailed_analysis: str


class EnhancedMethodologyRecommender:
    """
    Advanced methodology recommendation system using:
    1. Semantic embeddings for domain understanding
    2. LLM-based analysis for deep project understanding
    3. Multi-factor scoring (applicability, domain fit, technical match)
    4. Context-aware ranking
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None, methodology_database: Optional[Dict] = None):
        """Initialize the recommender"""
        self.api_key = gemini_api_key or os.environ.get('GOOGLE_API_KEY')
        self.ai_enabled = GEMINI_AVAILABLE and self.api_key is not None
        
        if self.ai_enabled:
            genai.configure(api_key=self.api_key)
            self.client = genai
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            # For embeddings, use the embedding model
            self.embedding_model = 'models/text-embedding-004'  # Gemini embedding model
        else:
            self.client = None
            self.model = None
            self.embedding_model = None
        
        # Get methodology database
        global METHODOLOGY_DATABASE
        if methodology_database:
            self.methodology_db = methodology_database
        elif METHODOLOGY_DATABASE:
            self.methodology_db = METHODOLOGY_DATABASE
        else:
            # Try to import it
            try:
                import sys
                import importlib
                # Import pdd_agent module to get METHODOLOGY_DATABASE
                from agents import pdd_agent
                self.methodology_db = pdd_agent.METHODOLOGY_DATABASE
            except Exception as e:
                print(f"Warning: Could not load METHODOLOGY_DATABASE: {e}")
                self.methodology_db = {}
        
        # Build methodology embeddings cache
        self._methodology_embeddings = None
        self._build_methodology_profiles()
    
    def _build_methodology_profiles(self):
        """Build rich profiles for each methodology for matching"""
        self.methodology_profiles = {}
        
        for mid, method in self.methodology_db.items():
            # Create comprehensive profile text for semantic matching
            profile_text = f"""
            Methodology: {method['id']} - {method['title']}
            Category: {method['category']}
            Description: {method['description']}
            Applicability: {', '.join(method.get('applicability', []))}
            Sectoral Scopes: {', '.join(map(str, method.get('sectoral_scopes', [])))}
            Key Parameters: {', '.join([p.get('name', '') for p in method.get('key_parameters', [])])}
            """
            
            # Extract keywords and domain indicators
            keywords = self._extract_keywords(method)
            
            self.methodology_profiles[mid] = {
                'text': profile_text,
                'keywords': keywords,
                'category': method.get('category', ''),
                'sectoral_scopes': method.get('sectoral_scopes', []),
                'applicability': method.get('applicability', []),
                'description': method.get('description', ''),
                'title': method.get('title', '')
            }
    
    def _extract_keywords(self, method: Dict) -> List[str]:
        """Extract relevant keywords from methodology"""
        keywords = []
        
        # From title
        title_words = method.get('title', '').lower().split()
        keywords.extend([w for w in title_words if len(w) > 3])
        
        # From description
        desc = method.get('description', '').lower()
        important_terms = [
            'ev', 'electric vehicle', 'charging', 'forest', 'tree', 'deforestation',
            'redd', 'agriculture', 'soil', 'waste', 'compost', 'cookstove',
            'renewable', 'solar', 'wind', 'biochar', 'wetland', 'mangrove',
            'seagrass', 'blue carbon', 'concrete', 'cement', 'livestock'
        ]
        for term in important_terms:
            if term in desc:
                keywords.append(term)
        
        # From applicability
        for app in method.get('applicability', []):
            words = app.lower().split()
            keywords.extend([w for w in words if len(w) > 4])
        
        return list(set(keywords))
    
    def recommend_methodologies(
        self, 
        project_description: str,
        top_k: int = 5,
        use_llm: bool = True
    ) -> List[MethodologyMatch]:
        """
        Recommend methodologies based on project description
        
        Args:
            project_description: Natural language description of the project
            top_k: Number of top recommendations to return
            use_llm: Whether to use LLM for deep analysis (requires API key)
        
        Returns:
            List of MethodologyMatch objects sorted by confidence score
        """
        if not project_description or len(project_description.strip()) < 10:
            return []
        
        # Step 1: Semantic similarity matching
        semantic_matches = self._semantic_similarity_match(project_description)
        
        # Step 2: Keyword-based matching (fallback or enhancement)
        keyword_matches = self._keyword_based_match(project_description)
        
        # Step 3: LLM-based deep analysis (if enabled)
        if self.ai_enabled and use_llm:
            llm_analysis = self._llm_analyze_project(project_description)
            semantic_matches = self._combine_with_llm_analysis(semantic_matches, llm_analysis)
        
        # Step 4: Multi-factor scoring
        scored_matches = self._multi_factor_scoring(
            project_description,
            semantic_matches,
            keyword_matches
        )
        
        # Step 5: Rank and return top K
        ranked = sorted(scored_matches, key=lambda x: x.confidence_score, reverse=True)
        return ranked[:top_k]
    
    def _semantic_similarity_match(self, project_desc: str) -> Dict[str, float]:
        """Use embeddings to find semantically similar methodologies"""
        if not self.ai_enabled or not self.embedding_model:
            return {}
        
        try:
            # Get embedding for project description using Gemini
            project_embedding_result = genai.embed_content(
                model=self.embedding_model,
                content=project_desc,
                task_type="retrieval_document"
            )
            project_embedding = project_embedding_result['embedding']
            
            # Calculate similarity with each methodology
            similarities = {}
            for mid, profile in self.methodology_profiles.items():
                # Get methodology embedding
                method_embedding_result = genai.embed_content(
                    model=self.embedding_model,
                    content=profile['text'],
                    task_type="retrieval_query"  # Use query type for methodology text
                )
                method_embedding = method_embedding_result['embedding']
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(project_embedding, method_embedding)
                similarities[mid] = similarity
            
            return similarities
        except Exception as e:
            print(f"Error in semantic matching: {e}")
            return {}
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import math
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _keyword_based_match(self, project_desc: str) -> Dict[str, float]:
        """Traditional keyword-based matching"""
        desc_lower = project_desc.lower()
        scores = {}
        
        for mid, profile in self.methodology_profiles.items():
            score = 0.0
            matched_keywords = []
            
            for keyword in profile['keywords']:
                if keyword in desc_lower:
                    score += 1.0
                    matched_keywords.append(keyword)
            
            # Normalize by number of keywords
            if len(profile['keywords']) > 0:
                score = score / len(profile['keywords'])
            
            if score > 0:
                scores[mid] = {
                    'score': score,
                    'matched_keywords': matched_keywords
                }
        
        return scores
    
    def _llm_analyze_project(self, project_desc: str) -> Dict[str, Any]:
        """Use LLM to deeply analyze project and extract domain information"""
        if not self.ai_enabled:
            return {}
        
        try:
            prompt = f"""
            Analyze the following carbon project description and extract key information:
            
            Project Description: {project_desc}
            
            Please provide a JSON response with:
            1. "primary_domain": The main domain/category (e.g., "Transport", "Forestry", "Energy", "Waste")
            2. "key_activities": List of main activities mentioned
            3. "technologies": Technologies or methods mentioned
            4. "location_indicators": Geographic or location-related terms
            5. "emission_sources": Sources of emissions being addressed
            6. "project_scale": Scale indicators (small, medium, large, distributed, etc.)
            7. "suitable_methodologies": List of methodology IDs that might apply (from: VM0038, VM0047, VM0048, VM0033, VM0042, VM0044, AMS-III.E, VMR0006, AMS-I.D, VM0043)
            8. "reasoning": Brief explanation of why these methodologies might apply
            
            Respond only with valid JSON.
            """
            
            # Use Gemini for LLM analysis
            full_prompt = f"""You are an expert in Verra VCS carbon project methodologies. Analyze projects and recommend appropriate methodologies.

{prompt}

Return only valid JSON."""
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=2000
                )
            )
            
            # Try to extract JSON from response
            text = response.text.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            analysis = json.loads(text)
            return analysis
        except Exception as e:
            print(f"Error in LLM analysis: {e}")
            return {}
    
    def _combine_with_llm_analysis(
        self, 
        semantic_scores: Dict[str, float],
        llm_analysis: Dict[str, Any]
    ) -> Dict[str, float]:
        """Combine semantic scores with LLM recommendations"""
        if not llm_analysis:
            return semantic_scores
        
        # Boost scores for methodologies recommended by LLM
        recommended = llm_analysis.get('suitable_methodologies', [])
        boost_factor = 1.3  # 30% boost
        
        for mid in recommended:
            if mid in semantic_scores:
                semantic_scores[mid] *= boost_factor
            else:
                semantic_scores[mid] = 0.5  # Add with moderate score
        
        return semantic_scores
    
    def _multi_factor_scoring(
        self,
        project_desc: str,
        semantic_scores: Dict[str, float],
        keyword_scores: Dict[str, Any]
    ) -> List[MethodologyMatch]:
        """Calculate multi-factor scores for each methodology"""
        matches = []
        
        # Combine all candidate methodologies
        all_methods = set(semantic_scores.keys()) | set(keyword_scores.keys())
        
        for mid in all_methods:
            if mid not in self.methodology_db:
                continue
            
            method = self.methodology_db[mid]
            profile = self.methodology_profiles[mid]
            
            # Factor 1: Semantic similarity (0-1)
            semantic_score = semantic_scores.get(mid, 0.0)
            
            # Factor 2: Keyword match (0-1)
            keyword_data = keyword_scores.get(mid, {})
            keyword_score = keyword_data.get('score', 0.0) if isinstance(keyword_data, dict) else 0.0
            matched_keywords = keyword_data.get('matched_keywords', []) if isinstance(keyword_data, dict) else []
            
            # Factor 3: Domain alignment (0-1)
            domain_score = self._calculate_domain_alignment(project_desc, profile)
            
            # Factor 4: Applicability match (0-1)
            applicability_score = self._calculate_applicability_match(project_desc, method)
            
            # Weighted combination
            weights = {
                'semantic': 0.4,
                'keyword': 0.2,
                'domain': 0.2,
                'applicability': 0.2
            }
            
            confidence = (
                semantic_score * weights['semantic'] +
                keyword_score * weights['keyword'] +
                domain_score * weights['domain'] +
                applicability_score * weights['applicability']
            )
            
            # Generate match reasons
            match_reasons = []
            if semantic_score > 0.7:
                match_reasons.append("High semantic similarity")
            if keyword_score > 0.3:
                match_reasons.append(f"Matched keywords: {', '.join(matched_keywords[:3])}")
            if domain_score > 0.7:
                match_reasons.append("Strong domain alignment")
            if applicability_score > 0.6:
                match_reasons.append("Good applicability match")
            
            # Generate detailed analysis
            detailed_analysis = self._generate_detailed_analysis(
                project_desc, method, profile, confidence
            )
            
            match = MethodologyMatch(
                methodology_id=mid,
                title=method.get('title', ''),
                category=method.get('category', ''),
                confidence_score=confidence,
                match_reasons=match_reasons,
                applicability_score=applicability_score,
                domain_alignment=domain_score,
                detailed_analysis=detailed_analysis
            )
            
            matches.append(match)
        
        return matches
    
    def _calculate_domain_alignment(self, project_desc: str, profile: Dict) -> float:
        """Calculate how well project aligns with methodology domain"""
        desc_lower = project_desc.lower()
        profile_text = profile['text'].lower()
        
        # Count domain-specific terms
        domain_terms = [
            'transport', 'vehicle', 'ev', 'electric', 'charging',
            'forest', 'tree', 'deforestation', 'redd', 'carbon stock',
            'agriculture', 'soil', 'crop', 'farming',
            'waste', 'compost', 'landfill', 'organic',
            'energy', 'renewable', 'solar', 'wind', 'grid',
            'cookstove', 'cooking', 'biomass', 'fuel',
            'wetland', 'mangrove', 'seagrass', 'coastal', 'blue carbon',
            'biochar', 'pyrolysis', 'char',
            'concrete', 'cement', 'co2', 'carbonation'
        ]
        
        matches = sum(1 for term in domain_terms if term in desc_lower and term in profile_text)
        return min(matches / 5.0, 1.0)  # Normalize to 0-1
    
    def _calculate_applicability_match(self, project_desc: str, method: Dict) -> float:
        """Calculate how well project matches methodology applicability conditions"""
        desc_lower = project_desc.lower()
        applicability = method.get('applicability', [])
        
        if not applicability:
            return 0.5  # Neutral if no applicability info
        
        # Check if project description mentions applicability-related terms
        matches = 0
        for condition in applicability:
            condition_lower = condition.lower()
            # Simple word overlap
            condition_words = set(condition_lower.split())
            desc_words = set(desc_lower.split())
            overlap = len(condition_words & desc_words)
            if overlap > 0:
                matches += 1
        
        return min(matches / len(applicability), 1.0)
    
    def _generate_detailed_analysis(
        self,
        project_desc: str,
        method: Dict,
        profile: Dict,
        confidence: float
    ) -> str:
        """Generate detailed analysis text for the match"""
        analysis = f"""
        This methodology ({method['id']}: {method['title']}) has a {confidence:.0%} match confidence.
        
        **Why this methodology applies:**
        - {method.get('description', 'N/A')}
        
        **Key Applicability Conditions:**
        {chr(10).join(['- ' + app for app in method.get('applicability', [])[:3]])}
        
        **Sectoral Scope:** {', '.join(map(str, method.get('sectoral_scopes', [])))}
        """
        
        return analysis.strip()
    
    def suggest_methodology_simple(self, project_description: str) -> List[Dict]:
        """
        Simplified interface for backward compatibility
        Returns list of dicts matching the old format
        """
        matches = self.recommend_methodologies(project_description, top_k=5)
        
        results = []
        for match in matches:
            results.append({
                "id": match.methodology_id,
                "title": match.title,
                "category": match.category,
                "match_reason": "; ".join(match.match_reasons) if match.match_reasons else f"{match.confidence_score:.0%} confidence match",
                "confidence": match.confidence_score,
                "applicability": self.methodology_db[match.methodology_id].get('applicability', []),
                "detailed_analysis": match.detailed_analysis
            })
        
        return results

