from storageHandler import write_to_outputfile, readRepoStorageFile, writeRepoToStorage
from tools import FindRepoName, CreateTypedRepoName, isUrl, WriteRepoName
from fetchGithubData import RepoFetcher, saveTheRepoUrlQuestion, findRepo

# Function that changes the variables that handles the program stopping functions
def CancelProgramDTF(cancelMessage: str) -> None:
    global cancelProgram, reasonForCancel
    cancelProgram = True
    reasonForCancel = reasonForCancel + "\n" + cancelMessage  # safe now

#Output information to a output.txt file -- maybe change to report.txt for iteration1?
def RepoOutputDisplay(files, fileAndContributors, projectContributors, repoName):
    repoNameStr = str(repoName or "")
    print(f"\n\\#/ after program is ran, here are the resulting lists for the repo '{repoNameStr}':")

    # Safe representation of files
    if files is None:
        files = {}
    print(files)

    output_lines = []
    files_str = ", ".join(files) if isinstance(files, (list, tuple)) else str(files)
    output_lines.append(f"Files: {files_str}")

    output_lines.append("Files and their contributors:")

    if not fileAndContributors:
        output_lines.append("  (no files)")
    else:
        for filename, obj in fileAndContributors.items():
            output_lines.append(f"\nFile data: {filename}")
            # Support both dict-style and object-style (FileContributors)
            if isinstance(obj, dict):
                contributors = obj.get("contributors", [])
                commits = obj.get("commits", None)
            else:
                # assume object with attributes .contributors and .commits
                contributors = getattr(obj, "contributors", [])
                commits = getattr(obj, "commits", None)

            # Print summary once per file (commits apply to file)
            output_lines.append(f"  commits: {commits}")
            for contributor in contributors or []:
                output_lines.append(f"    contributor: {contributor}")

    # Project contributors: accept list or set
    if projectContributors is None:
        projectContributors = []
    if isinstance(projectContributors, (list, tuple, set)):
        proj_str = ", ".join(sorted(projectContributors)) if isinstance(projectContributors, set) else ", ".join(projectContributors)
    else:
        proj_str = str(projectContributors)

    output_lines.append(f"\nAll contributors: {proj_str}")

    # Print to console
    for line in output_lines:
        print(line)

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
        readyToCont = input("Command|: ")
        if (readyToCont.lower() == "stop" or readyToCont == "0"):
            CancelProgramDTF("User stopped program before analyzation.")
    
    # Main loop

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
            repoName = out.get("repoName")
        outputFetchingString = RepoOutputDisplay(files, fileAndContributors, projectContributors, repoName)
        write_to_outputfile(outputFilePlacement, outputFetchingString)

    else:
        print("Task was canceled. \nThis is the full log")
        print(reasonForCancel)

# run main loop
main_loop()