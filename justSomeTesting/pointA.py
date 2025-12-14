from pointB import assignList, assignList2

def runTrial():
    global badlist
    print(verdikupong)
    print("Testing if list is assigned by other file")
    print("List start status = ")
    print(badlist)

    print("Trial1")
    assignList(badlist)
    print("Results for list: ")
    print(badlist)

    print("Trial2")
    badlist = []
    badlist = assignList2(badlist)
    print("Results for list2: ")
    print(badlist)

badlist = ["MORADI"]
verdikupong = 10

runTrial()