from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI


from dotenv import load_dotenv
load_dotenv()

import asyncio

async def main():
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": ["mathserver.py"],
                "transport": "stdio"
            },
            "weather": {
               "url": "http://localhost:8000/mcp",
                "transport": "streamable-http"
            }
        }
    )
    tools = await client.get_tools()
    llm = ChatOpenAI(model="gpt-4-0613", temperature=0)
    agent = create_agent(llm, tools)

    math_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "What is the result of add(5, 3) and multiply(4, 2)?"}]}
    )

    print("Math response:", math_response['messages'][-1].content)

    weather_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "What is the weather like in New York?"}]}
    )

    print("Weather response:", weather_response['messages'][-1].content)

asyncio.run(main())