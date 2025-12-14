from storageHandler import write_to_outputfile, readRepoStorageFile, writeRepoToStorage
from tools import FindRepoName, CreateTypedRepoName, isUrl, WriteRepoName
from fetchGithubData import RepoFetcher, saveTheRepoUrlQuestion, findRepo

# Define Variables to store information that is picked up
files = []
fileAndContributors = {} # an object containing multiple "file" objects. File.contributors should contain every user that has channged that file. Also it should contain how many commits it has been part of, amount of times changed in commits.
projectContributors = [] # a list that will contain all contributors from the git project. Include everyone who has ever commited changes. Idea: Put in loop during fetch - or after fetch, where you iterate through the file-object list? What is more efficient?
# issues = [] # list with amount of issues from the github. OBS: not implemented yet
foldersToInclude = []
repoName = ""


# Function that changes the variables that handles the program stopping functions
def CancelProgramDTF(cancelMessage: str) -> None:
    global cancelProgram, reasonForCancel
    cancelProgram = True
    reasonForCancel = reasonForCancel + "\n" + cancelMessage  # safe now

#Output information to a output.txt file -- maybe change to report.txt for iteration1?
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


def main_loop():
    print("#/3#/3 Welcome to the SATD Tool 3\\#3\\#")

    #stage 1
    print("What repository do you want to analyze?")

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

    if (cancelProgram != True):
        print('System is ready to analyze the github \"' + FindRepoName(REPOURL) + '\". Type any key + ENTER to continue, or type "stop" or 0 to stop the program. ')
        readyToCont = input("Command|: ")
        if (readyToCont.lower() == "stop" or readyToCont == "0"):
            CancelProgramDTF("User stopped program before analyzation.")
    
    # Main loop

    if (cancelProgram == False):
        print("Here the program should have started \__")
        files, fileAndContributors, projectContributors, repoName = RepoFetcher( REPOURL, cancelProgram, False ) # OBS, set isLocal to FALSE by default, its not implemented yet, may not need to be
        RepoOutputDisplay()
    else:
        print("Task was canceled. \nThis is the full log")
        print(reasonForCancel)

# run main loop
main_loop()