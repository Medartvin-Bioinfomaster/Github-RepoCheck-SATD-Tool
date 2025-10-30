from pydriller import Repository
# filter readmes? example data folder? (.rdata, .rds, r-markdown, .Rmnd)

# opt-in: ask users  what folders to loook throguh ( like R folder) - pydriller clones a whole repo, can we only download R-folder?

# repoUrl = "https://github.com/bobauser/parapim-quiz"
repositoryToInput = 'https://github.com/Medartvin-Bioinfomaster/Test-R-Data-Repo'
# C:\Users\edvin\Desktop\Studiegreier\Masteroppgave\Test-R-Data-Repo

files = [] # a list containing all files? useful?

fileAndContributors = {} # a object containing multiple file object. File.contributors should contain every user that has channged that file. Also it should contain how many commits it has been part of, amount of times changed in commits.

projectContributors = [] # a list that will contain all contributors from the git project. Include everyone who has ever commited changes. Idea: Put in loop during fetch - or after fetch, where you iterate through the file-object list? What is more efficient?

issues = [] # list with amount of issues from the github

# foldersToInclude = []

repoName = ""

cancelProgram = False
reasonForCancel = ""

print("Write a command here, 'cancel' to cancel the program.")
urlForRepo = input("Write repo url here (type 'st' for the standard one): ")

if urlForRepo.lower() == "st": 
    urlForRepo = repositoryToInput
elif urlForRepo.lower() == "cancel":  
    cancelProgram = True
    reasonForCancel = "User cancelled"

# useDateFilter = input("Do you want to filter commits based on dates? ('yes/1' or 'no/0'):")

# if (useDateFilter == "yes" or useDateFilter == "0"):
#     print("TEST")
#     dateToUse = input("Write the date to filter from ('DD:MM:YYYY' format): ")
#     dates = dateToUse.split(":")


# continue using date or not

def findRepo (repoUrl):

    if repoUrl.startswith('http://') or repoUrl.startswith('https://'):
        print('Link is OK')
    else:
        print('Link is NOT a URL. Trying to access as a local path.')
        # Her kan du også implementere logikk for validering av lokal sti hvis nødvendig.

    try:
        for commit in Repository(repoUrl).traverse_commits():
            # Gjør noe med commit, for eksempel: print(commit)
            print(commit)
    except Exception as e:
        print(f'Error accessing repository: {e}')
        cancelProgram = True
        reasonForCancel = "Error accessing local repository. e: " + e

        # cancelProgram = True
        # return
        # remove the return for now, just make sure that a local repo can be picked up

if cancelProgram != True:
    findRepo( repositoryToInput )

outputFilePlacement = "output.txt"

if (cancelProgram == False):
    for commit in Repository( repositoryToInput ).traverse_commits():
        # print("Commit #" + commit.hash)
        repoName = commit.project_name
        print("This is the repo name###: " + repoName)
        print("Commit #" + commit.hash + "\nMessage: " + commit.msg)
        print("Author: " + commit.author.name)
        # print("Author: " + commit.author.email)
        # print("Author: " + commit.branches.)
        # print("Author: " + commit.committer.)

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
        
        # print("More data, files: " + commit.files)
        # print("--co authors: " + commit.co_authors)
        # print("--in main branch?: " + commit.in_main_branch)
        # print("--lines: " + commit.lines)
        # print("--branches: " + commit.branches)
        # print("--committer: " + commit.committer)
        # print("--deletions: " + commit.deletions)
        # print("--merge: " + commit.merge)
        # print("--parents: " + commit.parents)
        print('*End\n')

#TODO: find issues from github using Git API???

def write_to_outputfile(output_string):
    with open(outputFilePlacement, 'w') as fil:
        fil.write(output_string)
        print("Written to outputfile success.")

if (cancelProgram == False):

    outputString = ""

    print("\n\\#/ after program is ran, here are the resulting lists for the repo '" + repoName + "':")

    print(files)

    outputString = "Files: " + ", ".join(files)  # Use join to create a comma-separated string of files
    print(fileAndContributors)

    outputString += "\nFiles and their contributors: "  # Using += for a more concise addition

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


else:
    print("Task was canceled")