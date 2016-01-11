'''strategy setting file, note: this is an important file. You should be careful when modifying the file.
   Please keep the format. 
   The words is case sensitive.
   You can modify parameters group order in 'param_order' and parameters group in 'param_group'.
'''
strategy={
    "neutron_cw":{
        # task type
        "type":"neutron_cw",
        # param group format: 'group_name':[ group_member1,group_member2,...]  
        "param_group":{
            'scale': ["Scale"],
            'zero':  ["Zero"],
            'simple background': ["BACK[0]"],
            'cell a,b,c':  ["a-Pha","b-P","c-P"],
            'W':     ["W-Pr"],
            'complex background': ["BACK"],
            "U,V,W":   ["U-Pr","V-Pr","W-Pr"],
            "Asym":  ["PA"],
            'Y,X':   ["Y-Pr","X-Pr"],
            'Atom x y z':        ["X-Atom","Y-Atom","Z-Atom"],
            'Pref,Bov':          ["Pref","Bov"], 
            'D_H':               ["D_HG2","D_HL","Shift"],
            'Biso-Atom':         ["Biso-Atom"],
            'GausS,1G':          ["GausS","1G"],
            'Occ-Atom':          ["Occ-Atom"],
            'Anisotropic Thermal factors': ["B1","B2","B3"],
            'S_L,D_L':           ["PA", "S_L","D_L"],
            'instrument':        [#"Sysin",             #"Displacement",
                                  #"LorSiz",            #"SZ",
                                  "Sycos","Transparency",
                                  #"Str",
                                  ],
            "manual background": ["BCK"]
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
            "U,V,W",
            "Y,X",
            "D_H",
            "Pref,Bov",
            "GausS,1G",
            "instrument",
            "Occ-Atom",
            "Anisotropic Thermal factors",
            "manual background"            
        ]
        }
}