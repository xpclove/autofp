def check(str):
    p = open(str, "r")
    c = p.read()
    p.close()
    err = 0

    if c.find("Asymmetry parameters usage invalid") != -1:
        err = -31
    else:
        if c.rfind("Rwp") == -1:
            err = -32

    if c.find("Singular matrix") != -1:
        err = -33

    if err < 0:
        print "!out file check error code=", err
        
    return err
