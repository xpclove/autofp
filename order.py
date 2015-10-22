
Param_Group=[
    ["Profile","Background","Contribution"],
    ["Pattern"],
    ["Atom","AtomicDisplacementFactor","Phase"],
    ["StrainParameter","PreferOrient","AsymmetryParameter"]
    ]
Param_Order=[
    "Scale",
    "a-Pha","b-Pha","c-Pha",
    "W-Pr",
    "Back",
    "V-Pr",
    "U-Pr",
    "Back",
    "PA",
    "X-Atom","Y-Atom","Z-Atom",
    "Occ-Atom",
    "Bov",
    #"B1",
    #"B2","B3",
    "Biso-Atom",
    "GausS",
    "Sysin",
    "X-Pr",
    "Y-Pr",
    "LorSiz",
    "Str",
    "Pref",
    "Zero",
    "Sycos", 
    ]
order=[]

#get a order for the rietveld
def get_order(paramlist):
    str=""
    for i in range(0,len(Param_Order)):
        for j in range(0,len(paramlist)):
            str=paramlist[j].parname+"-"+paramlist[j].type
            if str.find(Param_Order[i])!=-1:
                order.append(j)

        