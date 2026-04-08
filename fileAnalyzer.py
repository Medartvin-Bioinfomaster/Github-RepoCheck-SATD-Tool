import os
import re
import sys
import subprocess
import shutil
import tempfile

from tools import FindRepoName
from dataClasses import RFileData
 


from satd_knowledgebase import add_to_knowledge_base  

KEYWORDS = ['TODO', 'TO-DO', 'FIXME', 'FIX-ME', 'FIX:', 'HACK', 'NOTE', 'WARNING:', 'SATD']
_SINGLE_RE = re.compile(r'#.*(' + '|'.join(KEYWORDS) + ').*', re.IGNORECASE)

# R function pattern: matches function definitions
R_FUNCTION_PATTERN = re.compile(r'^\s*[\w\.\[\]<-]+\s*(<-|=)\s*function\s*\(', re.IGNORECASE)

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
    total_satd_in_file = 0 
    total_compromised_lines = 0
    unique_compromised_lines = set()

    i = 0
    while i < len(lines):
        line = lines[i]
        lineno = i + 1
        m = _SINGLE_RE.search(line)
        
        if m:
            # Found a SATD keyword - collect consecutive comment lines
            total_satd_in_file += 1
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
                    # print(f"  Captured entire function at line {first_code_idx + 1} (SATD at line {lineno})")
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

            # complines = len(context_after) if context_type == 'function' else 0
            compromised_lines = len(context_after) if context_type == 'function' else 0


            results.append({
                'file': file_path,
                'line': original_line,
                'type': m.group(1).upper(),
                'text': full_text,
                'comment': comment_text,
                'context_after': context_after,
                'context_type': context_type,  # 'lines' or 'function'
                'compromised_lines': compromised_lines  # total amount of lines compromised in file
            })
            
            # Skip the lines we've already processed
            i = j
        else:
            i += 1
    
    for item in results:
        start_linje = item['line']
        for i, code_line in enumerate(item['context_after']):
            line_id = f"{item['file']}:{start_linje + i}"
            unique_compromised_lines.add(line_id)
    total_compromised_lines = len(unique_compromised_lines)

    return results, total_satd_in_file, total_compromised_lines


def analyze_file(RFileInstance: RFileData, repo_name: str, context_lines=3, capture_full_function=True, add_to_kb=True, repo_url=None, user_id=None):
    file_has_satd = False
    textResult = ""
    content = "" # this has to be here, must declare the variable before its use
    loc = 0
    foundFile = False
    file_path = RFileInstance.fullpath
    satd_count = 0 #changed to 0 instead -1
    lines_compromised = 0

    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as fh: #opens the file
            content = fh.read() #reads the file, stores the script in "content" variable
            loc = content.count("\n") if content else 0 # denne kodesnutten kan bli byttet ut med en mer "genuin" innhentingsmetode, hvis funksjonen går igjennom filer line for line i for-loop, så er dette bedre og mer robust
            foundFile = True
    except Exception as e:
        foundFile = False
        # if file has no content (could have been deleted or emptied), skip it

    if content:
        results, total_satd_in_file, total_compromised_lines = detect_satd_in_code(content, file_path, context_lines=context_lines, capture_full_function=capture_full_function)

        if results:
            satd_count = total_satd_in_file
            lines_compromised = total_compromised_lines
            file_has_satd = True
            textResult = generate_report_string(file_path, results)
            # unique_compromised_lines = set()
            # for item in results:
            #     start_linje = item['line']
            #     for i, code_line in enumerate(item['context_after']):
            #         line_id = f"{item['file']}:{start_linje + i}"
            #         unique_compromised_lines.add(line_id)

            # lines_compromised = len(unique_compromised_lines)
            # print(f"Found {len(results)} SATD items in: {os.path.basename(file_path)}")
            if add_to_kb:
                print(f"Adding {len(results)} SATD entries to knowledge base...")
                add_to_knowledge_base(results, repo_name, repo_url=repo_url, user_id=user_id)

    return file_has_satd, textResult, loc, foundFile, satd_count, lines_compromised


def generate_report_string(original_file_path, results):
    res = ""
    res += "╔" + "═" * 78 + "╗\n"
    res += "║" + " " * 78 + "║\n"
    res += "║" + "SATD ANALYSIS REPORT".center(78) + "║\n"
    res += "║" + " " * 78 + "║\n"
    res += "╚" + "═" * 78 + "╝\n\n"
    res += f" File: {original_file_path}\n"
    res += f" Total SATD items found: {len(results)}\n"
    res += "\n" + "─" * 80 + "\n\n"
    
    for idx, item in enumerate(results, 1):
        header_text = f"┌─ SATD Item #{idx} "
        res += header_text + "─" * (80 - len(header_text)) + "\n"
        res += "│\n"
        res += f"│  Type: {item['type']}\n"
        res += f"│  Location: Line {item['line']}\n"
        res += "│\n"
        res += "├─  SATD Comment:\n"
        res += "│\n"
        for text_line in item['text'].split('\n'):
            res += f"│   {text_line.lstrip()}\n"
        res += "│\n"
        if item.get('context_after'):
            title = "Related Function (Complete)" if item.get('context_type') == 'function' else "Code Context"
            res += f"├─  {title}:\n"
            res += "│\n"
            for ctx_line in item['context_after']:
                res += f"│   {ctx_line.rstrip()}\n"
            res += "│\n"
        res += "└" + "─" * 79 + "\n\n"
        
    return res
