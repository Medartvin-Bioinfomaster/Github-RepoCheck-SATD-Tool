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