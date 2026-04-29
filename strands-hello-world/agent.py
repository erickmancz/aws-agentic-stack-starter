"""
Strands hello-world agent.

Demonstrates the minimum viable Strands agent: one model provider (Bedrock Claude),
one tool (get_current_time), and a simple conversational loop.

Reference: https://strandsagents.com/
"""
from strands import Agent, tool
from strands.models import BedrockModel
from datetime import datetime
from zoneinfo import ZoneInfo


@tool
def get_current_time(timezone: str = "UTC") -> str:
    """
    Return the current time in the specified IANA timezone.

    Args:
        timezone: IANA timezone name (e.g., 'America/Sao_Paulo', 'UTC', 'Europe/London').
                  Defaults to UTC.

    Returns:
        Formatted timestamp string including timezone.
    """
    try:
        tz = ZoneInfo(timezone)
        now = datetime.now(tz)
        return now.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception as e:
        return f"Error resolving timezone '{timezone}': {e}"


def build_agent() -> Agent:
    """
    Build a Strands agent backed by Claude on Bedrock, with one tool registered.

    Model selection note (April 2026):
      - Default here is Claude Haiku 4.5 — cheapest model that handles tool use well.
      - For higher-quality reasoning, swap to claude-sonnet-4-5-20250929-v1:0.
      - Avoid claude-3-5-sonnet-20241022-v2:0: it moved to Public Extended Access
        in Dec 2025 and now costs $6/M input · $30/M output (2x the original price).
    """
    model = BedrockModel(
        model_id="anthropic.claude-haiku-4-5-20251001-v1:0",
        region_name="us-east-1",
    )

    agent = Agent(
        model=model,
        tools=[get_current_time],
        system_prompt=(
            "You are a helpful assistant. When the user asks about time, "
            "use the get_current_time tool. Be concise."
        ),
    )
    return agent


def main():
    agent = build_agent()

    # Single-turn example
    response = agent("What time is it right now in São Paulo?")
    print("\n--- Agent response ---")
    print(response)


if __name__ == "__main__":
    main()
