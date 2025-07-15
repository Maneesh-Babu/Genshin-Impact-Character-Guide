#!/usr/bin/env python3
"""
Genshin Impact MCP Server Demo
A Model Context Protocol server that provides character information and build guides for Genshin Impact.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
import httpx
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("genshin-mcp-server")

@dataclass
class Character:
    name: str
    element: str
    weapon_type: str
    rarity: int
    role: str
    description: str

@dataclass
class Build:
    character: str
    role: str
    main_stats: Dict[str, str]
    artifact_sets: List[str]
    weapons: List[str]
    substats_priority: List[str]
    talent_priority: List[str]

class GenshinDatabase:
    """Mock database with Genshin Impact character and build data"""
    
    def __init__(self):
        self.characters = {
            "mavuika": Character(
                name="Mavuika",
                element="Pyro",
                weapon_type="Claymore",
                rarity=5,
                role="DPS/Support",
                description="The Pyro Archon with powerful elemental abilities"
            ),
            "neuvillette": Character(
                name="Neuvillette",
                element="Hydro",
                weapon_type="Catalyst",
                rarity=5,
                role="DPS",
                description="Hydro DPS with charge attack focus"
            ),
            "kazuha": Character(
                name="Kazuha",
                element="Anemo",
                weapon_type="Sword",
                rarity=5,
                role="Support",
                description="Anemo support with crowd control and elemental damage bonus"
            ),
            "nahida": Character(
                name="Nahida",
                element="Dendro",
                weapon_type="Catalyst",
                rarity=5,
                role="Support/DPS",
                description="Dendro Archon with reaction-based abilities"
            ),
            "furina": Character(
                name="Furina",
                element="Hydro",
                weapon_type="Sword",
                rarity=5,
                role="Support",
                description="Hydro support with summoning abilities"
            )
        }
        
        self.builds = {
            "mavuika": [
                Build(
                    character="Mavuika",
                    role="DPS",
                    main_stats={"sands": "ATK%", "goblet": "Pyro DMG%", "circlet": "CRIT Rate/DMG"},
                    artifact_sets=["Crimson Witch of Flames", "Gilded Dreams"],
                    weapons=["Wolf's Gravestone", "Serpent Spine", "Prototype Archaic"],
                    substats_priority=["CRIT Rate", "CRIT DMG", "ATK%", "Energy Recharge"],
                    talent_priority=["Elemental Skill", "Elemental Burst", "Normal Attack"]
                ),
                Build(
                    character="Mavuika",
                    role="Support",
                    main_stats={"sands": "Energy Recharge", "goblet": "Pyro DMG%", "circlet": "CRIT Rate"},
                    artifact_sets=["Noblesse Oblige", "Emblem of Severed Fate"],
                    weapons=["Favonius Greatsword", "Sacrificial Greatsword"],
                    substats_priority=["Energy Recharge", "CRIT Rate", "ATK%", "CRIT DMG"],
                    talent_priority=["Elemental Burst", "Elemental Skill", "Normal Attack"]
                )
            ],
            "neuvillette": [
                Build(
                    character="Neuvillette",
                    role="DPS",
                    main_stats={"sands": "HP%", "goblet": "Hydro DMG%", "circlet": "CRIT Rate/DMG"},
                    artifact_sets=["Heart of Depth", "Marechaussee Hunter"],
                    weapons=["Lost Prayer to the Sacred Winds", "The Widsith", "Prototype Amber"],
                    substats_priority=["CRIT Rate", "CRIT DMG", "HP%", "Energy Recharge"],
                    talent_priority=["Normal Attack", "Elemental Skill", "Elemental Burst"]
                )
            ],
            "kazuha": [
                Build(
                    character="Kazuha",
                    role="Support",
                    main_stats={"sands": "Energy Recharge/Elemental Mastery", "goblet": "Elemental Mastery", "circlet": "Elemental Mastery"},
                    artifact_sets=["Viridescent Venerer", "Instructor"],
                    weapons=["Freedom-Sworn", "Iron Sting", "Sacrificial Sword"],
                    substats_priority=["Elemental Mastery", "Energy Recharge", "ATK%", "CRIT Rate"],
                    talent_priority=["Elemental Burst", "Elemental Skill", "Normal Attack"]
                )
            ]
        }
        
        self.team_comps = {
            "mavuika": [
                {"name": "Vape Team", "members": ["Mavuika", "Xingqiu", "Bennett", "Kazuha"]},
                {"name": "Melt Team", "members": ["Mavuika", "Rosaria", "Kaeya", "Bennett"]},
                {"name": "Mono Pyro", "members": ["Mavuika", "Bennett", "Xiangling", "Kazuha"]}
            ],
            "neuvillette": [
                {"name": "Hydro Team", "members": ["Neuvillette", "Furina", "Kazuha", "Baizhu"]},
                {"name": "Hypercarry", "members": ["Neuvillette", "Zhongli", "Kazuha", "Bennett"]}
            ],
            "kazuha": [
                {"name": "National Team", "members": ["Kazuha", "Xiangling", "Xingqiu", "Bennett"]},
                {"name": "Freeze Team", "members": ["Kazuha", "Ayaka", "Mona", "Diona"]}
            ]
        }

class GenshinMCPServer:
    def __init__(self):
        self.server = Server("genshin-impact-guide")
        self.db = GenshinDatabase()
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.server.list_resources()
        async def handle_list_resources() -> list[types.Resource]:
            """List available Genshin Impact resources"""
            return [
                types.Resource(
                    uri="genshin://characters",
                    name="Genshin Impact Characters",
                    description="Database of Genshin Impact characters with stats and information",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="genshin://builds",
                    name="Character Builds",
                    description="Optimal builds and artifacts for characters",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="genshin://teams",
                    name="Team Compositions",
                    description="Recommended team compositions for different characters",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read specific Genshin Impact resource"""
            if uri == "genshin://characters":
                return json.dumps({
                    name: {
                        "name": char.name,
                        "element": char.element,
                        "weapon_type": char.weapon_type,
                        "rarity": char.rarity,
                        "role": char.role,
                        "description": char.description
                    }
                    for name, char in self.db.characters.items()
                }, indent=2)
            
            elif uri == "genshin://builds":
                builds_data = {}
                for char_name, builds in self.db.builds.items():
                    builds_data[char_name] = []
                    for build in builds:
                        builds_data[char_name].append({
                            "role": build.role,
                            "main_stats": build.main_stats,
                            "artifact_sets": build.artifact_sets,
                            "weapons": build.weapons,
                            "substats_priority": build.substats_priority,
                            "talent_priority": build.talent_priority
                        })
                return json.dumps(builds_data, indent=2)
            
            elif uri == "genshin://teams":
                return json.dumps(self.db.team_comps, indent=2)
            
            else:
                raise ValueError(f"Unknown resource: {uri}")
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools for Genshin Impact queries"""
            return [
                types.Tool(
                    name="get_character_info",
                    description="Get detailed information about a specific character",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "character_name": {
                                "type": "string",
                                "description": "Name of the character (e.g., 'mavuika', 'neuvillette')"
                            }
                        },
                        "required": ["character_name"]
                    }
                ),
                types.Tool(
                    name="get_character_builds",
                    description="Get optimal builds for a character",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "character_name": {
                                "type": "string",
                                "description": "Name of the character"
                            },
                            "role": {
                                "type": "string",
                                "description": "Specific role (DPS, Support, etc.) - optional",
                                "enum": ["DPS", "Support", "Sub-DPS", "Healer"]
                            }
                        },
                        "required": ["character_name"]
                    }
                ),
                types.Tool(
                    name="get_team_compositions",
                    description="Get recommended team compositions for a character",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "character_name": {
                                "type": "string",
                                "description": "Name of the character"
                            }
                        },
                        "required": ["character_name"]
                    }
                ),
                types.Tool(
                    name="create_build_guide",
                    description="Create a comprehensive build guide for a character",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "character_name": {
                                "type": "string",
                                "description": "Name of the character"
                            },
                            "include_teams": {
                                "type": "boolean",
                                "description": "Include team composition recommendations",
                                "default": True
                            }
                        },
                        "required": ["character_name"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls for Genshin Impact queries"""
            
            if name == "get_character_info":
                char_name = arguments["character_name"].lower()
                if char_name in self.db.characters:
                    char = self.db.characters[char_name]
                    info = f"""
**{char.name}**
- Element: {char.element}
- Weapon Type: {char.weapon_type}
- Rarity: {char.rarity}★
- Role: {char.role}
- Description: {char.description}
"""
                    return [types.TextContent(type="text", text=info)]
                else:
                    return [types.TextContent(type="text", text=f"Character '{arguments['character_name']}' not found in database.")]
            
            elif name == "get_character_builds":
                char_name = arguments["character_name"].lower()
                role_filter = arguments.get("role")
                
                if char_name in self.db.builds:
                    builds = self.db.builds[char_name]
                    if role_filter:
                        builds = [b for b in builds if b.role.lower() == role_filter.lower()]
                    
                    result = f"**Build Guide for {char_name.title()}**\n\n"
                    for build in builds:
                        result += f"**{build.role} Build:**\n"
                        result += f"- Main Stats: {build.main_stats}\n"
                        result += f"- Artifact Sets: {', '.join(build.artifact_sets)}\n"
                        result += f"- Weapons: {', '.join(build.weapons)}\n"
                        result += f"- Substat Priority: {' > '.join(build.substats_priority)}\n"
                        result += f"- Talent Priority: {' > '.join(build.talent_priority)}\n\n"
                    
                    return [types.TextContent(type="text", text=result)]
                else:
                    return [types.TextContent(type="text", text=f"No builds found for '{arguments['character_name']}'.")]
            
            elif name == "get_team_compositions":
                char_name = arguments["character_name"].lower()
                if char_name in self.db.team_comps:
                    teams = self.db.team_comps[char_name]
                    result = f"**Team Compositions for {char_name.title()}**\n\n"
                    for team in teams:
                        result += f"**{team['name']}:**\n"
                        result += f"- {' | '.join(team['members'])}\n\n"
                    return [types.TextContent(type="text", text=result)]
                else:
                    return [types.TextContent(type="text", text=f"No team compositions found for '{arguments['character_name']}'.")]
            
            elif name == "create_build_guide":
                char_name = arguments["character_name"].lower()
                include_teams = arguments.get("include_teams", True)
                
                if char_name not in self.db.characters:
                    return [types.TextContent(type="text", text=f"Character '{arguments['character_name']}' not found.")]
                
                char = self.db.characters[char_name]
                result = f"# Complete Build Guide for {char.name}\n\n"
                result += f"**Character Overview:**\n"
                result += f"- Element: {char.element}\n"
                result += f"- Weapon: {char.weapon_type}\n"
                result += f"- Rarity: {char.rarity}★\n"
                result += f"- Role: {char.role}\n"
                result += f"- Description: {char.description}\n\n"
                
                # Add builds
                if char_name in self.db.builds:
                    result += "## Recommended Builds\n\n"
                    for build in self.db.builds[char_name]:
                        result += f"### {build.role} Build\n"
                        result += f"**Main Stats:** {build.main_stats}\n"
                        result += f"**Artifact Sets:** {', '.join(build.artifact_sets)}\n"
                        result += f"**Weapons:** {', '.join(build.weapons)}\n"
                        result += f"**Substat Priority:** {' > '.join(build.substats_priority)}\n"
                        result += f"**Talent Priority:** {' > '.join(build.talent_priority)}\n\n"
                
                # Add team compositions
                if include_teams and char_name in self.db.team_comps:
                    result += "## Team Compositions\n\n"
                    for team in self.db.team_comps[char_name]:
                        result += f"**{team['name']}:** {' | '.join(team['members'])}\n"
                
                return [types.TextContent(type="text", text=result)]
            
            else:
                return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    server = GenshinMCPServer()
    
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="genshin-impact-guide",
                server_version="1.0.0",
                capabilities=server.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )

if __name__ == "__main__":
    # Install required packages:
    # pip install mcp httpx
    asyncio.run(main())
