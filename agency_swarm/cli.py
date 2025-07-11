import argparse
import os
import sys

from dotenv import load_dotenv

from agency_swarm.util.helpers import list_available_agents

from .integrations.mcp_server import run_mcp


def main():
    parser = argparse.ArgumentParser(description="Agency Swarm CLI.")

    subparsers = parser.add_subparsers(
        dest="command", help="Utility commands to simplify the agent creation process."
    )
    subparsers.required = True

    # create-agent-template
    create_parser = subparsers.add_parser(
        "create-agent-template", help="Create agent template folder locally."
    )
    create_parser.add_argument(
        "--path", type=str, default="./", help="Path to create agent folder."
    )
    create_parser.add_argument(
        "--use_txt",
        action="store_true",
        default=False,
        help="Use txt instead of md for instructions and manifesto.",
    )
    create_parser.add_argument("--name", type=str, help="Name of agent.")
    create_parser.add_argument("--description", type=str, help="Description of agent.")

    # mcp-server
    mcp_parser = subparsers.add_parser("mcp-server", help="Run the MCP server.")
    mcp_parser.add_argument(
        "--tools-dir", type=str, required=True, help="Directory containing tool modules"
    )
    mcp_parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Host to bind the server to"
    )
    mcp_parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind the server to"
    )
    mcp_parser.add_argument(
        "--app-token-env", type=str, default="APP_TOKEN", 
        help="Environment variable name for authentication token"
    )
    mcp_parser.add_argument(
        "--server-name", type=str, default="mcp-tools-server", 
        help="Name identifier for the MCP server"
    )
    mcp_parser.add_argument(
        "--cors-origins", type=str, default="*", 
        help="Comma-separated list of allowed CORS origins"
    )

    # genesis-agency
    genesis_parser = subparsers.add_parser("genesis", help="Start genesis agency.")
    genesis_parser.add_argument(
        "--openai_key", default=None, type=str, help="OpenAI API key."
    )
    genesis_parser.add_argument(
        "--with_browsing",
        default=False,
        action="store_true",
        help="Enable browsing agent.",
    )

    # import-agent
    import_parser = subparsers.add_parser(
        "import-agent", help="Import pre-made agent by name to a local directory."
    )
    available_agents = list_available_agents()
    import_parser.add_argument(
        "--name",
        type=str,
        required=True,
        choices=available_agents,
        help="Name of the agent to import.",
    )
    import_parser.add_argument(
        "--destination",
        type=str,
        default="./",
        help="Destination path to copy the agent files.",
    )

    args = parser.parse_args()

    if args.command == "create-agent-template":
        from agency_swarm.util import create_agent_template

        create_agent_template(args.name, args.description, args.path, args.use_txt)
    elif args.command == "mcp-server":
        cors_origins_list = [origin.strip() for origin in args.cors_origins.split(',')]
        try:
            run_mcp(
                tools=args.tools_dir,  # Pass directory path directly
                host=args.host,
                port=args.port,
                app_token_env=args.app_token_env,
                server_name=args.server_name,
                cors_origins=cors_origins_list
            )
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == "genesis":
        load_dotenv()
        if not os.getenv("OPENAI_API_KEY") and not args.openai_key:
            print(
                "OpenAI API key not set. "
                "Please set it with --openai_key argument or by setting OPENAI_API_KEY environment variable."
            )
            return

        if args.openai_key:
            from agency_swarm import set_openai_key

            set_openai_key(args.openai_key)

        from agency_swarm.agency.genesis import GenesisAgency

        agency = GenesisAgency(with_browsing=args.with_browsing)
        agency.run_demo()
    elif args.command == "import-agent":
        from agency_swarm.util import import_agent

        import_agent(args.name, args.destination)


if __name__ == "__main__":
    main()
