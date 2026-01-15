from pydriller import Repository

from storageHandler import write_to_outputfile, readRepoStorageFile, writeRepoToStorage

from tools import FindRepoName, CreateTypedRepoName, isUrl, WriteRepoName, choose_separator

from dataClasses import RepoDetails, FileContributors, FileData
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
    if isUrl(repoUrl):
        print('Link URL is OK')
    else:
        print('Link is NOT a URL. Trying to access as a local path.')
        # Her kan du også implementere logikk for validering av lokal sti hvis nødvendig.

    try:
        for commit in Repository(repoUrl).traverse_commits():
            # Gjør noe med commit, for eksempel: print(commit)

            repoName = commit.project_name
            print("This is the repo name###: " + repoName)
            print("Commit #" + commit.hash + "\nMessage: " + commit.msg)
            repoOK = True
            print("Found repo: " + str(repoUrl))
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

def saveTheRepoUrlQuestion(repo, reposInStorage):
    print("sadukmos")
    print(reposInStorage)
    print(repo)

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
            writeRepoToStorage(repo)
            #TODO: Implement the file saving of the repository
        elif (saveRepo.lower() == "no" or saveRepo == "0"):
            print("Continuing without saving")
        else:
            print("Command not recognized. Continuing without saving")


#TODO: find issues from github using Git API???

# Main file fetch loop
def RepoFetcher(repoUrl, cancelcommand, isLocal = False):

    filesToReturn = {}
    fileAndContributors = {}
    projectContributors = []
    rFilesToUse = [] #R only files

    repoName = "" # FIXME: Unnødvendig??

    fileTagsToInclude = "R" #just a placeholder for now
 

    if (cancelcommand == True):
        # CancelProgramDTF("Program already cancelled. Cancelcommand set true. Not running.")
        return {"text": "Program already cancelled. Cancelcommand set true. Not running.", "status": False}

    print("START FETCH: fetching from \'" + repoUrl + "\'")

    for commit in Repository( repoUrl ).traverse_commits(): # kan endres til traverse files?
        repoName = commit.project_name
        print("This is the repo name###: " + repoName)
        print("Commit #" + commit.hash + "\nMessage: " + commit.msg)
        print("Author: " + commit.author.name)

        print("Analyzing github ...")

        for file in commit.modified_files: 

            relative = file.new_path or file.old_path
            symbol = choose_separator(repoUrl)
            absolute = repoUrl + symbol + relative
            fileObj = FileData(file.filename, absolute)
            # print("Here are the absolutes lmao:")
            # print(absolute)
            # print("\nN\nN\nN")

            if file.filename not in filesToReturn:
                # print("*    Add unique file to list")
                filesToReturn[file.filename] = fileObj
                if file.filename.lower().endswith(".r"):
                    # rFilesToUse.append(file.filename) # legger til .R filer til folder, fullpath
                    rFilesToUse.append(absolute) # legger inn fullpath, sjekk at navn er riktig etc.
                    

            if file.filename not in fileAndContributors:
                # print("*-   unique file will be added")
                fileDictionary = FileContributors(file.filename, absolute, commit.author.name, 1)
                # fileDictionary["contributors"].append(commit.author.name)
                # fileDictionary["commits"] += 1
                fileAndContributors[file.filename] = fileDictionary ## Fungerer CLASS???
                if commit.author.name not in projectContributors:
                    projectContributors.append(commit.author.name)
            else:
                existing = fileAndContributors[file.filename]
                existing.commits += 1
                if commit.author.name not in existing.contributors:
                    existing.contributors.append(commit.author.name)
                if commit.author.name not in projectContributors:
                    projectContributors.append(commit.author.name)
            # print(' \\' + file.filename, ' has changed')
        
        print('*End\n')
    
    # filesToReturn = []
    # fileAndContributors = {}
    # projectContributors = [] 
    return {"files": filesToReturn, "fileAndContributors": fileAndContributors, "projectContributors": projectContributors, "rFilesToUse": rFilesToUse, "repoName": repoName}
