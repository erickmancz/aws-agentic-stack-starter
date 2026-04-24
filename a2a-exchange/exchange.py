"""
A2A (Agent-to-Agent) exchange — didactic simulation.

Demonstrates the three steps of an A2A interaction:
  1. Discovery: Agent A advertises capabilities; Agent B queries the directory
  2. Handshake: Agent B confirms Agent A can handle its request
  3. Delegation: Agent B asks Agent A to perform a task and receives the result

This is a single-process simulation for learning. In a real deployment each agent
runs in its own process (likely its own AgentCore runtime), discovers the other
via a registry or service mesh, and communicates over HTTP with structured
message envelopes.

Reference: https://a2a-protocol.org/
"""
from dataclasses import dataclass, field
from typing import Callable


################################################################################
# Shared message envelope — what travels between agents.
################################################################################

@dataclass
class A2AMessage:
    """Structured message exchanged between agents."""
    sender: str
    recipient: str
    intent: str              # e.g. "query_capabilities", "delegate_task", "task_result"
    payload: dict = field(default_factory=dict)


################################################################################
# Simple agent registry — the "discovery" layer.
################################################################################

class AgentRegistry:
    """In-memory registry of agents and their declared capabilities."""
    def __init__(self):
        self._agents: dict[str, dict] = {}

    def register(self, agent_name: str, capabilities: list[str], handler: Callable):
        self._agents[agent_name] = {
            "capabilities": capabilities,
            "handler": handler,
        }
        print(f"[registry] {agent_name} registered with capabilities: {capabilities}")

    def find_agent_for(self, capability: str) -> str | None:
        for name, meta in self._agents.items():
            if capability in meta["capabilities"]:
                return name
        return None

    def deliver(self, message: A2AMessage) -> A2AMessage:
        """Route a message to its recipient agent and return the response."""
        recipient = self._agents.get(message.recipient)
        if recipient is None:
            return A2AMessage(
                sender="registry",
                recipient=message.sender,
                intent="error",
                payload={"reason": f"Agent '{message.recipient}' not found"},
            )
        return recipient["handler"](message)


################################################################################
# Agent A: translation specialist.
################################################################################

def translation_agent_handler(message: A2AMessage) -> A2AMessage:
    """
    Handles incoming A2A messages addressed to the translation agent.

    In a real implementation this would invoke an LLM with the text to translate.
    Here we return a deterministic fake response for demonstration.
    """
    if message.intent == "query_capabilities":
        return A2AMessage(
            sender="translation-agent",
            recipient=message.sender,
            intent="capabilities_response",
            payload={"capabilities": ["translate_pt_en", "translate_en_pt"]},
        )

    if message.intent == "delegate_task":
        text = message.payload.get("text", "")
        target = message.payload.get("target_language", "en")
        # Fake translation: in reality this would call Bedrock.
        fake_result = f"[translated to {target}] {text}"
        return A2AMessage(
            sender="translation-agent",
            recipient=message.sender,
            intent="task_result",
            payload={"translated_text": fake_result},
        )

    return A2AMessage(
        sender="translation-agent",
        recipient=message.sender,
        intent="error",
        payload={"reason": f"Unknown intent: {message.intent}"},
    )


################################################################################
# Agent B: customer support orchestrator that delegates translation.
################################################################################

def customer_support_agent(registry: AgentRegistry, user_message_pt: str) -> str:
    """
    Orchestrator agent. Receives a user message in Portuguese, discovers a
    translation agent, delegates the translation, returns the English result.
    """
    print(f"\n[cs-agent] Received message from user: {user_message_pt!r}")

    # Step 1: discovery
    translator_name = registry.find_agent_for("translate_pt_en")
    if translator_name is None:
        return "No translator available."
    print(f"[cs-agent] Found translator: {translator_name}")

    # Step 2: handshake — confirm capabilities
    handshake = A2AMessage(
        sender="cs-agent",
        recipient=translator_name,
        intent="query_capabilities",
    )
    handshake_response = registry.deliver(handshake)
    if "translate_pt_en" not in handshake_response.payload.get("capabilities", []):
        return "Translator does not support pt→en."
    print(f"[cs-agent] Handshake OK, capabilities confirmed")

    # Step 3: delegate
    delegation = A2AMessage(
        sender="cs-agent",
        recipient=translator_name,
        intent="delegate_task",
        payload={"text": user_message_pt, "target_language": "en"},
    )
    result = registry.deliver(delegation)
    translated = result.payload.get("translated_text", "")
    print(f"[cs-agent] Received translation: {translated!r}")

    return translated


################################################################################
# Demo: wire it all together.
################################################################################

def main():
    registry = AgentRegistry()
    registry.register(
        agent_name="translation-agent",
        capabilities=["translate_pt_en", "translate_en_pt"],
        handler=translation_agent_handler,
    )

    user_input = "Olá, preciso de ajuda com meu pedido ORD-1003."
    final_response = customer_support_agent(registry, user_input)

    print(f"\n{'='*60}")
    print(f"Final response to user: {final_response}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
