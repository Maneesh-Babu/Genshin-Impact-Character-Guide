# Genshin Impact MCP Server Demo

This is a demo Model Context Protocol (MCP) server that provides character information and build guides for Genshin Impact.

## Features

- **Character Information**: Get detailed stats and info for characters
- **Build Guides**: Optimal artifact sets, weapons, and stat priorities
- **Team Compositions**: Recommended team comps for different characters
- **Comprehensive Guides**: Complete build guides with all information

## Installation

### 1. Install Dependencies

```bash
pip install mcp httpx
```

### 2. Project Structure

```
genshin-mcp-project/
├── genshin_mcp_server.py    # Main MCP server
├── genshin_mcp_client.py    # Test client
├── requirements.txt         # Dependencies
└── README.md               # This file
```

### 3. Requirements File

Create `requirements.txt`:
```
mcp>=1.0.0
httpx>=0.25.0
```

## Usage

### Option 1: Test with Client Script

```bash
python genshin_mcp_client.py
```

### Option 2: Use with Claude Desktop

1. **Edit Claude Desktop Config**:
   - Location: `~/.claude/claude_desktop_config.json` (macOS/Linux)
   - Or: `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

2. **Add Server Configuration**:
```json
{
  "mcpServers": {
    "genshin-impact-guide": {
      "command": "python",
      "args": ["/full/path/to/genshin_mcp_server.py"],
      "env": {
        "PYTHONPATH": "/full/path/to/project"
      }
    }
  }
}
```

3. **Restart Claude Desktop**

4. **Test with Prompts**:
   - "Create a build guide for Mavuika"
   - "Show me Neuvillette's character info"
   - "What are the best team compositions for Kazuha?"

## Example Interactions

### Character Information
```
User: "Tell me about Mavuika"
→ MCP provides character stats, element, weapon type, role
→ Claude creates detailed response with context
```

### Build Guide
```
User: "Create a build guide for Mavuika"
→ MCP provides artifact sets, weapons, stat priorities
→ Claude creates comprehensive build guide
```

### Team Compositions
```
User: "What teams work well with Kazuha?"
→ MCP provides team composition data
→ Claude explains synergies and strategies
```

## Current Database

The demo includes data for:
- **Mavuika** (Pyro Claymore)
- **Neuvillette** (Hydro Catalyst)
- **Kazuha** (Anemo Sword)
- **Nahida** (Dendro Catalyst)
- **Furina** (Hydro Sword)

## Extending the Server

### Adding New Characters

1. **Add to Characters Database**:
```python
self.characters["new_character"] = Character(
    name="New Character",
    element="Element",
    weapon_type="Weapon",
    rarity=5,
    role="Role",
    description="Description"
)
```

2. **Add Build Information**:
```python
self.builds["new_character"] = [
    Build(
        character="New Character",
        role="DPS",
        main_stats={"sands": "ATK%", "goblet": "Element DMG%", "circlet": "CRIT Rate"},
        artifact_sets=["Set 1", "Set 2"],
        weapons=["Weapon 1", "Weapon 2"],
        substats_priority=["CRIT Rate", "CRIT DMG", "ATK%"],
        talent_priority=["Skill", "Burst", "Normal"]
    )
]
```

### Adding Real Data Sources

Replace the mock database with real data fetching:

```python
class GenshinWikiScraper:
    async def fetch_character_data(self, character_name):
        # Scrape from Genshin Wiki
        # Parse character stats
        # Return structured data
        pass
    
    async def fetch_builds(self, character_name):
        # Scrape from build guide sites
        # Parse artifact recommendations
        # Return build data
        pass
```

### Adding New Tools

```python
@self.server.list_tools()
async def handle_list_tools():
    return [
        # ... existing tools ...
        types.Tool(
            name="calculate_damage",
            description="Calculate damage output for a build",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "attack_value": {"type": "number"},
                    "crit_rate": {"type": "number"},
                    "crit_damage": {"type": "number"}
                },
                "required": ["character_name", "attack_value"]
            }
        )
    ]
```

## Troubleshooting

### Common Issues

1. **Module Not Found**: Ensure MCP is installed correctly
2. **Server Not Starting**: Check Python path and file permissions
3. **Claude Desktop Not Connecting**: Verify config file path and syntax

### Debug Mode

Run with debug logging:
```bash
PYTHONPATH=. python -m logging.basicConfig level=DEBUG genshin_mcp_server.py
```

## Future Enhancements

- Real-time data from game APIs
- Damage calculation tools
- Artifact optimization
- Event and banner information
- Build comparison tools
- Meta tier lists integration

## Contributing

This is a demo project. To extend it:

1. Fork the project
2. Add new features or data sources
3. Test with the client script
4. Submit improvements

## License

MIT License - feel free to use and modify for your own projects!
