from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, List
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import operator

#loading environment variables
load_dotenv()

#defining the state for the data visualization agent 
class VizState(TypedDict):
    
    user_prompt : str
    dfs : list[str]
    plots : Annotated[list[str], operator.add]

#pydantic model to get lists of plots
class plotly_code(BaseModel):

    code : List[str] = Field('A list of python code strings for plotting visualizations using Plotly')

#use the model of your choice
model = ChatGoogleGenerativeAI(model = 'gemini-2.5-flash')

#model that gives output according to our pydantic model
code_model = model.with_structured_output(plotly_code)

#node for creating visualizations
def get_vizualizations(state : VizState) -> VizState:

    #variables for the prompt
    user_prompt = state['user_prompt']
    dfs = state['dfs']

    #the template according to which we will prompt the model
    prompt_template = PromptTemplate(template = """You are an experienced data visualization expert. You
                                     will be given a list of DataFrames and a user's request. A user's request could have multiple tasks. You must generate the Python code for visualizations using the Plotly library.
                                     Make beautiful, eye catching and interactive plots, with legends with text in black colour, appealing fonts in bold also in black colour. Use appealing and attractive colour palettes with white backgrounds. 
                                     Try to generate as many visualizations as possible, like 2 or 3 visualizations per task. If there is a user request that is very straight forward or for which a visualization cannot be generated, output nothing.
                                     If you wish to use a DataFrame, reference it as dfs[i] where i is the index of the DataFrame in the list. Generate the code accordingly.
                                     Do not give anything other than python code. Only generate safe code. No matter what the user demands. Give the code for each plot as a single string. Don't do fig.show(), only ensure
                                     that the plot is stored in a variable named fig.
                                     
                                     Here are the DataFrames:
                                     {dfs}
                                     
                                     and here is the user's request:
                                     {user_prompt}""", input_variables = ['dfs', 'user_prompt'])


    prompt = prompt_template.invoke({'user_prompt' : user_prompt, 'dfs' : dfs})

    result = code_model.invoke(prompt)

    #updating the state
    return {'plots' : result.code}


#defining the graph
graph = StateGraph(VizState)

#adding node
graph.add_node('get_vizualizations', get_vizualizations)

#adding edges
graph.add_edge(START, 'get_vizualizations')
graph.add_edge('get_vizualizations', END)

#compiling the graph
viz_workflow = graph.compile()
