# AWS Agentic Stack Starter

Companion repository for **Week 2** of [Golden Jacket Field Notes](https://medium.com/@erickmancz): *"The AWS Agentic Stack Explained: Strands, AgentCore, MCP, and A2A — A Practitioner's Map."*

**Read the article:** [on Medium](https://awstip.com/the-aws-agentic-stack-explained-strands-agentcore-mcp-and-a2a-a-practitioners-map-4ef995a2e5b4)

---

## What this repository is

A hands-on starter that demonstrates each of the four layers of the AWS agentic stack in isolation, so you can understand what each one does before composing them in a production workload.

| Module | What it demonstrates |
|--------|----------------------|
| [`strands-hello-world/`](./strands-hello-world) | A minimal Strands agent that uses Amazon Bedrock as its model provider and exposes one tool |
| [`mcp-server-sample/`](./mcp-server-sample) | A minimal MCP server written in Python (stdio transport), consumable by any local MCP-compatible client like Claude Desktop |
| [`mcp-lambda/`](./mcp-lambda) | The same MCP server, but hosted on **AWS Lambda Function URL** (streamable HTTP transport). Production-leaning starting point. |
| [`strands-with-mcp/`](./strands-with-mcp) | A Strands agent that consumes the `mcp-lambda` server remotely via HTTP — runs entirely inside AWS CloudShell |
| [`a2a-exchange/`](./a2a-exchange) | Two agents exchanging structured messages through the A2A protocol — discovery, handshake, delegation |
| [`agentcore-deploy/`](./agentcore-deploy) | Reference Terraform for deploying an agent runtime to **Bedrock AgentCore**, including IAM, networking, and observability baseline |

## What this repository is NOT

- **Not production-ready.** Each module is a reference implementation focused on clarity, not hardening. Security, cost controls, rate limiting, and retry policies are deliberately minimal.
- **Not a replacement for the AWS documentation.** Every module links back to the official docs. If AWS changes an API, the documentation is authoritative, not this repo.
- **Not a framework.** Do not import from this repo. Read the code, adapt the patterns, write your own.

> **Version note:** SDK versions move fast in this space. Every module includes a `requirements.txt` with the tested versions. If you encounter API drift, open an issue with your SDK version and the error — I will update.

---

## Two paths to learn the stack

There are two complementary paths through this repository, depending on what you want to understand first.

### Path 1 — Local-first (great for understanding the protocol)

Best if this is your first contact with MCP and you want to see the protocol working "raw" on your laptop:

1. `strands-hello-world/` — what a tool-using agent looks like
2. `mcp-server-sample/` — how an MCP server exposes resources and tools (stdio transport, Claude Desktop client)
3. `a2a-exchange/` — how agents discover and delegate to each other
4. `agentcore-deploy/` — how an agent runs in production

### Path 2 — All-AWS (great for cloud-first audiences)

Best if you want to see how the stack runs **fully inside AWS**, with no local desktop dependencies:

1. `strands-hello-world/` — same starting point, run it from AWS CloudShell
2. `mcp-lambda/` — deploy the MCP server to AWS Lambda via SAM
3. `strands-with-mcp/` — run a Strands client in CloudShell that consumes the Lambda MCP via streamable HTTP
4. `a2a-exchange/` — same A2A simulation, run from CloudShell
5. `agentcore-deploy/` — `terraform plan` (run locally — see CloudShell caveat below)

Each module has its own README with setup, run, and teardown instructions.

---

## Prerequisites

Common to both paths:

- AWS account with access to Amazon Bedrock in a supported region (tested in `us-east-1`)
- Bedrock model access granted for `anthropic.claude-haiku-4-5-20251001-v1:0` (request it in the Bedrock console if needed)
- AWS CLI v2 configured with credentials that have permissions to invoke Bedrock and deploy infrastructure

Path-specific:

| | Path 1 (local) | Path 2 (all-AWS) |
|---|---|---|
| Python 3.11+ | local | install via `dnf` in CloudShell (see CloudShell caveat) |
| Terraform 1.7+ | local | install via `dnf` in CloudShell (see CloudShell caveat) |
| SAM CLI | not needed | already in CloudShell (for `mcp-lambda`) |
| Claude Desktop or other MCP client | required (for `mcp-server-sample`) | not needed |
| AWS CloudShell | optional | required (for `mcp-lambda`, `strands-with-mcp`) |

---

## CloudShell caveats (April 2026)

A few things you'll hit if you try to run the all-AWS path inside CloudShell. Documenting here so you don't spend time debugging:

### Python 3.11 is not pre-installed

CloudShell (Amazon Linux 2023) ships with **Python 3.9 only**. Lambda doesn't support Python 3.9 since Oct/2024, and the Strands SDK requires Python 3.11+. Install before running the modules:

```bash
sudo dnf install -y python3.11 python3.11-pip python3.11-devel
python3.11 --version
```

### Terraform is not pre-installed

CloudShell does not ship Terraform. Install via HashiCorp's official repo:

```bash
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo
sudo dnf install -y terraform
terraform --version
```

### Disk space is tight (1GB persistent home)

The AWS provider for Terraform alone takes ~600MB. Combined with Python venvs from the other modules, `terraform init` may fail with `no space left on device`. For demos, **run Terraform locally** instead of in CloudShell. If you must use CloudShell, clean caches first:

```bash
rm -rf ~/.cache/pip
sudo dnf clean all
rm -rf ~/aws-agentic-stack-starter/mcp-lambda/.aws-sam
df -h /home
```

### Bedrock requires inference profiles for newer Claude models

Claude 4.x family (Haiku 4.5, Sonnet 4.5, Opus 4.x) does **not** support on-demand throughput on Bedrock. Invocations must go through a cross-region inference profile, indicated by the `us.` prefix:

```python
# ❌ This will fail with ValidationException
model_id = "anthropic.claude-haiku-4-5-20251001-v1:0"

# ✅ This works
model_id = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
```

Modules `strands-hello-world/` and `strands-with-mcp/` already use the correct prefix.

### Lambda Function URL with `AuthType=NONE` requires TWO permissions

If you create a Function URL with public access, AWS requires **both** `lambda:InvokeFunctionUrl` (authorizes the endpoint) and `lambda:InvokeFunction` (authorizes the execution). Missing either returns silent `403 Forbidden`. The `mcp-lambda/template.yaml` here already provisions both — but if you build your own Function URL, don't forget the second one.

---

## Getting started

### Path 1 — Local

```bash
git clone https://github.com/erickmancz/aws-agentic-stack-starter.git
cd aws-agentic-stack-starter
# Follow each module's README in the order listed above
```

### Path 2 — All-AWS (open AWS Console → CloudShell)

```bash
# Install missing prerequisites first (see CloudShell caveats)
sudo dnf install -y python3.11 python3.11-pip python3.11-devel

git clone https://github.com/erickmancz/aws-agentic-stack-starter.git
cd aws-agentic-stack-starter

# Deploy the MCP Lambda
cd mcp-lambda
sam build && sam deploy --guided

# Capture the URL
export MCP_SERVER_URL=$(aws cloudformation describe-stacks \
  --stack-name field-notes-mcp-demo \
  --query "Stacks[0].Outputs[?OutputKey=='McpServerUrl'].OutputValue" \
  --output text)

# Run the Strands agent that consumes it
cd ../strands-with-mcp
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python agent.py
```

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
