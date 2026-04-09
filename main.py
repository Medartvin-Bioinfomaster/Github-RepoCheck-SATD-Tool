import json
from storageHandler import write_to_outputfile, readRepoStorageFile, writeRepoToStorage, lagre_til_csv, write_to_churnlog_to_outputfile
from tools import FindRepoName, CreateTypedRepoName, isUrl, WriteRepoName, RepoOutputDisplay, getChurnForAFile, normalize_windows_path, WriteListOfReportsStored, churn_stats_from_logs, checkDensityToThreshold, calculate_project_health
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

    cancelProgram = False
    reasonForCancel = ""

    action = 0
    print("\n#/3#/3 Welcome to the SATD Tool 3\\#3\\#")

    while cancelProgram == False:
        print('Select an option below by typing in its number. \n (1) Start Github Analysis\n (2) Open Earlier Report\n (3) Open Knowledgebase\n (4) Open Semantic Similarity Search\n type "STOP", "0" or "X" to exit program.')
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
                openHtmlReportFile('satd_knowledgebase.html')
            except FileNotFoundError as fn:
                print("The Knowledgebase wasn't found, please try again. Action can have failed due to the knowledgebase being moved or deleted.")
        elif (action == 4):
            start_db_interaction()
        #_
    #_
#_


def OpenReportRoutine():
    reportssaved_bucket = readRepoStorageFile(reportssaved_path)
    report_url = WriteListOfReportsStored(reportssaved_bucket["repos"])
    if (report_url == ""):
        print("empty url, can't open.")
    else:
        openHtmlReportFile(report_url)

    
def RepositoryAnalyzation():
    global cancelProgram 
    global reasonForCancel 

    REPONAME = ""
    r_files_data: Dict[RFileData] = {}
    projectContributors: Dict[Contributor] = {}
    totalCommits = 0
    
    outputFileAnalyzeString = "Main report\n\n"
    lateSatdText = "Here is the rundown of the Total Findings:\n"
    rFileOutputStrings = []

    rFilesNotFound=totalSatdCounter=linesWithSatdCounter=totalLoc=totalFilesSatd=totalFiles = 0 # all defined as 0

    # Get repoURL
    storageBucket = readRepoStorageFile(storage_path)
    _url = WriteRepoName(storageBucket["repos"])
    REPOURL = normalize_windows_path(_url)

    report_data = {
        "data": {
            "repoName": "",
            "commits": 0,
        },
        "files": {}
    }

    #stage 1
    # print("What repository do you want to analyze?")

    repo_been_found_and_is_valid = findRepo( REPOURL, cancelProgram ) #check if the url is valid
    wasValid = (repo_been_found_and_is_valid.get("status"))
    if wasValid == False:
        cancelProgram = CancelProgram("Repo couldn't be found or its not a valid git repository. " + repo_been_found_and_is_valid.get("text"))
        return

    if cancelProgram != True:
        saveTheRepoUrlQuestion( REPOURL, storageBucket["repos"], storage_path)

    # Simple pause before analyzation
    if (cancelProgram != True):
        print('System is ready to analyze the github \"' + FindRepoName(REPOURL) + '\". Type \"ENTER\" to continue, or type "stop" or 0 to stop the program. ')
        readyToContinue = input("Command|: ")
        if (readyToContinue.lower() == "stop" or readyToContinue == "0"):
            cancelProgram = CancelProgram("User stopped program before analysis started.")
            return
    
    # Fetching Data Phase:
    if (cancelProgram == False):
        print()
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
    print('\nGithub analyzation complete! You can begin the file analyzation. ')

    # Individual File Analyzation Program
    if (cancelProgram != True):
        print('\nPress "ENTER" to continue, or type "STOP", "X" or 0 to stop the program. ')
        readyToContinue = input("Command|: ")
        if (readyToContinue.lower() == "stop" or readyToContinue == "0" or readyToContinue == "x"):
            cancelProgram = CancelProgram("User stopped program before analyzation.")

    print("Running file analyzer...\n")

    averageChurnPrLoc = 0
    
    report_data["data"]["satd_density_average"] = 17.82503192
    report_data["data"]["satd_density_max"] = 181.818
    report_data["data"]["satd_density_standard_deviation"] = 27.84

    report_data["data"]["compromised_density_average"] = 83.807
    report_data["data"]["compromised_density_max"] = 454.550
    report_data["data"]["compromised_density_standard_deviation"] = 94.54

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
            addedlines = 0
            deletedlines = 0
            init_commit_addL = 0
            init_commit_delL = 0

            for iteration, log in enumerate(r_file.churnlogs):
                #we can skip the initial commit and base the other churn types of this as a "proportional" churn value

                addL = log["added"]
                delL = log["deleted"]
                comDate = log["commitdate"]

                delL = abs(delL) #normalizing the deleted lines to be a positive number

                addedlines += addL
                deletedlines += delL

                if (iteration == 0):
                    init_commit_addL = addL
                    init_commit_delL = delL
                iteration += 1
            #_

            a2, t2, p2, a4, t4, p4, a6, t6, p6, ya, yt, yp = churn_stats_from_logs(r_file.churnlogs, r_file.filename)
            # ^^ this includes the past yearly activity, this is also interesting information if you have it, send to html!
            
            total_churn_add = addedlines + deletedlines
            total_churn_sub = addedlines - deletedlines
            # code decay, the initial commit should have added lines and deleted = 0, therefore we remove them from both sides:
            code_decay_add = (addedlines - init_commit_addL) + (deletedlines - init_commit_delL) # always 0?
            code_decay_sub = (addedlines - init_commit_addL) - (deletedlines - init_commit_delL) # always 0?

            total_churn = 0


            churn_per_loc = -1

            averageChurnPrLoc += 0


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

            satd_density = round((satd_count / loc) * 1000, 2)
            satd_density_percentage = round((((satd_count / loc) * 1000) / 1000)*100, 2)
            lines_compromised_density = round((lines_compromised / loc) * 1000, 2)
            lines_compromised_density_percentage = round((((lines_compromised / loc) * 1000) / 1000)*100, 2)
            
            #danger levels, 1 is ok risk, 2 is bad, 3 is warning
            satd_density_score = (0 if satd_density < 2.5 else 1 if satd_density > 2.5 and satd_density < 40 
                                  else 2 if satd_density > 40 and satd_density < 180 else 3)
            # SATDDensity = 40%, ComPDensity = 60%
            
            report_data["data"]["satd_density_average"] = 17.82503192
            report_data["data"]["satd_density_max"] = 181.818
            report_data["data"]["satd_density_standard_deviation"] = 27.84

            report_data["data"]["compromised_density_average"] = 83.807
            report_data["data"]["compromised_density_max"] = 454.550
            report_data["data"]["compromised_density_standard_deviation"] = 94.54

            
            low_stddensity_risk = report_data["data"]["satd_density_average"] #can be within this number to be low risk
            medium_stddensity_risk = report_data["data"]["satd_density_max"] - report_data["data"]["satd_density_standard_deviation"]

            low_compdens_risk = report_data["data"]["compromised_density_average"] #can be within this number to be low risk
            medium_compdens_risk = report_data["data"]["compromised_density_max"] - report_data["data"]["compromised_density_standard_deviation"]

            stddens_normalized = checkDensityToThreshold(satd_density, medium_stddensity_risk, low_stddensity_risk) * 0.4
            compromised_normalized = checkDensityToThreshold(lines_compromised_density, medium_compdens_risk, low_compdens_risk) * 0.6
            risk_number = stddens_normalized + compromised_normalized
            risk = ""

            if (risk_number >= 2.5):
                risk = "High"
            elif risk_number >= 1.5:
                risk = "Medium"
            else:
                risk = "Low"


            text_with_details = SingleFileSatdText(r_file, file_has_satd, total_churn, loc, 
                                                   404, risk, total_churn_add, total_churn_sub, code_decay_add, code_decay_sub, satd_count, lines_compromised)
        
            fullText = text_with_details + "\n\n" + textResult

            datajson = {
                "Text": fullText,
                "filename": r_file.filename,
                "file": r_file.fullpath,
                "contributor_data": contributor_stats,
                "risk_level": risk,
                "metrics": {
                    "hasSatd": file_has_satd,
                    "commits": r_file.commits,
                    "lines_added": addedlines,
                    "lines_deleted": deletedlines,
                    "churn_total": total_churn_add,
                    "churn_activity": total_churn_sub,
                    "loc": loc,
                    "satd_count": satd_count,
                    "file_td_density": satd_density,  #SATD density <---
                    "td_density_percentage": satd_density_percentage,  #SATD density <---
                    "lines_compromised": lines_compromised,
                    "lines_compromised_percentage": round((lines_compromised / loc) * 100, 2),
                    "lines_compromised_density": lines_compromised_density,
                    "lines_compromised_density_percentage": lines_compromised_density_percentage,
                    "churn_per_loc": round(churn_per_loc, 2),
                    "past_year_activity": { #This section down here should not be shown in the final report if it doesn't work, as a general rule, don't include stuff that doesn't work
                        "average": ya,
                        "total": yt,
                        "peak": yp,
                        "average_normalized": round((ya / loc) * 1000, 2),
                        "total_normalized": round((yt / loc) * 1000, 2),
                        "peak_normalized": round((yp / loc) * 1000, 2),
                        "dev_status": "No current Development" if yt == 0 else "Inactive" if yt > 0 and yt < 120 else "Active development"
                    }
                }
            }
            rFileOutputStrings.append(datajson)
            report_data["files"][r_file.filename] = datajson

        else:
            rFilesNotFound += 1

    
    satd_percentage = (linesWithSatdCounter / totalLoc * 100) if totalLoc > 0 else 0
    total_td_density = round((totalSatdCounter / totalLoc) * 1000, 2)

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

    avg_score, health_label, health_color = calculate_project_health(report_data["files"])
    report_data["data"]["health_status"] = health_label
    report_data["data"]["health_color"] = health_color

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