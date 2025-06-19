# MCP System Performance Analysis

A Python application for analyzing system performance metrics using the Model Context Protocol (MCP). This project leverages LangChain and the MCP framework to provide AI-powered analysis of CPU utilization and memory performance data.

## Overview

This project demonstrates how to use the Model Context Protocol (MCP) to create tools for system performance analysis that can be accessed by AI models. It consists of:

1. A server component that exposes system performance analysis tools through MCP
2. A client component that uses LangChain and an LLM (GPT-4o) to analyze the system performance data

The application analyzes system performance data stored in JSON format to identify:
- Processes with high CPU contention
- Processes with high memory usage

## Requirements

- Python 3.8+
- OpenAI API key for access to GPT-4o
- Required Python packages:
  - langchain-openai
  - langchain-mcp-adapters
  - langgraph

## Installation

1. Clone this repository
2. Install the required dependencies:


pip install mcp langchain-openai langchain-mcp-adapters langgraph


3. Set your OpenAI API key as an environment variable:

# For Windows PowerShell
$env:OPENAI_API_KEY = "your-api-key"

Alternatively, you can modify the `client.py` file to include your API key directly:

```python
model = ChatOpenAI(model="gpt-4o", api_key="your_api_key_here")
```

## Project Structure

```
MCP/json/
  ├── server.py           # MCP server with performance analysis tools
  ├── client.py           # Client app that connects to server and uses LLM
  ├── sys_perf.json       # Sample system performance data
  └── sys_perf_2.json     # Additional system performance data
```

## Data Format

The system performance data is stored in JSON files with a specific structure:
- `buckets`: Time-segmented performance data
- Each bucket contains:
  - `LowLevelMetric`: Contains detailed metrics for CPU and memory usage
  - CPU metrics include process-level data on CPU time and ready time
  - Memory metrics include data on working set size and commit size for processes

## Usage

1. Start the MCP server in one terminal:

```bash
cd path/to/MCP/
python server.py
```

2. Run the client application in a separate terminal:

```bash
cd path/to/MCP/
python client.py
```

The client will:
1. Connect to the MCP server
2. Load the available MCP tools for performance analysis
3. Create a LangChain ReAct agent with GPT-4o
4. Execute CPU contention and memory pressure analysis using natural language queries
5. Display the analysis results

## Example Queries

The client sends the following queries to the agent:

- **CPU Analysis**: "Find the top 5 processes with high CPU contention where ReadyTimeMsByPriority is at least 25% of CPUTimeInMs"
- **Memory Analysis**: "Identify the top 5 processes with high PeakWorkingSetSizeMiB for memory pressure"


## References

- [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp-adapters)
- [Model Context Protocol (MCP)](https://techcommunity.microsoft.com/blog/educatordeveloperblog/unleashing-the-power-of-model-context-protocol-mcp-a-game-changer-in-ai-integrat/4397564)
