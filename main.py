import os
from crewai import Crew
from crewai import Task
from crewai import Agent
from tool import get_hotels, get_flights, get_places, get_iata_code, get_country_code
from load_dotenv import load_dotenv
from crewai import LLM, Agent, Crew
from pprint import pprint

# load_dotenv()

aviation_stackKey = st.secrets["aviation_stackKey"]
api_key = st.secrets["OPENAI_API_KEY"]
SERP_API =  st.secrets["SERP_API"]


# 1️⃣ Define your OpenAI model
from crewai import LLM

# aviation_stackKey = os.environ.get("aviation_stackKey")
# SERP_API = os.environ.get("SERP_API")

if not aviation_stackKey:
    raise RuntimeError("aviation_stackKey not set in environment")
if not SERP_API:
    raise RuntimeError("SERP_API not set in environment")

openai_llm = LLM(
    model="openai/gpt-4o",
    temperature=0.7,
    api_key=api_key
)
print(openai_llm)
print(openai_llm.provider)


event_planner_agent = Agent(
    role="Event Planner",
    goal="Plan complete trips based on user preferences using travel data APIs.",
    backstory=(
        "You are an expert event planner who organizes vacations, conferences, and tours. "
        "You use APIs to check flights, hotels, and local attractions."
    ),
    tools=[get_hotels, get_flights, get_places, get_iata_code, get_country_code],
    llm=openai_llm,
    verbose=True  
)  

print(event_planner_agent)
print("*******************agent created:**************************")

# dynamic_task.py
def create_dynamic_task(user_query: str):
    """
    Takes user input (like 'Plan my trip to Goa from Mumbai for this weekend')
    and returns a Task that uses the agent and tools.
    """
    task_description = (
        f"Understand the user request: '{user_query}'. "
        f"Use the available tools (get_hotels, get_flights, get_places) if it needed. And also use any other information from web search as well i.e. google search"
        f"to fetch and summarize relevant travel options. "
        f"Return a structured trip plan including hotels, flights, and places to visit in a text format"
    )
    return Task(description=task_description, expected_output="""Structured trip plan with best options for hotels, flights and attractions based on user preferences like no of days and budget etc in textual format with title and subcontent and then content but don't give any other details like tokens or any extra information that are not relevant \
    Example: 
    N days goa trip   
    Flights:
       -----
    Hotels:
      ------
    Tourist Places:
    Ist day:
    2nd day:
    3rd day:
    like that
      ----
    """, agent=event_planner_agent)


def handle_user_query(user_query: str):
    # Dynamically create task based on query
    dynamic_task = create_dynamic_task(user_query)

    print("Created Task:", dynamic_task.description)

    # Create Crew
    crew = Crew(
        agents=[event_planner_agent],
        tasks=[dynamic_task]
    )

    print("Starting Crew with task:", dynamic_task.description)

    # Run the Crew
    result = crew.kickoff()
    print("final result:", result)
    return result



