from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from agents.query_agent import query_workflow
from agents.summary_agent import summary_workflow
from agents.viz_agent import viz_workflow
from helper import get_dfs, summarize_dfs
import operator

#defining the state for the graph that will handle the entire system
class MasterState(TypedDict):

    user_prompt : str
    dfs : list[any]
    summary : str
    plots : Annotated[list[str], operator.add]


#wrapping the query agent into a node 
def query_node(state : MasterState) -> MasterState:

    user_prompt = state['user_prompt']

    queries = query_workflow.invoke({'user_prompt' : user_prompt})['sql_queries']

    dfs = get_dfs(queries)

    return {'dfs' : dfs}

#wrapping the visualization agent into a node 
def viz_node(state : MasterState) -> MasterState:

    user_prompt = state['user_prompt']

    dfs = state['dfs']

    plots = viz_workflow.invoke({'user_prompt' : user_prompt, 'dfs' : dfs})['plots']

    return {'plots' : plots}

#wrapping the summarizer agent into a node 
def summary_node(state : MasterState) -> MasterState:

    user_prompt = state['user_prompt']

    dfs = state['dfs']

    dfs = summarize_dfs(dfs)

    summary = summary_workflow.invoke({'user_prompt' : user_prompt, 'dfs' : dfs})['summary']

    return {'summary' : summary}

#creating the graph
graph = StateGraph(MasterState)

#adding nodes
graph.add_node('query_node', query_node)
graph.add_node('viz_node', viz_node)
graph.add_node('summary_node', summary_node)

#adding edges
graph.add_edge(START, 'query_node')
#adding parallelism
graph.add_edge('query_node', 'viz_node')
graph.add_edge('query_node', 'summary_node')
graph.add_edge('viz_node', END)
graph.add_edge('summary_node', END)

#compiling the graph
master_workflow = graph.compile()
