import requests
import os
from dotenv import load_dotenv
from langchain.tools import tool 
from bs4 import BeautifulSoup
from crewai import Agent, Task
from langchain_openai import ChatOpenAI

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
        response = requests.get(website)
        if response.status_code != 200:
            return "Failed to retrieve website content"

        soup = BeautifulSoup(response.text, "html.parser")
        content = "\n\n".join([p.text for p in soup.find_all('p')])
        content = [content[i:i + 8000] for i in range(0, len(content), 8000)]
        summaries = []
        for chunk in content:
            agent = Agent(
                role="Principal Researcher",
                goal="Do amazing researches and summaries based on the content you are working with",
                backstory="You're a Principal Researcher at an University and you need to do a research about a given topic.",
                llm=gpt35,
                #function_calling_llm=gpt35,
                allow_delegation=False)
            task = Task(
                agent=agent,
                description=f"Analyze and make a LONG summary of the content bellow, make sure to include the ALL relevant information in the summary, return only the summary with the Link: {website} nothing else.\n\nCONTENT:\n----------\n{chunk}.",
                )
            summary = task.execute()
            summaries.append(summary)
        
        final_summary = "\n\n".join(summaries)
        return f'\nScrapped Content: {final_summary}\n'
    

website = "https://www.sciencedirect.com/science/article/pii/S2444569X2300029X" 
result = CustomSearchTools.scrape_and_summarize_website(website)
print(result)
    
#query = '("Artificial Intelligence" OR "AI" OR "Machine Learning" OR "ML" OR "Deep Learning" OR "Natural Language Processing" OR "NLP") AND ("Global Health" OR "Public Health" OR "Healthcare Challenges" OR "Health Challenges" OR "Epidemiology" OR "Disease Surveillance" OR "Health Data Analysis") AND ("Challenges" OR "Solutions" OR "Applications" OR "Impact" OR "Innovation")'
#search_results = CustomSearchTools.google_custom_search(query)
#print(search_results)