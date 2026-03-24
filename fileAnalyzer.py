import os
import re
import sys
import subprocess
import shutil
import tempfile

from tools import FindRepoName
from dataClasses import RFileData
from satd_knowledgebase import add_to_knowledge_base
from contextAI import extract_context_with_ai  # NEW IMPORT

KEYWORDS = ['TODO', 'TO-DO', 'FIXME', 'FIX-ME', ' FIX:', 'HACK', 'NOTE:', 'WARNING:', 'SATD']
_SINGLE_RE = re.compile(r'#.*(' + '|'.join(KEYWORDS) + ').*', re.IGNORECASE)


def clone_repository(url: str, dest: str) -> str:
    """Clone repository into dest. Exits on failure."""
    try:
        subprocess.run(['git', 'clone', '--depth', '1', url, dest],
                       check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print("Error cloning repository:", e.stderr.strip())
        sys.exit(1)
    except FileNotFoundError:
        print("Git not found. Install Git and ensure it's on PATH.")
        sys.exit(1)
    return dest


def detect_satd_in_code(content: str, file_path: str):
    """
    Detect SATD in code with AI-enhanced context extraction.
    
    Args:
        content: File content as string
        file_path: Path to the file being analyzed
    
    Returns:
        List of dicts with SATD info and AI-extracted context
    """
    results = []
    lines = content.splitlines()
    
    print("  Using AI-enhanced context extraction")
    
    i = 0
    while i < len(lines):
        line = lines[i]
        lineno = i + 1
        m = _SINGLE_RE.search(line)
        
        if m:
            # Found a SATD keyword
            comment_lines = [line.strip()]
            original_line = lineno
            
            # Collect consecutive comment lines
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if next_line.startswith('#') and not _SINGLE_RE.search(next_line):
                    comment_lines.append(next_line)
                    j += 1
                else:
                    break
            
            comment_end_idx = j  # Index after last comment line
            
            # Get full and cleaned comment text
            full_text = '\n'.join(comment_lines)
            comment_text = '\n'.join([cl.lstrip('#').strip() for cl in comment_lines])
            
            # Get code after comment (up to 50 lines for AI analysis)
            code_after = lines[comment_end_idx:comment_end_idx + 50]
            
            # Use AI to extract relevant context
            context_after = extract_context_with_ai(comment_text, code_after)
            
            print(f"  Line {lineno} [{m.group(1).upper()}]: AI captured {len(context_after)} lines")
            
            results.append({
                'file': file_path,
                'line': original_line,
                'type': m.group(1).upper(),
                'text': full_text,
                'comment': comment_text,
                'context_after': context_after,
                'context_type': 'lines'
            })
            
            # Skip processed lines
            i = j
        else:
            i += 1
    
    return results


def generateTextResponseForFile(original_file_path, results):
    """Generate text summary of SATD findings."""
    fileTextString = ""
    fileTextString += f"File: {original_file_path}\n"
    fileTextString += f"Total SATD items found: {len(results)}\n"
    fileTextString += "=" * 50 + "\n\n"
    for item in results:
        fileTextString += f"Line {item['line']} [{item['type']}]:\n"
        fileTextString += f"{item['text'].lstrip()}\n"
        fileTextString += "-" * 50 + "\n"
    return fileTextString


def save_report_for_file(results, output_dir: str, original_file_path: str, repo_name: str) -> str:
    """Save SATD findings to a formatted text file."""
    os.makedirs(output_dir, exist_ok=True)

    # Create .gitignore
    gitignore_path = os.path.join(output_dir, ".gitignore")
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w", encoding="utf-8") as gi:
            gi.write("*\n!.gitignore\n")

    base = os.path.splitext(os.path.basename(original_file_path))[0]
    filename = f"{base}.txt"
    report_path = os.path.join(output_dir, filename)

    counter = 1
    name_without_ext = os.path.join(output_dir, base)
    while os.path.exists(report_path):
        report_path = f"{name_without_ext}_{counter}.txt"
        counter += 1

    with open(report_path, 'w', encoding='utf-8') as f:
        # Header
        f.write("╔" + "═" * 78 + "╗\n")
        f.write("║" + " " * 78 + "║\n")
        f.write("║" + "SATD ANALYSIS REPORT (AI-Enhanced)".center(78) + "║\n")
        f.write("║" + " " * 78 + "║\n")
        f.write("╚" + "═" * 78 + "╝\n\n")
        
        f.write(f" File: {original_file_path}\n")
        f.write(f" Repository: {repo_name}\n")
        f.write(f" Total SATD items found: {len(results)}\n")
        f.write("\n" + "─" * 80 + "\n\n")
        
        for idx, item in enumerate(results, 1):
            f.write(f"┌─ SATD Item #{idx} " + "─" * (80 - len(f"┌─ SATD Item #{idx} ")) + "\n")
            f.write(f"│\n")
            f.write(f"│  Type: {item['type']}\n")
            f.write(f"│  Location: Line {item['line']}\n")
            f.write(f"│\n")
            
            # SATD Comment
            f.write(f"├─ SATD Comment:\n")
            f.write(f"│\n")
            for text_line in item['text'].split('\n'):
                f.write(f"│   {text_line.lstrip()}\n")
            f.write(f"│\n")
            
            # AI-extracted context
            if item.get('context_after'):
                if item.get('context_type') == 'function':
                    f.write(f"├─ AI-Selected Context (Function):\n")
                else:
                    f.write(f"├─ AI-Selected Context (Lines):\n")
                f.write(f"│\n")
                
                for ctx_line in item['context_after']:
                    f.write(f"│   {ctx_line.rstrip()}\n")
                f.write(f"│\n")
            
            f.write(f"└" + "─" * 79 + "\n\n")
    
    return report_path


def analyze_file(repo_path: str, RFileInstance: RFileData, output_dir: str, repo_name: str, 
                add_to_kb=True, repo_url=None):
    """
    Analyze a single R file for SATD with AI-enhanced context extraction.
    
    Args:
        repo_path: Path to repository
        RFileInstance: R file data object
        output_dir: Where to save reports
        repo_name: Name of repository
        add_to_kb: Whether to add findings to knowledge base
        repo_url: URL of repository (optional)
    
    Returns:
        tuple: (total_findings, file_has_satd, textResult, loc, foundFile)
    """

    total_findings = 0
    file_has_satd = False
    textResult = ""
    content = ""
    loc = 0
    foundFile = False
    file_path = RFileInstance.fullpath

    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as fh:
            print(f"Reading file: {FindRepoName(file_path)}")
            content = fh.read()
            loc = content.count("\n") + 1 if content else 0
            foundFile = True
            print(f"  File has {loc} lines of code")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        foundFile = False
    
    if content:
        results = detect_satd_in_code(content, file_path)
        
        if results:
            total_findings += len(results)
            file_has_satd = True
            textResult = generateTextResponseForFile(file_path, results)
            
            print(f"  Found {len(results)} SATD items in: {os.path.basename(file_path)}")

            if add_to_kb:
                print(f"  Adding {len(results)} SATD entries to knowledge base...")
                add_to_knowledge_base(results, repo_name, repo_url=repo_url)

    return total_findings, file_has_satd, textResult, loc, foundFile