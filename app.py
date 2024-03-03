import os
import datetime
from crewai import Agent, Task, Crew, Process
from langchain.agents import load_tools
from langchain_openai import AzureChatOpenAI
from tools import CustomSearchTools
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_community.llms import Ollama


load_dotenv()

ollama = Ollama(model="solar")

gpt35 = ChatOpenAI(
    model_name="gpt-3.5-turbo", temperature="0"
)

azure = AzureChatOpenAI(
    model='azure',
    api_version='2023-07-01-preview',
    api_key=os.getenv("AZURE_API_KEY"),
    base_url=os.getenv("AZURE_BASE"),
)

@tool("read_file")
def read_file():
    """
    Reads the scientific search results file and returns its content, no need for an tool input.
    """
    # Get the current date
    date = datetime.datetime.now().strftime("%Y_%m_%d")

    # Define the filename
    filename = f"{date}.txt"

    # Check if the file exists
    if os.path.exists(filename):
        # Read the file
        with open(filename, 'r') as f:
            content = f.read()
        return content
    else:
        return f"No file named {filename} found."

# Define the topic of interest
topic = input("Please enter the research topic: ")

# Loading Human Toolsa
human_tools = load_tools(["human"])

researcher = Agent(
    role="Senior Researcher",
    goal=f"Identify and collect relevant boolean keywords and search for scientific literature related to the Research Topic: {topic}.",
    verbose=True,
    allow_delegation=False,
    backstory="""Your expertise lies in uncovering valuable insights within scientific databases and journals.
    With a sharp analytical mind, you adeptly navigate through complex information landscapes to find the most pertinent literature.""",
    llm=azure,
    tools=[CustomSearchTools.google_custom_search],
    max_iter=10,
)

scraper = Agent(
    role='Scraper',
    goal=f'Use the provided links and scrape the text from them',
    verbose=True,
    allow_delegation=False,
    backstory="""Expert in extracting links from content and scraping the text from the web""",
    llm=azure,
)

writer = Agent(
    role='Expert Writer',
    goal=f'Use the provided text and blend it coherent into a scientific article, use a academic concise writing style.',
    verbose=True,
    allow_delegation=False,
    backstory="""With a concise scientific writing style, you are adept at producing detailed drafts that incorporate critical findings.
    Your capacity to integrate cited literature into coherent narratives showcases your proficiency in generating well-supported academic texts.""",
    llm=azure,
)

generate_keywords = Task(
    description=f"Identify 5 - 10 boolean keywords related to {topic} for a scientific research.",
    expected_output="5 - 10 boolean keywords combined in one query.",
    agent=researcher,
    async_execution=False,
)

search = Task(
    description="Do a literature search with the provided keywords.",
    expected_output="A list with Topic's and Link's",
    agent=researcher,
    async_execution=False,
    context=[generate_keywords], 
)

scrape_text = Task(
    description="Use all provided links one by one and scrape the text with scrape_and_summarize_website tool.",
    agent=scraper,
    async_execution=False,
    tools=[CustomSearchTools().scrape_and_summarize_website],
)

write_article = Task(
    description=f"Use read_file tool to retrieve the content of the search results and write a detailed scientific article around {topic}, integrating all insights only from the search results, make sure to cite (the links) in numbers style and maintain a bibliography.",
    expected_output="Detailed article with a bibliography section, formated in markdown",
    agent=writer,
    tools=[read_file]
)

crew = Crew(
    #agents=[writer],
    #tasks=[write_article],
    agents=[researcher,scraper,writer],
    tasks=[generate_keywords,search,scrape_text,write_article],
    #manager_llm=azure, # The manager's LLM that will be used internally
	#process=Process.hierarchical,  # Designating the hierarchical approach
    process=Process.sequential,
    #full_output=True
)

# Kick off the crew's work
results = crew.kickoff()
print("---------Crew Work Results---------")
print(results)