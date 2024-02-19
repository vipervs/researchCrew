import os
from crewai import Agent, Task, Crew, Process
from langchain.agents import load_tools
from langchain_openai import AzureChatOpenAI
from tools import CustomSearchTools
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

load_dotenv()

lmstudio = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    temperature=0.7,
)

gpt35 = ChatOpenAI(
    model_name="gpt-3.5-turbo", temperature="0"
)

azure = AzureChatOpenAI(
    model='azure',
    api_version='2023-07-01-preview',
    api_key=os.getenv("AZURE_API_KEY"),
    base_url=os.getenv("AZURE_BASE"),
)

gemini = ChatGoogleGenerativeAI(model="gemini-pro",
    verbose=True,
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

# Define the topic of interest
topic = 'AI in Global Health Challenges'

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
    tools=[CustomSearchTools.google_custom_search, CustomSearchTools().scrape_and_summarize_website],
    max_iter=20,
)

reader = Agent(
    role="Expert Reader",
    goal=f"Evaluate the found literature for relevance and alignment with the Resarch Topic: {topic}, if not you can request more literature.",
    verbose=True,
    allow_delegation=True,
    backstory="""You have an exceptional critical eye, enabling you to meticulously review and assess the literature. 
    Your role is pivotal in ensuring that only the most relevant and impactful sources are selected for further analysis and content creation.""",
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
    agent=researcher,
    async_execution=False,
    context=[search],
)

read_text = Task(
    description=f"Read the summaries and decide if they line up with the Research Topic: {topic}, if not ask for more sources from the Researcher",
    agent=reader,
    async_execution=False,
    context=[scrape_text],
)

# Forming the crew with a hierarchical process including the manager
crew = Crew(
    agents=[researcher,reader],
    tasks=[generate_keywords,search,scrape_text],
    #manager_llm=azure, # The manager's LLM that will be used internally
	#process=Process.hierarchical,  # Designating the hierarchical approach
    process=Process.sequential,
    #full_output=True
)

# Kick off the crew's work
results = crew.kickoff()

# Print the results
print("Crew Work Results:")
print(results)