from storageHandler import write_to_outputfile, write_file_to_directory

def MainReport(projectroot, reportName, content):
    # write_to_outputfile(f"{outputfolder}/{reportName}.txt", content)
    write_file_to_directory(projectroot, f"{reportName}.txt", content)
    print("Main report generated.")

def CreateSingleFileReport(projectroot, fileFolderName, reportName, content):
    # write_to_outputfile(f"{outputfolder}/{fileFolderName}/{reportName}.txt", content)
    write_file_to_directory(projectroot, f"{reportName}.txt", content, fileFolderName)
    print("single file report generated.")

def SingleFileSatdText(r_file, satd_status, total_churn, loc, churn_per_loc, risk):
    print("hegw")
    text = ""
    text += f"Filename: {r_file.filename}"
    text += f"\nFilepath: {r_file.fullpath}"
    text += f"\nContains SATD: {satd_status}"
    text += f"\nAmount of commits: {r_file.commits}"
    text += f"\nlines_added: {r_file.churndata['added']}"
    text += f"\nlines_deleted: {r_file.churndata['deleted']}"
    text += f"\ntotal_churn: {total_churn}"
    text += f"\nloc: {loc}"
    text += f"\nchurn_per_loc: {round(churn_per_loc, 2)}"
    text += f"\nrisk_level: {risk}"
    return text