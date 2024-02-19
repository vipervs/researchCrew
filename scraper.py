from bs4 import BeautifulSoup
import requests

def scrape_data(url):
    if 'frontiersin.org' in url:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            content_section = soup.find('div', class_='JournalFullText')
            content_text = content_section.get_text(strip=True) if content_section else 'Content not found'
            return content_text
        else:
            return 'Failed to retrieve the page'
    elif 'pubmed.ncbi.nlm.nih.gov' in url:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            abstract_section = soup.find('div', class_='abstract')
            abstract_text = abstract_section.get_text(strip=True) if abstract_section else 'Abstract not found'
            return abstract_text
        else:
            return 'Failed to retrieve the page'
    else:
        return 'URL does not match known patterns'

#TESTING
#print(scrape_data("https://www.frontiersin.org/articles/10.3389/frai.2021.652669/full"))
#print(scrape_data("https://pubmed.ncbi.nlm.nih.gov/30544648/"))


    @tool("Scrape literature")
    def scrape_literature(url):
        """
        Scrapes the content of the provided link

        Args:
            url (str): The URL of the website to scrape and summarize.
            
        Returns:
            str: A summary of the scraped website content.
        """
        return scrape_data(url)