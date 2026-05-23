import os
import re

vault_dir = r"C:\Users\bigi9\Il mio Drive\DriveSyncFiles\D&D - Athea"

def is_empty(filepath):
    try:
        if not os.path.exists(filepath):
             return True
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return len(content.strip()) < 10
    except:
        return True

# 1. Gather all notes
notes = {}
empty_notes = []
all_note_names = []

for root, dirs, files in os.walk(vault_dir):
    if '.obsidian' in root or '.git' in root or '.vscode' in root:
        continue
    for f in files:
        if f.endswith('.md'):
            filepath = os.path.join(root, f)
            notename = f[:-3]
            all_note_names.append(notename)
            if is_empty(filepath):
                empty_notes.append(notename)
            else:
                notes[notename] = filepath

# prefixes list as defined before
prefixes = [
    "Regno di ", "Impero di ", "Città di ", "Cittadina di ", "Cittadinia di ",
    "Terre di ", "Foresta di ", "Monti ", "Isola ", "Rovine di ",
    "Il Sacro Regno di ", "L'Impero Elfico di ", "L'Impero Progressista di ",
    "La Teocrazia di ", "Le Terre Libere di ", "Continente di ",
    "Arcipelago ", "Fiume ", "Lago ", "Catena montuosa "
]

# build linking dictionary
link_candidates = []

for notename in notes:
    link_candidates.append((notename, notename))
    for p in prefixes:
        if notename.startswith(p):
            alias = notename[len(p):].strip()
            if alias:
                link_candidates.append((alias, notename))

# Sort by length descending
link_candidates.sort(key=lambda x: len(x[0]), reverse=True)

empty_notes_set = set(empty_notes)

def is_target_empty(target):
    target = target.strip()
    base_target = target.split('#')[0]
    if not base_target: return False 
    
    if base_target in empty_notes_set: return True
    if base_target not in all_note_names: return True
    return False

# Build regex pattern for plain text. We want it case-sensitive.
escaped_candidates = [re.escape(c[0]) for c in link_candidates]
pattern = r'\b(' + '|'.join(escaped_candidates) + r')\b'
regex = re.compile(pattern)

def process_file_content(content):
    yaml_match = re.match(r'^---\n(.*?)\n---\n?', content, re.DOTALL)
    if yaml_match:
        frontmatter = yaml_match.group(0)
        rest = content[len(frontmatter):]
    else:
        frontmatter = ""
        rest = content

    # Step 1: Remove links to empty notes
    def repl_existing_link(match):
        full_match = match.group(0)
        target = match.group(1)
        label = match.group(2) if match.group(2) else target
        if is_target_empty(target):
            return label # return plain text
        return full_match # keep as is
    
    rest = re.sub(r'\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]', repl_existing_link, rest)
    
    # Step 2: add links where text matches candidates
    parts = re.split(r'(\[\[.*?\]\])', rest)
    new_parts = []
    
    for part in parts:
        if part.startswith('[[') and part.endswith(']]'):
            new_parts.append(part)
        else:
            def repl_match(m):
                match_text = m.group(1)
                target_note = None
                for c in link_candidates:
                    if c[0] == match_text:
                        target_note = c[1]
                        break
                if target_note:
                    if match_text == target_note:
                        return f"[[{target_note}]]"
                    else:
                        return f"[[{target_note}|{match_text}]]"
                return match_text
            
            curr_text = regex.sub(repl_match, part)
            new_parts.append(curr_text)
            
    return frontmatter + ''.join(new_parts)

files_updated = 0
for notename, filepath in notes.items():
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = process_file_content(content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {notename}")
        files_updated += 1
        
print(f"Done processing notes! Updated {files_updated} files.")
