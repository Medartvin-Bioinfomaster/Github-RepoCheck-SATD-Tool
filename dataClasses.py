class RepoDetails:
    def __init__(self, repoName, files):
        self.repoName = repoName
        self.files = files

class FileData:
    def __init__(self, filename, fullpath):
        self.filename = filename
        self.fullpath = fullpath

class RFileData:
    def __init__(self, filename, fullpath, churndata, contributor, commits, commitHash):
        self.filename = filename
        self.fullpath = fullpath
        self.commits = commits
        self.contributors = []
        self.commitHashes = []
        self.churn = 0
        self.churndata = {"added": 0, "deleted": 0, "loc": 0}
        if churndata is not None:
            self.churndata = churndata
        if contributor is not None:
            self.contributors.append(contributor)
        if commitHash is not None:
            self.commitHashes.append(commitHash)

    def addContributor(self, contributor):
        if contributor not in self.contributors:
            self.contributors.append(contributor)

    def addCommitHash(self, commitHash):
        if commitHash not in self.commitHashes:
            self.commitHashes.append(commitHash)

    def addCommit(self):
        self.commits += 1

    def addChurnValue(self, churnvalue):
        self.churn = churnvalue

# class GitFetchReturn:
#     def in
        

# fileDictionary = {
#                     "filename:" : file.filename,
#                     "contributors": [],
#                     "commits" : 0,
#                 } 