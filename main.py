import json
from storageHandler import write_to_outputfile, readRepoStorageFile, writeRepoToStorage
from tools import FindRepoName, CreateTypedRepoName, isUrl, WriteRepoName, RepoOutputDisplay, getChurnForAFile, normalize_windows_path
from fetchGithubData import RepoFetcher, saveTheRepoUrlQuestion, findRepo
from fileAnalyzer import scan_repo_and_save_reports, analyze_file
from reportGenerator import MainReport, CreateSingleFileReport

from pathlib import Path

from typing import List
from dataClasses import RFileData

# Function that changes the variables that handles the program stopping functions
def CancelProgram(cancelMessage: str) -> None:
    global cancelProgram, reasonForCancel
    cancelProgram = True
    reasonForCancel = reasonForCancel + "\n" + cancelMessage  # <-- has caused errors before, safe now

def getProjectRoot():
    PROJECT_ROOT = Path(__file__).resolve().parent
    return PROJECT_ROOT

def main_loop():
    files = {}
    fileAndContributors = {} # an object containing multiple "file" objects. File.contributors should contain every user that has channged that file. Also it should contain how many commits it has been part of, amount of times changed in commits.
    projectContributors = [] # a list that will contain all contributors from the git project. Include everyone who has ever commited changes. Idea: Put in loop during fetch - or after fetch, where you iterate through the file-object list? What is more efficient?
    # issues = [] # list with amount of issues from the github. OBS: not implemented yet
    repoName = ""
    print("#/3#/3 Welcome to the SATD Tool 3\\#3\\#")

    #stage 1
    print("What repository do you want to analyze?")

    storage_path = 'repostorage.txt'

    cancelProgram = False
    reasonForCancel = ""

    storageBucket = readRepoStorageFile(storage_path)

    _url = WriteRepoName(storageBucket["repos"])
    REPOURL = normalize_windows_path(_url)

    repo_been_found_and_is_valid = findRepo( REPOURL, cancelProgram ) #check if the url is valid

    if repo_been_found_and_is_valid == False:
        CancelProgram("Repo couldn't be found or its not a valid git repository")

    if cancelProgram != True:
        saveTheRepoUrlQuestion( REPOURL, storageBucket["repos"], storage_path)

    if (cancelProgram != True):
        print('System is ready to analyze the github \"' + FindRepoName(REPOURL) + '\". Type any key + ENTER to continue, or type "stop" or 0 to stop the program. ')
        readyToContinue = input("Command|: ")
        if (readyToContinue.lower() == "stop" or readyToContinue == "0"):
            CancelProgram("User stopped program before analyzation.")
    
    if (cancelProgram == False):
        print("Here the program should have started \__")
        data_fetched = RepoFetcher( REPOURL, cancelProgram, False ) # OBS, set isLocal to FALSE by default, its not implemented yet, may not need to be
        if (data_fetched.get("status")):
            CancelProgram("Something went wrong:", data_fetched.get("text"))
        else:
            files = data_fetched.get("files", [])
            fileAndContributors = data_fetched.get("fileAndContributors", {})
            projectContributors = data_fetched.get("projectContributors", [])
            RFilesToAnalyze: list[RFileData] = data_fetched.get("rFilesToUse", [])
            repoName = data_fetched.get("repoName")

            write_to_outputfile("fileandcontributors.txt", str(fileAndContributors))
            write_to_outputfile("projectContributors.txt", str(projectContributors))
    else:
        print("Task was canceled. \nThis is the full log")
        print(reasonForCancel)

    if (cancelProgram != True):
        print('Github analyzation complete! You can begin the file analyzation. Type any key + ENTER to continue, or type "stop" or 0 to stop the program. ')
        readyToContinue = input("Command|: ")
        if (readyToContinue.lower() == "stop" or readyToContinue == "0"):
            CancelProgram("User stopped program before analyzation.")

    print("Running file analyzer...")

    outputFileAnalyzeString = "Here is the rundown of the Total Findings:"
    rFileOutputStrings = []
    rFilesNotFound = 0
    for r_file in RFilesToAnalyze:
        outputFileAnalyzeString += f"\nAnalyze results for File: {FindRepoName(r_file.fullpath)}"

        total_findings, files_with_satd, textResult, loc, foundFile = analyze_file(repo_path=REPOURL, RFileInstance=r_file, output_dir="dirTestFileAnalyze", repo_name=repoName) # <-- forsøker å analysere Filene
        
        if foundFile:
            churndatafromrf = r_file.churndata
            churndatafromrf["loc"] = loc
            r_file.churndata = churndatafromrf
            outputFileAnalyzeString += f"\nTotal findings: {total_findings}\nFiles that contain SATD: {files_with_satd}\n"
            
            total_churn = r_file.churndata["added"] + r_file.churndata["deleted"]
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

            datajson = {
                "Text": textResult,
                "filename": r_file.filename,
                "file": r_file.fullpath,
                "metrics": {
                    "commits": 0,
                    "lines_added": r_file.churndata["added"],
                    "lines_deleted": r_file.churndata["deleted"],
                    "total_churn": total_churn,
                    "loc": loc,
                    "churn_per_loc": round(churn_per_loc, 2)
                },
                "risk_level": risk
            }
            rFileOutputStrings.append(datajson)

        else:
            datajson = {
                "filename": r_file.filename + "_(Not found)",
                "file": r_file.fullpath,
            }
            rFileOutputStrings.append(datajson)

    if rFilesNotFound > 0:
        outputFileAnalyzeString += f"\n\nFiles not found during analyzation: {rFilesNotFound}"

    outputfilefolder = "File_Reports" #name of the folder where individual file reports are stored

    MainReport(getProjectRoot(), "Main", outputFileAnalyzeString)
    
    for filereport in rFileOutputStrings:
        CreateSingleFileReport(getProjectRoot(), outputfilefolder, filereport["filename"], (json.dumps(filereport, indent=4)))

    print("Analyzation process complete. Results have been stored.")

# run main loop
main_loop()