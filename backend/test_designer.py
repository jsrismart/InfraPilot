from app.agents.designer_agent import DesignerAgent

agent = DesignerAgent()
result = agent.generate_from_prompt_parsing('Create a azure vm in A series size at South india location')

print('Result type:', type(result))
print('Keys:', result.keys() if isinstance(result, dict) else 'N/A')
for k, v in result.items():
    print(f'{k}: {len(str(v))} chars')
