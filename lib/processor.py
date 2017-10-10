import subprocess


# passes arguments to shell, implements arbitrary length pipes
# returns decoded stdout as string
# if stderr happens in last call it is also returned, otherwise lost
def chaincall(querystring):

    subqueries = querystring.split("|")
    querylists = [x.strip() for x in subqueries]

    jobs = []
    first = querylists.pop(0)
    jobs.append(subprocess.Popen(first,
                                 shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE))
    for query in querylists:
        print(querylists)
        jobs.append(subprocess.Popen(query,
                                     shell=True,
                                     stdin=jobs[-1].stdout,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE))
    out, err = jobs[-1].communicate()
    if err:
        return "%s\n\nShell has returned the error:\n%s" % (out.decode('utf-8'), err.decode('utf-8'))
    else:
        return out.decode('utf-8')
