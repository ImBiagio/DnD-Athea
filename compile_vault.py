import os

vault_dir = r"C:\Users\bigi9\Il mio Drive\DriveSyncFiles\D&D - Athea"
output_file = os.path.join(vault_dir, "Athea_Knowledge_Base_Completa.md")

ignore_dirs = {'.git', '.obsidian', '.smart-env', '.vscode', 'copilot'}
ignore_files = {'Athea_Knowledge_Base_Completa.md', 'compile_vault.py', 'process_links.py'}

def compile_notes():
    compiled_count = 0
    with open(output_file, 'w', encoding='utf-8') as out_f:
        out_f.write("# Athea D&D Knowledge Base - Omnibus Completo\n")
        out_f.write("Questo file raccoglie tutte le note della campagna del mondo di Athea. ")
        out_f.write("Ideale per essere dato in pasto a un LLM per domande rapide durante le sessioni.\n\n")
        out_f.write("---\n\n")
        
        for root, dirs, files in os.walk(vault_dir):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in sorted(files):
                if file.endswith('.md') and file not in ignore_files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, vault_dir)
                    
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as in_f:
                            content = in_f.read().strip()
                        
                        out_f.write(f"# FILE: {rel_path.replace(os.sep, '/')}\n")
                        out_f.write(f"**Titolo Nota:** {file[:-3]}\n")
                        out_f.write("---\n")
                        if content:
                            out_f.write(content)
                        else:
                            out_f.write("*(Nota vuota)*")
                        out_f.write("\n\n---\n\n")
                        compiled_count += 1
                    except Exception as e:
                        print(f"Errore nella lettura di {rel_path}: {e}")
                        
    print(f"Compilazione completata! {compiled_count} note unite in: {output_file}")

if __name__ == '__main__':
    compile_notes()
