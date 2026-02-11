from storageHandler import write_to_outputfile, write_file_to_directory

def MainReport(projectroot, reportName, content):
    # write_to_outputfile(f"{outputfolder}/{reportName}.txt", content)
    write_file_to_directory(projectroot, f"{reportName}.txt", content)
    print("Main report generated.")

def CreateSingleFileReport(projectroot, fileFolderName, reportName, content):
    # write_to_outputfile(f"{outputfolder}/{fileFolderName}/{reportName}.txt", content)
    write_file_to_directory(projectroot, f"{reportName}.txt", content, fileFolderName)
    print("single file report generated.")