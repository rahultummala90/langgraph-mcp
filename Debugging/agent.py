from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import START, END
from langgraph.graph.state import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage
from IPython.display import Image, display


from dotenv import load_dotenv
load_dotenv()

# import os
# os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
# os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING", "true")
# os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
# os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "true")


from langchain.chat_models import init_chat_model
llm = init_chat_model("gpt-4-0613")

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def make_tool_graph():
    
    @tool
    def add(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b
    
    tools = [add]
    tool_node = ToolNode(tools)

    llm_with_tool = llm.bind_tools(tools)

    def call_llm_with_tools(state: State) -> State:
        response = llm_with_tool(state["messages"])
        return {"messages": state["messages"] + [response]}
    
    builder = StateGraph(State)

    builder.add_node("llm_tool_call", call_llm_with_tools)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "llm_tool_call")
    builder.add_conditional_edges(
        "llm_tool_call",
        tools_condition
    )
    builder.add_edge("tools", END)

    graph = builder.compile()

    return graph

tool_agent = make_tool_graph()