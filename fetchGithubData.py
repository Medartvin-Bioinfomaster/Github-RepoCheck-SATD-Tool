from pydriller import Repository

from storageHandler import write_to_outputfile, readRepoStorageFile, writeRepoToStorage

from tools import FindRepoName, CreateTypedRepoName, isUrl, WriteRepoName, choose_separator

from dataClasses import RepoDetails, FileContributors, FileData, RFileData

import time

# filter readmes? example data folder? (.rdata, .rds, r-markdown, .Rmnd)

# opt-in: ask users  what folders to loook throguh ( like R folder) - pydriller clones a whole repo, can we only download R-folder?

#Idea for these values: Create an interface or Dictionary containing them, so its easier to refer to them, and it gives them a title like: "ReturnData.files" ...





#TODO: include a filter on the period you want to recieve commits for. You can choose to view them all or just a period of commits
# useDateFilter = input("Do you want to filter commits based on dates? ('yes/1' or 'no/0'):")

# if (useDateFilter == "yes" or useDateFilter == "0"):
#     print("TEST")
#     dateToUse = input("Write the date to filter from ('DD:MM:YYYY' format): ")
#     dates = dateToUse.split(":")


# continue using date or not

#File should be called RepoHandler? Since Main will call on functions from other classes or tools, this "repoFetcher" class acts more
# as the manager for handling and fetching from a repository

def findRepo (repoUrl, cancelcommand=False):
    
    if cancelcommand == True:
        # CancelProgramDTF("Canceled at RepoCheck.")
        return {"text": "Canceled at RepoCheck.", "status": False}
    
    repoOK = False

    printFeedback = ""

    if isUrl(repoUrl):
        printFeedback = 'Link URL is OK'
    else:
        printFeedback = 'Link is NOT a URL. Trying to access as a local path.'
        # Her kan du også implementere logikk for validering av lokal sti hvis nødvendig.

    try:
        for commit in Repository(repoUrl).traverse_commits():
            # Gjør noe med commit, for eksempel: print(commit)

            repoName = commit.project_name
            printFeedback += "\nThis is the repo name###: " + repoName
            # print("Commit #" + commit.hash + "\nMessage: " + commit.msg)
            repoOK = True
            printFeedback += f"\nFound repo \"{repoName}\": {str(repoUrl)}"
            break
    except Exception as e:
        print(f'Error accessing repository:')
        # CancelProgramDTF("Error accessing local repository. e: ")
        return {"text": "Error accessing local repository. e: ", "status": False}
        repoOK = False

        # cancelProgram = True
        # return
        # remove the return for now, just make sure that a local repo can be picked up

    return repoOK


# TODO: Implement this folder opt-in system to the program
# def includeFolders ():
#     endSection = False
#     print("Write what folders and files you would like to include. \nWrite a name of a folder in the repo and hit 'enter' to add it. Type +f and a name to add single files. Type -r to remove an item from the view.")
    
#     while endSection == False and cancelProgram == False:
#         print("Current selection: " + foldersToInclude)
#         folderInput = input("Write what folders and files you would like to include")

#         if (folderInput.lower() == "cancel"):
#             # CancelProgramDTF("User canceled at file inclusion section.")
#             return {"text": "User canceled at file inclusion section.", "status": False}

#         elif (folderInput.lower() == "done"):
#             endSection = True

#         elif (folderInput.lower().__contains__("+f")):
#             foldersToInclude.append( "(F)" + folderInput.removeprefix("+f ") )
#             #FIXME: her er det ikke implementert å bytte ut +f med denne (F) stringen i stedet. Dette bør legges til asap

#         elif (folderInput.lower().__contains__("-r")):
#             foldersToInclude.remove(folderInput)
#             #TODO: implement feedback to user if folder/file isn't found

#         else:
#             foldersToInclude.append(folderInput)

    # foldersToInclude

def saveTheRepoUrlQuestion(repo, reposInStorage, path):
    # print("sadukmos")
    # print(reposInStorage)
    # print(repo)
    print("")

    if (repo == "" or repo == None):
        print("Error: repo name is empty")
        # CancelProgramDTF("Error: Repo name is empty")
        return {"text": "Error: Repo name is empty", "status": False}
    # if repo in reposInStorage:
        # print("RepoURL from storage detected, continuing...")
    # else:
    if repo not in reposInStorage:
        print("The Repo Url or Local path is valid, want to store the repo? (Yes / 1 or No / 0)")
        saveRepo = input("Command|: ")

        if (saveRepo.strip().lower() == "cancel"):
            print("Canceling program.")
            # CancelProgramDTF("User canceled progam at saving stage")
            return {"text": "User canceled progam at saving stage", "status": False}
        elif (saveRepo.lower() == "yes" or saveRepo == "1"):
            print("Saving repo...")
            writeRepoToStorage(repo, path)
            #TODO: Implement the file saving of the repository
        elif (saveRepo.lower() == "no" or saveRepo == "0"):
            print("Continuing without saving")
        else:
            print("Command not recognized. Continuing without saving")


#TODO: find issues from github using Git API???

# Main file fetch loop - isLocal tag not implemented yet, probably not a problem right?
def RepoFetcher(repoUrl, cancelcommand, isLocal = False):

    #TODO: change of file return. We only need a metric for the amount of files + commits in the repo. 
    # Otherwise, R files and creating a connection between an R file and its contributors and commits can be nice
    # potentially we can also create a general connection from contributors to other files in the system, if a specific contributor is tied to alot of SATD already
    filesToReturn = {}
    fileAndContributors = {}
    projectContributors = []
    rFilesToUse = [] #R only files

    firstCommitHash = ""
    lastCommitHash = ""

    listOfAbsolutePaths = []

    repoName = "" # FIXME: Unnødvendig??

    fileTagsToInclude = "R" #just a placeholder for now

    startAnalyzation = time.time()
 

    if (cancelcommand == True):
        # CancelProgramDTF("Program already cancelled. Cancelcommand set true. Not running.")
        return {"text": "Program already cancelled. Cancelcommand set true. Not running.", "status": False}

    print("START FETCH: fetching from \'" + repoUrl + "\'")

    comTraveresed = 0
    filesTraversed = 0

    for commit in Repository( repoUrl ).traverse_commits(): # kan endres til traverse files?
        if repoName == "":
            repoName = commit.project_name
        # print("This is the repo name###: " + repoName)
        # print("Commit #" + commit.hash + "\nMessage: " + commit.msg)
        # print("Author: " + commit.author.name)
        # print(f"Is in Main branch?: {commit.in_main_branch}")
        # print("Branch name: " + Repository.)
        # print(f"Can we find total commits? {Repository.}")

        if (firstCommitHash == ""):
            firstCommitHash = commit.hash
        lastCommitHash = commit.hash

        comTraveresed += 1

        print("Analyzing github ...")

        for file in commit.modified_files: 

            filesTraversed += 1

            relative = file.new_path or file.old_path
            symbol = choose_separator(repoUrl)
            absolute = repoUrl + symbol + relative
            fileObj = FileData(file.filename, absolute)
            # print("Here are the absolutes lmao:")
            # print(absolute)
            # print("\nN\nN\nN")
            if (absolute not in listOfAbsolutePaths): #check that the full path of a file is NOT already in this list
                listOfAbsolutePaths.append(absolute)
                filesToReturn[file.filename] = fileObj

                if file.filename.lower().endswith(".r"): # CHECKS SPECIFICALLY R FILES -->
                    # rFilesToUse.append(file.filename) # legger til .R filer til folder, fullpath
                    churn_stats = {"added": 0, "deleted": 0, "commits": 0, "loc": 0}
                    # path = file.new_path.replace("\\", "/") if file.new_path else None
                    churn_stats["added"] = file.added_lines
                    churn_stats["deleted"] = file.deleted_lines
                    churn_stats["commits"] = 1
                    churn_stats["loc"] = 1
                    newRFile = RFileData(file.filename, absolute, churn_stats)
                    rFilesToUse.append(newRFile) # legger inn fullpath, sjekk at navn er riktig etc.

                # still under the "if path is not registered" if-statement
                fileDictionary = FileContributors(file.filename, absolute, commit.author.name, 1, commit.hash)
                fileAndContributors[file.filename] = fileDictionary
                if commit.author.name not in projectContributors:
                    projectContributors.append(commit.author.name)

            else: #Otherwise, update data in file+Contributors
                existing = fileAndContributors[file.filename]
                existing.addCommit()
                # existing.addContributor(commit.author.name)
                existing.addCommitHash(commit.hash)

                if commit.author.name not in existing.contributors:
                    existing.addContributor(commit.author.name)

                # add contributor to the counter of total cont- in the project, if not there already
                if commit.author.name not in projectContributors:
                    projectContributors.append(commit.author.name)
            # print(' \\' + file.filename, ' has changed')

                    
            # if (file.filename not in filesToReturn) or (absolute not in rFilesToUse):
                # print("*    Add unique file to list")
                
                # filesToReturn - list looks like this:
                # {
                #   filename: {
                #               filename: "filename.filetype",
                #               fullpath: "path/path/filename.filetype"
                #             },
                #   ...
                # }
                    



        print(f'Commits read: {comTraveresed}, files iterated: {filesTraversed}')
    
    endAnalyzation = time.time()
    print(f"\nTime spent fetching: {endAnalyzation - startAnalyzation} seconds")

    # filesToReturn = []
    # fileAndContributors = {}
    # projectContributors = [] 
    return {"files": filesToReturn, "fileAndContributors": fileAndContributors, "projectContributors": projectContributors, "rFilesToUse": rFilesToUse, "repoName": repoName, "firstCommitHash": firstCommitHash, "lastCommitHash": lastCommitHash}
