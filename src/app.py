import streamlit as st
from ai.langchain_rag import create_agent


st.title("Law GPT Indonesia")

if "messages" not in st.session_state:
    st.session_state.messages = []

def convert_message_to_history():
    history = []
    for message in st.session_state.messages:
        history.append({
            "role": message["role"],
            "content": "\n".join([str(message_content[1]) for message_content in message["content"]])
        })
    
    return history

agent = create_agent(debug_mode=True)

# display all historical messages
for message in st.session_state.messages:
    role_message = st.chat_message(message["role"])
    for cont_type, content in message["content"]:
        if cont_type == "markdown":
            role_message.markdown(content)
        elif cont_type == "code_sql":
            role_message.code(content, language="sql", line_numbers=True)
        elif cont_type == "dataframe":
            role_message.dataframe(content)
        elif cont_type == "plotly":
            role_message.plotly_chart(content)
        elif cont_type == "error":
            role_message.error(content)
        else:
            role_message.write(content)

prompt = st.chat_input("Ada kasus apakah yang terjadi?")

if prompt:
    # display the prompt
    st.chat_message("user").markdown(prompt)
    # store the user prompts inside the messages session state
    st.session_state.messages.append({
        "role": "user",
        "content": [("markdown", prompt)]
    })
    assistant_message = st.chat_message("assistant")

    response = agent.run(prompt, stream=False).content
    if response:
        assistant_message.markdown(response)
        st.session_state.messages.append({
            "role": "assistant",
            "content": [("markdown", response)]
        })
