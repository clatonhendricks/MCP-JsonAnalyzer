import asyncio
from mcp import ClientSession, StdioServerParameters
from langchain_openai import ChatOpenAI
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent


# Define server parameters

server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
)


# make sure to have the key set in the environment variable OPENAI_API_KEY
# or set it in the code directly as a parameter to ChatOpenAI
# e.g., model = ChatOpenAI(model="gpt-4o", api_key="your_api_key_here")
model = ChatOpenAI(model="gpt-4o") # type: ignore

async def run_agent():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools)
            
            # CPU contention analysis example
            cpu_query = "Find the top 5 processes with high CPU contention where ReadyTimeMsByPriority is at least 25% of CPUTimeInMs"
            cpu_response = await agent.ainvoke({"messages": cpu_query})
            
            # Memory pressure analysis example
            memory_query = "Identify the top 5 processes with high PeakWorkingSetSizeMiB for memory pressure"
            memory_response = await agent.ainvoke({"messages": memory_query})
            
            return {
                "cpu_analysis": cpu_response["messages"][3].content,
                "memory_analysis": memory_response["messages"][3].content,
                "cpu_response": cpu_response
            }

if __name__ == "__main__":
    results = asyncio.run(run_agent())
    print("\n--- CPU Contention Analysis ---")
    print(results["cpu_analysis"])
        
    print("\n--- Memory Pressure Analysis ---")
    print(results["memory_analysis"])

    # print("\n--- Full CPU Response ---")
    # print(results["cpu_response"])