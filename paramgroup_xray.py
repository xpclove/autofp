import re
Param_Order_Group=[
    ["Scale"],
    ["Transparency","Zero"],
    ["BACK[0]","BACK[1]"],
    ["a-Pha","b-P","c-P"],
    ["W-Pr"],
    ["BACK"],
    ["V-Pr", "U-Pr"],
    ["PA"],
    ["Y-Pr","X-Pr"],
    ["X-Atom","Y-Atom","Z-Atom"],
    ["Pref","Bov"], 
    ["Biso-Atom"],
    ["GausS","1G"],
    ["Occ-Atom"],
    ["B1","B2","B3"],
    ["PA",
    "S_L","D_L",
    #"Sysin","Displacement",
    #"LorSiz","SZ",
    #"Sycos","Transparency",
    #"Str",
    ],
    ["BCK"]
    ]
Param_Group=[
    ["Profile","Background","Contribution","Phase"],
    ["Pattern"],
    ["Atom"],
    ["AtomicDisplacementFactor"],
    ["StrainParameter","PreferOrient","AsymmetryParameter","SpecialReflection"],
    ["Atom_Occ"]
    ]
Param_Order_Group_Name=[
                        "scale",
                        "zero",
                        "simple background" , 
                        "a b c",
                        "W",
                        "complex background" ,
                        "V,U",
                        "Asym",
                        "Y,X",
                        "Atom x y z",
                        "Pref,Bov",
                        "Biso-Atom",
                        "GausS,1G",
                        "Occ-Atom",
                        "Tempeture factors",
                        "S_L,D_L",
                        "manual background "
]

Param_Num_Order=range(0,len(Param_Order_Group))
target={}
#for the alias count
atom=-1
back=-1

order=[]
def name_to_alias(name="",fit=None):
    global atom
    global back
    name=name.replace("Sycos","Displacement")
    name=name.replace("Sysin","Transparency")
    name=name.replace("Lambda","Wavelength")
    name=name.replace("GausSiz","1G")
    name=name.replace("LorSiz","SZ")
    if name.find("BACK")!=-1:
        back+=1
    name=name.replace("BACK","BACK["+str(back)+"]")
    
    if name.find("B11")!=-1:
        atom+=1
    reobj=re.compile(r"B[0-9][0-9]")
    atom_name=fit.get("Phase")[0].get("Atom")[atom].get("Name")
    if reobj.search(name):
        name=name.replace("B","Atom["+atom_name+"]-B")
        
    return name


#get a order for the rietveld
def get_order(params,param_switch,param_order_num=Param_Num_Order,job=0):
    s=""
    global order
    order=[]#init order
    Param_Order=[]
    for i in param_order_num:
        Param_Order.extend(Param_Order_Group[i])	
    for i in range(0,len(Param_Order)):
        for j in range(0,len(params.paramlist)):
            s=params.alias[j]
            if (s.find(Param_Order[i])!=-1 and param_switch[j]==True):
                order.append(j)
                print "order-",s,param_switch[j]

        