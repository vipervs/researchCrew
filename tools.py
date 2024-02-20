import requests
import os
import time
from dotenv import load_dotenv
from langchain.tools import tool 
from bs4 import BeautifulSoup
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

load_dotenv()

gpt35 = ChatOpenAI(
    model_name="gpt-3.5-turbo", temperature="0"
)

lmstudio = ChatOpenAI(
    base_url="http://localhost:1234/v1",
)

class CustomSearchTools:

    @tool("Perform literature search")
    def google_custom_search(query):
        """
        Performs a literature search using Google Custom Search Engine (CSE).
        The search is tailored to find scientific literature related to the provided query.
        """
        # Base URL for the API
        api_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': query,
            'key': {os.environ['GOOGLE_CSE_KEY']},
            'cx': {os.environ['GOOGLE_CSE_ID']}
        }
        # Headers for the API request (optional for this API, but shown for completeness)
        headers = {
        'Accept': 'application/json'
        }
        # Send the request to the API
        response = requests.get(api_url, params=params, headers=headers)
        response.raise_for_status()  # If the response has an HTTP error status, this will raise an exception
        # Parse the JSON data
        json_data = response.json()
        # Extract the search results
        items = json_data.get("items", [])
        # Extract and return only the 'title' and 'link' from the search results
        results = [{"title": item["title"], "link": item["link"]} for item in items]
        # Limit results to 10
        results = results[:10]
    
        return results
    
    @tool("Scrape website content")
    def scrape_and_summarize_website(website):
        """
        Useful to scrape and summarize a website content. Just pass a string with
        only the full URL, no need for a final slash `/`, e.g., https://google.com or https://clearbit.com/about-us
        """
        summaries = []
        if 'sciencedirect.com' in website:
            # Setup webdriver
            webdriver_service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=webdriver_service)
            
            driver.get(website)
            
            # Wait for the page to load
            time.sleep(5)
            
            # Get title and abstract
            title = driver.find_element(By.TAG_NAME, 'h1').text
            abstract = driver.find_element(By.CLASS_NAME, 'abstract').text
            conclusion = driver.find_element(By.XPATH, '//h2[text()="Conclusion"]/following-sibling::p[1]').text

            return f'Title: {title}\n\nLink: {website}\n\nAbstract: {abstract}\n\nConclusion: {conclusion}'
        elif 'frontiersin.org' in website:
            response = requests.get(website)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                journal_abstract_section = soup.find('div', class_='JournalAbstract')
                if journal_abstract_section:
                    title_section = journal_abstract_section.find('h1')
                    title_text = title_section.get_text(strip=True) if title_section else 'Title not found'
                    abstract_section = journal_abstract_section.find('p')
                    abstract_text = abstract_section.get_text(strip=True) if abstract_section else 'Abstract not found'
                    return f'Title: {title_text}\n\nLink: {website}\n\nAbstract: {abstract_text}'
                else:
                    return 'Failed to find the JournalAbstract section'
            else:
                return 'Failed to retrieve the page'
        elif 'pubmed.ncbi.nlm.nih.gov' in website:
            response = requests.get(website)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                title_section = soup.find('h1', class_='heading-title')
                title_text = title_section.get_text(strip=True) if title_section else 'Title not found'
                abstract_section = soup.find('div', class_='abstract-content selected')
                abstract_text = abstract_section.get_text(strip=True) if abstract_section else 'Abstract not found'
                return f'Title: {title_text}\n\nLink: {website}\n\nAbstract: {abstract_text}'
            else:
                return 'Failed to retrieve the page'

#website ="https://www.frontiersin.org/articles/10.3389/frai.2021.553987"
#result = CustomSearchTools.scrape_and_summarize_website(website)
#print(result)

#query = '("Artificial Intelligence" OR "AI" OR "Machine Learning" OR "ML" OR "Deep Learning" OR "Natural Language Processing" OR "NLP") AND ("Global Health" OR "Public Health" OR "Healthcare Challenges" OR "Health Challenges" OR "Epidemiology" OR "Disease Surveillance" OR "Health Data Analysis") AND ("Challenges" OR "Solutions" OR "Applications" OR "Impact" OR "Innovation")'
#search_results = CustomSearchTools.google_custom_search(query)
#print(search_results)