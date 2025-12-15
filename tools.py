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
    repName = FindRepoName(repourl)
    # linklength = len(lastlinkname)
    tag = "URL" if isUrl(repourl) else "Local"
    # print(f"- {str(iteration + 1)}: {lastlinkname[linklength - 1]} ({tag})")
    typedName = f"- {str(iteration + 1)}: {repName} ({tag})"
    return typedName


def isUrl(repolink):
    if (repolink.startswith('http://') or repolink.startswith('https://')):
        return True
    else:
        return False
    
def WriteRepoName(reposInStorage):

    if (reposInStorage and len(reposInStorage) > 0):
        print("\nStored repos:")
        for i, repo in enumerate(reposInStorage):
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
    print("repo?")
    print(urlToReturn)
    # Retruing the reponame
    return urlToReturn


def choose_separator(repoUrl):
    if "/" in repoUrl and "\\" not in repoUrl:
        return "/"
    if "\\" in repoUrl and "/" not in repoUrl:
        return "\\"
    # Hvis begge eller ingen finnes, velg forward slash som standard
    return "/"