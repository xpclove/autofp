Param_Group=[
    ["Profile","Background","Contribution"],
    ["Pattern"],
    ["Atom","AtomicDisplacementFactor","Phase"],
    ["StrainParameter","PreferOrient"]
    ]
Param_Order=[
    "Scale",
    "Zero",
    "Sycos","Sysin",
    "Back",
    "Bov",
    "a-P","b-P","c-P",
    "W-Pr"
    "X-Atom","Y-Atom","Z-Atom",
    "Occ-Atom","Biso-Atom","Occ-Atom","Biso",
    "U-Pr","V-Pr",
    "B1","B2","B3",
    "Pref","GausS","LorSiz","Str"
    ]
order=[]
def get_order(paramlist):
    str="hello"
    for i in range(0,len(Param_Order)):
        for j in range(0,len(paramlist)):
            str=paramlist[j].parname+"-"+paramlist[j].type
            if str.find(Param_Order[i])!=-1:
                order.append(j)

        