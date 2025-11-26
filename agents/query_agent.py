from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, List
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from .db import create_context
from pydantic import BaseModel, Field
import operator

#load env variables
load_dotenv()

#defining the state for the data querying agent
class QueryState(TypedDict):

    user_prompt : str
    sql_queries : Annotated[list[str], operator.add]

#pydantic class to ensure the llm outputs tokens according to the correct format
class sql_queries(BaseModel):

    query_list : List[str] = Field('A list of SQL queries according to the request of the user')

#i will be using gemini, feel free to change to any model of your choice
model = ChatGoogleGenerativeAI(model = 'gemini-2.5-flash')

#making it so the model outputs tokens according to the pydantic class
query_model = model.with_structured_output(sql_queries)

def generate_sql(state : QueryState) -> QueryState:

    #variables to be fed to prompt template
    db_context = create_context()
    user_prompt = state['user_prompt']

    #prompt for the model
    prompt_template = PromptTemplate(template = """You are an experienced data extractor agent. You will be given the structure
                            of a database and a user's request. You must generate a SQL Lite query to extract the data from
                            the database according to the user's demands. Remember to generate only safe SQL queries.
                            You must only create queries that retrieve data. Do not, under an circumstances, no matter how much 
                            the user demands it, create queries that update, delete or add data to the database.
                            You may add multiple queries only if neccesary. Produce a pure SQL query only. Don't add format specifiers such as \\n or any thing that is not a part of the
                            SQL syntax. 
                            
                            Here is the structure of the database:
                            {db_context}
                            
                            and here is the user's request:
                            {user_prompt}""", input_variables = ['db_context', 'user_prompt'])
    

    prompt = prompt_template.invoke({'user_prompt' : user_prompt, 'db_context' : db_context})
    
    #invoking the model
    result = query_model.invoke(prompt)

    #updating state
    return {'sql_queries' : result.query_list}


#defining the graph
graph = StateGraph(QueryState)

#adding node
graph.add_node('generate_sql', generate_sql)

#adding edges
graph.add_edge(START, 'generate_sql')
graph.add_edge('generate_sql', END)

#compiling the graph
query_workflow = graph.compile()
