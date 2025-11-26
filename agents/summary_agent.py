from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

#loading environment variables
load_dotenv()

#defining the state for the agent that provides insights and summaries about the data
class SummaryState(TypedDict):

    user_prompt : str
    dfs : list[str]
    summary : str


#use the model of your choice here
model = ChatGoogleGenerativeAI(model = 'gemini-2.5-flash')

#defining the node that will create the summary
def create_summary(state : SummaryState) -> SummaryState:

    #variables to be fed to prompt template
    user_prompt = state['user_prompt']
    dfs = state['dfs']

    #the prompt template that the model will be fed
    prompt_template = PromptTemplate(template = """You are a senior data analyst. You will be given a user's request and a list of summary statistics or the whole dataframe. 
                                    Your job is to analyze the data and produce accurate, concise insights according to the user's request without guessing.
                                    Always base your reasoning strictly on the data. If the data is simple and small, there is no need to overanalyze it according
                                    to the guidelines given below. Analyze and give insights based on the data's complexity. Remember they are
                                    guidlines, not hard and fast rules that need to be addressed all the time. You must respond as if the user has 
                                    directly asked you a question.

                                    Guidelines:
                                    1. Overall summary  
                                    

                                    2. Trends and patterns  
                                    - Describe any increasing or decreasing trends.  
                                    - Identify any cyclic, seasonal, or irregular patterns.  
                                    - Note any correlations between columns.

                                    3. Insights and interpretation  
                                    - What does the data imply?  
                                    - What are the notable findings, outliers, or anomalies? 
                                     
                                    REQUIREMENTS:
                                    - Use only the data provided.
                                    - Refer to specific values or ranges when making claims.
                                    - If something cannot be determined, explicitly say so.                                     
                                    
                                    User Request:
                                    {user_prompt}

                                    Data:
                                    {dfs}
                                     
                                     """, input_variables = ['user_prompt','dfs'])
    
    
    prompt = prompt_template.invoke({'user_prompt' : user_prompt, 'dfs' : dfs})

    result = model.invoke(prompt)

    #updating the state
    return {'summary' : result.content}


#defining the graph
graph = StateGraph(SummaryState)

#adding node
graph.add_node('create_summary', create_summary)

#adding edges
graph.add_edge(START, 'create_summary')
graph.add_edge('create_summary', END)

#compiling the graph
summary_workflow = graph.compile()
