"""
Simple Context Extractor
Extracts structured information from project descriptions
"""

import os
import re
from typing import Dict, Any


class ContextExtractor:
    """Extract structured context from project description"""
    
    @staticmethod
    def extract(description: str) -> Dict[str, Any]:
        """
        Extract structured context from project description
        Uses simple, reliable pattern matching
        """
        desc_lower = description.lower()
        
        # Extract project name (first meaningful phrase)
        project_name = ContextExtractor._extract_project_name(description)
        
        # Extract location
        location = ContextExtractor._extract_location(description)
        
        # Extract project type and category
        project_type, category = ContextExtractor._extract_type_and_category(desc_lower)
        
        # Extract carbon metrics
        carbon_metrics = ContextExtractor._extract_carbon_metrics(description)
        
        # Extract technology details
        tech_details = ContextExtractor._extract_technology(description)
        
        # Extract stakeholders
        stakeholders = ContextExtractor._extract_stakeholders(description)
        
        # Determine scale based on annual reductions
        annual_reductions = carbon_metrics.get('annual_reductions') or 0
        scale = 'Large-scale' if annual_reductions > 60000 else 'Small-scale'
        
        return {
            'project_name': project_name,
            'location': location,
            'project_type': project_type,
            'category': category,
            'scale': scale,
            'carbon_metrics': carbon_metrics,
            'technology': tech_details,
            'stakeholders': stakeholders,
            'original_description': description
        }
    
    @staticmethod
    def _extract_project_name(description: str) -> str:
        """Extract or infer project name"""
        # Try to find project name patterns
        patterns = [
            r'(?:project name|called|named)\s+["\']?([^"\'\n]+)["\']?',
            r'([A-Z][A-Za-z\s]+(?:Project|Initiative|Program))',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1).strip()[:100]
        
        # Use first sentence as project name
        first_sent = description.split('.')[0].strip()
        if len(first_sent) < 100:
            return first_sent
        
        return 'Carbon Reduction Project'
    
    @staticmethod
    def _extract_location(description: str) -> Dict[str, str]:
        """Extract location information"""
        # Common countries
        countries = {
            'india': 'India', 'china': 'China', 'brazil': 'Brazil', 
            'indonesia': 'Indonesia', 'kenya': 'Kenya', 'uganda': 'Uganda',
            'tanzania': 'Tanzania', 'peru': 'Peru', 'colombia': 'Colombia',
            'mexico': 'Mexico', 'usa': 'United States', 'united states': 'United States',
            'canada': 'Canada', 'australia': 'Australia'
        }
        
        desc_lower = description.lower()
        country = ''
        
        for key, value in countries.items():
            if key in desc_lower:
                country = value
                break
        
        # Extract city names (capital letters followed by comma or common patterns)
        city_match = re.search(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),', description)
        city = city_match.group(1) if city_match else ''
        
        return {
            'country': country,
            'region': '',
            'city': city
        }
    
    @staticmethod
    def _extract_type_and_category(desc_lower: str) -> tuple:
        """Extract project type and category"""
        type_mappings = {
            ('ev', 'electric vehicle', 'charging'): ('Electric Vehicle Charging Infrastructure', 'Transport'),
            ('solar', 'photovoltaic', 'pv'): ('Solar Energy Generation', 'Energy'),
            ('wind', 'wind farm', 'wind turbine'): ('Wind Energy Generation', 'Energy'),
            ('afforestation', 'tree planting', 'reforestation'): ('Afforestation and Reforestation', 'Forestry'),
            ('redd', 'deforestation', 'forest conservation'): ('REDD+ Forest Conservation', 'Forestry'),
            ('agriculture', 'cropland', 'soil carbon'): ('Agricultural Land Management', 'Agriculture'),
            ('wetland', 'mangrove', 'seagrass'): ('Wetland Restoration', 'Blue Carbon'),
            ('cookstove', 'clean cooking'): ('Improved Cookstoves', 'Clean Cooking'),
            ('biochar',): ('Biochar Production', 'Biochar'),
            ('livestock', 'manure'): ('Livestock Management', 'Agriculture'),
            ('concrete', 'cement'): ('Concrete CO2 Utilization', 'Industrial')
        }
        
        for keywords, (ptype, category) in type_mappings.items():
            if any(kw in desc_lower for kw in keywords):
                return ptype, category
        
        return 'Carbon Reduction Project', 'Other'
    
    @staticmethod
    def _extract_carbon_metrics(description: str) -> Dict[str, float]:
        """Extract carbon reduction metrics"""
        desc_lower = description.lower()
        
        # Find numbers followed by tCO2e or similar
        annual_pattern = r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:tco2e?|tonnes?\s+co2|tons?\s+co2)(?:\s*/\s*(?:year|annum|annually))?'
        numbers = re.findall(annual_pattern, desc_lower)
        
        annual_reductions = None
        total_reductions = None
        
        if numbers:
            # First number is usually annual, second (if exists) is total
            try:
                annual_reductions = float(numbers[0].replace(',', ''))
                if len(numbers) > 1:
                    total_reductions = float(numbers[1].replace(',', ''))
            except:
                pass
        
        # Extract crediting period
        period_match = re.search(r'(\d+)\s*(?:year|yr)s?\s*(?:crediting|period)', desc_lower)
        crediting_period = int(period_match.group(1)) if period_match else 10
        
        # Calculate total if we have annual
        if annual_reductions is not None and total_reductions is None:
            total_reductions = annual_reductions * crediting_period
        
        return {
            'annual_reductions': annual_reductions or 0,  # Default to 0 if None
            'total_reductions': total_reductions or 0,    # Default to 0 if None
            'crediting_period': crediting_period
        }
    
    @staticmethod
    def _extract_technology(description: str) -> Dict[str, Any]:
        """Extract technology details"""
        # Extract numbers for capacity/count
        desc_lower = description.lower()
        
        tech_info = {'description': description[:300]}
        
        # EV specific
        if 'charging' in desc_lower or 'charger' in desc_lower:
            # Extract number of chargers
            charger_match = re.search(r'(\d+)\s*(?:public\s+)?(?:charging\s+)?stations?', desc_lower)
            if charger_match:
                tech_info['num_chargers'] = int(charger_match.group(1))
            
            # Extract Level 2 count
            l2_match = re.search(r'(\d+)\s*level\s*2', desc_lower)
            if l2_match:
                tech_info['level2_count'] = int(l2_match.group(1))
            
            # Extract DC Fast count
            dc_match = re.search(r'(\d+)\s*dc\s*fast', desc_lower)
            if dc_match:
                tech_info['dcfast_count'] = int(dc_match.group(1))
        
        return tech_info
    
    @staticmethod
    def _extract_stakeholders(description: str) -> Dict[str, str]:
        """Extract stakeholder information"""
        stakeholders = {}
        
        # Look for company/organization names (capitalized words)
        org_patterns = [
            r'(?:operated by|developed by|managed by)\s+([A-Z][A-Za-z\s&]+(?:Ltd|Inc|Corp|Corporation|Company|Pvt)?\.?)',
            r'([A-Z][A-Za-z\s&]+(?:Ltd|Inc|Corp|Corporation|Company|Pvt)\.?)\s+(?:will|is|operates)'
        ]
        
        for pattern in org_patterns:
            match = re.search(pattern, description)
            if match:
                stakeholders['project_proponent'] = match.group(1).strip()
                break
        
        return stakeholders
