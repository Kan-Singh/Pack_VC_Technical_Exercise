"""
Pack Ventures Founder Finder
Automatically extracts founder names from company websites
"""

import json
import re
import time
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup



print("Script started!")

class FounderFinder:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # Common patterns for founder-related pages
        self.about_paths = ['/about', '/about-us', '/team', '/our-story', '/company', '/leadership']
        
    def extract_company_info(self, line):
        """Parse company name and URL from input line"""
        # Match pattern: "Company Name (URL)"
        match = re.match(r'(.+?)\s*\((.+?)\)', line.strip())
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return line.strip(), None
    
    def search_for_founders_on_page(self, url):
        """
        Fetch page content and search for founder mentions
        Uses multiple strategies to identify founders
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Strategy 1: Look for structured data (JSON-LD)
            founders = self._extract_from_structured_data(soup)
            if founders:
                return founders
            
            # Strategy 2: Search page text for founder patterns
            founders = self._extract_from_text(soup)
            return founders
            
        except Exception as e:
            print(f"  Error fetching {url}: {str(e)}")
            return []
    
    def _extract_from_structured_data(self, soup):
        """Extract founders from JSON-LD structured data"""
        founders = []
        scripts = soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                # Look for founder mentions in structured data
                if isinstance(data, dict):
                    if 'founder' in data:
                        founder_data = data['founder']
                        if isinstance(founder_data, list):
                            founders.extend([f.get('name') for f in founder_data if isinstance(f, dict) and 'name' in f])
                        elif isinstance(founder_data, dict) and 'name' in founder_data:
                            founders.append(founder_data['name'])
            except:
                continue
                
        return [f for f in founders if f]
    
    def _extract_from_text(self, soup):
        """
        Extract founder names from page text using pattern matching
        Looks for common phrases like "Founded by", "Co-founder:", etc.
        """
        # Get all text content
        text = soup.get_text()
        
        # Common founder patterns
        patterns = [
            r'(?:founded by|co-founded by|founders?:?)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+(?:(?:\s+and|\s*,)\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)*)',
            r'(?:CEO and (?:Co-)?Founder|Founder and CEO)[\s:]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+),?\s+(?:Co-)?Founder',
        ]
        
        founders = set()
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract names from the match
                names_text = match.group(1)
                # Split by 'and' or comma
                name_parts = re.split(r'\s+and\s+|,\s*', names_text)
                for name in name_parts:
                    name = name.strip()
                    # Validate name (2-4 words, each starting with capital)
                    if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}$', name):
                        founders.add(name)
        
        return sorted(list(founders))
    
    def find_founders(self, company_name, company_url):
        """
        Main method to find founders for a company
        Tries company homepage and common about pages
        """
        print(f"\nSearching for founders of {company_name}...")
        
        if not company_url:
            print("  No URL provided")
            return []
        
        # Try homepage first
        founders = self.search_for_founders_on_page(company_url)
        if founders:
            print(f"  Found on homepage: {founders}")
            return founders
        
        # Try common about pages
        parsed_url = urlparse(company_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        for path in self.about_paths:
            try:
                about_url = base_url + path
                print(f"  Trying {about_url}...")
                founders = self.search_for_founders_on_page(about_url)
                if founders:
                    print(f"  Found: {founders}")
                    return founders
                time.sleep(0.5)  # Be respectful with requests
            except:
                continue
        
        print(f"  No founders found for {company_name}")
        return []
    
    def process_companies_file(self, input_file, output_file):
        """
        Process input file and generate founders JSON
        """
        results = {}
        
        try:
            with open(input_file, 'r') as f:
                lines = f.readlines()
            
            print(f"Processing {len(lines)} companies...")
            
            for line in lines:
                if line.strip():
                    company_name, company_url = self.extract_company_info(line)
                    founders = self.find_founders(company_name, company_url)
                    results[company_name] = founders
                    time.sleep(1)  # Rate limiting
            
            # Write results to JSON file
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\n✓ Results saved to {output_file}")
            print(f"Found founders for {sum(1 for v in results.values() if v)}/{len(results)} companies")
            
        except FileNotFoundError:
            print(f"Error: {input_file} not found")
        except Exception as e:
            print(f"Error processing file: {str(e)}")

def main():
    finder = FounderFinder()
    finder.process_companies_file('companies.txt', 'founders.json')

if __name__ == "__main__":
    main()