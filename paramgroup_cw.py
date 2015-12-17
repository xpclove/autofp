import re
Param_Group=[
    ["Profile","Background","Contribution","Phase"],
    ["Pattern"],
    ["Atom"],
    ["AtomicDisplacementFactor"],
    ["StrainParameter","PreferOrient","AsymmetryParameter","SpecialReflection"],
    ["Atom_Occ"]
    ]
Param_Order_Group_Name=[
                        "Scale",
                        "a b c",
                        "simple background",
                        "Zero",
                        "Atom",
                        "Asym",
                        "complex background",
                        "U,V,W",
                        "Y,X",
                        "D_HG2,D_HL,Shift",
                        "Pref,Tempeture factors,Occ"]

Param_Order_Group=[
    ["Scale"],
    ["a-Pha","b-P","c-P"],
    ["BACK[0]"],
    ["Zero"],
    ["X-Atom","Y-Atom","Z-Atom"],
    ["PA","Biso-Atom",],
    ["BACK"],
    ["U-Pr","V-Pr","W-Pr"],
    ["Y-Pr","X-Pr"],
    ["D_HG2","D_HL","Shift"],
    ["Pref","Bov", 
    "GausS","1G",
    "Sycos","Transparency",
    "Occ-Atom",
    "B1","B2","B3",
    #"S_L","D_L",
    #"Sysin","Displacement",
    #"LorSiz","SZ",
    #"Str",
    "BCK"
    ]
    ]
Param_Num_Order=range(0,len(Param_Order_Group))
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
        name=name.replace("B","Atom["+str(atom_name)+"]-B")
        
    return name


#get a order for the rietveld
def get_order(params,param_switch,param_order_num=Param_Num_Order):
    s=""
    global order
    order=[] # init the order[]
    Param_Order=[]
    for i in param_order_num:
        Param_Order.extend(Param_Order_Group[i])	
    for i in range(0,len(Param_Order)):
        for j in range(0,len(params.paramlist)):
            s=params.alias[j]
            if (s.find(Param_Order[i])!=-1 and param_switch[j]==True ):
                order.append(j)

