import json
from storageHandler import write_to_outputfile, readRepoStorageFile, writeRepoToStorage, lagre_til_csv, write_to_churnlog_to_outputfile
from tools import FindRepoName, CreateTypedRepoName, isUrl, WriteRepoName, RepoOutputDisplay, getChurnForAFile, normalize_windows_path, WriteListOfReportsStored, churn_stats_from_logs
from fetchGithubData import RepoFetcher, saveTheRepoUrlQuestion, findRepo
from fileAnalyzer import analyze_file
from reportGenerator import MainReport, CreateSingleFileReport, SingleFileSatdText, generateDataJs, openHtmlReportFile
from view_knowledgebase import start_db_interaction

from pathlib import Path

from typing import List, Dict
from dataClasses import RFileData, Contributor

reportssaved_path = 'local/reportstorage.txt'
storage_path = 'local/repostorage.txt'
cancelProgram = False
reasonForCancel = ""

# Function that changes the variables that handles the program stopping functions
def CancelProgram(cancelMessage: str) -> None:
    global cancelProgram, reasonForCancel
    cancelProgram = True
    print("Progam was cancelled or met an error.")
    try:
        if not reasonForCancel:
            reasonForCancel = ""
        reasonForCancel += ". " + cancelMessage  # <-- has caused errors before, safe now
    except NameError as Ne:
        op = 0
    return True

def getProjectRoot():
    PROJECT_ROOT = Path(__file__).resolve().parent
    return PROJECT_ROOT


def main_loop():
    # files = {}
    # fileAndContributors = {} # an object containing multiple "file" objects. File.contributors should contain every user that has channged that file. Also it should contain how many commits it has been part of, amount of times changed in commits.
    # projectContributors = [] # a list that will contain all contributors from the git project. Include everyone who has ever commited changes. Idea: Put in loop during fetch - or after fetch, where you iterate through the file-object list? What is more efficient?
    # issues = [] # list with amount of issues from the github. OBS: not implemented yet
    

    cancelProgram = False
    reasonForCancel = ""

    print("\n#/3#/3 Welcome to the SATD Tool 3\\#3\\#")
    action = 0

    while cancelProgram == False:
        print('Select an option below by typing in its number. \n (1) Start Github Analyzation\n (2) Open Earlier Report\n (3) Open Knowledgebase\n (4) Open Semantic Similarity Search\n type "STOP", "0" or "X" to exit program.')
        readyToContinue = input("Command|: ")
        if (readyToContinue.lower() == "stop" or readyToContinue == "0" or readyToContinue == "x"):
            cancelProgram = CancelProgram("User stopped program at first menu")
            return
        elif readyToContinue == "1":
            action = 1
        elif readyToContinue == "2":
            action = 2
        elif readyToContinue == "3":
            action = 3
        elif readyToContinue == "4":
            action = 4
        else:
            print("Sorry, command not recognized. \n")

        if (action == 1):
            RepositoryAnalyzation()
        elif (action == 2):
            OpenReportRoutine()
        elif (action == 3):
            try:
                print('\nOpening Knowledge base...\n')
                openHtmlReportFile('satd_knowledge_base.html')
            except FileNotFoundError as fn:
                print("The Knowledgebase wasn't found, please try again. Action can have failed due to the knowledgebase being moved or deleted.")
        elif (action == 4):
            start_db_interaction()


def OpenReportRoutine():
    reportssaved_bucket = readRepoStorageFile(reportssaved_path)
    report_url = WriteListOfReportsStored(reportssaved_bucket["repos"])
    if (report_url == ""):
        print("empty url, can't open.")
    else:
        openHtmlReportFile(report_url)

    
def RepositoryAnalyzation():
    # define variables to use
    global cancelProgram 
    global reasonForCancel 

    REPONAME = ""
    files = []
    r_files_data: Dict[RFileData] = {}
    projectContributors: Dict[Contributor] = {}
    commits_churndata = {}
    outputfilefolder = "File_Reports" #name of the folder where individual file reports are stored
    totalCommits = 0
    
    outputFileAnalyzeString = "Main report\n\n"
    lateSatdText = "Here is the rundown of the Total Findings:\n"
    rFileOutputStrings = []
    rFilesNotFound = 0

    totalSatdCounter = 0
    linesWithSatdCounter = 0
    totalLoc = 0
    totalFilesSatd = 0
    totalFiles = 0

    report_data = {
        "data": {
            "repoName": "",
            "commits": 0,
        },
        "files": {}
    }
    #stage 1
    print("What repository do you want to analyze?")

    # Get repoURL
    storageBucket = readRepoStorageFile(storage_path)
    _url = WriteRepoName(storageBucket["repos"])
    REPOURL = normalize_windows_path(_url)

    repo_been_found_and_is_valid = findRepo( REPOURL, cancelProgram ) #check if the url is valid
    wasValid = (repo_been_found_and_is_valid.get("status"))
    if wasValid == False:
        cancelProgram = CancelProgram("Repo couldn't be found or its not a valid git repository. " + repo_been_found_and_is_valid.get("text"))
        return

    if cancelProgram != True:
        saveTheRepoUrlQuestion( REPOURL, storageBucket["repos"], storage_path)

    # Simple pause before analyzation
    if (cancelProgram != True):
        print('System is ready to analyze the github \"' + FindRepoName(REPOURL) + '\". Type any key + ENTER to continue, or type "stop" or 0 to stop the program. ')
        readyToContinue = input("Command|: ")
        if (readyToContinue.lower() == "stop" or readyToContinue == "0"):
            cancelProgram = CancelProgram("User stopped program before analyzation.")
            return
    
    # Fetching Data Phase:
    if (cancelProgram == False):
        print("Here the program should have started \__")
        data_fetched = RepoFetcher( REPOURL, cancelProgram, False ) # OBS, set isLocal to FALSE by default, its not implemented yet, may not need to be

        if (data_fetched.get("status")):
            cancelProgram = CancelProgram("Something went wrong:", data_fetched.get("text"))
            return
        else:
            files = data_fetched.get("filesToReturn", [])
            r_files_data = data_fetched.get("r_files", {})
            projectContributors = data_fetched.get("projectContributors", {})
            REPONAME = data_fetched.get("repositoryName")
            totalCommits = data_fetched.get("totalCommits")
            # commits_churndata = data_fetched.get("commits_churndata")
    else:
        print("Task was canceled. \nThis is the full log")
        print(reasonForCancel)

    database_contribution = False

    # Individual File Analyzation Program
    if (cancelProgram != True):
        print('\nGithub analyzation complete! You can begin the file analyzation. ')

        print('\nDo you wish to store any SATD findings to our database?. Answer: (yes/1) or (no/0), then press "ENTER" to continue, or type "STOP" or "X" to stop the program. ')
        readyToContinue = input("Command|: ")
        if (readyToContinue.lower() == "stop" or readyToContinue == "x"):
            cancelProgram = CancelProgram("User stopped program before analyzation.")
            return
        elif (readyToContinue.lower() == "yes" or readyToContinue == "1"):
            database_contribution = True
        else:
            database_contribution = False
        yesnot = "not" if database_contribution == False else ""
        print(f"Database contribution was {yesnot} agreed to. Will {yesnot} save to database.")
        
        print('\nPress "ENTER" to continue, or type "STOP", "X" or 0 to stop the program. ')
        readyToContinue = input("Command|: ")
        if (readyToContinue.lower() == "stop" or readyToContinue == "0" or readyToContinue == "x"):
            cancelProgram = CancelProgram("User stopped program before analyzation.")

    print("Running file analyzer...")

    # Counters and list storage

    # print(f"The size of the R list: {r_files_data}, {len(r_files_data)}")

    averageChurnPrLoc = 0
    csvList = []

    for r_file in r_files_data.values():
        lateSatdText += f"\nAnalyze results for File: {r_file.filename}"

        file_has_satd, textResult, loc, foundFile, satd_count, lines_compromised = analyze_file(RFileInstance=r_file, repo_name = REPONAME, add_to_kb=database_contribution) # <-- forsøker å analysere Filene
    
        # counters update
        if satd_count > 0:
            totalSatdCounter += satd_count
        
        if lines_compromised > 0:
            linesWithSatdCounter += lines_compromised
        
        totalLoc += loc

        if foundFile:
            churn_data_from_r_file = r_file.churndata
            churn_data_from_r_file["loc"] = loc
            r_file.churndata = churn_data_from_r_file
            fileHasSatdFormat = "Yes🔴" if file_has_satd else "No🟢"
            if file_has_satd:
                totalFilesSatd += 1 # metric that counts out of X total files, how many do indeed have satd
            
            totalFiles += 1

            lateSatdText += f"\nTotal findings: {satd_count}\nFile contains SATD: {fileHasSatdFormat}\n"
            
            # churn calculation
            # total_churn = r_file.churndata["added"] + r_file.churndata["deleted"]
            addedlines = 0
            deletedlines = 0
            init_commit_addL = 0
            init_commit_delL = 0
            # iteration = 0

            for iteration, log in enumerate(r_file.churnlogs):
                #we can skip the initial commit and base the other churn types of this as a "proportional" churn value
                # print(iteration)
                # print(log)

                addL = log["added"]
                delL = log["deleted"]
                comDate = log["commitdate"]

                # print(comDate)
                
                delL = abs(delL) #normalizing the deleted lines to be a positive number

                addedlines += addL
                deletedlines += delL

                if (iteration == 0):
                    init_commit_addL = addL
                    init_commit_delL = delL
                iteration += 1
            #_

            a2, t2, p2, a4, t4, p4, a6, t6, p6, ya, yt, yp = churn_stats_from_logs(r_file.churnlogs)
            # ^^ this includes the past yearly activity, this is also interesting information if you have it, send to html!
            
            total_churn_add = addedlines + deletedlines
            total_churn_sub = addedlines - deletedlines
            # code decay, the initial commit should have added lines and deleted = 0, therefore we remove them from both sides:
            code_decay_add = (addedlines - init_commit_addL) + (deletedlines - init_commit_delL)
            code_decay_sub = (addedlines - init_commit_addL) - (deletedlines - init_commit_delL)

            # if (r_file.filename == "calculator.R"):
            #     # write_to_outputfile(r_file.churnlogs, "calculator_churnlog.txt")
            #     write_to_churnlog_to_outputfile(r_file.churnlogs, "calculator_churnlog.txt")

            # Set to 0 NOW so then later we switch out with an actual Churn Formula
            total_churn = 0
            risk = "Not implemented"
            churn_per_loc = -1

            # if loc > 0:
            #     churn_per_loc = total_churn / loc
            # else:
            #     churn_per_loc = 0

            # # these tags might be unneccessary
            # if churn_per_loc >= 5:
            #     risk = "High"
            # elif churn_per_loc >= 1:
            #     risk = "Medium"
            # else:
            #     risk = "Low"

            # averageChurnPrLoc += churn_per_loc
            averageChurnPrLoc += 0

            
            

            text_with_details = SingleFileSatdText(r_file, file_has_satd, total_churn, loc, 
                                                   404, "not-measured rn", total_churn_add, total_churn_sub, code_decay_add, code_decay_sub, satd_count, lines_compromised)
        
            fullText = text_with_details + "\n\n" + textResult

            #contributor & endringer:
            contributor_stats = []
            total_file_hashes = len(r_file.commitHashes) #tbh we dont need this, but its more "safe"

            if total_file_hashes > 0:
                for contributor in projectContributors.values():
                    shared_hashes = set(r_file.commitHashes).intersection(set(contributor.commitHashes))
                    user_file_commits = len(shared_hashes)
                    
                    if user_file_commits > 0:
                        percentage = (user_file_commits / total_file_hashes) * 100
                        
                        contributor_stats.append({
                            "username": contributor.username,
                            "contribution_percent": f"{round(percentage, 1)}%",
                            "commits_to_file": user_file_commits
                        })

            # sorted so that the biggest contributors are first in list
            contributor_stats.sort(key=lambda x: float(x["contribution_percent"].strip('%')), reverse=True)
            
            density = round((satd_count / loc) * 1000, 2)
            hasStatd = "SATD" if file_has_satd == True else "Clean"

            """
            total_churn_add, total_churn_sub, code_decay_add, code_decay_sub
            
            avg_2 = avg_4 = avg_6 = 0
            peak_2 = peak_4 = peak_6 = 0
            total_2 = total_4 = total_6 = 0
            """

            # if len(csvList):
            #     csvList.append(f"r_file.filename;loc;r_file.commits;hasStatd;REPONAME;len(contributor_stats);satd_count;lines_compromised;total_churn_add;total_churn_sub;code_decay_add;code_decay_sub;avg_2;peak_2;total_2;avg_4;peak_4;total_4;avg_6;peak_6;total_6")
            file_csv_format = f"{r_file.filename};{loc};{r_file.commits};{hasStatd};{REPONAME};{len(contributor_stats)};{satd_count};{lines_compromised};{total_churn_add};{total_churn_sub};{addedlines};{deletedlines};{a2};{t2};{p2};{a4};{t4};{p4};{a6};{t6};{p6};{ya};{yt};{yp}"
            csvList.append(file_csv_format)

            datajson = {
                "Text": fullText,
                "filename": r_file.filename,
                "file": r_file.fullpath,
                "contributor_data": contributor_stats,
                "metrics": {
                    "hasSatd": file_has_satd,
                    "commits": r_file.commits,
                    "lines_added": addedlines,
                    "lines_deleted": deletedlines,
                    "churn_total": total_churn_add,
                    "churn_activity": total_churn_sub,
                    "loc": loc,
                    "satd_count": satd_count,
                    "file_td_density": (satd_count / loc) * 1000,  #SATD density <---
                    "td_density_percentage": (((satd_count / loc) * 1000) / 1000)*100,  #SATD density <---
                    "lines_compromised": lines_compromised,
                    "churn_per_loc": round(churn_per_loc, 2),
                    "past_year_activity": {
                        "average": ya,
                        "total": yt,
                        "peak": yp,
                        "average_normalized": (ya / loc) * 1000,
                        "total_normalized": (yt / loc) * 1000,
                        "peak_normalized": (yp / loc) * 1000,
                        "dev_status": "No current Development" if yt == 0 else "Inactive" if yt > 0 and yt < 120 else "Active development"
                    }
                },
                "risk_level": risk
            }
            rFileOutputStrings.append(datajson)
            report_data["files"][r_file.filename] = datajson

            # Create File and store result
        else:
            # datajson = {
            #     "filename": r_file.filename + "_(Not found)",
            #     "file": r_file.fullpath,
            # }
            rFilesNotFound += 1
            # rFileOutputStrings.append(datajson)

    
    satd_percentage = (linesWithSatdCounter / totalLoc * 100) if totalLoc > 0 else 0
    total_td_density = round((totalSatdCounter / totalLoc) * 1000, 2)

    lagre_til_csv(csvList, REPONAME + ".csv")
    
    outputFileAnalyzeString += (
        f"\nTotal amount of SATD comments found: {totalSatdCounter}"
        f"\nRepo's total lines of code: {totalLoc}"
        f"\nNumber of lines compromised: {linesWithSatdCounter}"
        f"\nPercentage of code compromised by SATD: {satd_percentage}%\n"
    )

    # assign data -->
    report_data["data"]["repoName"] = REPONAME
    report_data["data"]["commits"] = totalCommits
    report_data["data"]["satd_count"] = totalSatdCounter
    report_data["data"]["loc"] = totalLoc
    report_data["data"]["density"] = total_td_density
    report_data["data"]["locCompromised"] = linesWithSatdCounter
    report_data["data"]["filessatd"] = totalFilesSatd
    report_data["data"]["totalfiles"] = totalFiles
    report_data["data"]["totalcontributors"] = len(projectContributors)


    outputFileAnalyzeString += f"\nR-files with SATD: {totalFilesSatd} out of {totalFiles} total"

    outputFileAnalyzeString += f"\n\nCommits distribution among contributors:"
    cont_datalist = {}
    for contributor in projectContributors.values():
        outputFileAnalyzeString += f"\n  {contributor.username} - {contributor.commits} commits"
        cont_datalist[contributor.username] = {"username": contributor.username, "commits": contributor.commits}
    report_data["data"]["contributorCommits"] = cont_datalist

    if rFilesNotFound > 0:
        outputFileAnalyzeString += f"\n\nFiles not found during analyzation: {rFilesNotFound}📄"

    outputFileAnalyzeString += "\n" + lateSatdText

    # create main report
    repo_path, file_reports_path = MainReport(getProjectRoot(), REPONAME, "Main", outputFileAnalyzeString)

    for out_data in rFileOutputStrings:
        CreateSingleFileReport(file_reports_path, out_data["filename"], out_data["Text"]) #(json.dumps(datajson, indent=4))


    print("Analyzation process complete. Results have been stored.")
    htmlfilepath = generateDataJs(repo_path, report_data)
    writeRepoToStorage(htmlfilepath, reportssaved_path)

    if (cancelProgram != True):
            print('Do you wish to view the reports in the browser? Answer: (yes/1) (no/0)')
            readyToContinue = input("Command|: ")
            if (readyToContinue.lower() == "yes" or readyToContinue == "1"):
                    openHtmlReportFile(htmlfilepath)

    print("End of process.")

# run main loop
main_loop()