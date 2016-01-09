'''strategy setting file, note: this is an important file. You should be careful when modifying the file.
   Please keep the format. 
   The words is case sensitive.
   You can modify parameters group order in 'param_order' and parameters group in 'param_group'.
'''
strategy={
    "neutron_tof":{
        # task type
        "type":"neutron_tof",
        # param group format: 'group_name':[ group_member1,group_member2,...]  
        "param_group":{
            'scale': ["Scale","Extinct"],
            'zero':  ["Transparency","Zero"],
            'simple background': ["BACK[0]"],
            'cell a,b,c':  ["a-Pha","b-P","c-P"],
            'W':     ["W-Pr"],
            'complex background': ["BACK"],
            "UVW":   ["Sig2-Pr", "Sig1-Pr","Sig0-Pr"],
            "Asym":  ["ALPH","BETA"],
            'Y,X':   ["Gam1-Pr","Gam2-Pr"],
            'Atom x y z':        ["X-Atom","Y-Atom","Z-Atom"],
            'Pref,Bov':          ["Pref","Bov"], 
            'Biso-Atom':         ["Biso-Atom"],
            'GausS,1G':          ["Z1","GausS","1G"],
            'Occ-Atom':          ["Occ-Atom"],
            'Tempeture factors': ["B1","B2","B3"],
            'D_H':               ["D_HG2","D_HL","Shift"],
            'S_L,D_L':           ["PA", "S_L","D_L"],
                                  #"Sysin","Displacement",
                                  #"Dtt1",                    # == "Sysin","Displacement",
                                  #"Gam0"                     # == "LorSiz","SZ",
                                  #"LStr","LSiz","Str",                                     
            'instrument':         ["Dtt2"#,"Sycos","Transparency"
                                  #"Str",
                                  ],
            "manual background": ["BCK"],
            'ABS':["ABS"]
                     },
        # param order format: [group_name1,group_name2,...]
        'param_order': [
            "scale",
            "cell a,b,c",
            "simple background" , 
            "zero",
            "Atom x y z",
            "Asym",
            "Biso-Atom",
            "complex background" ,
            "UVW",
            "Y,X",
            'D_H',
            "Pref,Bov",
            "GausS,1G",
            "instrument",
            "Occ-Atom",
            "Tempeture factors",
            "ABS",
            "manual background"            
        ]
        }
}