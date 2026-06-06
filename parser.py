import json
import re

with open('gabarito_bruto.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

gabarito = {}
current_num = None
current_questions = []
current_answers = []
has_started_questions = False

for line in lines:
    line = line.strip()
    if not line:
        continue
    
    match = re.match(r'^(?:Tarefa\s*)?(\d+)\s*-', line, re.IGNORECASE)
    if match and 'KC' in line.upper():
        if current_num:
            if has_started_questions:
                current_questions.append(current_answers)
            gabarito[current_num] = current_questions
            
        current_num = str(match.group(1))
        current_questions = []
        current_answers = []
        has_started_questions = False
        continue
        
    if current_num is None:
        continue
        
    q_match = re.match(r'^(\d+)\.', line)
    if q_match:
        if has_started_questions:
            current_questions.append(current_answers)
        has_started_questions = True
        current_answers = []
            
        if 'Selecione' in line and ':' in line:
            continue
            
        ans = re.sub(r'^\d+\.\s*', '', line).strip()
        if ans == '?':
            pass
        elif ans:
            current_answers.append(ans)
            
    elif line.startswith('•') or line.startswith('·') or line.startswith('-'):
        ans = re.sub(r'^[•·-]\s*', '', line).strip()
        if ans:
            current_answers.append(ans)
    else:
        if current_answers:
            current_answers[-1] += " " + line

if current_num:
    if has_started_questions:
        current_questions.append(current_answers)
    gabarito[current_num] = current_questions

with open('gabarito.json', 'w', encoding='utf-8') as f:
    json.dump(gabarito, f, ensure_ascii=False, indent=4)
