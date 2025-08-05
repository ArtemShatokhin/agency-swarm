"""
Agency Swarm Streaming Demo

Simple demonstration of real-time streaming in Agency Swarm v1.x.
Shows how to handle streaming events and filter text vs tool call data.
"""

import asyncio
import logging
import os
import sys

# Path setup for standalone examples
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from agents import function_tool
from dotenv import load_dotenv

from agency_swarm import Agency, Agent

load_dotenv()

# Minimal logging setup
logging.basicConfig(level=logging.WARNING)

# --- Simple Tool --- #


@function_tool
def get_weather(location: str) -> str:
    """Get weather information for a location."""
    return f"The weather in {location} is sunny, 22°C with light winds."


# --- Agent Setup --- #


def create_demo_agency():
    """Create a demo agency for terminal demo"""

    # Create agents using v1.x pattern (direct instantiation)
    ceo = Agent(
        name="CEO",
        description="Chief Executive Officer - oversees all operations",
        instructions="You are the CEO. When asked about weather, delegate to Worker with a specific location (use London if not specified).",
        tools=[],
    )

    worker = Agent(
        name="Worker",
        description="Worker - performs tasks and writes weather reports",
        instructions="You handle weather tasks. Use the get_weather tool which returns weather reports.",
        tools=[get_weather],
    )

    # Create agency with communication flows (v1.x pattern)
    agency = Agency(
        ceo,  # Entry point agent (positional argument)
        communication_flows=[
            (ceo, worker),
        ],
        name="TerminalDemoAgency",
    )

    return agency


agency = create_demo_agency()

# --- Streaming Handler --- #


async def stream_response(message: str):
    """Stream a response and handle events properly."""
    print(f"\n🔥 Streaming: {message}")
    print("📡 Response: ", end="", flush=True)

    full_text = ""

    async for event in agency.get_response_stream(message):
        # Handle streaming events with data
        if hasattr(event, "data"):
            data = event.data

            # Only capture actual response text, not tool call arguments
            if hasattr(data, "delta") and hasattr(data, "type"):
                if data.type == "response.output_text.delta":
                    # Stream the actual response text in real-time
                    delta_text = data.delta
                    if delta_text:
                        print(delta_text, end="", flush=True)
                        full_text += delta_text
                # Skip tool call deltas (we don't want to show those to users)
                elif data.type == "response.function_call_arguments.delta":
                    continue

        # Handle validation errors
        elif isinstance(event, dict):
            event_type = event.get("event", event.get("type"))
            if event_type == "error":
                print(f"\n❌ Error: {event.get('content', event.get('data', 'Unknown error'))}")
                break

    print("\n✅ Stream complete")
    print(f"📋 Total: {len(full_text)} characters streamed")
    return full_text


# --- Main Demo --- #


async def main():
    """Run simple streaming demo."""
    print("🌟 Agency Swarm Streaming Demo")
    print("=" * 40)
    print("🎯 Watch text stream in real-time!")

    await stream_response("What's the weather in London?")

    print("\n🎉 Demo complete! Streaming works perfectly.")


if __name__ == "__main__":
    asyncio.run(main())
