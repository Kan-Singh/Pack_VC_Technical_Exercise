"""
Pack Ventures Founder Finder - Selenium Version
Handles JavaScript-rendered websites by using a real browser
"""

import json
import re
import time
from urllib.parse import urlparse

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("WARNING: Selenium not installed. Install with: pip install selenium webdriver-manager")

print("Script started!")

class FounderFinder:
    def __init__(self, use_selenium=True):
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        
        if self.use_selenium:
            print("Initializing with Selenium (JavaScript rendering enabled)...")
            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✓ Selenium initialized successfully")
            except Exception as e:
                print(f"WARNING: Could not initialize Selenium: {e}")
                print("Falling back to basic requests mode")
                self.use_selenium = False
        else:
            print("Using basic requests mode (no JavaScript rendering)")
        
        # Common patterns for founder-related pages
        self.about_paths = ['/founders', '/about', '/about-us', '/team', '/our-story', '/company', '/leadership']
    
    def __del__(self):
        if self.use_selenium and hasattr(self, 'driver'):
            self.driver.quit()
        
    def extract_company_info(self, line):
        """Parse company name and URL from input line"""
        match = re.match(r'(.+?)\s*\((.+?)\)', line.strip())
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return line.strip(), None
    
    def get_page_text(self, url):
        """
        Fetch page and return text content
        Uses Selenium if available to render JavaScript
        """
        try:
            if self.use_selenium:
                print(f"    Loading page with JavaScript rendering...")
                self.driver.get(url)
                # Wait for page to load
                time.sleep(3)  # Give time for JavaScript to render
                text = self.driver.find_element(By.TAG_NAME, 'body').text
                return text
            else:
                # Fallback to requests
                import requests
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                return soup.get_text()
        except Exception as e:
            print(f"    Error: {str(e)}")
            return None
    
    def extract_founders_from_text(self, text):
        """
        Extract founder names from text using comprehensive pattern matching
        """
        if not text:
            return []
        
        founders = set()
        
        # Enhanced patterns to catch more variations
        patterns = [
            # "Founded by X" or "Co-founded by X and Y"
            r'(?:founded by|co-founded by)\s+([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+(?:and|&)\s+[A-Z][a-z]+\s+[A-Z][a-z]+)*)',
            
            # "Name\nCo-Founder & CEO" (name on separate line from title)
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s*\n\s*Co-?Founder',
            
            # "Name Co-Founder" (on same line, no punctuation)
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+Co-?Founder',
            
            # "Co-Founder & CEO\nName" (title before name)
            r'Co-?Founder.*?\n\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
            
            # "Name, Co-Founder" or "Name - Co-Founder"
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s*[,\-–—]\s*Co-?Founder',
            
            # Look for the pattern: Name followed by title with CEO/CTO/COO
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s*\n\s*Co-?Founder\s*(?:&|and)?\s*(?:CEO|CTO|COO)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                name = match.group(1).strip()
                # Validate it looks like a real name
                if self._is_valid_name(name):
                    founders.add(name)
        
        return sorted(list(founders))
    
    def _is_valid_name(self, name):
        """Check if string looks like a valid person name"""
        # Should be 2-3 words
        words = name.split()
        if len(words) < 2 or len(words) > 3:
            return False
        
        # Each word should start with capital
        for word in words:
            if not word[0].isupper():
                return False
        
        # Filter out common false positives
        false_positives = ['Our Team', 'Meet The', 'About Us', 'Contact Us']
        if name in false_positives:
            return False
        
        return True
    
    def find_founders(self, company_name, company_url):
        """
        Main method to find founders for a company
        """
        print(f"\nSearching for founders of {company_name}...")
        
        if not company_url:
            print("  No URL provided")
            return []
        
        # Try homepage first
        print(f"  Trying homepage: {company_url}")
        text = self.get_page_text(company_url)
        if text:
            founders = self.extract_founders_from_text(text)
            if founders:
                print(f"  ✓ Found on homepage: {founders}")
                return founders
        
        # Try common about pages
        parsed_url = urlparse(company_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        for path in self.about_paths:
            about_url = base_url + path
            print(f"  Trying: {about_url}")
            text = self.get_page_text(about_url)
            if text:
                founders = self.extract_founders_from_text(text)
                if founders:
                    print(f"  ✓ Found: {founders}")
                    return founders
            time.sleep(1)  # Rate limiting
        
        print(f"  ✗ No founders found for {company_name}")
        return []
    
    def process_companies_file(self, input_file, output_file):
        """Process input file and generate founders JSON"""
        results = {}
        
        try:
            with open(input_file, 'r') as f:
                lines = f.readlines()
            
            print(f"\nProcessing {len(lines)} companies...")
            
            for i, line in enumerate(lines, 1):
                if line.strip():
                    print(f"\n[{i}/{len(lines)}]")
                    company_name, company_url = self.extract_company_info(line)
                    founders = self.find_founders(company_name, company_url)
                    results[company_name] = founders
            
            # Write results
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\n{'='*60}")
            print(f"✓ Results saved to {output_file}")
            print(f"Found founders for {sum(1 for v in results.values() if v)}/{len(results)} companies")
            print("\nSummary:")
            for company, founders in results.items():
                status = "✓" if founders else "✗"
                print(f"  {status} {company}: {founders if founders else '[]'}")
            
        except FileNotFoundError:
            print(f"Error: {input_file} not found")
        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()

def main():
    finder = FounderFinder(use_selenium=True)
    finder.process_companies_file('companies.txt', 'founders.json')

if __name__ == "__main__":
    main()