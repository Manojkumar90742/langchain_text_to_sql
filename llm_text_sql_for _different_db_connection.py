import streamlit as st
import google.generativeai as genai
import mysql.connector

# Configure Genai Key
genai.configure(api_key="AIzaSyBlXxC5QS0_eOAvbaktOem-J8F7UGKZpJk")

# Function to generate SQL query
def get_gemini_response(user_input, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt, user_input])
    return response.text

# Function to retrieve query result from MySQL database
def read_mysql_query(sql, host, user, password, database):
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    connection.close()
    return rows

# Function to retrieve table schemas from MySQL database
def get_mysql_table_schemas(host, user, password, database):
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    table_schemas = {}
    for table in tables:
        table_name = table['Tables_in_' + database]
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        table_schemas[table_name] = [column['Field'] for column in columns]
    connection.close()
    return table_schemas

# Streamlit app
def main():
    st.title('Text to SQL Natural Language Query using GenAI')

    # Input fields for MySQL connection details
    mysql_host = st.text_input("MySQL Host")
    mysql_user = st.text_input("MySQL User")
    mysql_password = st.text_input("MySQL Password", type="password")
    mysql_database = st.text_input("MySQL Database")

    # Retrieve table schemas if MySQL connection details are provided
    table_schemas = None
    if mysql_host and mysql_user and mysql_password and mysql_database:
        table_schemas = get_mysql_table_schemas(mysql_host, mysql_user, mysql_password, mysql_database)

    # User input
    user_input = st.text_input('Enter Your Need: ')

    # Construct prompt with table schemas
    prompt = f"""You are a SQL code generator.
    Convert the following English query into a SQL query, considering possible variations and allowing for flexibility in user input.
    The user may not know the exact name in the database. Get the database schema details inbuilt. Generate an accurate query and fetch exact details from the database.
    Get trained on schemas where the database is connected. The names of user input may vary from the actual table names. Read and understand the meaning of user input very carefully.
    If the user input is irrelevant to the database display message as follows:
    "I'm sorry, but I am a SQL code generator and
    I cannot process the input provided as it does not relate to the database.
    If you have any specific questions related this database, please feel free to ask.\n"""

    if table_schemas:
        prompt += "\nTables in database:\n"
        for table_name, columns in table_schemas.items():
            prompt += f"- {table_name} ({', '.join(columns)})\n"

    prompt += f"""\nDo not infer any data based on previous training, strictly use only source text given below as input.\n
    ========
    {user_input}
    ========
    """

    # Generate SQL query
    if st.button('Generate Output'):
        if not user_input.strip():
            st.warning("Please provide a valid input.")
            return

        response = get_gemini_response(user_input, prompt)
        response = response.replace("```sql", "").replace("```", "").strip()
        st.write("Generated SQL Query:", response)
        
        if mysql_host and mysql_user and mysql_password and mysql_database:
            # If MySQL connection details are provided
            rows = read_mysql_query(response, mysql_host, mysql_user, mysql_password, mysql_database)
        else:
            st.warning("Please provide MySQL connection details.")
            return
        
        st.write("Query Result:")
        st.write(rows)

        # Convert SQL query to natural language using Gemini Pro
        natural_language = get_gemini_response(str(rows), 'Convert the following SQL query result into natural language:')
        st.write("Natural Language Output:")
        st.write(natural_language)


    # Refresh button
    if st.button('Refresh'):
        st.rerun()

if __name__ == "__main__":
    main()



