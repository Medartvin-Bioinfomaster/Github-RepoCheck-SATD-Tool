from pydriller.metrics.process.code_churn import CodeChurn
from pathlib import Path


def FindRepoName(repourl):
    lastlinkname = None
    if repourl.__contains__('\\'):
        lastlinkname = repourl.split("\\")
    else:
        lastlinkname = repourl.split("/")
        
    linklength = len(lastlinkname)
    nameFromList = lastlinkname[linklength - 1]
    return nameFromList

def CreateTypedRepoName(repourl, iteration):
    # lastlinkname = None
    # if repourl.__contains__('\\'):
    #     lastlinkname = repourl.split("\\")
    # else:
    #     lastlinkname = repourl.split("/")
    try :
        repName = FindRepoName(repourl)
        # linklength = len(lastlinkname)
        tag = "URL" if isUrl(repourl) else "Local"
        # print(f"- {str(iteration + 1)}: {lastlinkname[linklength - 1]} ({tag})")
        typedName = f"- {str(iteration + 1)}: {repName} ({tag})"
        return typedName
    except IndexError:
        return f"- Broken Reponame or Link"

def CreateTypedReportName(reporturl, iteration):
    try:
        normalized_path = reporturl.replace('\\', '/')
        path_parts = normalized_path.split('/')
        folder_name = path_parts[-2]
        stro = folder_name.split('_')
        if len(stro) >= 2:
                repName = stro[0]
                count = stro[1]
        else:
            repName = folder_name
            count = "0"

        typedName = f"- {iteration + 1}: {repName} ({count})"

        return typedName
    except IndexError:
        return f"- Broken Reponame or Link"


def isUrl(repolink):
    if (repolink.startswith('http://') or repolink.startswith('https://')):
        return True
    else:
        return False
    
def WriteRepoName(reposInStorage):

    if (reposInStorage and len(reposInStorage) > 0):
        print("\nStored repos:")
        for i, repo in enumerate(reposInStorage):
            if not repo or repo.strip() == "": # skip any whitespace
                continue
            # lastlinkname = None
            # if repo.__contains__('\\'):
            #     lastlinkname = repo.split("\\")
            # else:
            #     lastlinkname = repo.split("/")
            # linklength = len(lastlinkname)
            # tag = "URL" if isUrl(repo) else "Local"
            # print(f"- {str(i + 1)}: {lastlinkname[linklength - 1]} ({tag})")
            repoNameTyped = CreateTypedRepoName(repo, i)
            print(repoNameTyped)

    print("Write the repo url bellow. To load a saved repo, type the number from a stored repo above.")
    urlForRepo = input("Command|: ")
    urlToReturn = ""

    if urlForRepo.lower() == "cancel":  
        # CancelProgramDTF("User cancelled")
        return {"text": "User cancelled", "status": False}
    elif urlForRepo.isnumeric():
        index = int(urlForRepo) - 1
        if index >= 0 and index < len(reposInStorage):
            urlToReturn = reposInStorage[index] #translate the record to index
        #_
    else:
        urlToReturn = urlForRepo
    # print("repo?")
    # print(urlToReturn)
    # Retruing the reponame
    return urlToReturn


def WriteListOfReportsStored(reportsInStorage):
    if (reportsInStorage and len(reportsInStorage) > 0):
        print("\nStored Reports:")
        for i, repo in enumerate(reportsInStorage):
            if not repo or repo.strip() == "":
                continue
            reportNameTyped = CreateTypedReportName(repo, i) # <-- fix to find the name of the report file
            print(reportNameTyped)

        print('Write the number of the report you wish to open from the list above. Or type "cancel" to cancel the task."')
        urlForRepo = input("Command|: ")
        urlToReturn = ""

        if urlForRepo.lower() == "cancel":  
            # CancelProgramDTF("User cancelled")
            return {"text": "User cancelled", "status": False}
        elif urlForRepo.isnumeric():
            index = int(urlForRepo) - 1
            if index >= 0 and index < len(reportsInStorage):
                urlToReturn = reportsInStorage[index] #translate the record to index
            #_
        else:
            print("Number not recognized.\n")
            urlToReturn = ""
        # print("repo?")
        # print(urlToReturn)
        # Retruing the reponame
        return urlToReturn
    else:
        print("No reports saved yet! A report will be generated and saved after you have analyzed a repository. Returning to menu.\n")
        return ""

# TLDR: This is a help-function. Some paths use a / and others use \, this function is used to more easily disect which symbol to use
def choose_separator(repoUrl):
    if "/" in repoUrl and "\\" not in repoUrl:
        return "/"
    if "\\" in repoUrl and "/" not in repoUrl:
        return "\\"
    # Hvis begge eller ingen finnes, velg forward slash som standard
    return "/"


#Output information to a output.txt file -- maybe change to report.txt for iteration1?
def RepoOutputDisplay(files, fileAndContributors, projectContributors, rFiles, repoName): # FIXME: Her trengs det en refac, mye uleselig kode grunnet chatDGBGT
    repoNameStr = str(repoName or "")
    # print(f"\n\\#/ after program is ran, here are the resulting lists for the repo '{repoNameStr}':")

    # ===== Files section =====
    output_lines = []

    # Normalize and print files info:
    if files is None:
        files = {}

    files_repr = []
    # Case A: files is a dict mapping filename -> FileData (or dict)
    if isinstance(files, dict):
        for fname, fobj in files.items():
            # fobj may be FileData or dict; handle both
            if fobj is None:
                fullpath = None
            elif hasattr(fobj, "fullpath"):
                fullpath = fobj.fullpath
            elif isinstance(fobj, dict):
                fullpath = fobj.get("fullpath")
            else:
                fullpath = str(fobj)
            files_repr.append(f"{fname} ({fullpath})" if fullpath else f"{fname}")
    # Case B: files is a list/tuple of FileData or strings
    elif isinstance(files, (list, tuple)):
        for entry in files:
            if isinstance(entry, str):
                files_repr.append(entry)
            elif hasattr(entry, "filename"):
                name = entry.filename
                fullpath = getattr(entry, "fullpath", None)
                files_repr.append(f"{name} ({fullpath})" if fullpath else name)
            elif isinstance(entry, dict):
                name = entry.get("filename") or entry.get("name") or str(entry)
                fullpath = entry.get("fullpath")
                files_repr.append(f"{name} ({fullpath})" if fullpath else name)
            else:
                files_repr.append(str(entry))
    else:
        # fallback: any other type -> stringify
        files_repr.append(str(files))

    output_lines.append("Files: " + ", ".join(files_repr) if files_repr else "Files: (none)")
    # print(output_lines[-1])

    # ===== Files and contributors =====
    output_lines.append("Files and their contributors:")
    # print(output_lines[-1])

    if not fileAndContributors:
        output_lines.append("  (no files with contributor info)")
        # print(output_lines[-1])
    else:
        for filename, obj in fileAndContributors.items():
            output_lines.append(f"\nFile data: {filename}")
            output_lines.append(f"\n - File Absolute Path: {obj.fullpath}")
            lengthOfComHashes = -1
            if (obj.commitHashes):
                lengthOfComHashes = len(obj.commitHashes)
            output_lines.append(f"\n - Amount of Commit hashes registered: { 'None' if lengthOfComHashes < 0 else lengthOfComHashes}")
            # output_lines.append(f"\n commithashsh: {obj.commitHashes}")
            # try:
            #     output_lines.append(f"\n - First hash: {obj.commitHashes[0]}, Last hash: {obj.commitHashes[len(obj.commitHashes)]}")
            # except(IndexError):
            #     print("false..")

            # Support dict-style and object-style for obj
            if isinstance(obj, dict):
                contributors = obj.get("contributors", [])
                commits = obj.get("commits")
            else:
                contributors = getattr(obj, "contributors", [])
                commits = getattr(obj, "commits", None)

            output_lines.append(f"  commits: {commits}")
            # print(f"File data: {filename}  commits: {commits}")
            for contributor in contributors or []:
                output_lines.append(f"    contributor: {contributor}")
                # print(f"    contributor: {contributor}")

    if not rFiles:
        output_lines.append("\n  (no R files  registered)")
    else:
        output_lines.append(f"\n **R files found:")

        for rF in rFiles:
            # ab_path = rF.fu
            # RfileName = ""
            # RfileName = FindRepoName(ab_path)
            output_lines.append(f"\n - R File \"{rF.filename}\" Absolute Path: {rF.fullpath}")
            
    # ===== Project contributors =====
    if projectContributors is None:
        projectContributors = []
    if isinstance(projectContributors, set):
        proj_str = ", ".join(sorted(projectContributors))
    elif isinstance(projectContributors, (list, tuple)):
        proj_str = ", ".join(projectContributors)
    else:
        proj_str = str(projectContributors)

    output_lines.append(f"\nAll contributors: {proj_str}")
    # print("All contributors:", proj_str)

    return "\n".join(output_lines)

def getChurnForAFile(repopath, firstCommit, lastCommit):
    metric = CodeChurn(path_to_repo=repopath,
                   from_commit=firstCommit,
                   to_commit=lastCommit)
    
    files_count = metric.count()
    return files_count

def normalize_windows_path(REPOURL: str) -> str:
    return str(Path(REPOURL).resolve())