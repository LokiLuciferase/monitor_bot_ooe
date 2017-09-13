import subprocess


def chaincall(querystring):

    subqueries = querystring.split("|")
    querylists = [x.strip() for x in subqueries]

    jobs = []
    first = querylists.pop(0)
    jobs.append(subprocess.Popen(first, shell=True, stdout=subprocess.PIPE))
    for query in querylists:
        print(querylists)
        jobs.append(subprocess.Popen(query, shell=True, stdin=jobs[-1].stdout, stdout=subprocess.PIPE))
    out, err = jobs[-1].communicate()

    return out.decode('utf-8')


def macro(querystring):

    # define useful macros here which would be tedious to write on a phone.
    macrodic = {"checkbots" : "ps aux | grep -i '[b]ot'",
                "checksamba": "ps aux | grep -i 'smbd'",
                "stats"     : "./scripts/stats.sh",
                "stats -v"  : "./scripts/stats.sh -v",
                "bothistory": "cat ./logs/history.log | tail -500",
                "exceptions": "cat ./logs/monitorlog.log | grep 'Traceback' | wc -l"}

    if querystring == "macros":
        return "Existierende Makros:\n" + "".join(["%s : %s\n" % (x, y) for x, y in macrodic.items()])

    try:
        answer = macrodic[querystring]
        return chaincall(answer)
    except KeyError:
        return "Ein solches Makro existiert nicht."
