#build a chatbot with an orchestrator to orchestrate the intend "buy prooduct" "information" "find product"
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import operator
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
import openai
import chromadb
import configparser
os.environ['OPENAI_API_KEY'] = "API KEY" 
# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="cdb.db")


# Define state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_step: str
    context: str

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o")

# Create intent classifier
intent_classifier_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a classifier that determines the user's intent. Classify as either: 'buy_product', 'information', 'find_product', or 'other'."),
    MessagesPlaceholder(variable_name="messages"),
    ("system", "Return only the classification as a single word.")
])

def classify_intent(state):
    response = llm.invoke(
        intent_classifier_prompt.format(messages=state["messages"])
    )
    return {"next_step": response.content.strip().lower()}

# Create context retriever
def get_context(state):
    
    config = configparser.ConfigParser()
    config.read('config.ini')
    start_url = config['DEFAULT']['collection_name']
    collection = chroma_client.get_collection(name=start_url)
    query = state["messages"][-1].content
    results = collection.query(
        query_texts=[query],
        n_results=2
    )
    context = "\n".join(results["documents"][0])
    return {"context": context}

# Create handlers for each intent
def handle_buy_product(state):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful sales assistant. Use the following context to help the customer make a purchase:\n{context}"),
        MessagesPlaceholder(variable_name="messages"),
    ])
    response = llm.invoke(prompt.format(context=state["context"], messages=state["messages"]))
    return {"messages": [AIMessage(content=response.content)]}

def handle_information(state):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an informative assistant. Use the following context to provide accurate information:\n{context}"),
        MessagesPlaceholder(variable_name="messages"),
    ])
    response = llm.invoke(prompt.format(context=state["context"], messages=state["messages"]))
    return {"messages": [AIMessage(content=response.content)]}

def handle_find_product(state):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a product finder. Use the following context to help locate specific products:\n{context}"),
        MessagesPlaceholder(variable_name="messages"),
    ])
    response = llm.invoke(prompt.format(context=state["context"], messages=state["messages"]))
    return {"messages": [AIMessage(content=response.content)]}

def handle_other(state):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Provide a general response:\n{context}"),
        MessagesPlaceholder(variable_name="messages"),
    ])
    response = llm.invoke(prompt.format(context=state["context"], messages=state["messages"]))
    return {"messages": [AIMessage(content=response.content)]}

# Create workflow graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("classify", classify_intent)
workflow.add_node("get_context", get_context)
workflow.add_node("buy_product", handle_buy_product)
workflow.add_node("information", handle_information)
workflow.add_node("find_product", handle_find_product)
workflow.add_node("other", handle_other)

# Create edges
workflow.set_entry_point("classify")
workflow.add_edge("classify", "get_context")

# Add conditional edges from get_context
workflow.add_conditional_edges(
    "get_context",
    lambda x: x["next_step"],
    {
        "buy_product": "buy_product",
        "information": "information",
        "find_product": "find_product",
        "other": "other"
    }
)

# Set end nodes
workflow.add_edge("buy_product", END)
workflow.add_edge("information", END)
workflow.add_edge("find_product", END)
workflow.add_edge("other", END)

# Compile workflow
app = workflow.compile()

# Function to run chat
def chat(message: str):
    result = app.invoke({"messages": [HumanMessage(content=message)]})
    return result["messages"][-1].content



