import streamlit as st
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
#<span style="background: linear-gradient(to right, darkblue, #B0FC38); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">to</span>
def main():


    try:
        # Add title to your Streamlit app


        # Load and display an image from a local file
        image_path ="dg_logo_bg.png"
        st.sidebar.image(image_path, use_column_width=True)
        text = '<font color="teal" font-family: caveat>"Text to SQL Natural Language Query using GenAI is a tool.It is the part of data genius team that can help you generate SQL queries from natural language. This can make it much easier to use SQL, even if you are not a programmer."</font>'
        st.sidebar.write(text, unsafe_allow_html=True)
        image_path_2 ="MicrosoftTeams-image.png"
        st.sidebar.image(image_path_2 ,use_column_width=True)
        text_2 = '<font color="teal" font-family: caveat>"Hi Buddy"</font>'
        st.sidebar.write(text_2, unsafe_allow_html=True)
        text_3 = '<font color="teal" font-family: caveat>"Pozent - Pioneering AI Solutions . Deep Dive In AI Excellence"</font>'
        st.sidebar.write(text_3, unsafe_allow_html=True)
        text_4 = '<font color="black" font-family: caveat> For More Enthusiasm </font>'
        st.sidebar.write(text_4, unsafe_allow_html=True)
        st.sidebar.write('<a href="https://pozent.com/">        Contact Us</a>', unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"An error occurred: {e}")

    styled_text = """
    <h1 style="font-family: 'Peace Sans', sans-serif;">
        <span style="color: #006DB5;">Text</span>
        <span style="color: #006DB5;"> </span>
        <span style="color: #006DB5;">To</span>
        <span style="color: #006DB5;"> </span>
        <span style="color: #006DB5;">SQL</span>
        <span style="color: #006DB5;"> </span>
        <span style="color: #006DB5;">Natural</span>
        <span style="color: #0XFF0D47A1;"> </span>
        <span style="background: linear-gradient(to right, #006DB5, #00FF00); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Language</span>
        <span style="color: #00FF00;"> </span>
        <span style="color: #00FF00;">Query</span>
        <span style="color: #00FF00;"> </span>
        <span style="color: #00FF00;">using </span>
        <span style="color: #00FF00;"> </span>
        <span style="color: #00FF00;">GenAI</span>
    </h1>
"""

# Display the styled text
    st.write(styled_text, unsafe_allow_html=True)


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
