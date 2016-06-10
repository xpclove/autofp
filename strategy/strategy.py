'''strategy setting file, note: this is an important file. You should be careful when modifying the file.
   Please keep the format. 
   The words is case sensitive.
   You can modify parameters group order in 'param_order' and parameters group in 'param_group'.
'''
strategy={
    "xray":{
        # task type
        "type":"xray",
        # param group format: 'group_name':[ group_member1,group_member2,...]  
        "param_group":{
            'scale': ["Scale"],
            'zero':  ["Transparency","Zero"],
            'simple background': ["BACK[0]","BACK[1]"],
            'cell a,b,c':  ["a-Pha","b-P","c-P"],
            'W':     ["W-Pr"],
            'complex background': ["BACK"],
            "V,U":   ["V-Pr", "U-Pr"],
            "Asym":  ["PA"],
            'Y,X':   ["Y-Pr","X-Pr"],
            'Atom x y z':        ["X-Atom","Y-Atom","Z-Atom"],
            'Pref,Bov':          ["Pref","Bov"], 
            'Biso-Atom':         ["Biso-Atom"],
            'GausS,1G':          ["GausS","1G"],
            'Occ-Atom':          ["Occ-Atom"],
            'Tempeture factors': ["B1","B2","B3"],
            'S_L,D_L':           ["PA", "S_L","D_L",
                                  #"Sysin","Displacement",
                                  #"LorSiz","SZ",
                                  #"Sycos","Transparency",
                                  #"Str",
                                  ],
            "manual background": ["BCK"]
                     },
        # param order format: [group_name1,group_name2,...]
        'param_order': [
            "scale",
            "zero",
            "simple background" , 
            "cell a,b,c",
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
            "manual background"            
        ],
        'target':'MIN=R_Factor["Rwp"]'
        }
}