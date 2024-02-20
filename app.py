import os
from crewai import Agent, Task, Crew, Process
from langchain.agents import load_tools
from langchain_openai import AzureChatOpenAI
from tools import CustomSearchTools
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

gpt35 = ChatOpenAI(
    model_name="gpt-3.5-turbo", temperature="0"
)

azure = AzureChatOpenAI(
    model='azure',
    api_version='2023-07-01-preview',
    api_key=os.getenv("AZURE_API_KEY"),
    base_url=os.getenv("AZURE_BASE"),
)

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
    goal=f'Use only the provided links and scrape the text with your tool',
    verbose=True,
    allow_delegation=False,
    backstory="""Expert in extracting links from content and scraping the text from the web""",
    llm=gpt35,
    tools=[CustomSearchTools().scrape_and_summarize_website],
)

writer = Agent(
    role='Expert Writer',
    goal=f'You will be provided abstracts and links around the topic: {topic}, make sure you only use the provided text and blend it coherent into a scientific article.',
    verbose=True,
    allow_delegation=False,
    backstory="""With a talent for blending scholarly research with exceptional writing skills, you are adept at producing detailed drafts that incorporate critical findings.
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
    description="Scrape the text from all provided links.",
    agent=scraper,
    async_execution=False,
    context=[search],
)

write_article = Task(
    description=f"Write a detailed scientific article around {topic}, integrating all insights from the literature search provided to you, make sure to cite the links in numbers style and maintain a bibliography referencing them.",
    agent=writer,
    context=[scrape_text],
)

crew = Crew(
    agents=[researcher,scraper,writer],
    tasks=[generate_keywords,search,scrape_text],
    #manager_llm=azure, # The manager's LLM that will be used internally
	#process=Process.hierarchical,  # Designating the hierarchical approach
    process=Process.sequential,
    #full_output=True
)

# Kick off the crew's work
results = crew.kickoff()
print("---------Crew Work Results---------")
print(results)