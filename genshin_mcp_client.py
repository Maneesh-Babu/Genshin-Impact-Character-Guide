#!/usr/bin/env python3
"""
Test client for Genshin Impact MCP Server
This script demonstrates how to interact with the MCP server.
"""

import asyncio
import json
from mcp.client import Client
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

async def test_genshin_mcp_server():
    """Test the Genshin Impact MCP server functionality"""
    
    # Server parameters - adjust path as needed
    server_params = StdioServerParameters(
        command="python",
        args=["genshin_mcp_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the client
            await session.initialize()
            
            print("🎮 Genshin Impact MCP Server Test")
            print("=" * 50)
            
            # Test 1: List available resources
            print("\n📋 Available Resources:")
            resources = await session.list_resources()
            for resource in resources:
                print(f"  - {resource.name}: {resource.description}")
            
            # Test 2: List available tools
            print("\n🔧 Available Tools:")
            tools = await session.list_tools()
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Test 3: Get character info
            print("\n👤 Character Information:")
            char_info = await session.call_tool("get_character_info", {"character_name": "mavuika"})
            print(char_info[0].text)
            
            # Test 4: Get character builds
            print("\n⚔️ Character Builds:")
            builds = await session.call_tool("get_character_builds", {"character_name": "mavuika"})
            print(builds[0].text)
            
            # Test 5: Get team compositions
            print("\n👥 Team Compositions:")
            teams = await session.call_tool("get_team_compositions", {"character_name": "mavuika"})
            print(teams[0].text)
            
            # Test 6: Create complete build guide
            print("\n📖 Complete Build Guide:")
            guide = await session.call_tool("create_build_guide", {
                "character_name": "mavuika",
                "include_teams": True
            })
            print(guide[0].text)
            
            # Test 7: Read characters resource
            print("\n📚 Characters Database:")
            chars_data = await session.read_resource("genshin://characters")
            chars = json.loads(chars_data)
            print(f"Available characters: {', '.join(chars.keys())}")

if __name__ == "__main__":
    asyncio.run(test_genshin_mcp_server())
