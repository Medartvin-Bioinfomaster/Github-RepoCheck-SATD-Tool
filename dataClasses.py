class RepoDetails:
    def __init__(self, repoName, files):
        self.repoName = repoName
        self.files = files

class FileContributors:
    def __init__(self, filename, fullpath, contributor, commits):
        self.filename = filename
        self.fullpath = fullpath
        self.contributors = []
        if contributor is not None:
            self.contributors.append(contributor)
        self.commits = commits

class FileData:
    def __init__(self, filename, fullpath):
        self.filename = filename
        self.fullpath = fullpath

# class GitFetchReturn:
#     def in
        

# fileDictionary = {
#                     "filename:" : file.filename,
#                     "contributors": [],
#                     "commits" : 0,
#                 } 