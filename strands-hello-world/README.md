# Strands hello-world

The smallest Strands agent that does something interesting: a Claude-powered agent on Bedrock with one tool.

## What it shows

- How to instantiate a Strands `Agent` with a Bedrock model
- How to define a tool with the `@tool` decorator
- How the agent autonomously decides when to call the tool

## Prerequisites

- Bedrock access in `us-east-1` (or change `region_name` in `agent.py`)
- Model access granted for `anthropic.claude-3-5-sonnet-20241022-v2:0` (or change `model_id`)
- AWS credentials configured locally

## Run it

```bash
cd strands-hello-world
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python agent.py
```

Expected output:

```
--- Agent response ---
The current time in São Paulo is 2026-04-24 16:45:12 BRT.
```

## Make it yours

Try modifying the tool to do something relevant to your workload:

- A tool that queries DynamoDB for an order status
- A tool that calls an internal REST API with a bearer token
- A tool that returns the last N entries from CloudWatch Logs Insights

The pattern is identical: `@tool` decorator, typed arguments, return a string.

## When Strands is the right choice

- You need an agent that decides which tool to call based on user intent
- You want the reasoning to happen in the agent code, not hidden behind an API
- You want to swap model providers without rewriting the agent
- You want local development with the same code that runs in production

## When Strands is the wrong choice

- You only need a single prompt with no tool use → just call Bedrock directly
- You need a managed runtime with autoscaling → pair it with AgentCore (see sibling module)
- You need agent-to-agent communication → pair it with A2A (see sibling module)

## References

- [Strands Agents documentation](https://strandsagents.com/)
- [Bedrock model IDs](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html)
