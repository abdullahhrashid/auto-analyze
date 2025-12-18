# AutoAnalyze

**AutoAnalyze** is an **AI-powered data analysis engine** built using **LangGraph** and **Streamlit**.  
It allows you to query your database using natural language and receive visualizations, insights, and data summaries automatically.

---

##  Features

-  Natural-language data querying  
-  Automated Plotly visualizations  
-  Powered by LLMs (OpenAI, Anthropic, or Google)  
-  Modular LangGraph workflow  
-  Interactive Streamlit dashboard  

---

##  Setup Instructions

### 1. Connect Your Database
Update the `db.py` file located in the `agents/` folder.

Inside `db.py`, configure your SQL database connection using **SQLAlchemy**:

### 2. Create a .env file and add the API key from the LLM provider of your choice
This project utilizes Gemini as it's brain. If you want to use another model, simply change 2 lines of code in the agent files to use the model from the company of your choice.

### 3. Run the App
Simply run the command `streamlit run app.py` and ask questions in natural language and get ready insights into your data. The better your LLM provider, the better the results.
