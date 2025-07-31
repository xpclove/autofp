import re
import com
import os
import paramgroup_xray
import paramgroup_cw
import paramgroup_tof

Pgs = [
    paramgroup_xray,
    paramgroup_cw,
    paramgroup_tof
]
Pgs_key = {
    "xray": 0, "neutron_cw": 1, "neutron_tof": 2
}
Pgs_type = ["xray", "neutron_cw", "neutron_tof"]


def load_strategy(sfolder=os.path.join(com.root_path, "strategy")):
    global Pgs
    print(os.path.abspath(sfolder))
    for key in Pgs_key:
        sfilemodule = os.path.join(sfolder, "strategy_"+key+".py")

        files = open(sfilemodule)
        con = files.read()
        exec(con, globals())
        s_xray = strategy[key]
        print(s_xray.keys())

        group = s_xray["param_group"]
        order = s_xray["param_order"]
        target_s = s_xray["target"]
        target_s = re.sub(r"R_Factor", r'com.R', target_s)
        print("target=", target_s)
        target_s = target_s
        n = Pgs_key[key]
        Pgs[n].Param_Order_Group_Name = []
        Pgs[n].Param_Order_Group = []
        Pgs[n].target["string"] = target_s
        target_name = re.sub("MIN=", "", target_s)
        target_name = re.sub('com.R', '', target_name)
        target_name = re.sub(r'"', r'', target_name)
        target_name = re.sub(r'[\[\]]', r'', target_name)
        print(target_name)
        Pgs[n].target["name"] = target_name
        for item in order:
            Pgs[n].Param_Order_Group_Name.append(item)
            Pgs[n].Param_Order_Group.append(group[item])
        Pgs[n].Param_Num_Order = range(0, len(Pgs[n].Param_Order_Group))
    return 0


Param_Group = [
    ["Profile", "Background", "Contribution", "Phase"],
    ["Pattern"],
    ["Atom"],
    ["AtomicDisplacementFactor"],
    ["StrainParameter", "PreferOrient", "AsymmetryParameter", "SpecialReflection"],
    ["Atom_Occ"]
]
Param_Order_Group_Name = [
    "scale,zero",
    "background , a b c",
    "W",
    "V,U",
    "PA,Y,X",
    "Atom x y z",
    "Pref,Tempeture factors,Occ,S_L,D_L, neutron_cw_mode"]

Param_Order_Group = [
    ["Scale", "Transparency", "Zero"],
    ["BACK", "a-Pha", "b-P", "c-P"],
    ["BACK", "W-Pr"],
    ["BACK", "V-Pr", "U-Pr"],
    ["PA", "Y-Pr", "X-Pr"],
    ["X-Atom", "Y-Atom", "Z-Atom"],
    ["BACK", "Pref", "Bov",
     "Biso-Atom",
     "GausS", "1G",
     "Sycos", "Transparency",
     "Occ-Atom",
     "B1", "B2", "B3",
     "PA",
     "S_L", "D_L",
     "D_HG2", "D_HL", "Shift"
     # "Sysin","Displacement",
     # "LorSiz","SZ",
     # "Str",
     ]
]
Param_Num_Order = range(0, len(Param_Order_Group))
# for the alias count
atom = -1
back = -1
phase_last = 0

order = []


def name_to_alias(name="", phase=0, fit=None):
    global atom
    global back
    global phase_last
    name = name.replace("Sycos", "Displacement")
    name = name.replace("Sysin", "Transparency")
    name = name.replace("Lambda", "Wavelength")
    name = name.replace("GausSiz", "1G")
    name = name.replace("LorSiz", "SZ")
    if name.find("BACK") != -1:
        back += 1
    name = name.replace("BACK", "BACK["+str(back)+"]")

    atom_bool = False
    for pi in fit.get("Phase"):
        jbt_i = pi.get("Jbt")
        if jbt_i != 2:
            atom_bool = True
    if atom_bool == False:
        return name

    if name.find("X-Atom") != -1:
        atom += 1
        if phase_last != phase:
            atom = 0
            phase_last = phase

    atomobj = re.compile(r"Atom\[")
    reobj = re.compile(r"B[0-9][0-9]")
    atom_name = fit.get("Phase")[phase].get("Atom")[atom].get("Name")
    if atomobj.search(name):
        name = name.replace("Atom", "Atom["+atom_name+"]-")
    if reobj.search(name):
        name = name.replace("B", "Atom["+atom_name+"]-B")

    return name


# get a order for the rietveld
def get_order(params, param_switch, param_order_num=Param_Num_Order, job=0):
    s = ""
    global order
    Param_Order = []
    for i in param_order_num:
        Param_Order.extend(Param_Order_Group_X[i])
    for i in range(0, len(Param_Order)):
        for j in range(0, len(params.paramlist)):
            s = params.alias[j]
            if (s.find(Param_Order[i]) != -1 and param_switch[j] == True):
                order.append(j)

# get a order_group_n for the rietveld


def get_order_group_n(params, param_switch, group_n, param_order_num=None, job=0):
    s = ""
    global order
    order = []
    Param_Order = []
    pog = Pgs[job].Param_Order_Group
    if param_order_num == None:
        param_order_num = Pgs[job].Param_Num_Order

    for i in param_order_num:
        Param_Order.extend(pog[i])
    for i in range(0, len(Param_Order)):
        group = []
        for j in range(0, len(params.paramlist)):
            s = params.alias[j]
            if (s.find(Param_Order[i]) != -1 and param_switch[j] == True):
                group.append(j)
        order.append(group)
