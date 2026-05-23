import re

with open(r'backend\rasa\data\nlu.yml', 'r', encoding='utf-8') as f:
    content = f.read()

entity_counts = {}

intent_pattern = r'- intent: (\w+)\s+examples: \|\n((?:    - .+\n)*)'
intents = re.findall(intent_pattern, content)

for name, block in intents:
    lines = [l.strip()[2:] for l in block.strip().split('\n') if l.strip().startswith('- ')]
    for line in lines:
        # Pattern 1: [value](entity_name)
        simple = re.findall(r'\[([^\]]+)\]\((\w+)\)', line)
        for val, ent in simple:
            entity_counts[ent] = entity_counts.get(ent, 0) + 1
        
        # Pattern 2: [value]{"entity":"xxx", "role":"negated"}
        negated = re.findall(r'\[([^\]]+)\]\{"entity"\s*:\s*"(\w+)"\s*,\s*"role"\s*:\s*"negated"\}', line)
        for val, ent in negated:
            key = ent + '.negated'
            entity_counts[key] = entity_counts.get(key, 0) + 1

print('=== ENTITY DISTRIBUTION ===')
total = 0
for ent in sorted(entity_counts.keys()):
    count = entity_counts[ent]
    total += count
    print(f'{ent}: {count}')
print(f'TOTAL ENTITY ANNOTATIONS: {total}')
print(f'UNIQUE ENTITY TYPES: {len(entity_counts)}')
