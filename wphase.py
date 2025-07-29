import os
import math
import run
import re
# weight of phase is define by
# weight cell : Scale*Unit*ATZ


def get_w_phase(phase=[]):
    pn = len(phase)
    pw = []
    phase_w = []
    pi = []
    for pi in phase:
        pw.append(pi[0]*pi[1]*pi[2])
    pw_sum = 0
    for pw_i in pw:
        pw_sum += pw_i
    for pw_i in pw:
        phase_w.append(pw_i*1.0/pw_sum)
    return phase_w


def get_w_phase_n(phase, n):
    p = get_w_phase(phase)
    w = p[n]
    return w


def get_volume(path, n):
    outfile = open(path)
    context = outfile.read()
    obj = re.compile(r'Direct Cell Volume =\s*\w*\d')
    con = obj.findall(context)
    vol = []
    for i in range(0, n):
        con_i = con[i]
        sc = con_i.split(' ')
        vol.append(float(sc[-1]))
    return vol


def get_w(r_):
    r = run.Run()
    r = r_
    n = r.phase_num
    pcell = []
    unit = get_volume(r.outfilename, n)
    for p_i in range(0, n):
        atz = r.fit.get("Phase")[p_i].get("ATZ")
        scale = r.fit.get("Contribution")[p_i].get("Scale")
        pcell.append([scale, unit[p_i], atz])
    w = get_w_phase(pcell)
    return w


if __name__ == "__main__":
    print "w"
    get_volume("./test/out/out.out", 2)
    r = run.Run()
    r.reset("./test/cvo/cvo.pcr")
    w = get_w(r)
    print w
