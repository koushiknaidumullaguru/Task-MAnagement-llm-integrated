from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

def get_Query(text : str):

    llm = OllamaLLM(model="gemma:2b")
    prompt_template = """
    You are an expert in SQL query generation. Below are the schemas of two tables:

### Table 1: "users" ###
- id: Integer (Primary Key, Auto Increment) → User ID
- username: String (255, Not Null) → Username
- email: String (255, Unique, Not Null) → User Email
- password: String (255, Not Null) → User Password

### Table 2: "TODO" ###
- id: Integer (Primary Key, Auto Increment) → Task ID
- activity: String (255, Not Null) → Task Description
- Time_Created: DateTime (Default: Current Timestamp) → Task Creation Time
- Status: String (255, Not Null) → Task Status
- isExisted: Boolean (Default: True, Not Null) → Whether the task exists
- user_id: Integer (Foreign Key → users.id, Cascade on Delete, Not Null) → Foreign key linking to users table

Using the above table schemas, **generate an optimized SQL query** for the following natural language request:

    ### DON'T GIVE THE EXPLANATION. GIVE ONLY SQL STATEMENT. GIVE STATEMENT IN ONE LINE ###

    Query: {query}

    SQL:
"""


    prompt = PromptTemplate(input_variables=["query"], template=prompt_template)
    llm_chain = prompt | llm
    user_prompt = text
    sql_query = llm_chain.invoke({"query": user_prompt})
    return sql_query[6:-3]