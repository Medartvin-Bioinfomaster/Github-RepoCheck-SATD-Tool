import os
import re
import sys
import subprocess
import shutil
import tempfile

from tools import FindRepoName
from dataClasses import RFileData
from datetime import datetime  


from satd_knowledgebase import add_to_knowledge_base  

KEYWORDS = ['TODO', 'TO-DO', 'FIXME', 'FIX-ME', 'FIX', 'HACK', 'XXX', 'NOTE', 'WARNING', 'SATD']
_SINGLE_RE = re.compile(r'#.*(' + '|'.join(KEYWORDS) + ').*', re.IGNORECASE)

# R function pattern: matches function definitions
R_FUNCTION_PATTERN = re.compile(r'^\s*[\w\.\[\]<-]+\s*(<-|=)\s*function\s*\(', re.IGNORECASE)


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


def find_function_end(lines, start_idx):
    """
    Find the end of an R function starting at start_idx.
    Returns the index of the last line of the function.
    """
    brace_count = 0
    in_function = False
    
    for i in range(start_idx, len(lines)):
        line = lines[i]
        
        # Count opening and closing braces
        for char in line:
            if char == '{':
                brace_count += 1
                in_function = True
            elif char == '}':
                brace_count -= 1
                
        # If we've closed all braces, function is complete
        if in_function and brace_count == 0:
            return i
    
    # If no closing brace found, return a reasonable default
    return min(start_idx + 20, len(lines) - 1)


def extract_full_function(lines, start_idx):
    """
    Extract the complete function starting at start_idx.
    Returns list of lines comprising the entire function.
    """
    end_idx = find_function_end(lines, start_idx)
    return lines[start_idx:end_idx + 1]


def is_function_definition(line):
    """Check if a line is a function definition in R."""
    return R_FUNCTION_PATTERN.match(line) is not None


def detect_satd_in_code(content: str, file_path: str, context_lines=3, capture_full_function=True):
    """
    Returns:
        List of dicts with SATD info and context
    """
    results = []
    lines = content.splitlines()
    
    i = 0
    while i < len(lines):
        line = lines[i]
        lineno = i + 1
        m = _SINGLE_RE.search(line)
        
        if m:
            # Found a SATD keyword - collect consecutive comment lines
            comment_lines = [line.strip()]
            original_line = lineno
            
            # Look ahead for consecutive comment lines
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if next_line.startswith('#') and not _SINGLE_RE.search(next_line):
                    comment_lines.append(next_line)
                    j += 1
                else:
                    break
            
            comment_end_idx = j  # Index after last comment line
            
            # Capture context AFTER with smart function detection
            context_after = []
            context_type = "lines"  # or "function"
            
            # Find first non-comment, non-blank line after SATD
            first_code_idx = None
            for k in range(comment_end_idx, min(len(lines), comment_end_idx + 20)):
                line_stripped = lines[k].strip()
                if line_stripped and not line_stripped.startswith('#'):
                    first_code_idx = k
                    break
            
            if first_code_idx is not None:
                # Check if first code line is a function definition
                if capture_full_function and is_function_definition(lines[first_code_idx]):
                    # Extract the ENTIRE function
                    context_after = extract_full_function(lines, first_code_idx)
                    context_type = "function"
                    print(f"  Captured entire function at line {first_code_idx + 1} (SATD at line {lineno})")
                else:
                    # Just capture N lines of code
                    for k in range(comment_end_idx, min(len(lines), comment_end_idx + context_lines + 10)):
                        line_stripped = lines[k].strip()
                        if line_stripped and not line_stripped.startswith('#'):
                            context_after.append(lines[k])
                            if len(context_after) >= context_lines:
                                break
            
            full_text = '\n'.join(comment_lines)
            comment_text = '\n'.join([cl.lstrip('#').strip() for cl in comment_lines])
            
            results.append({
                'file': file_path,
                'line': original_line,
                'type': m.group(1).upper(),
                'text': full_text,
                'comment': comment_text,
                'context_after': context_after,
                'context_type': context_type  # 'lines' or 'function'
            })
            
            # Skip the lines we've already processed
            i = j
        else:
            i += 1
    
    return results

def generateTextResponseForFile(original_file_path, results):
    fileTextString = ""
    fileTextString += f"File: {original_file_path}\n"
    fileTextString += f"Total SATD items found: {len(results)}\n"
    fileTextString += "=" * 50 + "\n\n" # hva er dette??
    for item in results:
        # sørg for å fjerne eventuelle ledende mellomrom i output
        fileTextString += f"Line {item['line']} [{item['type']}]:\n"
        fileTextString += f"{item['text'].lstrip()}\n"
        fileTextString += "-" * 50 + "\n"
    return fileTextString

def generateTextResponseForFile(original_file_path, results):
    fileTextString = ""
    fileTextString += f"File: {original_file_path}\n"
    fileTextString += f"Total SATD items found: {len(results)}\n"
    fileTextString += "=" * 50 + "\n\n" # hva er dette??
    for item in results:
        # sørg for å fjerne eventuelle ledende mellomrom i output
        fileTextString += f"Line {item['line']} [{item['type']}]:\n"
        fileTextString += f"{item['text'].lstrip()}\n"
        fileTextString += "-" * 50 + "\n"
    return fileTextString


def save_report_for_file(results, output_dir: str, original_file_path: str, repo_name: str) -> str:
    #better format for more user friendly output
    os.makedirs(output_dir, exist_ok=True)

    # create .gitignore to avoid tracking findings in any repo
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

        # Ouput format is based on AI code from claude code

    with open(report_path, 'w', encoding='utf-8') as f:
        # Header
        f.write("╔" + "═" * 78 + "╗\n")
        f.write("║" + " " * 78 + "║\n")
        f.write("║" + "SATD ANALYSIS REPORT".center(78) + "║\n")
        f.write("║" + " " * 78 + "║\n")
        f.write("╚" + "═" * 78 + "╝\n\n")
        
        f.write(f" File: {original_file_path}\n")
        f.write(f" Total SATD items found: {len(results)}\n")
        f.write("\n" + "─" * 80 + "\n\n")
        
        for idx, item in enumerate(results, 1):
            
            
            f.write(f"┌─ SATD Item #{idx} " + "─" * (80 - len(f"┌─ SATD Item #{idx} ")) + "\n")
            f.write(f"│\n")
            f.write(f"│  Type: {item['type']}\n")
            f.write(f"│  Location: Line {item['line']}\n")
            f.write(f"│\n")
            
            # SATD Comment section
            f.write(f"├─  SATD Comment:\n")
            f.write(f"│\n")
            for text_line in item['text'].split('\n'):
                f.write(f"│   {text_line.lstrip()}\n")
            f.write(f"│\n")
            
            # Context section
            if item.get('context_after'):
                if item.get('context_type') == 'function':
                    f.write(f"├─  Related Function (Complete):\n")
                else:
                    f.write(f"├─  Code Context:\n")
                f.write(f"│\n")
                
                for ctx_line in item['context_after']:
                    f.write(f"│   {ctx_line.rstrip()}\n")
                f.write(f"│\n")
            
            f.write(f"└" + "─" * 79 + "\n\n")
    
    return report_path









def analyze_file(repo_path: str, RFileInstance: RFileData, output_dir: str, repo_name: str, 
                context_lines=3, capture_full_function=True, add_to_kb=True, repo_url=None, user_id=None):
    total_findings = 0
    file_has_satd = False
    textResult = ""
    content = ""
    loc = 0
    foundFile = False
    file_path = RFileInstance.fullpath

    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as fh:
            print("Found content, file has been read")
            content = fh.read()
            loc = content.count("\n") + 1 if content else 0 # denne kodesnutten kan bli byttet ut med en mer "genuin" innhentingsmetode, hvis funksjonen går igjennom filer line for line i for-loop, så er dette bedre og mer robust
            foundFile = True
            print(f"File {FindRepoName(file_path)} has {loc} lines of code")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        foundFile = False
        # continue
    # if file has no content (could have been deleted or emptied), skip it
    if content: #før var det if not content, men da blir det to like returns. Heller bedre å bare skippe ifen all together hvis fil ikke ble funnet
        results = detect_satd_in_code(content, file_path)
        if results:
            total_findings += len(results)
            file_has_satd = True
            textResult = generateTextResponseForFile(file_path, results)
            # rp = save_report_for_file(results, output_dir, file_path, repo_name)
            # reports.append(rp)
            # reports.append(textResult)
            print(f"Found {len(results)} SATD items in: {os.path.basename(file_path)}")

            if add_to_kb:
                print(f"Adding {len(results)} SATD entries to knowledge base...")
                add_to_knowledge_base(results, repo_name, repo_url=repo_url, user_id=user_id)

    return total_findings, file_has_satd, textResult, loc, foundFile










# function not used , may delete later





def scan_repo_and_save_reports(repo_path: str, output_dir: str, repo_name: str, 
                               context_lines=3, capture_full_function=True):
    """
    Scan repository for SATD and save reports with context.
    
    Args:
        repo_path: Path to repository
        output_dir: Where to save reports
        repo_name: Name of repository
        context_lines: Number of code lines to capture after SATD (default 5)
        capture_full_function: If True, capture entire function when found after SATD
    """
    total_findings = 0
    files_with_satd = 0
    reports = []
    
    for root, dirs, files in os.walk(repo_path):
        if '.git' in root:
            continue
        for fname in files:
            if not fname.lower().endswith('.r'):
                continue
            path = os.path.join(root, fname)
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as fh:
                    print(f"Reading: {os.path.basename(path)}")
                    content = fh.read()
            except Exception as e:
                print(f"Error reading {path}: {e}")
                continue
            
            results = detect_satd_in_code(content, path, context_lines=context_lines, 
                                         capture_full_function=capture_full_function)
            
            if results:
                total_findings += len(results)
                files_with_satd += 1
                rp = save_report_for_file(results, output_dir, path, repo_name)
                reports.append(rp)
                print(f"  Found {len(results)} SATD items in: {os.path.basename(path)}")
    
    return total_findings, files_with_satd, reports
                print(f"Found {len(results)} SATD items in: {os.path.basename(path)}")
    return total_findings, files_with_satd, reports


def analyze_file(repo_path: str, RFileInstance: RFileData, output_dir: str, repo_name: str): # remove repopath? <--
    total_findings = 0
    file_has_satd = False
    textResult = ""
    content = ""
    loc = 0
    foundFile = False
    file_path = RFileInstance.fullpath

    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as fh:
            print("Found content, file has been read")
            content = fh.read()
            loc = content.count("\n") + 1 if content else 0 # denne kodesnutten kan bli byttet ut med en mer "genuin" innhentingsmetode, hvis funksjonen går igjennom filer line for line i for-loop, så er dette bedre og mer robust
            foundFile = True
            print(f"File {FindRepoName(file_path)} has {loc} lines of code")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        foundFile = False
        # continue
    # if file has no content (could have been deleted or emptied), skip it
    if content: #før var det if not content, men da blir det to like returns. Heller bedre å bare skippe ifen all together hvis fil ikke ble funnet
        results = detect_satd_in_code(content, file_path)
        if results:
            total_findings += len(results)
            file_has_satd = True
            textResult = generateTextResponseForFile(file_path, results)
            # rp = save_report_for_file(results, output_dir, file_path, repo_name)
            # reports.append(rp)
            # reports.append(textResult)
            print(f"Found {len(results)} SATD items in: {os.path.basename(file_path)}")

    return total_findings, file_has_satd, textResult, loc, foundFile

# def analyze_file(repo_path: str, output_dir: str, repo_name: str) {

# }
