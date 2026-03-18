from storageHandler import write_to_outputfile, write_file_to_directory, write_main_report

from report_to_html_generator import generate_full_report

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

def SingleFileSatdText(r_file, satd_status, total_churn, loc, churn_per_loc, risk, total_churn_add, total_churn_sub, code_decay_add, code_decay_sub, satd_count, lines_compromised):
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
    text += f"\n\ntotal_churn Add (new): {total_churn_add}"
    text += f"\n\ntotal_churn Sub (New): {total_churn_sub}"
    text += f"\n\ncode decay churn Add (New): {code_decay_add}"
    text += f"\n\ncode decay churn Sub (New): {code_decay_sub}"
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
    
    # Generer rapporten
    final_url = generate_full_report(repo_path_str, report_data, report_data["data"])

    return final_url

def openHtmlReportFile(url):
    print(f"Opening File: {url}")
    webbrowser.open(url)