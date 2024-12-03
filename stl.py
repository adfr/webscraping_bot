import streamlit as st
from build_bot import chat
from index_pipeline import crawl_website

st.title("Website Chatbot")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.indexed = False

# Website URL input
collection_name = st.text_input("Enter a name for this website:", "my_website")
website_url = st.text_input("Enter website URL to index:", "https://www.example.com")

if st.button("Index Website") and not st.session_state.indexed:
    with st.spinner("Indexing website content..."):
        crawl_website(website_url,collection_name)
    # Write collection name to config for persistence
    import configparser
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'collection_name': collection_name}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    st.session_state.indexed = True
    st.success("Website indexed successfully!")

if st.session_state.indexed:
    # Display chat messages from history on rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What would you like to know about this website?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        response = chat(prompt)
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.info("Please index a website first before starting the chat.")
