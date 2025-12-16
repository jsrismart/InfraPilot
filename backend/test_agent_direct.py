from app.agents.designer_agent import DesignerAgent

print("Testing Designer Agent...")
agent = DesignerAgent()
print("Agent created successfully")

result = agent.generate_from_prompt_parsing("Create a azure vm in A series size at South india location")
print(f"Result type: {type(result)}")
print(f"Result keys: {list(result.keys())}")
print("Success!")
