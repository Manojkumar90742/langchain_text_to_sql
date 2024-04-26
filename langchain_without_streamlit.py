import os
import google.generativeai as genai
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough


db_user = "root"
db_password = "manojkumar123"
db_host = "localhost"
db_name = "company_details"

#db = SQLDatabase.from_uri('mysql+mysqlconnector://root:manojkumar123@localhost:3306/department_management')

db = SQLDatabase.from_uri(f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}")

# Type of database.
print(db.dialect) 

# Display the table names
print(db.get_usable_table_names())

#Display the table details
print(db.table_info)


llm = ChatGoogleGenerativeAI(model='gemini-pro',temperature=0)
# genai.Gen
generate_query = create_sql_query_chain(llm,db)



execute_query = QuerySQLDataBaseTool(db=db)
chain = generate_query|execute_query


answer_prompt = PromptTemplate.from_template(
     """Given the following user question, corresponding SQL query, and SQL result, answer the user question with some neat description.
     If the user input is irrelevant to the database display message as follows:
    "I'm sorry, I cannot process the input provided as it does not relate to this database "company_details".
    If you have any specific questions related this database , please feel free to ask."
 Question: {question}
 SQL Query: {query}
 SQL Result: {result}
 Answer: """
)

rephrase_answer = answer_prompt | llm | StrOutputParser()

chain = (
     RunnablePassthrough.assign(query=generate_query).assign(
         result=itemgetter("query") | execute_query
     )
     | rephrase_answer
 )

user_input=input('Enter your need : ')

output=chain.invoke({'question':f'Provide me only the query dont give any other additional words such as sql to the human {user_input}'})
print(output)