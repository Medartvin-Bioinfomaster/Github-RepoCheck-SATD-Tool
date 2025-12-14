class RepoDetails:
    def __init__(self, repoName, files):
        self.repoName = repoName
        self.files = files

class FileContributors:
    def __init__(self, filename, contributor, commits):
        self.filename = filename
        self.contributors = []
        self.contributors.append(contributor)
        self.commits = commits
        
        

# fileDictionary = {
#                     "filename:" : file.filename,
#                     "contributors": [],
#                     "commits" : 0,
#                 } 