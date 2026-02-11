from pydriller import Repository

from storageHandler import write_to_outputfile, readRepoStorageFile, writeRepoToStorage

from tools import FindRepoName, CreateTypedRepoName, isUrl, WriteRepoName, choose_separator

from dataClasses import RepoDetails, FileContributors, FileData, RFileData

import time

def findRepo (repoUrl, cancelcommand=False):
    
    if cancelcommand == True:
        return {"text": "Canceled at RepoCheck.", "status": False}
    
    repoOK = False

    printFeedback = ""

    if isUrl(repoUrl):
        printFeedback = 'Link URL is OK'
    else:
        printFeedback = 'Link is NOT a URL. Trying to access as a local path.'

    try:
        for commit in Repository(repoUrl).traverse_commits():
            repoName = commit.project_name
            printFeedback += "\nThis is the repo name###: " + repoName
            repoOK = True
            printFeedback += f"\nFound repo \"{repoName}\": {str(repoUrl)}"
            break
    except Exception as e:
        print(f'Error accessing repository:')
        return {"text": "Error accessing local repository. e: ", "status": False}
        repoOK = False

    return repoOK

def saveTheRepoUrlQuestion(repo, reposInStorage, path):

    if (repo == "" or repo == None):
        print("Error: repo name is empty")
        return {"text": "Error: Repo name is empty", "status": False}
    if repo not in reposInStorage:
        print("The Repo Url or Local path is valid, want to store the repo? (Yes / 1 or No / 0)")
        saveRepo = input("Command|: ")

        if (saveRepo.strip().lower() == "cancel"):
            print("Canceling program.")
            return {"text": "User canceled progam at saving stage", "status": False}
        elif (saveRepo.lower() == "yes" or saveRepo == "1"):
            print("Saving repo...")
            writeRepoToStorage(repo, path)
        elif (saveRepo.lower() == "no" or saveRepo == "0"):
            print("Continuing without saving")
        else:
            print("Command not recognized. Continuing without saving")


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

    startAnalyzation = time.time()
 

    if (cancelcommand == True):
        return {"text": "Program already cancelled. Cancelcommand set true. Not running.", "status": False}

    print("START FETCH: fetching from \'" + repoUrl + "\'")

    commitsTraveresedCounter = 0
    filesTraveresedCounter = 0 # remember, it can be old versions of files, now deleted files etc. counter of files traveresed during every commit

    print("Analyzing github ...")
    
    for commit in Repository( repoUrl ).traverse_commits(): # change / possible to change to traversing files?
        if (firstCommitHash == ""):
            firstCommitHash = commit.hash
        lastCommitHash = commit.hash

        commitsTraveresedCounter += 1

        for file in commit.modified_files: 

            filesTraveresedCounter += 1

            relative_filepath = file.new_path or file.old_path
            symbol = choose_separator(repoUrl)
            absolute_path = repoUrl + symbol + relative_filepath
            fileObj = FileData(file.filename, absolute_path)

            if (absolute_path not in listOfAbsolutePaths): #check that the full path of a file is NOT already in this list
                listOfAbsolutePaths.append(absolute_path)
                filesToReturn[file.filename] = fileObj

                if file.filename.lower().endswith(".r"): # CHECKS SPECIFICALLY R FILES -->
                    churn_stats = {"added": 0, "deleted": 0, "commits": 0, "loc": 0}
                    churn_stats["added"] = file.added_lines
                    churn_stats["deleted"] = file.deleted_lines
                    churn_stats["commits"] = 1
                    churn_stats["loc"] = 1
                    newRFile = RFileData(file.filename, absolute_path, churn_stats)
                    rFilesToUse.append(newRFile)

                # still under the "if path is not registered" if-statement
                fileDictionary = FileContributors(file.filename, absolute_path, commit.author.name, 1, commit.hash)
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

        print(f'Commits read: {commitsTraveresedCounter}, total files iterated: {filesTraveresedCounter}')
    
    endAnalyzation = time.time()
    print(f"\nTime spent fetching: {endAnalyzation - startAnalyzation} seconds")

    return {"files": filesToReturn, "fileAndContributors": fileAndContributors, "projectContributors": projectContributors, "rFilesToUse": rFilesToUse, "repoName": repoName, "firstCommitHash": firstCommitHash, "lastCommitHash": lastCommitHash}
