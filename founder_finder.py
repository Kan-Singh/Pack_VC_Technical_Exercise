
# imports
import json
import re
import time
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup



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


# I've added in print messages throughout the code that are solely for 
# the purpose of clarity for whoever's running this
print("Script started!")

class FounderFinder:

    # initializing selenium so I can use it to access the websites
    def __init__(self, use_selenium=True):
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        
        if self.use_selenium:
            print("Initializing with Selenium (JavaScript rendering enabled)...")
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # error checking to ensure that selenium is initialized correctly
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
        
        # these are the pages that will be checked/scriped for each website
        # in this exercise, I've kept things minimal so that it doesn't take
        # forever, but more pages can be added if we want to expand this to a bigger project
        self.about_paths = [ '/about', '/founders', '/team']
    
    def __del__(self):
        if self.use_selenium and hasattr(self, 'driver'):
            self.driver.quit()
        
    # gets the company's name and URL from the input file
    def extract_company_info(self, line):
        match = re.match(r'(.+?)\s*\((.+?)\)', line.strip())
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return line.strip(), None
    
    # actually opens the pages, loads and extracts the text in them
    def get_page_text(self, url, save_debug=False):
        try:
            if self.use_selenium:
                print(f"    Loading page with JavaScript rendering...")
                self.driver.get(url)
                
                # Waits so that more content from the page can load
                # can be adjusted based on future need
                time.sleep(5)  
                
                
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
                
                
                text = self.driver.find_element(By.TAG_NAME, 'body').text
                
                
                html = self.driver.page_source
                
                # save a debug file that contains all the text from each page you open
                # this can help a programmer check issues such as- 
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
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                return soup.get_text()
        except Exception as e:
            print(f"    Error: {str(e)}")
            return None
    
    # tries to find the founder names from the extracted website text
    def extract_founders_from_text(self, text):

        if not text:
            return []
        
        founders = set()
        
        # in regex, these are the patterns I am looking for 
        patterns = [
           
            r'([A-Z][a-z]+(?:\s+[A-Z][a-zA-Z\-]+)+),?\s*(?:PhD|MD)?\s*\n+\s*Founder\b(?:[^\r\n]*)?',

            # "Founded by X" or "Co-founded by X and Y"
            r'(?:founded by|co-founded by)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            
            # Name followed by Founder or Co-Founder
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
        
        # go through and test all the above patterns on a webpage, iteratively
        for i, pattern in enumerate(patterns):
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                name = match.group(1).strip()
                name = re.sub(r',?\s*(?:PhD|MD|Ph\.D\.|M\.D\.)$', '', name).strip()
                if self._is_valid_name(name):
                    print(f"      DEBUG: Pattern {i+1} matched: '{name}'")
                    founders.add(name)
        
        return sorted(list(founders))
    
    # Used to check if a string resembles a conventional name
    # def not a one-size-fits all approach, may need to be workshopped
    def _is_valid_name(self, name):
        """Check if string looks like a valid person name"""
        words = name.split()

        if len(words) < 1 or len(words) > 4:
            return False
        
        for word in words:
            if not word[0].isupper():
                return False
        
        # comparing against some hard-coded common false positives. those may need to 
        # be adjusted based on what the most common false postitives are
        false_positives = ['Our Team', 'Meet The', 'About Us', 'Contact Us', 'Head Of']
        if name in false_positives:
            return False
        
        return True
    
    # this calls some earlier methods about extracting webpage text, 
    # pattern matching for founder names, etc 
    # ultimately finds the founder names for a company
    def find_founders(self, company_name, company_url):
        print(f"\nSearching for founders of {company_name}...")
        
        # error message in case the company's URL hasn't been provided
        if not company_url:
            print("  No URL provided")
            return []
        
        # goes through the homepage to see if it can find names
        print(f"  Trying homepage: {company_url}")
        text = self.get_page_text(company_url, save_debug=True)
        if text:
            founders = self.extract_founders_from_text(text)
            if founders:
                print(f"  ✓ Found on homepage: {founders}")
                return founders
        
        parsed_url = urlparse(company_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # goes through any additional paths to see if it can find names
        for path in self.about_paths:
            about_url = base_url + path
            print(f"  Trying: {about_url}") 
            text = self.get_page_text(about_url, save_debug=(path in ['/about', '/founders', '/team']))

            # if you find any founder names, extract them, as well as inform the user
            if text:
                founders = self.extract_founders_from_text(text)
                if founders:
                    print(f"  ✓ Found: {founders}")
                    return founders
            time.sleep(1)
        
        # in case no founder names were found
        print(f"  ✗ No founders found for {company_name}")
        return []
    
    # this generates the output file (founders)
    def process_companies_file(self, input_file, output_file):
        results = {}
        
        try:
            with open(input_file, 'r') as f:
                lines = f.readlines()
            
            print(f"\nProcessing {len(lines)} companies...")
            
            # goes through every line in the input file
            for i, line in enumerate(lines, 1):
                if line.strip():
                    print(f"\n[{i}/{len(lines)}]")
                    company_name, company_url = self.extract_company_info(line)
                    founders = self.find_founders(company_name, company_url)
                    results[company_name] = founders
            
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            # some debugging messages to let you know what's happening
            print(f"\n{'='*60}")
            print(f"✓ Results saved to {output_file}")
            print(f"Found founders for {sum(1 for v in results.values() if v)}/{len(results)} companies")
            print("\nSummary:")
            for company, founders in results.items():
                status = "✓" if founders else "✗"
                print(f"  {status} {company}: {founders if founders else '[]'}")
            
        # ensures input file is found    
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