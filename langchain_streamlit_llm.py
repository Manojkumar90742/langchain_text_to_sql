import streamlit as st
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
def main():
    st.title('Text to SQL Natural Language Query using GenAI')

    db_user = st.text_input("MySQL User")
    db_password = st.text_input("MySQL Password", type="password")
    db_host = st.text_input("MySQL Host")
    db_name = st.text_input("MySQL Database")
    db = None  # Initialize db variable to None

    if db_user and db_password and db_host and db_name:
        db = SQLDatabase.from_uri(f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}")
    user_input = st.text_input('Enter Your Need: ')

    llm = ChatGoogleGenerativeAI(model='gemini-pro', temperature=0)

    if db:  # Check if db is not None before using it
        generate_query = create_sql_query_chain(llm, db)
        execute_query = QuerySQLDataBaseTool(db=db)
        chain = generate_query | execute_query


        answer_prompt = PromptTemplate.from_template(
            """Given the following user question, corresponding SQL query, and SQL result, answer the user question with some neat description.
            If the user input is irrelevant to the database display message as follows:
            "I'm sorry, I cannot process the input provided as it does not relate to this database "company_details".
            If you have any specific questions related this database, please feel free to ask."
            Question: {question}
            SQL Query: {query}
            SQL Result: {result}
            Answer: """
        )

    if st.button('Generate Output'):
            rephrase_answer = answer_prompt | llm | StrOutputParser()
            chain = (
                RunnablePassthrough.assign(query=generate_query).assign(
                    result=itemgetter("query") | execute_query
                )
                | rephrase_answer
            )
            st.write("Natural Language Output : ")
            st.write(chain.invoke({'question': f'Provide me only the query dont give any other additional words such as sql to the human {user_input}'}))

    if st.button('Refresh'):
        st.rerun()

if __name__ == "__main__":
    main()
