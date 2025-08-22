#!/usr/bin/env python3
"""
AI-Powered Response Analyzer for AISEO Insights
Analyzes LLM responses to understand why certain companies/products are mentioned
"""

import os
import csv
import json
from datetime import datetime
import re


class ResponseAnalyzer:
    def __init__(self):
        self.csv_path = os.getenv('ANALYSIS_CSV_PATH', 'analysis_results.csv')
        self.analysis_model = os.getenv('ANALYSIS_MODEL', 'gpt-4.1')
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.analyze_enabled = os.getenv('ANALYZE_RESPONSES', 'false').lower() == 'true'
        
        # Initialize CSV if it doesn't exist
        if self.analyze_enabled:
            self._initialize_csv()
    
    def _initialize_csv(self):
        """Create CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.csv_path):
            headers = [
                'timestamp',
                'query',
                'provider',
                'companies_mentioned',
                'mention_reasons',
                'authority_signals',
                'key_features',
                'sources_cited',
                'ranking_factors',
                'sentiment',
                'optimization_insights'
            ]
            
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            
            print(f"[OK] Created analysis CSV: {self.csv_path}")
    
    def analyze_with_ai(self, response_text, query, provider):
        """Use AI to analyze response and extract AISEO insights"""
        
        if not self.analyze_enabled:
            return None
        
        # Convert response to string for analysis
        response_str = str(response_text)
        
        analysis_prompt = f"""Analyze this AI response for SEO/AISEO optimization insights.

Extract the following information in JSON format:

1. companies_mentioned: List all companies/brands/products mentioned
2. mention_reasons: For each company, why was it mentioned? (features, authority, popularity, etc.)
3. authority_signals: Authority phrases used (e.g., "leading", "popular", "trusted", "industry standard")
4. key_features: What features/benefits were highlighted as important?
5. sources_cited: Any sources, websites, or references mentioned
6. ranking_factors: What seems to determine the order/prominence of mentions?
7. sentiment: Overall sentiment toward mentioned entities (positive/neutral/negative)
8. optimization_insights: Specific actionable tips for AISEO based on this response

Original Query: {query}
Provider: {provider}

Response to analyze:
{response_str}

Return ONLY valid JSON with these exact keys. Be specific and actionable in optimization_insights."""
        
        try:
            # Use OpenAI to analyze
            import openai
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key)
            
            # Escape problematic characters in the response text
            # Truncate very long responses to avoid token limits
            if len(response_str) > 5000:
                response_str = response_str[:5000] + "... [truncated for analysis]"
            
            response = client.chat.completions.create(
                model=self.analysis_model,
                messages=[
                    {"role": "system", "content": "You are an AI optimization expert analyzing responses for AISEO insights. Always return valid JSON."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=4000,
                temperature=0.3,  # Lower temperature for more consistent analysis
                response_format={"type": "json_object"}  # Force JSON response
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse JSON from response
            # Handle potential markdown code blocks
            if '```json' in analysis_text:
                analysis_text = analysis_text.split('```json')[1].split('```')[0]
            elif '```' in analysis_text:
                analysis_text = analysis_text.split('```')[1].split('```')[0]
            
            # Try to parse JSON, with better error handling
            try:
                analysis = json.loads(analysis_text.strip())
            except json.JSONDecodeError as je:
                print(f"[WARNING] JSON parse error, attempting to fix: {je}")
                # Try to fix common JSON issues
                fixed_text = analysis_text.strip()
                # Remove any trailing commas
                fixed_text = re.sub(r',\s*}', '}', fixed_text)
                fixed_text = re.sub(r',\s*]', ']', fixed_text)
                analysis = json.loads(fixed_text)
            
            # Ensure all required fields are present
            required_fields = {
                'companies_mentioned': [],
                'mention_reasons': {},
                'authority_signals': [],
                'key_features': [],
                'sources_cited': [],
                'ranking_factors': '',
                'sentiment': 'neutral',
                'optimization_insights': ''
            }
            
            # Merge with defaults
            for field, default in required_fields.items():
                if field not in analysis:
                    analysis[field] = default
            
            # Add metadata
            analysis['timestamp'] = datetime.now().isoformat()
            analysis['query'] = query
            analysis['provider'] = provider
            
            return analysis
            
        except Exception as e:
            print(f"[ERROR] Analysis failed for {provider}: {e}")
            return self._get_fallback_analysis(response_str, query, provider)
    
    def _get_fallback_analysis(self, response_text, query, provider):
        """Basic analysis without AI when API fails"""
        
        # Simple pattern matching for companies and keywords
        text_lower = response_text.lower() if isinstance(response_text, str) else str(response_text).lower()
        
        # Common company patterns
        companies = []
        company_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Capitalized words
            r'\b(?:Inc|Corp|LLC|Ltd|Company)\b',  # Company suffixes
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, response_text if isinstance(response_text, str) else str(response_text))
            companies.extend(matches[:5])  # Limit to avoid noise
        
        # Authority signals
        authority_signals = []
        authority_words = ['leading', 'popular', 'trusted', 'best', 'top', 'industry', 'standard', 'widely']
        for word in authority_words:
            if word in text_lower:
                authority_signals.append(word)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'provider': provider,
            'companies_mentioned': list(set(companies))[:10],
            'mention_reasons': {'extracted': 'Fallback analysis - AI unavailable'},
            'authority_signals': authority_signals,
            'key_features': [],
            'sources_cited': [],
            'ranking_factors': 'Analysis unavailable',
            'sentiment': 'neutral',
            'optimization_insights': 'AI analysis unavailable - manual review recommended'
        }
    
    def save_to_csv(self, analysis_data):
        """Append analysis results to CSV file"""
        
        if not self.analyze_enabled or not analysis_data:
            return
        
        try:
            with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Convert complex fields to JSON strings
                row = [
                    analysis_data.get('timestamp', datetime.now().isoformat()),
                    analysis_data.get('query', ''),
                    analysis_data.get('provider', ''),
                    json.dumps(analysis_data.get('companies_mentioned', [])),
                    json.dumps(analysis_data.get('mention_reasons', {})),
                    json.dumps(analysis_data.get('authority_signals', [])),
                    json.dumps(analysis_data.get('key_features', [])),
                    json.dumps(analysis_data.get('sources_cited', [])),
                    analysis_data.get('ranking_factors', ''),
                    analysis_data.get('sentiment', 'neutral'),
                    analysis_data.get('optimization_insights', '')
                ]
                
                writer.writerow(row)
                
        except Exception as e:
            print(f"[ERROR] Failed to save to CSV: {e}")
    
    def display_insights(self, analysis_data):
        """Display key insights from analysis"""
        
        if not analysis_data:
            return
        
        print(f"\n[{analysis_data.get('provider', 'Unknown')}] Analysis Insights:")
        print("-" * 40)
        
        companies = analysis_data.get('companies_mentioned', [])
        if companies:
            print(f"Companies mentioned: {', '.join(companies[:5])}")
        
        signals = analysis_data.get('authority_signals', [])
        if signals:
            print(f"Authority signals: {', '.join(signals[:5])}")
        
        insights = analysis_data.get('optimization_insights', '')
        if insights and insights != 'AI analysis unavailable - manual review recommended':
            # Handle both string and list/dict insights
            if isinstance(insights, str):
                print(f"Optimization tips: {insights[:200]}...")
            else:
                print(f"Optimization tips: {str(insights)[:200]}...")
        
        print()