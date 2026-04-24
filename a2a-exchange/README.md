# A2A exchange (didactic simulation)

A single-process simulation of two agents talking to each other using the Agent-to-Agent (A2A) protocol's three-step pattern: discovery, handshake, delegation.

## Why a simulation?

A2A is evolving as an open protocol. Rather than ship code that will break when the spec shifts, this module gives you the **mental model** of how an A2A exchange works, using a local in-memory registry and simulated agents.

Once you understand this pattern, porting to real A2A over HTTP with JSON message envelopes is mechanical.

## What it shows

- **Discovery**: Agent B queries a registry to find an agent with the capability it needs
- **Handshake**: Agent B confirms the discovered agent actually declares the capability
- **Delegation**: Agent B sends a task to Agent A and receives a structured result

## Run it

```bash
cd a2a-exchange
python exchange.py
```

Expected output:

```
[registry] translation-agent registered with capabilities: ['translate_pt_en', 'translate_en_pt']

[cs-agent] Received message from user: 'Olá, preciso de ajuda com meu pedido ORD-1003.'
[cs-agent] Found translator: translation-agent
[cs-agent] Handshake OK, capabilities confirmed
[cs-agent] Received translation: '[translated to en] Olá, preciso de ajuda com meu pedido ORD-1003.'

============================================================
Final response to user: [translated to en] Olá, preciso de ajuda com meu pedido ORD-1003.
============================================================
```

## From simulation to production

| Simulation here | Production equivalent |
|-----------------|------------------------|
| In-memory `AgentRegistry` dict | Service registry (Consul, AWS Cloud Map, or dedicated A2A registry) |
| `A2AMessage` dataclass | JSON envelope over HTTP POST |
| `registry.deliver()` direct call | HTTP request to agent's inbound endpoint |
| Synchronous delivery | Async with message queue (SQS, EventBridge) for long-running tasks |
| No authentication | Mutual TLS or signed requests between agents |

## When A2A is the right choice

- You have multiple agents that would be simpler as separate concerns than as one mega-agent
- You want to reuse a specialized agent across multiple orchestrator agents
- You need agents owned by different teams to collaborate without tight coupling

## When A2A is overkill

- You only have one agent. Just build the agent.
- Your "agents" are actually just function calls. Use tools, not A2A.
- You need synchronous response in <100ms. A2A adds latency.

## References

- [A2A Protocol](https://a2a-protocol.org/)
- Article: [The AWS Agentic Stack Explained](https://awstip.com/the-aws-agentic-stack-explained-strands-agentcore-mcp-and-a2a-a-practitioners-map-4ef995a2e5b4)
