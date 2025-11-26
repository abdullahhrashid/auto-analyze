from sqlalchemy import create_engine, MetaData
from langchain.tools import tool
import pandas as pd

#connect your own database here!
engine = create_engine('sqlite:///C:/Users/User/Desktop/ai analyst dashboard/agents/sakila.db')

#creates a context for your database for the agent
def create_context():

    metadata = MetaData()
    metadata.reflect(engine)

    context = ''

    #get the structure for each table
    for table_name, table in metadata.tables.items():
        context += f'\nTable: {table_name}'
        for column in table.columns:
            context += f'\n  {column.name} - {column.type} - nullable={column.nullable}'

    #get the foreign key relationship between each table
    context += '\nForeign Key Relationships:'
    for table_name, table in metadata.tables.items():
        for fk in table.foreign_keys:
            context += f'\n  {table_name}.{fk.parent.name} -> {fk.column.table.name}.{fk.column.name}'
    
    return(context)

#executes a sql query on our database and returns the result as a pandas dataframe
def execute_query(sql_query):
    
    df = pd.read_sql(sql = sql_query, con = engine) 

    return df
