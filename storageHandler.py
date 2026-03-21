from pathlib import Path

import os

def test():
    print("Testing")

def write_to_outputfile(outputFilePlacement, output_string):
    with open(outputFilePlacement, 'w') as fil:
        fil.write(output_string)
        # print("Written to outputfile success.")


def write_to_churnlog_to_outputfile(churn_list, filename):
    """
    Writes a list of churn data dictionaries to a text file.
    """
    try:
        with open(filename, 'w') as f:
            for entry in churn_list:
                # Formatting the dictionary into a readable line
                line = (f"Date: {entry['commitdate']} | "
                        f"Added: {entry['added']} | "
                        f"Deleted: {entry['deleted']}\n")
                f.write(line)
        print(f"Successfully wrote logs to {filename}")
    except Exception as e:
        print(f"An error occurred while writing to file: {e}")


def write_main_report(projectroot, repoName, outputFileName, output_string):
    repo_path, file_reports_path = create_repo_structure(projectroot, repoName)
    output_file_path = repo_path / outputFileName
    with output_file_path.open("w", encoding="utf-8") as file:
        file.write(output_string)
        # print("Written to outputfile success.")
    return repo_path, file_reports_path

def write_file_to_directory(directories, outputFileName, output_string):
    output_file_path = directories / outputFileName

    with output_file_path.open("w", encoding="utf-8") as file:
        file.write(output_string)
        # print("Written to outputfile success.")

def create_repo_structure(projectroot, repoName):
    """
    Creates:
    Results/
        reponame_1/
            File_Reports/
    """

    repo_name_clean = repoName.lower()

    base_results_path = CreateResultsDirectory(projectroot)

    counter = 1
    while True:
        repo_folder_name = f"{repo_name_clean}_{counter}"
        repo_path = base_results_path / repo_folder_name

        if not repo_path.exists():
            break

        counter += 1

    # Create reponame_X folder
    repo_path.mkdir()

    # Create File_Reports inside it
    file_reports_path = repo_path / "File_Reports"
    file_reports_path.mkdir()

    return repo_path, file_reports_path


# TODO: FIks repostorage

def CreateResultsDirectory(projectroot, moreDir=""):

    output_dir = ""
    if moreDir != "":
        output_dir = Path(projectroot) / "Results" / moreDir
    else:
        output_dir = Path(projectroot) / "Results"

    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def readRepoStorageFile(path):
    storedList = []
    itemnumber = 1
    terminateLoop = False

    try:
        with open(path, 'r', encoding='utf-8') as storage:
            print("Reading Storage...")
    except FileNotFoundError:
        print(f"Storage not found. Creating a new one")
        with open(path, 'w', encoding='utf-8') as storage:  # creates the file
            pass
        storedList = []

    with open(path, 'r') as storage:
        storedList = [line.rstrip('\n') for line in storage]
        itemnumber = len(storedList)
    #Returns data as a dictionary
    return {"repos": storedList, "count": itemnumber}
#_

def writeRepoToStorage(repo, path):
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

# non used function, only used during research and manual analyzation
def lagre_til_csv(data_liste, filnavn):
    mappe_sti = os.path.join("local", "csv")
    if not os.path.exists(mappe_sti):
        os.makedirs(mappe_sti)
        print(f"Opprettet mappe: {mappe_sti}")

    fil_sti = os.path.join(mappe_sti, filnavn)
    
    filen_eksisterer = os.path.exists(fil_sti) and os.path.getsize(fil_sti) > 0

    with open(fil_sti, mode="a", encoding="utf-8", newline="") as f:
        for i, linje in enumerate(data_liste):
            if not filen_eksisterer and i == 0:
                f.write(linje)
                filen_eksisterer = True
            else:
                f.write("\n" + linje)

    print(f"Lagret {len(data_liste)} rader til {fil_sti}")

# --- EKSEMPEL PÅ BRUK ---
# Her kan du selv bestemme hvor mange attributter du vil ha
# eksempel_data = [
#     "2026-03-12;commit_123;Oleg;150;40",
#     "2026-03-13;commit_456;Gemini;200;10"
# ]

# lagre_til_csv(eksempel_data, "churn_data.csv")