from storageHandler import write_to_outputfile, readRepoStorageFile, writeRepoToStorage
from tools import FindRepoName, CreateTypedRepoName, isUrl, WriteRepoName, RepoOutputDisplay, getChurnForAFile, normalize_windows_path
from fetchGithubData import RepoFetcher, saveTheRepoUrlQuestion, findRepo
from fileAnalyzer import scan_repo_and_save_reports, analyze_file
from reportGenerator import MainReport, CreateSingleFileReport

from pathlib import Path

from typing import List
from dataClasses import RFileData

# Function that changes the variables that handles the program stopping functions
def CancelProgramDTF(cancelMessage: str) -> None:
    global cancelProgram, reasonForCancel
    cancelProgram = True
    reasonForCancel = reasonForCancel + "\n" + cancelMessage  # safe now

def getProjectRoot():
    PROJECT_ROOT = Path(__file__).resolve().parent
    return PROJECT_ROOT


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

    _url = WriteRepoName(storageBucket["repos"])
    REPOURL = normalize_windows_path(_url)

    repofound = findRepo( REPOURL, cancelProgram ) #check if the url is valid

    if repofound == False:
        CancelProgramDTF("Repo wasnt found")

    if cancelProgram != True:
        saveTheRepoUrlQuestion( REPOURL, storageBucket["repos"], path)

    # if cancelProgram != True:
    #     includeFolders()

    outputFilePlacement = "output.txt" # Fjern etterhvert, er kun for å teste at GitFetching gikk OK

    # CancelProgramDTF("STAGED: set to cancel before fetching repository.") #REMOVE WHEN YOU WANT TO CONTINUE THE PROGRAM

    if (cancelProgram != True):
        print('System is ready to analyze the github \"' + FindRepoName(REPOURL) + '\". Type any key + ENTER to continue, or type "stop" or 0 to stop the program. ')
        readyToContinue = input("Command|: ")
        if (readyToContinue.lower() == "stop" or readyToContinue == "0"):
            CancelProgramDTF("User stopped program before analyzation.")
    
    # firstCommitHash = ""
    # lastCommitHash = ""

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
            RFilesToAnalyze: list[RFileData] = out.get("rFilesToUse", [])
            repoName = out.get("repoName")

            write_to_outputfile("fileandcontributors.txt", str(fileAndContributors))
            write_to_outputfile("projectContributors.txt", str(projectContributors))


            # firstCommitHash = out.get("firstCommitHash")
            # lastCommitHash = out.get("lastCommitHash")
        outputFetchingString = RepoOutputDisplay(files, fileAndContributors, projectContributors, RFilesToAnalyze, repoName)
        write_to_outputfile(outputFilePlacement, outputFetchingString) #outputer det fetcher mottar, fjern senere eller bruk i report.txt på et vis

    else:
        print("Task was canceled. \nThis is the full log")
        print(reasonForCancel)


    # calculating CHURN value:
    # churn = getChurnForAFile(REPOURL, firstCommitHash, lastCommitHash)
    # print(f"Calculated a Churn value, it iszzzz: {churn}")

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
    rFileOutputStrings = []
    rFilesNotFound = 0
    for rF in RFilesToAnalyze:
        # print("-empty for now-")
        #return --> total_findings, files_with_satd, reports
        outputFileAnalyzeString += f"\nAnalyze results for File: {FindRepoName(rF.fullpath)}" # <-- her burde det egt het FindFILEName??

        # total_findings, files_with_satd, reports = scan_repo_and_save_reports(repo_path=rF, output_dir="dirTestFileAnalyze", repo_name=repoName) # <-- forsøker å analysere Filene
        total_findings, files_with_satd, reports, loc, foundFile = analyze_file(repo_path=REPOURL, RFileInstance=rF, output_dir="dirTestFileAnalyze", repo_name=repoName) # <-- forsøker å analysere Filene
        
        if foundFile:
            churndatafromrf = rF.churndata
            churndatafromrf["loc"] = loc
            rF.churndata = churndatafromrf
            outputFileAnalyzeString += f"\nTotal findings: {total_findings}\nFiles that contain SATD: {files_with_satd}\nReports: {reports}\n"
            
            total_churn = rF.churndata["added"] + rF.churndata["deleted"]
            # loc = rF.churndata["loc"] or 1  # avoid division by zero
            if loc > 0:
                churn_per_loc = total_churn / loc
            else:
                churn_per_loc = 0

            if churn_per_loc >= 5:
                risk = "High"
            elif churn_per_loc >= 1:
                risk = "Medium"
            else:
                risk = "Low"

            rFileOutputStrings.append({
                "filename": rF.filename,
                "file": rF.fullpath,
                "metrics": {
                    "commits": 0,
                    "lines_added": rF.churndata["added"],
                    "lines_deleted": rF.churndata["deleted"],
                    "total_churn": total_churn,
                    "loc": loc,
                    "churn_per_loc": round(churn_per_loc, 2)
                },
                "risk_level": risk
            })
        else:
            rFileOutputStrings.append({
                "filename": rF.filename + "_(Not found)",
                "file": rF.fullpath,
            })

    # total_findings, files_with_satd, reports = scan_repo_and_save_reports(repo_path=REPOURL, output_dir="dirTestFileAnalyze", repo_name=repoName) # <-- forsøker å analysere Filene

    if rFilesNotFound > 0:
        outputFileAnalyzeString += f"\n\nFiles not found during analyzation: {rFilesNotFound}"

    outputfolder = "Results"
    outputfilefolder = "File_Reports"

    MainReport(getProjectRoot(), "Main", outputFileAnalyzeString)
    
    for filereport in rFileOutputStrings:
        CreateSingleFileReport(getProjectRoot(), outputfilefolder, filereport["filename"], str(filereport))


    # write_to_outputfile("fileAnalyzetest.txt", outputFileAnalyzeString)



    print("If everything went well, the findings should have been printed to a file in dir \"dirTestFileAnalyze\"")

# run main loop
main_loop()