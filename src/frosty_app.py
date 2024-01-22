from openai import OpenAI
import re
import streamlit as st
import matplotlib.pyplot as plt

from prompts import get_system_prompt

st.title("☃️ Frosty")

# Initialize the chat messages history
client = OpenAI(api_key=st.secrets.OPENAI_API_KEY)
if "messages" not in st.session_state:
    # system prompt includes table information, rules, and prompts the LLM to produce
    # a welcome message to the user.
    st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]

# Prompt for user input and save
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})

# display the existing chat messages
for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "results" in message:
            st.dataframe(message["results"])

# If last message is not from assistant, we need to generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        response = ""
        resp_container = st.empty()
        for delta in client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        ):
            response += (delta.choices[0].delta.content or "")
            resp_container.markdown(response)




# Check if the response contains instructions for plotting based on SQL results
if "plot_matplotlib_sql" in response:
    # Extract column names for x and y values from the instruction
    plot_instructions = response.split("\n")[1]
    plot_instruction_lines = plot_instructions.split("\n")

    # Extract x_column and y_column from the instruction
    x_column = y_column = None
    for line in plot_instruction_lines:
        if "x_column" in line:
            x_column = line.split("=")[1].strip(" '\"")
        elif "y_column" in line:
            y_column = line.split("=")[1].strip(" '\"")

    # Fetch data from Snowflake based on the SQL query
    sql_match = re.search(r"```sql\n(.*)\n```", response, re.DOTALL)
    if sql_match and x_column is not None and y_column is not None:
        sql_query = sql_match.group(1)
        conn = st.connection("snowflake")
        sql_results = conn.query(sql_query)

        # Extract x and y column data from the SQL results
        x_values = sql_results[x_column].tolist()
        y_values = sql_results[y_column].tolist()

        # Generate and display the line chart using Matplotlib
        plt.figure()
        plt.plot(x_values, y_values)
        st.pyplot(plt)



        message = {"role": "assistant", "content": response}
        # Parse the response for a SQL query and execute if available
        sql_match = re.search(r"```sql\n(.*)\n```", response, re.DOTALL)
        if sql_match:
            sql = sql_match.group(1)
            conn = st.connection("snowflake")
            message["results"] = conn.query(sql)
            st.dataframe(message["results"])
        st.session_state.messages.append(message)
