import os
doc=[
    "how to use? for example:  autofp -c 0 -a *.PCR",
    "-c n, run n cycles, cycle=0 represent auto-select the cycles number; cycle=n>0 represent run n cycles",
    "-a autoselect the parameters",
    "AutoFP version 1.3.x"
    ]
#----------------------------------------------------------------------
def show():
    """"""
    for i in doc:
        print (i)