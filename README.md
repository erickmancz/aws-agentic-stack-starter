# AWS Agentic Stack Starter

Companion repository for **Week 2** of [Golden Jacket Field Notes](https://github.com/erickmancz/golden-jacket-field-notes): *"The AWS Agentic Stack Explained: Strands, AgentCore, MCP, and A2A — A Practitioner's Map."*

**Read the article:** [on Medium](https://awstip.com/the-aws-agentic-stack-explained-strands-agentcore-mcp-and-a2a-a-practitioners-map-4ef995a2e5b4)

---

## What this repository is

A hands-on starter that demonstrates each of the four layers of the AWS agentic stack in isolation, so you can understand what each one does before composing them in a production workload.

| Module | What it demonstrates |
|--------|----------------------|
| [`strands-hello-world/`](./strands-hello-world) | A minimal Strands agent that uses Amazon Bedrock as its model provider and exposes one tool |
| [`agentcore-deploy/`](./agentcore-deploy) | Reference Terraform for deploying an agent runtime to AgentCore, including IAM, networking, and observability baseline |
| [`mcp-server-sample/`](./mcp-server-sample) | A minimal MCP server written in Python that exposes two resources and one tool, consumable by any MCP-compatible client |
| [`a2a-exchange/`](./a2a-exchange) | Two agents exchanging structured messages through the A2A protocol, demonstrating discovery, handshake, and delegation |

## What this repository is NOT

- **Not production-ready.** Each module is a reference implementation focused on clarity, not hardening. Security, cost controls, rate limiting, and retry policies are deliberately minimal.
- **Not a replacement for the AWS documentation.** Every module links back to the official docs. If AWS changes an API, the documentation is authoritative, not this repo.
- **Not a framework.** Do not import from this repo. Read the code, adapt the patterns, write your own.

> **Version note:** SDK versions move fast in this space. Every module includes `REQUIREMENTS.md` with the exact versions tested. If you encounter API drift, open an issue with your SDK version and the error — I will update.

---

## Prerequisites

- AWS account with access to Amazon Bedrock in a supported region (tested in `us-east-1`)
- Bedrock model access granted for Anthropic Claude models (request it in the Bedrock console if needed)
- Python 3.11+
- Terraform 1.7+ (only for the `agentcore-deploy` module)
- AWS CLI configured with credentials that have permissions to invoke Bedrock and deploy infrastructure

---

## Getting started

Clone the repo and pick the module you want to explore first:

```bash
git clone https://github.com/erickmancz/aws-agentic-stack-starter.git
cd aws-agentic-stack-starter
```

If this is your first time with the agentic stack, I recommend reading the modules in this order:

1. `strands-hello-world/` — understand what a tool-using agent is
2. `mcp-server-sample/` — understand how external context reaches an agent
3. `agentcore-deploy/` — understand how the agent runs at scale
4. `a2a-exchange/` — understand how agents talk to each other

Each module has its own README with setup, run, and teardown instructions.

---

## Architecture overview

The four pieces answer four different questions:

| Question | Answer |
|----------|--------|
| How does the agent reason and use tools? | **Strands** |
| How does the agent get external context at runtime? | **MCP (Model Context Protocol)** |
| Where does the agent run in production? | **AgentCore** |
| How does the agent collaborate with other agents? | **A2A (Agent-to-Agent)** |

For the full map with when to use each, read the [article](https://awstip.com/the-aws-agentic-stack-explained-strands-agentcore-mcp-and-a2a-a-practitioners-map-4ef995a2e5b4).

---

## License

MIT. See [LICENSE](./LICENSE). Opinions expressed here are my own.

---

## Feedback

If something is broken, outdated, or unclear, open an issue. Pull requests welcome, especially when an AWS SDK update breaks a pattern here. This repo evolves with the stack.

**Author:** [Erick Mancz](https://linkedin.com/in/erick-mancz) · AWS Golden Jacket · [Medium](https://medium.com/@erickmancz) · [AWS Builder Center](https://builder.aws.com/profiles/imancz)
