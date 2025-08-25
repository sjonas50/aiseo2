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
5. sources_cited: Extract ALL sources and references, including:
   - Explicit URLs or website mentions (e.g., "investopedia.com", "https://...")
   - Named products/platforms/tools (e.g., "iShares", "Aladdin platform", "Russell Indices")
   - Industry reports or indices mentioned (e.g., "S&P 500", "Russell 2000")
   - Specific data sources or statistics cited (e.g., "according to...", "data from...")
   - Publications or media outlets referenced (e.g., "Forbes", "Wall Street Journal")
   - Research firms or rating agencies (e.g., "Morningstar", "Moody's")
   - Any parenthetical citations or footnotes
   IMPORTANT: Include ANY named entity that serves as a source of information or authority
6. ranking_factors: What seems to determine the order/prominence of mentions?
7. sentiment: Overall sentiment toward mentioned entities (positive/neutral/negative)
8. optimization_insights: Specific actionable tips for AISEO based on this response

Original Query: {query}
Provider: {provider}

Response to analyze:
{response_str}

Return ONLY valid JSON with these exact keys. For sources_cited, be comprehensive - extract anything that could be considered a source, reference, or authoritative mention. Be specific and actionable in optimization_insights."""
        
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
            
            # Post-process sources_cited to extract additional patterns
            analysis['sources_cited'] = self._extract_additional_sources(response_str, analysis.get('sources_cited', []))
            
            # Add metadata
            analysis['timestamp'] = datetime.now().isoformat()
            analysis['query'] = query
            analysis['provider'] = provider
            
            return analysis
            
        except Exception as e:
            print(f"[ERROR] Analysis failed for {provider}: {e}")
            return self._get_fallback_analysis(response_str, query, provider)
    
    def _extract_additional_sources(self, response_text, existing_sources):
        """Extract additional sources from response text that may have been missed"""
        
        response_str = response_text if isinstance(response_text, str) else str(response_text)
        text_lower = response_str.lower()
        
        # Start with existing sources
        all_sources = list(existing_sources) if existing_sources else []
        
        # Look for specific patterns that indicate sources
        patterns_to_extract = [
            # Product/Platform mentions with indicators
            (r'\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+(?:platform|index|indices|ETF|ETFs|fund|funds)\b', True),
            # Parenthetical mentions (often sources)
            (r'\(([^)]+(?:Index|Indices|Platform|System|ETF|Fund)[^)]*)\)', False),
            # "Known for" pattern often mentions products/tools
            (r'known for (?:its |their )?([A-Z][^,\.\n]+)', False),
            # Specific product patterns
            (r'\b(i[A-Z][a-zA-Z]+)\b', False),  # iShares, iPhone, etc.
            (r'\b([A-Z]+[a-z]*\s+\d+)\b', False),  # S&P 500, Russell 2000, etc.
        ]
        
        for pattern, check_length in patterns_to_extract:
            matches = re.findall(pattern, response_str)
            for match in matches:
                if check_length and len(match) > 2:
                    all_sources.append(match.strip())
                elif not check_length:
                    all_sources.append(match.strip())
        
        # Check for specific known sources/platforms
        known_items = [
            'Aladdin', 'iShares', 'SPDR', 'Russell Indices', 'Russell 2000', 'Russell 3000',
            'S&P 500', 'S&P Global', 'Dow Jones', 'NASDAQ', 'NYSE', 'FTSE',
            'Morningstar', 'Bloomberg Terminal', 'Reuters', 'FactSet', 'Refinitiv',
            'MSCI', 'Lipper', 'Barclays Indices', 'ICE Data', 'CRSP',
            'Schwab Intelligent Portfolios', 'Vanguard Personal Advisor Services',
            'ETF.com', 'Investopedia', 'SEC filings', 'EDGAR database'
        ]
        
        for item in known_items:
            if item.lower() in text_lower and item not in all_sources:
                all_sources.append(item)
        
        # Extract URLs if not already included
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, response_str)
        all_sources.extend([url for url in urls if url not in all_sources])
        
        # Clean up and deduplicate
        cleaned_sources = []
        seen = set()
        for source in all_sources:
            # Clean the source
            source = source.strip()
            # Skip very short or very long sources (likely noise)
            if 2 < len(source) < 100:
                # Normalize for deduplication
                normalized = source.lower()
                if normalized not in seen:
                    seen.add(normalized)
                    cleaned_sources.append(source)
        
        return cleaned_sources[:30]  # Limit to 30 most relevant sources
    
    def _get_fallback_analysis(self, response_text, query, provider):
        """Basic analysis without AI when API fails"""
        
        # Simple pattern matching for companies and keywords
        text_lower = response_text.lower() if isinstance(response_text, str) else str(response_text).lower()
        response_str = response_text if isinstance(response_text, str) else str(response_text)
        
        # Common company patterns
        companies = []
        company_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Capitalized words
            r'\b(?:Inc|Corp|LLC|Ltd|Company)\b',  # Company suffixes
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, response_str)
            companies.extend(matches[:5])  # Limit to avoid noise
        
        # Authority signals
        authority_signals = []
        authority_words = ['leading', 'popular', 'trusted', 'best', 'top', 'industry', 'standard', 'widely']
        for word in authority_words:
            if word in text_lower:
                authority_signals.append(word)
        
        # Enhanced source extraction
        sources_cited = []
        
        # Extract URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, response_str)
        sources_cited.extend(urls)
        
        # Extract citations patterns
        citation_patterns = [
            r'according to ([A-Z][^,\.\n]+)',  # "according to X"
            r'data from ([A-Z][^,\.\n]+)',  # "data from X"
            r'reported by ([A-Z][^,\.\n]+)',  # "reported by X"
            r'source: ([^,\.\n]+)',  # "source: X"
            r'\(([A-Z][^)]+)\)',  # Parenthetical citations
        ]
        
        for pattern in citation_patterns:
            matches = re.findall(pattern, response_str, re.IGNORECASE)
            sources_cited.extend([m.strip() for m in matches if len(m.strip()) > 3])
        
        # Extract known indices and platforms
        known_sources = [
            'Russell Indices', 'S&P 500', 'Dow Jones', 'NASDAQ', 'NYSE',
            'Morningstar', 'Bloomberg', 'Reuters', 'Forbes', 'Wall Street Journal',
            'Financial Times', 'Barron\'s', 'CNBC', 'Yahoo Finance',
            'iShares', 'SPDR', 'Aladdin', 'FactSet', 'Refinitiv'
        ]
        
        for source in known_sources:
            if source.lower() in text_lower:
                sources_cited.append(source)
        
        # Extract platform/tool mentions with specific patterns
        platform_pattern = r'\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+(?:platform|system|tool|index|indices|ETF|ETFs)\b'
        platform_matches = re.findall(platform_pattern, response_str)
        sources_cited.extend([m for m in platform_matches if len(m) > 2])
        
        # Remove duplicates and clean up
        sources_cited = list(set([s for s in sources_cited if s and len(s.strip()) > 2]))[:20]
        
        return {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'provider': provider,
            'companies_mentioned': list(set(companies))[:10],
            'mention_reasons': {'extracted': 'Fallback analysis - AI unavailable'},
            'authority_signals': authority_signals,
            'key_features': [],
            'sources_cited': sources_cited,
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