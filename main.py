from storageHandler import write_to_outputfile, readRepoStorageFile, writeRepoToStorage
from tools import FindRepoName, CreateTypedRepoName, isUrl, WriteRepoName
from fetchGithubData import RepoFetcher, saveTheRepoUrlQuestion, findRepo
from fileAnalyzer import scan_repo_and_save_reports, analyze_file

# Function that changes the variables that handles the program stopping functions
def CancelProgramDTF(cancelMessage: str) -> None:
    global cancelProgram, reasonForCancel
    cancelProgram = True
    reasonForCancel = reasonForCancel + "\n" + cancelMessage  # safe now

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
        output_lines.append("  (no R files with registered)")
    else:
        output_lines.append(f"\n **R files found:")

        for ab_path in rFiles:
            RfileName = FindRepoName(ab_path)
            output_lines.append(f"\n - R File \"{RfileName}\" Absolute Path: {ab_path}")
            
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

def main_loop():
    # Define Variables to store information that is picked up
    files = {}
    fileAndContributors = {} # an object containing multiple "file" objects. File.contributors should contain every user that has channged that file. Also it should contain how many commits it has been part of, amount of times changed in commits.
    projectContributors = [] # a list that will contain all contributors from the git project. Include everyone who has ever commited changes. Idea: Put in loop during fetch - or after fetch, where you iterate through the file-object list? What is more efficient?
    # issues = [] # list with amount of issues from the github. OBS: not implemented yet
    foldersToInclude = []
    repoName = ""
    print("#/3#/3 Welcome to the SATD Tool 3\\#3\\#")

    #stage 1
    print("What repository do you want to analyze?")

    # HERE IS THE MAIN LOOP // MOVE TO MAIN LATER

    path = 'repostorage.txt'

    cancelProgram = False
    reasonForCancel = ""

    storageBucket = readRepoStorageFile(path)

    REPOURL = WriteRepoName(storageBucket["repos"])

    repofound = findRepo( REPOURL, cancelProgram ) #check if the url is valid

    if repofound == False:
        CancelProgramDTF("Repo wasnt found")

    if cancelProgram != True:
        saveTheRepoUrlQuestion( REPOURL, storageBucket["repos"] )

    # if cancelProgram != True:
    #     includeFolders()

    outputFilePlacement = "output.txt" # Fjern etterhvert, er kun for å teste at GitFetching gikk OK

    # CancelProgramDTF("STAGED: set to cancel before fetching repository.") #REMOVE WHEN YOU WANT TO CONTINUE THE PROGRAM

    if (cancelProgram != True):
        print('System is ready to analyze the github \"' + FindRepoName(REPOURL) + '\". Type any key + ENTER to continue, or type "stop" or 0 to stop the program. ')
        readyToContinue = input("Command|: ")
        if (readyToContinue.lower() == "stop" or readyToContinue == "0"):
            CancelProgramDTF("User stopped program before analyzation.")
    
    # Loop where Fetch happens
    if (cancelProgram == False):
        print("Here the program should have started \__")
        out = RepoFetcher( REPOURL, cancelProgram, False ) # OBS, set isLocal to FALSE by default, its not implemented yet, may not need to be
        if (out.get("status")):
            CancelProgramDTF("Something went wrong:", out.get("text"))
        else:
            # ingen feil — hent feltene med .get for å unngå KeyError
            files = out.get("files", [])
            fileAndContributors = out.get("fileAndContributors", {})
            projectContributors = out.get("projectContributors", [])
            RFilesToAnalyze = out.get("rFilesToUse", [])
            repoName = out.get("repoName")
        outputFetchingString = RepoOutputDisplay(files, fileAndContributors, projectContributors, RFilesToAnalyze, repoName)
        write_to_outputfile(outputFilePlacement, outputFetchingString) #outputer det fetcher mottar, fjern senere eller bruk i report.txt på et vis

    else:
        print("Task was canceled. \nThis is the full log")
        print(reasonForCancel)

    # one check before analyzing files, to avoid a long loop :)
    if (cancelProgram != True):
        print('Github analyzation complete! You can begin the file analyzation. Type any key + ENTER to continue, or type "stop" or 0 to stop the program. ')
        readyToContinue = input("Command|: ")
        if (readyToContinue.lower() == "stop" or readyToContinue == "0"):
            CancelProgramDTF("User stopped program before analyzation.")





    #Loop through files and analyze them:

    # ---- TODO: Implementer FileAnalyzer her 👈👈👈👈
    print("Running file analyzer...")

    #file analyzer code here:
    
    outputFileAnalyzeString = "Here is the rundown of the Total Findings:"
    # for key, fobj in files.items():
    for rF in RFilesToAnalyze:
        # print("-empty for now-")
        #return --> total_findings, files_with_satd, reports
        outputFileAnalyzeString += f"\nAnalyze results for File: {FindRepoName(rF)}" # <-- her burde det egt het FindFILEName??

        # total_findings, files_with_satd, reports = scan_repo_and_save_reports(repo_path=rF, output_dir="dirTestFileAnalyze", repo_name=repoName) # <-- forsøker å analysere Filene
        total_findings, files_with_satd, reports = analyze_file(repo_path=REPOURL, file_path=rF, output_dir="dirTestFileAnalyze", repo_name=repoName) # <-- forsøker å analysere Filene
        outputFileAnalyzeString += f"\nTotal findings: {total_findings}\nFiles that contain SATD: {files_with_satd}\nReports: {reports}\n"

    # total_findings, files_with_satd, reports = scan_repo_and_save_reports(repo_path=REPOURL, output_dir="dirTestFileAnalyze", repo_name=repoName) # <-- forsøker å analysere Filene

    write_to_outputfile("fileAnalyzetest.txt", outputFileAnalyzeString)



    print("If everything went well, the findings should have been printed to a file in dir \"dirTestFileAnalyze\"")

# run main loop
main_loop()