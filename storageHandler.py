def test():
    print("Testing")

def write_to_outputfile(outputFilePlacement, output_string):
    with open(outputFilePlacement, 'w') as fil:
        fil.write(output_string)
        print("Written to outputfile success.")

# TODO: FIks repostorage

def readRepoStorageFile(path):
    # print("Reading Storage..")
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
        # spot = storage.readline()

        # while (spot != "" and terminateLoop == False):
        #     storedList.append(spot.strip())
        #     # spot = storage.readline
        #     itemnumber += 1
        #     spot = storage.readline()
        #     if (itemnumber > 99): #loop shouldnt loop over 99 items anyway, cancels automatically if there is a bug or something. Avoids infinite loop
        #         terminateLoop = True

    # print(storedList)
    # print(f"Amount of items read: {itemnumber}")
    
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