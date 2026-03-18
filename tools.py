from pydriller.metrics.process.code_churn import CodeChurn
from pathlib import Path
import unicodedata
from dateutil.relativedelta import relativedelta

import plotly.graph_objects as go
import pandas as pd

from datetime import timedelta

def FindRepoName(repourl):
    lastlinkname = None
    if repourl.__contains__('\\'):
        lastlinkname = repourl.split("\\")
    else:
        lastlinkname = repourl.split("/")
        
    linklength = len(lastlinkname)
    nameFromList = lastlinkname[linklength - 1]
    return nameFromList

def CreateTypedRepoName(repourl, iteration):
    # lastlinkname = None
    # if repourl.__contains__('\\'):
    #     lastlinkname = repourl.split("\\")
    # else:
    #     lastlinkname = repourl.split("/")
    try :
        repName = FindRepoName(repourl)
        # linklength = len(lastlinkname)
        tag = "URL" if isUrl(repourl) else "Local"
        # print(f"- {str(iteration + 1)}: {lastlinkname[linklength - 1]} ({tag})")
        typedName = f"- {str(iteration + 1)}: {repName} ({tag})"
        return typedName
    except IndexError:
        return f"- Broken Reponame or Link"

def CreateTypedReportName(reporturl, iteration):
    try:
        normalized_path = reporturl.replace('\\', '/')
        path_parts = normalized_path.split('/')
        folder_name = path_parts[-2]
        stro = folder_name.split('_')
        if len(stro) >= 2:
                repName = stro[0]
                count = stro[1]
        else:
            repName = folder_name
            count = "0"

        typedName = f"- {iteration + 1}: {repName} ({count})"

        return typedName
    except IndexError:
        return f"- Broken Reponame or Link"


def isUrl(repolink):
    if (repolink.startswith('http://') or repolink.startswith('https://')):
        return True
    else:
        return False
    
def WriteRepoName(reposInStorage):

    if (reposInStorage and len(reposInStorage) > 0):
        print("\nStored repos:")
        for i, repo in enumerate(reposInStorage):
            if not repo or repo.strip() == "": # skip any whitespace
                continue
            # lastlinkname = None
            # if repo.__contains__('\\'):
            #     lastlinkname = repo.split("\\")
            # else:
            #     lastlinkname = repo.split("/")
            # linklength = len(lastlinkname)
            # tag = "URL" if isUrl(repo) else "Local"
            # print(f"- {str(i + 1)}: {lastlinkname[linklength - 1]} ({tag})")
            repoNameTyped = CreateTypedRepoName(repo, i)
            print(repoNameTyped)

    print("Write the repo url bellow. To load a saved repo, type the number from a stored repo above.")
    urlForRepo = input("Command|: ")
    urlToReturn = ""

    if urlForRepo.lower() == "cancel":  
        # CancelProgramDTF("User cancelled")
        return {"text": "User cancelled", "status": False}
    elif urlForRepo.isnumeric():
        index = int(urlForRepo) - 1
        if index >= 0 and index < len(reposInStorage):
            urlToReturn = reposInStorage[index] #translate the record to index
        #_
    else:
        urlToReturn = urlForRepo
    # print("repo?")
    # print(urlToReturn)
    # Retruing the reponame
    return urlToReturn


def WriteListOfReportsStored(reportsInStorage):
    if (reportsInStorage and len(reportsInStorage) > 0):
        print("\nStored Reports:")
        for i, repo in enumerate(reportsInStorage):
            if not repo or repo.strip() == "":
                continue
            reportNameTyped = CreateTypedReportName(repo, i) # <-- fix to find the name of the report file
            print(reportNameTyped)

        print('Write the number of the report you wish to open from the list above. Or type "cancel" to cancel the task."')
        urlForRepo = input("Command|: ")
        urlToReturn = ""

        if urlForRepo.lower() == "cancel":  
            # CancelProgramDTF("User cancelled")
            return {"text": "User cancelled", "status": False}
        elif urlForRepo.isnumeric():
            index = int(urlForRepo) - 1
            if index >= 0 and index < len(reportsInStorage):
                urlToReturn = reportsInStorage[index] #translate the record to index
            #_
        else:
            print("Number not recognized.\n")
            urlToReturn = ""
        # print("repo?")
        # print(urlToReturn)
        # Retruing the reponame
        return urlToReturn
    else:
        print("No reports saved yet! A report will be generated and saved after you have analyzed a repository. Returning to menu.\n")
        return ""

# TLDR: This is a help-function. Some paths use a / and others use \, this function is used to more easily disect which symbol to use
def choose_separator(repoUrl):
    if "/" in repoUrl and "\\" not in repoUrl:
        return "/"
    if "\\" in repoUrl and "/" not in repoUrl:
        return "\\"
    # Hvis begge eller ingen finnes, velg forward slash som standard
    return "/"


#Output information to a output.txt file -- maybe change to report.txt for iteration1?
def RepoOutputDisplay(files, fileAndContributors, projectContributors, rFiles, repoName): # FIXME: Her trengs det en refac, mye uleselig kode grunnet chatDGBGT
    repoNameStr = str(repoName or "")
    # print(f"\n\\#/ after program is ran, here are the resulting lists for the repo '{repoNameStr}':")

    # ===== Files section =====
    output_lines = []

    # Normalize and print files info:
    if files is None:
        files = {}

    files_repr = []
    # Case A: files is a dict mapping filename -> FileData (or dict)
    if isinstance(files, dict):
        for fname, fobj in files.items():
            # fobj may be FileData or dict; handle both
            if fobj is None:
                fullpath = None
            elif hasattr(fobj, "fullpath"):
                fullpath = fobj.fullpath
            elif isinstance(fobj, dict):
                fullpath = fobj.get("fullpath")
            else:
                fullpath = str(fobj)
            files_repr.append(f"{fname} ({fullpath})" if fullpath else f"{fname}")
    # Case B: files is a list/tuple of FileData or strings
    elif isinstance(files, (list, tuple)):
        for entry in files:
            if isinstance(entry, str):
                files_repr.append(entry)
            elif hasattr(entry, "filename"):
                name = entry.filename
                fullpath = getattr(entry, "fullpath", None)
                files_repr.append(f"{name} ({fullpath})" if fullpath else name)
            elif isinstance(entry, dict):
                name = entry.get("filename") or entry.get("name") or str(entry)
                fullpath = entry.get("fullpath")
                files_repr.append(f"{name} ({fullpath})" if fullpath else name)
            else:
                files_repr.append(str(entry))
    else:
        # fallback: any other type -> stringify
        files_repr.append(str(files))

    output_lines.append("Files: " + ", ".join(files_repr) if files_repr else "Files: (none)")
    # print(output_lines[-1])

    # ===== Files and contributors =====
    output_lines.append("Files and their contributors:")
    # print(output_lines[-1])

    if not fileAndContributors:
        output_lines.append("  (no files with contributor info)")
        # print(output_lines[-1])
    else:
        for filename, obj in fileAndContributors.items():
            output_lines.append(f"\nFile data: {filename}")
            output_lines.append(f"\n - File Absolute Path: {obj.fullpath}")
            lengthOfComHashes = -1
            if (obj.commitHashes):
                lengthOfComHashes = len(obj.commitHashes)
            output_lines.append(f"\n - Amount of Commit hashes registered: { 'None' if lengthOfComHashes < 0 else lengthOfComHashes}")
            # output_lines.append(f"\n commithashsh: {obj.commitHashes}")
            # try:
            #     output_lines.append(f"\n - First hash: {obj.commitHashes[0]}, Last hash: {obj.commitHashes[len(obj.commitHashes)]}")
            # except(IndexError):
            #     print("false..")

            # Support dict-style and object-style for obj
            if isinstance(obj, dict):
                contributors = obj.get("contributors", [])
                commits = obj.get("commits")
            else:
                contributors = getattr(obj, "contributors", [])
                commits = getattr(obj, "commits", None)

            output_lines.append(f"  commits: {commits}")
            # print(f"File data: {filename}  commits: {commits}")
            for contributor in contributors or []:
                output_lines.append(f"    contributor: {contributor}")
                # print(f"    contributor: {contributor}")

    if not rFiles:
        output_lines.append("\n  (no R files  registered)")
    else:
        output_lines.append(f"\n **R files found:")

        for rF in rFiles:
            # ab_path = rF.fu
            # RfileName = ""
            # RfileName = FindRepoName(ab_path)
            output_lines.append(f"\n - R File \"{rF.filename}\" Absolute Path: {rF.fullpath}")
            
    # ===== Project contributors =====
    if projectContributors is None:
        projectContributors = []
    if isinstance(projectContributors, set):
        proj_str = ", ".join(sorted(projectContributors))
    elif isinstance(projectContributors, (list, tuple)):
        proj_str = ", ".join(projectContributors)
    else:
        proj_str = str(projectContributors)

    output_lines.append(f"\nAll contributors: {proj_str}")
    # print("All contributors:", proj_str)

    return "\n".join(output_lines)

def getChurnForAFile(repopath, firstCommit, lastCommit):
    metric = CodeChurn(path_to_repo=repopath,
                   from_commit=firstCommit,
                   to_commit=lastCommit)
    
    files_count = metric.count()
    return files_count

def calculate_selfadmitted_technical_debt_density(satd_counts, compromised_lines, loc):
    return (compromised_lines / loc) * 1000

def getHtmlGraph(data):
    df = pd.DataFrame(data)

    # 2. Lag grafen med Plotly
    fig = go.Figure()

    # Legg til Total Churn som en linje
    fig.add_trace(go.Scatter(
        x=df['Date'], 
        y=df['Total Churn'],
        mode='lines+markers',
        name='Total Churn (Volatility)',
        text=df['Message'], # Vises når du hovrer over punktet
        line=dict(color='firebrick', width=2)
    ))

    # Legg til barer for Added og Deleted for mer detaljer
    fig.add_trace(go.Bar(x=df['Date'], y=df['Added'], name='Lines Added', marker_color='forestgreen', opacity=0.5))
    fig.add_trace(go.Bar(x=df['Date'], y=df['Deleted'], name='Lines Deleted', marker_color='royalblue', opacity=0.5))

    # 3. Styling for et "Research Paper" utseende
    fig.update_layout(
        title='Code Churn Timeline: Identifying Technical Debt Hotspots',
        xaxis_title='Tidslinje',
        yaxis_title='Antall linjer endret',
        template='plotly_white',
        hovermode='x unified',
        barmode='stack'
    )

    # 4. EKSPORT TIL HTML
    fig.write_html("churn_analysis.html")

    print("Grafen er ferdig! Åpne churn_analysis.html i nettleseren din.")

def normalize_windows_path(REPOURL: str) -> str:
    return str(Path(REPOURL).resolve())

def clean_name(name):
    """
    'ê', 'é', 'ö' to 'e', 'e', 'o'.
    """
    if not name:
        return ""
    
    nfd_form = unicodedata.normalize('NFD', name)
    new_cleaned_name = "".join([c for c in nfd_form if not unicodedata.combining(c)])
    
    return new_cleaned_name

def churn_stats_from_logs(churnlogs, filename=""):
    # if not churnlogs:
    #     raise ValueError("Ingen churnlogs funnet! Kan ikke beregne statistikk.")

    # # 1. Finn ankerpunktet (nyeste commit)
    # sorted_logs = sorted(churnlogs, key=lambda x: x['commitdate'], reverse=True)
    # latest_date = sorted_logs[0]['commitdate']

    # # 2. Opprett listene for de ulike tidsepokene
    # twoMonthList = []   # 0-60 dager
    # fourMonthList = []  # 61-120 dager
    # sixMonthList = []   # 121-180 dager

    # # 3. Fordel objektene (Viktig: Vi bruker >= og < for å unngå overlapp)
    # limit60 = latest_date - timedelta(days=60)
    # limit120 = latest_date - timedelta(days=120)
    # limit180 = latest_date - timedelta(days=180)

    # for log in sorted_logs:
    #     c_date = log['commitdate']
        
    #     if c_date >= limit60:
    #         twoMonthList.append(log)
    #     elif c_date >= limit120:
    #         fourMonthList.append(log)
    #     elif c_date >= limit180:
    #         sixMonthList.append(log)
    #     else:
    #         continue # Utenfor 6 måneder - ignoreres

    # # Funksjon for å regne ut matte per liste
    # def process_period_list(period_list):
    #     try:
    #         total_churn = 0
    #         daily_map = {}

    #         for log in period_list:
    #             # Churn Addition: added + abs(deleted)
    #             churn = log['added'] + abs(log['deleted'])
    #             total_churn += churn
                
    #             # Grupper på dato for å finne unike dager
    #             d = log['commitdate'].date()
    #             daily_map[d] = daily_map.get(d, 0) + churn

    #         # Matematikken
    #         active_days = len(daily_map)
    #         avg_per_day = total_churn / active_days
    #         highest_day = max(daily_map.values())

    #         return round(avg_per_day, 1), total_churn, highest_day
    #     except ZeroDivisionError:
    #         print("No ")
    #         return 0,0,0

    # # 4. Kjør beregningen på de ferdig-sorterte listene
    # a2, t2, p2 = process_period_list(twoMonthList)
    # a4, t4, p4 = process_period_list(fourMonthList)
    # a6, t6, p6 = process_period_list(sixMonthList)

    showlogs = False

    if (filename == "MulticoreParam-class.R"):
        showlogs = True


    # sort to make it reveal most recent commitdate first
    churnlogs.sort(key=lambda x: x["commitdate"], reverse=True)
    merged_data = {}

    if showlogs:
        print("Churnlog before merging")
        print(churnlogs)
        print()

    for entry in churnlogs:
        # Vi bruker bare .date() delen som nøkkel
        d_key = entry["commitdate"].date()
        
        if d_key in merged_data:
            # Hvis datoen finnes, oppdater eksisterende objekt
            merged_data[d_key]["added"] += entry["added"]
            merged_data[d_key]["deleted"] += entry["deleted"]
            # Vi legger til ID-en i en liste bare for å ha kontroll
            # if isinstance(merged_data[d_key]["id"], list):
            #     merged_data[d_key]["id"].append(entry["id"])
            # else:
            #     merged_data[d_key]["id"] = [merged_data[d_key]["id"], entry["id"]]
        else:
            # Hvis ny dato, lagre en kopi av objektet
            merged_data[d_key] = entry.copy()
            merged_data[d_key]["commitdate"] = d_key

    # after merging the same dates, use "datapoints" list from now on 
    datapoints = sorted(merged_data.values(), key=lambda x: x["commitdate"], reverse=True)

    most_recent_date = datapoints[0]["commitdate"] 

    if showlogs:
        print("Churnlog after merging")
        print(datapoints)
        print(most_recent_date)
        print()

    p1_limit = most_recent_date - relativedelta(months=2)
    # Periode 2: 3-4 måneder siden
    p2_limit = most_recent_date - relativedelta(months=4)
    # Periode 3: 5-6 måneder siden
    p3_limit = most_recent_date - relativedelta(months=6)
    year_limit = most_recent_date - relativedelta(months=12)

    stringos = ""
    period_0_2 = []
    period_3_4 = []
    period_5_6 = []
    year_cs = []
    trash_pile = []

    
    if showlogs:
        print("Year and period piles")
        print(period_0_2)
        print(period_3_4)
        print(period_5_6)
        print(year_cs)
        print()

    for entry in datapoints:
        dt = entry["commitdate"]
        
        if dt >= p1_limit:
            period_0_2.append(entry)
        elif dt >= p2_limit:
            period_3_4.append(entry)
        elif dt >= p3_limit:
            period_5_6.append(entry)
        elif dt >= year_limit:
            year_cs.append(entry)
        # else:
        #     trash_pile.append(entry)
    #_
    a2=t2=p2=a4=t4=p4=a6=t6=p6=0
    ya=yt=yp=0

    if len(period_0_2) > 0:
        for item in period_0_2:
            tiny_churn = item["added"] + item["deleted"]
            t2 += tiny_churn
            if (p2 == 0 or tiny_churn > p2):
                p2 = tiny_churn
        a2 = t2 / len(period_0_2) #so here, the average is equal to the total churn divided by activitites, activities are a combination of all commits (adds and deletes) on the same day, no duplicate days. This measures the activity and not just add/delete average for each commit
    if len(period_3_4) > 0:
        for item in period_3_4:
            tiny_churn = item["added"] + item["deleted"]
            t4 += tiny_churn
            if (p4 == 0 or tiny_churn > p4):
                p4 = tiny_churn
        a4 = t4 / len(period_3_4) #so here, the average is equal to the total churn divided by activitites, activities are a combination of all commits (adds and deletes) on the same day, no duplicate days. This measures the activity and not just add/delete average for each commit
    if len(period_5_6) > 0:
        for item in period_5_6:
            tiny_churn = item["added"] + item["deleted"]
            t6 += tiny_churn
            if (p6 == 0 or tiny_churn > p6):
                p6 = tiny_churn
        a6 = t6 / len(period_5_6) #so here, the average is equal to the total churn divided by activitites, activities are a combination of all commits (adds and deletes) on the same day, no duplicate days. This measures the activity and not just add/delete average for each commit
    if len(year_cs) > 0:
        for item in year_cs:
            tiny_churn = item["added"] + item["deleted"]
            yt += tiny_churn
            if (yp == 0 or tiny_churn > yp):
                yp = tiny_churn
        ya = yt / len(year_cs)
        

    return a2, t2, p2, a4, t4, p4, a6, t6, p6, ya, yt, yp
"""
Hva er "Total" og "Average"?
Siden du var usikker på logikken, her er en rask forklaring:

Total Churn Addition: Hvis du legger til 10 linjer og sletter 5 linjer, har du "rørt" 15 linjer totalt. Dette tallet (15) er Total. Det viser hvor mye aktivitet som faktisk har skjedd i fila.

Average: Dette er Total / antall datapunkt med "aktivitet for en dag" i tidsperioden. Det forteller deg om endringene gjort i denne perioden og den sier litt om størrelsen deres, i stedet for å sjekke commits

Peak: Den dagen i perioden hvor det ble gjort aller mest (f.eks. hvis én dag hadde 500 i churn, mens resten hadde 10).
"""