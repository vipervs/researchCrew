# ResearchNET
 **# Automated Research Article Generation with CrewAI**

This project demonstrates how to automate the generation of a scientific article using CrewAI, a framework for orchestrating multi-agent AI collaboration. 

**Key Features:**

- **AI-Powered Research and Writing:** Leverages multiple AI agents with distinct roles to conduct research, gather information, and craft a comprehensive article.
- **Collaborative AI Workflow:** Employs CrewAI to coordinate the agents' efforts, ensuring a cohesive and efficient process.
- **Customizable Topic Selection:** Allows users to specify the desired research topic, enabling tailored content creation.
- **Integrated Research and Writing Tools:** Utilizes external tools like Google Custom Search and text scraping capabilities for comprehensive data retrieval.
- **Scientific Writing Style:** Generates articles in a concise, academic writing style, incorporating citations and a bibliography.

**Getting Started:**

1. Install required libraries:
   ```bash
   pip install crewai langchain langchain-openai dotenv
   ```
2. Create a `.env` file and add your API Information.
3. Run the project:
   ```bash
   python main.py
   ```
4. Enter the desired research topic when prompted.

**Workflow:**

1. **Researcher Agent:**
   - Generates relevant keywords for the specified topic.
   - Conducts a literature search using Google Custom Search.
2. **Scraper Agent:**
   - Scrapes text from the provided links using a custom scraping tool.
3. **Writer Agent:**
   - Retrieves the scraped text.
   - Composes a detailed scientific article with citations and a bibliography.
   - Formats the article in Markdown.

**Output:**

The project prints the generated article to the console.
