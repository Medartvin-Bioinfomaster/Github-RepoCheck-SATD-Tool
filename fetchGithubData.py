from pydriller import Repository

from storageHandler import write_to_outputfile, readRepoStorageFile, writeRepoToStorage

from tools import FindRepoName, CreateTypedRepoName, isUrl, WriteRepoName, choose_separator

from dataClasses import RepoDetails, FileData, RFileData

from typing import Dict

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
    repositoryName = FindRepoName(repoUrl)
    filesToReturn = {}
    r_files_data_list: Dict[RFileData] = {} # Rfiles data
    all_contributors = []

    firstCommitHash = ""
    lastCommitHash = ""

    listOfAbsolutePaths = []

    startAnalyzation = time.time()

    if (cancelcommand == True):
        return {"text": "Program already cancelled. Cancelcommand set true. Not running.", "status": False}

    print("START FETCH: fetching from \'" + repositoryName + "\'")

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
            filename = file.filename

            fileObj = FileData(filename, absolute_path) #creating a basic dataclass for the file

            if (absolute_path not in listOfAbsolutePaths and filename.lower().endswith(".r")): #check that the full path of a file is NOT already in this list
                # add the files to the "keeping count" list
                listOfAbsolutePaths.append(absolute_path)
                filesToReturn[filename] = fileObj

                # Handle R file data and collect

                churn_stats = {"added": 0, "deleted": 0, "commits": 0, "loc": 0}
                churn_stats["added"] = file.added_lines
                churn_stats["deleted"] = file.deleted_lines
                churn_stats["commits"] = 1
                churn_stats["loc"] = 1
                
                r_file = RFileData(filename, 
                                   absolute_path, 
                                   churn_stats, 
                                   commit.author.name, 
                                   1, 
                                   commit.hash)
                
                # adding the final object to the list
                r_files_data_list[filename] = r_file

                if commit.author.name not in all_contributors: # add contributor to its own list
                    all_contributors.append(commit.author.name)

            else: # if the file has been logged, update data
                if (filename.lower().endswith(".r")):

                    existing_r_file: RFileData = r_files_data_list[filename]
                    existing_r_file.addCommit()
                    existing_r_file.addCommitHash(commit.hash)
                    # add only unique contributor
                    if commit.author.name not in existing_r_file.contributors:
                        existing_r_file.addContributor(commit.author.name)
                    # add unique contributor to the count list
                    if commit.author.name not in all_contributors:
                        all_contributors.append(commit.author.name)

        # print(f'Commits read: {commitsTraveresedCounter}, total files iterated: {filesTraveresedCounter}')

    endAnalyzation = time.time()
    print(f"\nTime spent fetching: {endAnalyzation - startAnalyzation} seconds")

    return {
            "repositoryName": repositoryName, 
            "files": filesToReturn, 
            "r_files": r_files_data_list, 
            "projectContributors": all_contributors, 
            "firstCommitHash": firstCommitHash, 
            "lastCommitHash": lastCommitHash
            }
