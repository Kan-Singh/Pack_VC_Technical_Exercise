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

I then have a set of Regex patterns. I go through the extracted website text with these patterns in order to find founder names. Any pattern matches are saved to the 
founders.json file. 

## 3. Assumptions

## 4. Future Improvements

