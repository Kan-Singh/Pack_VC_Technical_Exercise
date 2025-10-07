# Founder Finder

## Table of Contents
1. Running the Solution
2. Approach
3. Assumptions Made
4. Future Improvements
___
## 1. Running the Solution (Installing Dependencies & Environmental Setup)

 ### 1. Install VS Code
VS Code is a popular code editor.
- Download and install VS Code from: [https://code.visualstudio.com/](https://code.visualstudio.com/)
- Open VS Code after installation.

### 2. Install Git
Git is needed to clone and manage the repository.

- Download and install Git from: [https://git-scm.com/downloads](https://git-scm.com/downloads)
- Follow the installation instructions for your operating system.
- After installation, verify Git is installed by running:
  ```sh
  git --version
  ```

### 3. Configure Git and Login to GitHub
If you haven't used Git before, configure it with your name and email:

```sh
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

### 4. Install Python

- Download and install Python from: [https://www.python.org/downloads/]




### 5. Install Dependencies

Once inside the project folder, install dependencies needed to start running the code with the following command:

```
pip install selenium webdriver-manager beautifulsoup4 requests
```
This will download and install all required packages.

### 6. Opening and Running the Code
- Open VS Code and select **File > Open Folder**.
- Choose the cloned project folder.
- In the terminal/command line, enter the following command to run the code:
 
```
py founder_finder.py
```


## 2. Approach

I decided the best way to find founder names is to scrape the company websites to find any founder names they may contain. 
An alternative approach I could think of was using an API, such as 'Crunchbase' API in order to attempt to find founder names. However, 
given that many of the companies that Pack Ventures work with are very early in their stages as opposed to more established companies, I believe that
many of these external sources may not contain the relevant information, while the websites themselves were highly likely to. 

I then used Selenium to extract the text from the website. Selenium is essentially opening a Chrome webriver to fully render these websites. I then wait 
a couple seconds to allow for more content to load. Additionally, I 'scroll' up and down the website to find any trigger elements. All the text that can be
found is extracted. 

I then have a set of Regex patterns. I go through the extracted website text with these patterns in order to find founder names. After patterns are matched, 
the matching string is compared against some common name conventions (such as being between 2-4 words). Any founder names are then saved to the 
founders.json file. 

## 3. Assumptions

The most crucial assumption made in this approach is that the company websites contain founder names. For about half the websites in companies.txt, this assumption
doesn't hold true - I wasn't able to find founder names even when I manually went to the website to search for them. If this ratio holds true - that about 50% of companies
that people at Pack Ventures search for don't have founder names on their website, then this approach isn't actually very helpful. 

The pattern matching approach also assumes that there is a set amount of ways (patterns) that names can be stored and formatted in company websites. I did see a lot of variety 
on the websites that I visited, so this assumption requires nuance. I believe that there is probably a set of optimal patterns that will end up working for most websites, and I 
could probably find them with more time and more exposure to different company websites. However, that doesn't mean that it wouldn't be worth considering alternate ways of identifying 
names, if any seemed to be a more accurate fit. 

Another set of assumptions lies in the case of 'name conventions'. The ones in the code right now are general enough that they should work for many names, especially the vast majority of 
names that Pack Ventures is likely to enounter, but it's important to be mindful that other cultures may not fit within the contraints that we consider common, so optimization or changes 
could be done in the future with more research. 


## 4. Future Improvements

### 1. (Optionally) Also finding relevant information about Founders:

    If someone is searching up the name of a founder, it's likely that they may also want additional information about that founder, such as their contact information or their connection to UW.
   This information could be scraped for on the company website. Many founders might have their own website (about themselves, not the company), or at least a Linkedin profile. Links to this information
   might be available on the company website, or could be manually inputted the same way company website were. Additional founder information could then be scraped as well.

   (Linkedin scraping does have some constraints, so this is something I would further discuss before doing. Ultimately, since Pack Ventures is likely to be doing this on a very small scale and not in a scammy
   way, it shouldn't be a problem)

### 2.  Using AI models to find founder names from the extracted text.

   The current process collects all the webpage text, and then uses pattern-matching in order to find founder names. As mentioned in my approach section, while this method is functional, it may be prone to certain errors, depending on what patterns are defined or the variety in website formatting. Pattern matching also misses some contextual clues (such as if someone is listed as a founder, but for a different company). A model trained to find founder names may be able to navigate those issues better. I've been an undergraduate researcher at UW's Natural Language Processing lab for the past year, and my work has actually focused on something very similar: named entity recognition and entitity linking (among other things). While my research focused on legal documents specifically, it shouldn't be a radically different approach to work with website text. In this approach, I would extract website text with Selenium and create a file of that text (which my code already does), and then prompt a model to identify the founders. The potential issue here would be having enough data to meaningfully train the model to do this with high accuracy. However, there is a certain level of simplicity to website text and this prompt, so it is doable.

### 3. Saving or Caching this information, and potentially integrating it into a simpler "search" UI.

   The current format (creating an input file, running the python script, and then getting an output file) is not the easiest and most intuitive to use. Ideally, I would want this be software where people can enter a company URL into a search bar and then get founder names on the same page. Building that frontend is a fairly simple project.

   With a feature like that however, it would be optimal to not have to scrape the same website more than once. In order to avoid this, we could save the URL and associated founder names in a database. When a new URL is searched, we'd simply ensure that it didn't already exist in our database before scraping it.

### 4. Optimizing the code in this submission
  
   All of the above changes are great next steps. However, my first step if I had more than 2 hours would likely be to go back and simply optimize this submission. My main focus would be the pattern-matching regarding the names: I would want to create more concise and accurate regex patterns, and even research what other options there may be outside of pattern matching. I would also want to extend support for different alphabets/characters, as well as different cultural naming conventions. The name validation could potentially also be more sophisticated, such as by checking against a database of very common names. 
      
      
