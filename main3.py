import os
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain_community.llms import OpenAI as LangchainOpenAI
from sql_execution import execute_mysql_query  # Import the execute_mysql_query function
from trialprompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE1
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
from savedex import schema_venum
import uuid

# Setup env variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")

# schema_details
schema_details = schema_venum()

# Set Streamlit page configuration
st.set_page_config(page_title="AI SQL", layout="wide")

# Initialize session states
if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []
if "sql_queries" not in st.session_state:
    st.session_state["sql_queries"] = []
if "input_history" not in st.session_state:
    st.session_state["input_history"] = []
if "output_tables" not in st.session_state:
    st.session_state["output_tables"] = []
if "con_history" not in st.session_state:
    st.session_state["con_history"] = []
if "sql_statement" not in st.session_state:
    st.session_state["sql_statement"] = []
if 'chart_buffer' not in st.session_state:
    st.session_state['chart_buffer'] = None
if "sidebar_selection" not in st.session_state:
    st.session_state["sidebar_selection"] = "AI-SQL"

history = st.session_state["past"]

def new_chat():
    """
    Clears session state and starts a new chat.
    """
    save = []
    for i in range(len(st.session_state["generated"]) - 1, -1, -1):
        save.append("User:" + st.session_state["past"][i])
        save.append("Bot:" + str(st.session_state["generated"][i]))
    session = [(user, bot) for user, bot in zip(st.session_state["past"], st.session_state["generated"])]
    st.session_state["stored_session"].append(session)
    # Reset the session state
    st.session_state["generated"] = []
    st.session_state["past"] = []
    st.session_state["input"] = ""
    st.session_state["output_tables"] = []
    st.session_state["input_history"] = []
    st.session_state["sql_queries"] = []
    st.session_state["con_history"] = []
    st.session_state["sql_statement"] = []
    st.session_state.entity_memory.buffer.clear()

# Create an OpenAI instance
llm = LangchainOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo-instruct", verbose=False)

if "entity_memory" not in st.session_state:
    st.session_state.entity_memory = ConversationEntityMemory(llm=llm)

conversation_chain = ConversationChain(llm=llm, prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE1, verbose=True, memory=st.session_state.entity_memory)

# Add a button to start a new chat
st.markdown(
    """
<style>
button.st-emotion-cache-s48dsx {
    align-content: center;
    height: auto;
    width: auto;
    padding-left: 70px !important;  
    padding-right: 70px !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# Sidebar option menu
with st.sidebar:
    selected = option_menu("🏫Welcome SMVEC", ["Home", "AI-SQL", "Schema"],
                           icons=['house', 'database', 'table'], menu_icon="🏫", default_index=1, orientation="vertical",
                           styles={
                               "container": {
                                   "width": "290px",
                                   "padding": "5px",
                                   "float": "left",
                                   "background-color": "#202126",
                                   "font-family": "'Trebuchet MS',Helvetica,sans-serif"
                               },
                               "icon": {
                                   "color": "white",
                                   "font-size": "20px"
                               },
                               "nav-link": {
                                   "color": "white",
                                   "font-size": "20px",
                                   "margin": "0px",
                                   "hover-color": "red"
                               },
                               "nav-link-selected": {
                                   "background-color": "#e64c4c"
                               }
                           })

# Store the sidebar selection in the session state
st.session_state.sidebar_selection = selected

# Title
s = f"<center><span style='font-size:55px; color:rgb(180,0,60)'>AI SQL </span><span style='font-size:55px; color:rgb(255,255,255)'>Assistant</span></center>"
st.markdown(s, unsafe_allow_html=True)
st.divider()
with st.sidebar.empty():
    st.write(' ')
with st.sidebar.empty():
    st.write(' ')

if st.session_state.sidebar_selection == "Home":
    try:
        st.video('cts.mp4', loop=True)
    except:
        st.empty()
    st.subheader("About :rainbow[AI SQL Assistant]", divider="red")
    st.markdown(""" 
                - Introducing our :red[AI SQL] Assistant: a cutting-edge solution powered by :blue[generative AI] technology, designed to :orange[revolutionize] the way users interact with databases.  
                - Imagine having an :blue[intelligent] virtual assistant at your fingertips, capable of understanding your inquiries about :green[databases] and seamlessly converting them into :violet[SQL statements] to fetch and display the relevant data.  """)

    st.subheader("It's :rainbow[Functions]:", divider="red")
    st.markdown(""" 
                - At its core, our :red[AI SQL] Assistant harnesses the power of :blue[generative AI] to comprehend :violet[natural language] queries related to databases.  
                - Whether you're a seasoned :violet[data analyst] or a novice user, simply express your data needs in plain English, and our assistant will interpret your intent with remarkable :orange[accuracy].  """)

    st.subheader("It's :rainbow[Capabilities]:", divider="red")
    st.markdown(""" 
                - This assistant goes beyond mere :violet[keyword matching] by employing advanced :violet[natural language understanding] algorithms.  
                - It discerns the nuances of your queries, grasping the context and intent behind your :green[words].  
                - Whether you're requesting specific datasets, formulating :orange[complex analytical questions], or seeking :blue[insights] from your database, our :red[AI SQL] Assistant is up to the task.  
                - Once your query is :green[understood], our assistant :orange[seamlessly translates] it into :violet[SQL statements], the language of databases.  
                - It crafts :blue[optimized] queries tailored to your requirements, ensuring :violet[efficient data retrieval] with minimal effort on your part.  """)

    st.subheader(":rainbow[Key Feature]:", divider="red")
    st.markdown(""" 
                - Our AI SQL Assistant isn't just a :grey[cold, robotic] tool.  
                - It's designed to engage in :violet[natural conversation], adapting to your :blue[communication style] and :orange[responding dynamically] to your inputs.   
                - Whether you're providing additional "red[context], refining your :green[query], or simply engaging in small talk, our assistant maintains a :blue[fluid dialogue], enhancing the :rainbow[user experience].  """)

    st.subheader(":rainbow[Benefits] of AI-SQL Assistant", divider="red")
    st.markdown(""" 
                - With our :red[AI SQL] Assistant, interacting with databases becomes :orange[intuitive] and :orange[effortless].  
                - Gone are the days of :red[wrangling complex SQL syntax] or struggling to articulate your data needs.  
                - Instead, :orange[empower] yourself with a :orange[sophisticated] yet :blue[user-friendly] tool that streamlines the :violet[data retrieval process] and enables you to focus on deriving :blue[insights] and making :blue[informed decisions].  """)
    st.caption("""Join the forefront of data innovation with our AI SQL Assistant and unlock the 
                full potential of your database interactions. Experience the future of database management 
              today.""")
if st.session_state.sidebar_selection == "Schema":
    # Display the schema string in Streamlit with formatting
    st.markdown(f"<div style='font-family: Arial; color:white; line-height: 1.5;'>{schema_details}</div>", unsafe_allow_html=True)
if st.session_state.sidebar_selection == "AI-SQL":
    st.sidebar.button("New Chat", on_click=new_chat, type="primary")
    # Get the user input
    user_input = st.chat_input("Your AI assistant is here! Ask me anything ..")

    # Define icons
    user_icon = "👤"
    bot_icon = "🤖"

    download_data = []

    if user_input:
        with st.spinner("Generating your response"):
            # Generate SQL query
            sql_query = conversation_chain.run(input=user_input)

            # Concatenate user input and SQL query
            input_with_sql = f"{user_input} {sql_query}" if sql_query else user_input

            output = conversation_chain.run(input_with_sql)

            st.session_state.sql_statement.append(sql_query)

            # Check if the input contains a "SELECT" statement
            if "SELECT" in sql_query or "SHOW" in sql_query:
                # Execute the SQL query
                df = execute_mysql_query(sql_query)

                # Store user input and generated output
                st.session_state.past.append(user_input)
                st.session_state.generated.append(df)

                if isinstance(df, pd.DataFrame):
                    # Append the new DataFrame to the list of DataFrames
                    st.session_state.input_history.append(user_input)
                    st.session_state.output_tables.append(df)

            else:
                # If it's not a SELECT statement, simply append the user input
                st.session_state.past.append(user_input)
                st.session_state.generated.append(sql_query)
                if isinstance(sql_query, type(sql_query)):
                    st.session_state.con_history.append(sql_query)
                    st.session_state.input_history.append(user_input)

    # Display user input and AI response
    for input_, output, sql_query1 in zip(st.session_state.input_history, st.session_state.generated, st.session_state.sql_statement):
        st.markdown(f"{user_icon}<b>  :red[Your Input]</b>", unsafe_allow_html=True)
        with st.container():
            st.markdown(f"{input_}", unsafe_allow_html=True)
        st.write("")
        st.markdown(f"{bot_icon}<b>  :red[AI Response:]</b>", unsafe_allow_html=True)

        with st.container():
            if isinstance(output, pd.DataFrame) and not output.empty:
                tab_titles = ["Output", "SQL Query", "Visualization"]
                tabs = st.tabs(tab_titles)

                with tabs[0]:
                    st.markdown(":blue[Output]:")
                    st.write(output)

                with tabs[1]:
                    st.markdown("Generated :blue[SQL Query]:")
                    st.code(sql_query1)

                with tabs[2]:
                    st.markdown(":blue[Visualization]:")

                    def determine_chart_type(df):
                        num_cols = df.select_dtypes(include=['number']).columns
                        cat_cols = df.select_dtypes(include=['object', 'category']).columns

                        if len(cat_cols) == 1 and len(num_cols) == 1:
                            return 'bar'
                        elif (len(cat_cols)+len(num_cols)) == 1:
                            return 0
                        elif len(cat_cols) == 1 and len(num_cols) > 1:
                            return 'line'
                        elif len(cat_cols) > 1 and len(num_cols) == 1:
                            return 'stacked_bar'
                        elif len(cat_cols) == 0 and len(num_cols) > 1:
                            return 'scatter'
                        elif len(cat_cols) == 1 and 'percent' in num_cols[0].lower():
                            return 'pie'
                        else:
                            return 'line'

                    def generate_chart(df, chart_type):
                        fig, ax = plt.subplots(figsize=(10, 6))

                        if chart_type == 'bar':
                            cat_col = df.select_dtypes(include=['object', 'category']).columns[0]
                            num_col = df.select_dtypes(include=['number']).columns[0]
                            sns.barplot(x=cat_col, y=num_col, data=df, ax=ax, palette='viridis')
                            ax.set_title('Bar Chart')
                            ax.set_xlabel(cat_col.capitalize())
                            ax.set_ylabel(num_col.capitalize())

                        elif chart_type == 'line':
                            cat_col = df.select_dtypes(include=['object', 'category']).columns[0]
                            for num_col in df.select_dtypes(include=['number']).columns:
                                ax.plot(df[cat_col], df[num_col], marker='o', label=num_col.capitalize())
                            ax.set_title('Line Chart')
                            ax.set_xlabel(cat_col.capitalize())
                            ax.set_ylabel('Values')
                            ax.legend()

                        elif chart_type == 'stacked_bar':
                            num_col = df.select_dtypes(include=['number']).columns[0]
                            df.groupby(df.columns[0]).sum().plot(kind='bar', stacked=True, ax=ax)
                            ax.set_title('Stacked Bar Chart')
                            ax.set_xlabel('Categories')
                            ax.set_ylabel(num_col.capitalize())

                        elif chart_type == 'scatter':
                            num_cols = df.select_dtypes(include=['number']).columns
                            for i in range(len(num_cols)-1):
                                ax.scatter(df[num_cols[i]], df[num_cols[i+1]], label=f'{num_cols[i]} vs {num_cols[i+1]}')
                            ax.set_title('Scatter Chart')
                            ax.set_xlabel(num_cols[0].capitalize())
                            ax.set_ylabel(num_cols[1].capitalize())
                            ax.legend()

                        elif chart_type == 'pie':
                            cat_col = df.select_dtypes(include=['object', 'category']).columns[0]
                            num_col = df.select_dtypes(include=['number']).columns[0]
                            ax.pie(df[num_col], labels=df[cat_col], autopct='%1.1f%%', startangle=140)
                            ax.set_title('Pie Chart')

                        plt.tight_layout()
                        return fig

                    def plot_to_bytesio(df, chart_type):
                        fig = generate_chart(df, chart_type)
                        buf = BytesIO()
                        fig.savefig(buf, format="png")
                        buf.seek(0)
                        return buf

                    # Use ThreadPoolExecutor to handle chart generation in parallel
                    with ThreadPoolExecutor() as executor:
                        chart_type = determine_chart_type(output)
                        if chart_type:
                            future = executor.submit(plot_to_bytesio, output, chart_type)
                            buf = future.result()
                            st.session_state['chart_buffer'] = buf  # Store the chart buffer in session state

                            # Display the chart
                            unique_key = str(uuid.uuid4())
                            st.image(st.session_state['chart_buffer'], caption='Generated Chart', use_column_width=True)
                            # Prepare data for download
                            st.download_button(
                                    label="Download Data",
                                    data=st.session_state['chart_buffer'],
                                    file_name=f"chart{unique_key}.png",
                                    mime="image/png",
                                    key=f"download_button_data_{unique_key}"  # Unique key for this button
                                )


                        else:
                            st.write("No suitable chart type is found for the given data")
            elif isinstance(output, pd.DataFrame) and output.empty:
                st.write("No output obtained for the SQL query.")
            else:
                st.code(output)

    # Prepare data for download
    download_str = "\n".join(map(str, download_data))
    if download_str:
        st.download_button("Download", download_str)

    for i, sublist in enumerate(st.session_state.stored_session):
        with st.sidebar.expander(label=f"Conversation-Session:{i}"):
            st.write(sublist)

    # Allow the user to clear all stored conversation sessions
    if st.session_state.stored_session:
        if st.sidebar.checkbox("Clear-all"):
            del st.session_state.stored_session
