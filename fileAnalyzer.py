import os
import re
import sys
import subprocess
import shutil
import tempfile

from tools import FindRepoName
from dataClasses import RFileData

KEYWORDS = ['TODO', 'TO-DO', 'FIXME', 'FIX-ME', 'FIX', 'HACK', 'XXX', 'NOTE', 'WARNING', 'SATD']
_SINGLE_RE = re.compile(r'#.*(' + '|'.join(KEYWORDS) + ').*', re.IGNORECASE)
_MULTI_RE = re.compile(r'/\*.*?(' + '|'.join(KEYWORDS) + ').*?\*/', re.IGNORECASE | re.DOTALL)


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
    """Return list of detected SATD items from content."""
    results = []
    for lineno, line in enumerate(content.splitlines(), 1):
        m = _SINGLE_RE.search(line)
        if m:
            comment = line.strip().lstrip('#').strip()
            results.append({
                'file': file_path,
                'line': lineno,
                'type': m.group(1).upper(),
                'text': line.strip(),   # strip both leading and trailing whitespace
                'comment': comment
            })
    for m in _MULTI_RE.finditer(content):
        start_line = content[:m.start()].count('\n') + 1
        comment_text = ' '.join(m.group().split())
        comment_type = re.search('|'.join(KEYWORDS), m.group(), re.IGNORECASE).group().upper()
        results.append({
            'file': file_path,
            'line': start_line,
            'type': comment_type,
            'text': comment_text.strip(),
            'comment': comment_text
        })
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

def save_report_for_file(results, output_dir: str, original_file_path: str, repo_name: str) -> str:
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

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"File: {original_file_path}\n")
        f.write(f"Total SATD items found: {len(results)}\n")
        f.write("=" * 50 + "\n\n")
        for item in results:
            # sørg for å fjerne eventuelle ledende mellomrom i output
            f.write(f"Line {item['line']} [{item['type']}]:\n")
            f.write(f"{item['text'].lstrip()}\n")
            f.write("-" * 50 + "\n")
    return report_path


def scan_repo_and_save_reports(repo_path: str, output_dir: str, repo_name: str):
    total_findings = 0
    files_with_satd = 0
    reports = []
    content = ""
    for root, dirs, files in os.walk(repo_path):
        if '.git' in root:
            print(".git found in the root, for some reason we skip this then?")
            continue
        for fname in files:
            if not fname.lower().endswith('.r'):
                continue
            path = os.path.join(root, fname)
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as fh:
                    print("Found content, file has been read")
                    content = fh.read()
            except Exception as e:
                print(f"Error reading {path}: {e}")
                continue
            results = detect_satd_in_code(content, path)
            if results:
                total_findings += len(results)
                files_with_satd += 1
                rp = save_report_for_file(results, output_dir, path, repo_name)
                reports.append(rp)
                print(f"Found {len(results)} SATD items in: {os.path.basename(path)}")
    return total_findings, files_with_satd, reports


def analyze_file(repo_path: str, RFileInstance: RFileData, output_dir: str, repo_name: str): # remove repopath? <--
    total_findings = 0
    files_with_satd = 0
    textResult = ""
    content = ""
    loc = 0
    foundFile = False
    file_path = RFileInstance.fullpath

    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as fh:
            print("Found content, file has been read")
            content = fh.read()
            loc = sum(1 for line in fh)
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
            files_with_satd += 1
            textResult = generateTextResponseForFile(file_path, results)
            # rp = save_report_for_file(results, output_dir, file_path, repo_name)
            # reports.append(rp)
            # reports.append(textResult)
            print(f"Found {len(results)} SATD items in: {os.path.basename(file_path)}")

    return total_findings, files_with_satd, textResult, loc, foundFile

# def analyze_file(repo_path: str, output_dir: str, repo_name: str) {

# }
