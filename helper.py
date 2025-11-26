import pandas as pd
from agents.db import execute_query

#function for converting a list of sql queries into a list of dataframes
def get_dfs(queries):

    dfs = []

    for query in queries:
        df = execute_query(query)
        dfs.append(df)
    
    return dfs

#if dataframes are too big, llm's will either struggle or get very expensive to manage so we 
#send the summary statistics instead with this function 
def summarize_dfs(dfs):

    summarized_dfs = []
    
    for df in dfs:

        if df.shape[0] < 300:
            summarized_dfs.append(df)
        else:
            # summary = 'Summary Statstics:\n\n'
            # summary += str(df.describe()) + '\n\n\n' 
            # summary += 'Correlation Matrix:\n' + str(df.corr(numeric_only=True))
            summary = df.head(300)
            summarized_dfs.append(summary)

    return summarized_dfs
