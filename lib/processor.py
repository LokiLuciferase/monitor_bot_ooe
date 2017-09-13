import subprocess


# passes arguments to shell, implements arbitrary length pipes
# returns decoded stdout as string
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
