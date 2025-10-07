
# imports
import json
import re
import time
from urllib.parse import urlparse



# added this in to point out a potentially common error of someone not 
# installing selenium before running this code - or in case of debugging, 
# in case another programmer wants to check if selenium is working or not
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
        # using selenium to open up a chrome browser and then
        # extract all the text that's in Javascript (frameworks)
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        
        if self.use_selenium:
            print("Initializing with Selenium (JavaScript rendering enabled)...")
            chrome_options = Options()
            chrome_options.add_argument('--headless')
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
        
        self.about_paths = [ '/about', '/founders', '/team']
    
    def __del__(self):
        if self.use_selenium and hasattr(self, 'driver'):
            self.driver.quit()
        
    def extract_company_info(self, line):
        """Parse company name and URL from input line"""
        match = re.match(r'(.+?)\s*\((.+?)\)', line.strip())
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return line.strip(), None
    
    def get_page_text(self, url, save_debug=False):
        """Fetch page and return text content using Selenium"""
        try:
            if self.use_selenium:
                print(f"    Loading page with JavaScript rendering...")
                self.driver.get(url)
                
                # Wait longer for dynamic content to load
                time.sleep(5)  # Increased from 3 to 5 seconds
                
                # Try to scroll down to trigger lazy loading
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Scroll back up
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
                
                # Get all text
                text = self.driver.find_element(By.TAG_NAME, 'body').text
                
                # Also try to get HTML source and parse it
                html = self.driver.page_source
                
                if save_debug and text:
                    filename = url.replace('https://', '').replace('http://', '').replace('/', '_')
                    with open(f'debug_{filename}.txt', 'w', encoding='utf-8') as f:
                        f.write("=== RENDERED TEXT ===\n")
                        f.write(text)
                        f.write("\n\n=== HTML SOURCE ===\n")
                        f.write(html)
                    print(f"    DEBUG: Saved page text to debug_{filename}.txt")
                
                return text
            else:
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
        """Extract founder names from text using pattern matching"""

        # DEBUG: Test the pattern directly
        test_pattern = r'([A-Z][a-z]+(?:(?:\s+|-)[A-Z][a-z]+)+),\s*(?:PhD|MD|MSc)\s*\n\s*Founder'
        test_matches = re.findall(test_pattern, text, re.IGNORECASE | re.MULTILINE)
        print(f"      DEBUG: Direct test found: {test_matches}")

        if not text:
            return []
        
        founders = set()
        
      
        patterns = [
           
            r'([A-Z][a-z]+(?:\s+[A-Z][a-zA-Z\-]+)+),?\s*(?:PhD|MD)?\s*\n+\s*Founder\b(?:[^\r\n]*)?',

            # "Founded by X" or "Co-founded by X and Y"
            r'(?:founded by|co-founded by)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',

            r'([A-Z][a-z]+(?:\s+[A-Z][a-zA-Z\-]+)*)\s*(?=\n+\s*(?:Co-)?Founder\b)',

            r'(?:(?<=\n)|^)\s*([A-Z][a-z]+(?:\s+[A-Z][a-zA-Z\-]+)*)\s*(?=\n+\s*(?:Co-)?Founder\b)',

            
            # "Name\nCo-Founder & CEO"
            r'([A-Z][a-z]+(?:\s+[A-Z\-][a-z]+)+),?\s*(?:,\s*)?(?:PhD|MD)?\s*\n+\s*Co-?Founder',
            
            # "Name Co-Founder"
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s+Co-?Founder',
            
            # "Name, Co-Founder" or "Name - Co-Founder"
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s*[,\-–—]\s*Co-?Founder',

            # Pattern for "CEO & CO-FOUNDER\nMitra Raman" (Rosie style)
            r'(?:CEO|COO|CTO|CFO|CPO)\s*&\s*CO-?FOUNDER\s*\n\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+?)(?=\s*\n)', 

               # Also catch just "CO-FOUNDER" or "FOUNDER" followed by name
            r'CO-?FOUNDER\s*\n+\s*([A-Z][a-z]+(?:\s+[A-Z\-][a-z]+)+)',
            r'FOUNDER\s*\n+\s*([A-Z][a-z]+(?:\s+[A-Z\-][a-z]+)+)',


        ]
        
        for i, pattern in enumerate(patterns):
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                name = match.group(1).strip()
                name = re.sub(r',?\s*(?:PhD|MD|Ph\.D\.|M\.D\.)$', '', name).strip()
                if self._is_valid_name(name):
                    print(f"      DEBUG: Pattern {i+1} matched: '{name}'")
                    founders.add(name)
        
        return sorted(list(founders))
    
    def _is_valid_name(self, name):
        """Check if string looks like a valid person name"""
        words = name.split()
        if len(words) < 2 or len(words) > 4:
            return False
        
        for word in words:
            if not word[0].isupper():
                return False
        
        false_positives = ['Our Team', 'Meet The', 'About Us', 'Contact Us', 'Head Of']
        if name in false_positives:
            return False
        
        return True
    
    def find_founders(self, company_name, company_url):
        """Main method to find founders for a company"""
        print(f"\nSearching for founders of {company_name}...")
        
        if not company_url:
            print("  No URL provided")
            return []
        
        print(f"  Trying homepage: {company_url}")
        text = self.get_page_text(company_url, save_debug=True)
        if text:
            founders = self.extract_founders_from_text(text)
            if founders:
                print(f"  ✓ Found on homepage: {founders}")
                return founders
        
        parsed_url = urlparse(company_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        for path in self.about_paths:
            about_url = base_url + path
            print(f"  Trying: {about_url}")
            text = self.get_page_text(about_url, save_debug=(path in ['/about', '/founders', '/team']))
            if text:
                founders = self.extract_founders_from_text(text)
                if founders:
                    print(f"  ✓ Found: {founders}")
                    return founders
            time.sleep(1)
        
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