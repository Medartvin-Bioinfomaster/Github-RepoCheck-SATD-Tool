from pydriller import Repository
# filter readmes? example data folder? (.rdata, .rds, r-markdown, .Rmnd)

# opt-in: ask users  what folders to loook throguh ( like R folder) - pydriller clones a whole repo, can we only download R-folder?

repositoryToInput = 'https://github.com/Medartvin-Bioinfomaster/Test-R-Data-Repo' # FIXME: remove / delete after a while, only a test repo!!

#Idea for these values: Create an interface or Dictionary containing them, so its easier to refer to them, and it gives them a title like: "ReturnData.files" ...
files = []
fileAndContributors = {} # an object containing multiple "file" objects. File.contributors should contain every user that has channged that file. Also it should contain how many commits it has been part of, amount of times changed in commits.
projectContributors = [] # a list that will contain all contributors from the git project. Include everyone who has ever commited changes. Idea: Put in loop during fetch - or after fetch, where you iterate through the file-object list? What is more efficient?
# issues = [] # list with amount of issues from the github. OBS: not implemented yet
foldersToInclude = []


def WriteRepoName(reposInStorage):

    if (reposInStorage and len(reposInStorage) > 0):
        print("\nStored repos:")
        for i, repo in enumerate(reposInStorage):
            lastlinkname = None
            if repo.__contains__('\\'):
                lastlinkname = repo.split("\\")
            else:
                lastlinkname = repo.split("/")
            linklength = len(lastlinkname)
            tag = "URL" if isUrl(repo) else "Local"
            print(f"- {str(i + 1)}: {lastlinkname[linklength - 1]} ({tag})")

    print("Write the repo url bellow. To load a saved repo, type the number from a stored repo above.")
    urlForRepo = input("Command|: ")
    urlToReturn = ""

    if urlForRepo.lower() == "st": 
        urlToReturn = repositoryToInput
    elif urlForRepo.lower() == "cancel":  
        CancelProgramDTF("User cancelled")
    elif urlForRepo.isnumeric():
        index = int(urlForRepo) - 1
        if index >= 0 and index < len(reposInStorage):
            urlToReturn = reposInStorage[index] #translate the record to index
        #_
    else:
        urlToReturn = urlForRepo
    print("repo?")
    print(urlToReturn)
    # Retruing the reponame
    return urlToReturn


#TODO: include a filter on the period you want to recieve commits for. You can choose to view them all or just a period of commits
# useDateFilter = input("Do you want to filter commits based on dates? ('yes/1' or 'no/0'):")

# if (useDateFilter == "yes" or useDateFilter == "0"):
#     print("TEST")
#     dateToUse = input("Write the date to filter from ('DD:MM:YYYY' format): ")
#     dates = dateToUse.split(":")


# continue using date or not

def isUrl(repolink):
    if (repolink.startswith('http://') or repolink.startswith('https://')):
        return True
    else:
        return False

def findRepo (repoUrl, cancelcommand=False):
    
    if cancelcommand == True:
        CancelProgramDTF("Canceled at RepoCheck.")
        return False
    
    repoOK = False
    if isUrl(repoUrl):
        print('Link URL is OK')
    else:
        print('Link is NOT a URL. Trying to access as a local path.')
        # Her kan du også implementere logikk for validering av lokal sti hvis nødvendig.

    try:
        for commit in Repository(repoUrl).traverse_commits():
            # Gjør noe med commit, for eksempel: print(commit)
            authortest = commit.author
            repoOK = True
            print("Found repo: " + str(repoUrl))
            break
    except Exception as e:
        print(f'Error accessing repository:')
        CancelProgramDTF("Error accessing local repository. e: ")
        repoOK = False

        # cancelProgram = True
        # return
        # remove the return for now, just make sure that a local repo can be picked up

    return repoOK

def includeFolders ():
    endSection = False
    print("Write what folders and files you would like to include. \nWrite a name of a folder in the repo and hit 'enter' to add it. Type +f and a name to add single files. Type -r to remove an item from the view.")
    
    while endSection == False and cancelProgram == False:
        print("Current selection: " + foldersToInclude)
        folderInput = input("Write what folders and files you would like to include")

        if (folderInput.lower() == "cancel"):
            CancelProgramDTF("User canceled at file inclusion section.")

        elif (folderInput.lower() == "done"):
            endSection = True

        elif (folderInput.lower().__contains__("+f")):
            foldersToInclude.append( "(F)" + folderInput.removeprefix("+f ") )
            #FIXME: her er det ikke implementert å bytte ut +f med denne (F) stringen i stedet. Dette bør legges til asap

        elif (folderInput.lower().__contains__("-r")):
            foldersToInclude.remove(folderInput)
            #TODO: implement feedback to user if folder/file isn't found

        else:
            foldersToInclude.append(folderInput)

    # foldersToInclude

def saveTheRepoUrlQuestion(repo, reposInStorage):
    print("sadukmos")
    print(reposInStorage)
    print(repo)

    if (repo == "" or repo == None):
        print("Error: repo name is empty")
        CancelProgramDTF("Error: Repo name is empty")
        return
    # if repo in reposInStorage:
        # print("RepoURL from storage detected, continuing...")
    # else:
    if repo not in reposInStorage:
        print("The Repo Url or Local path is valid, want to store the repo? (Yes / 1 or No / 0)")
        saveRepo = input("Command|: ")

        if (saveRepo.strip().lower() == "cancel"):
            print("Canceling program.")
            CancelProgramDTF("User canceled progam at saving stage")
        elif (saveRepo.lower() == "yes" or saveRepo == "1"):
            print("Saving repo...")
            writeRepoToStorage(repo)
            #TODO: Implement the file saving of the repository
        elif (saveRepo.lower() == "no" or saveRepo == "0"):
            print("Continuing without saving")
        else:
            print("Command not recognized. Continuing without saving")


#TODO: find issues from github using Git API???

def write_to_outputfile(output_string):
    with open(outputFilePlacement, 'w') as fil:
        fil.write(output_string)
        print("Written to outputfile success.")

# TODO: FIks repostorage

def readRepoStorageFile():
    print("Reading Storage..")
    storedList = []
    itemnumber = 1
    terminateLoop = False

    try:
        with open(path, 'r', encoding='utf-8') as storage:
            print("Storage exists.")
    except FileNotFoundError:
        print(f"Storage not found. Creating a new one")
        with open(path, 'w', encoding='utf-8') as storage:  # creates the file
            pass
        storedList = []

    with open(path, 'r') as storage:
        storedList = [line.rstrip('\n') for line in storage]
        itemnumber = len(storedList)
        # spot = storage.readline()

        # while (spot != "" and terminateLoop == False):
        #     storedList.append(spot.strip())
        #     # spot = storage.readline
        #     itemnumber += 1
        #     spot = storage.readline()
        #     if (itemnumber > 99): #loop shouldnt loop over 99 items anyway, cancels automatically if there is a bug or something. Avoids infinite loop
        #         terminateLoop = True

    print(storedList)
    print(f"Amount of items read: {itemnumber}")
    
    #Returns data as a dictionary
    return {"repos": storedList, "count": itemnumber}
#_

def writeRepoToStorage(repo):
    repo = repo.strip()
    if not repo:
        return False
    with open(path, 'a', encoding='utf-8') as f:
        f.write('\n' + repo)
        print("Should have stored the repo in storeage now")
    #_
    print("Should have stored the repo in storeage now")
    return True
#_

def CancelProgramDTF(cancelMessage: str) -> None:
    global cancelProgram, reasonForCancel
    cancelProgram = True
    reasonForCancel = reasonForCancel + "\n" + cancelMessage  # safe now


# def write_to_repoStorage(reponame):
#     with open("repostorage.txt", 'w') as fil:
#         fil.write(output_string)
#         print("Written to outputfile success.")

# Main file fetch loop
def RepoFetcher(repoUrl, cancelcommand, isLocal = False):

    if (cancelcommand == True):
        CancelProgramDTF("Program already cancelled. Cancelcommand set true. Not running.")
        return

    print("START FETCH: fetching from \'" + repoUrl + "\'")

    for commit in Repository( repoUrl ).traverse_commits():
        repoName = commit.project_name
        print("This is the repo name###: " + repoName)
        print("Commit #" + commit.hash + "\nMessage: " + commit.msg)
        print("Author: " + commit.author.name)

        print("Files changed: ")

        for file in commit.modified_files: 

            if file.filename not in files:
                print("*    Add unique file to list")
                files.append(file.filename)

            if file.filename not in fileAndContributors:
                print("*-   unique file will be added")
                fileDictionary = {
                    "filename:" : file.filename,
                    "contributors": [],
                    "commits" : 0,
                }                
                fileDictionary["contributors"].append(commit.author.name)
                fileDictionary["commits"] += 1
                fileAndContributors[file.filename] = fileDictionary
                if commit.author.name not in projectContributors:
                    projectContributors.append(commit.author.name)
            else:
                fileAndContributors.get(file.filename)
                existingFileDict = fileAndContributors[file.filename]
                existingFileDict["commits"] += 1
                if (commit.author.name not in existingFileDict["contributors"]):
                    existingFileDict["contributors"].append(commit.author.name)
                
                if commit.author.name not in projectContributors:
                    projectContributors.append(commit.author.name)

            print(' \\' + file.filename, ' has changed')
        
        print('*End\n')


# Output the different Repo data
def RepoOutputDisplay():
    outputString = ""

    print("\n\\#/ after program is ran, here are the resulting lists for the repo '" + repoName + "':")

    print(files)

    outputString = "Files: " + ", ".join(files)
    print(fileAndContributors)

    outputString += "\nFiles and their contributors: "

    for filename, obj in fileAndContributors.items():
        print(filename)
        outputString += "\nFile data: " + filename
        # Append contributor information
        for contributor in obj["contributors"]:
            print("contributor: " + contributor + ' - commits :', obj["commits"])
            outputString += f": contributor: {contributor} - commits :{obj['commits']}, "  # Use f-strings for cleaner formatting

    if isinstance(projectContributors, list):
        projectContributorsString = ', '.join(projectContributors)  # Join if it's a list
    else:
        projectContributorsString = str(projectContributors)  # Ensure it's a string

    print(projectContributors)  # Print to console
    outputString += "\nAll contributors: " + projectContributorsString

    write_to_outputfile(outputString)





# HERE IS THE MAIN LOOP // MOVE TO MAIN LATER

repoName = ""
path = 'repostorage.txt'

cancelProgram = False
reasonForCancel = ""

storageBucket = readRepoStorageFile()

REPOURL = WriteRepoName(storageBucket["repos"])

repofound = findRepo( REPOURL, cancelProgram ) #check if the url is valid

if repofound == False:
    CancelProgramDTF("Repo wasnt found")

if cancelProgram != True:
    saveTheRepoUrlQuestion( REPOURL, storageBucket["repos"] )

# if cancelProgram != True:
#     includeFolders()

outputFilePlacement = "output.txt"



# CancelProgramDTF("STAGED: set to cancel before fetching repository.") #REMOVE WHEN YOU WANT TO CONTINUE THE PROGRAM



# Main loop

if (cancelProgram == False):
    RepoFetcher( REPOURL, cancelProgram, False ) # OBS, set isLocal to FALSE by default, its not implemented yet, may not need to be
    print("Here the program should have started \__")
else:
    print("Task was canceled. \nThis is the full log")
    print(reasonForCancel)