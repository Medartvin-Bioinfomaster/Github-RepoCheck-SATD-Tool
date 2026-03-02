from storageHandler import write_to_outputfile, write_file_to_directory, write_main_report

from filereportgenerator import generate_full_report

import webbrowser, json, os, urllib.request, urllib.parse

def MainReport(projectroot, repoName, reportName, content):
    # write_to_outputfile(f"{outputfolder}/{reportName}.txt", content)
    repo_path, file_reports_path = write_main_report(projectroot, repoName, f"{reportName}.txt", content)
    # print("Main report generated.")
    return repo_path, file_reports_path

def CreateSingleFileReport(directory, reportName, content):
    # write_to_outputfile(f"{outputfolder}/{fileFolderName}/{reportName}.txt", content)
    write_file_to_directory(directory, f"{reportName}.txt", content)
    # print("single file report generated.")

def SingleFileSatdText(r_file, satd_status, total_churn, loc, churn_per_loc, risk, satd_count, lines_compromised):
    # print("hegw")
    contributorsvisual = ""
    for cont in r_file.contributors:
        contributorsvisual += cont + ", "
    
    text = ""
    text += f"Filename: {r_file.filename}"
    text += f"\nFilepath: {r_file.fullpath}"
    text += f"\nContains SATD: {satd_status}"
    text += f"\nAmount of commits: {r_file.commits}"
    text += f"\nAmount of contributors: {len(r_file.contributors)}"
    text += f"\nContributor names: {contributorsvisual}"
    text += f"\nSATD comments detected: {satd_count}"
    text += f"\nlines_added: {r_file.churndata['added']}"
    text += f"\nlines_deleted: {r_file.churndata['deleted']}"
    text += f"\ntotal_churn: {total_churn}"
    text += f"\nLines of code (loc): {loc}"
    text += f"\nLines of code potentially compromised: {lines_compromised}"
    text += f"\nchurn_per_loc: {round(churn_per_loc, 2)}"
    text += f"\nrisk_level: {risk}"
    return text

def generateDataJs(repo_path, report_data):
    repo_path_str = str(repo_path)
    
    # 1. Lagre data.js
    if not os.path.exists(repo_path_str):
        os.makedirs(repo_path_str)
    
    # js_filepath = os.path.join(repo_path_str, 'data.js')
    # with open(js_filepath, 'w', encoding='utf-8') as f:
    #     f.write(f"const externalData = {json.dumps(report_data)};")

    # 2. Finn test.html
    # html_file_path = os.path.abspath('test.html')
    
    # 3. Lag URL-er
    # Vi bruker quote() på mappen for å håndtere mellomrom og norske tegn
    # html_url = 'file:' + urllib.request.pathname2url(html_file_path)
    # data_dir_param = urllib.parse.quote(repo_path_str)
    
    # final_url = f"{html_url}?dir={data_dir_param}"
    
    # PRINT denne i terminalen så du kan kopiere den manuelt hvis den feiler!
    # print(f"DEBUG: Forsøker å åpne: {final_url}")

    # Generer rapporten
    final_url = generate_full_report(repo_path_str, report_data, report_data["data"])

    return final_url

def openHtmlReportFile(url):
    """Åpner URL-en i standard nettleser."""
    print(f"Åpner rapport: {url}")
    webbrowser.open(url)