#!/usr/bin/env python
##############################################################################
#
# diffpy.pyfullprof by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2010 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Wenduo Zhou
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

'''class FPOutFileParser -- FullProf output parser and several related
routines, such as prfParser and subParser.
'''
from __future__ import print_function

__id__ = "$Id: fpoutputfileparsers.py 6843 2013-01-09 22:14:20Z juhas $"


def prfParser(prffname):
    """
    parse Fullprof output .prf file as the plots of 
    2theta/TOF - (Yobs, Ycal, Yobs-Ycal)
    reflection list

    return  --  2-tuple (2-D array)
                reflection list
                X variable
                excluded region list
    """
    # 1. import file
    prffile = open(prffname, "r")
    lines   = prffile.readlines()
    prffile.close()

    # 2. determine the information
    patpointnum = -1
    phasenumber = -1
    reflpeaknum = -1
    infoline    = -1

    # 2.1 determine information line
    linecounter = 0
    for line in lines:
        if line.count("Yobs") == 2 and line.count("Ycal") == 2:
            infoline = linecounter
            break
        linecounter += 1
    if infoline < 0:
        errmsg = "prfParser():  Unable to find line ... Yobs Ycal Yobs-Ycal in File %-10s"% (prffname)
        raise NotImplementedError(errmsg)

    # 2.2 determine the X-axis variable
    diffunit = lines[infoline].strip().split()[0]

    # 2.3 excluded region
    excludedregions = []
    for lineindex in range(infoline-1, -1, -1):
        line  = lines[lineindex]
        terms = line.split("\n")[0].strip().split()
        if len(terms) == 2:
            st = float(terms[0])
            ed = float(terms[1])
            excludedregions.append( (st, ed) )
        else:
            break

    # 2.4.1 reflection list info, inherit line and terms from broken loop above
    refterms = terms

    # 2.5 diffraction pattern info
    lineindex = lineindex - 1
    terms     = lines[lineindex].split("\n")[0].strip().split()
    phasenumber = int(terms[0])
    patpointnum = int(terms[1])
    
    # 2.4.2
    if len(refterms) != phasenumber*2+1:
        errmsg = "prfParser():  Unrecognizable line:  should be < Reflection-Number, 0, 1>, now %-30s"% (line)
        raise NotImplementedError(errmsg)
    reflpeaknum = 0
    for pindex in range(phasenumber):
        reflpeaknum += int(refterms[pindex])

    # 3. Read diffraction
    listx    = []
    listyobs = []
    listycal = []
    listydif = []
    stline   = infoline+1
    edline   = stline+patpointnum-1
    for l in range(stline, edline+1):
        # 3.1 Split the line
        try:
            terms = lines[l].split("\n")[0].strip().split()
        except IndexError as err:
            print("Line %-5s"% (l))
            print(lines[l])
        # END-TRY

        # 3.2 Parse
        x     = float(terms[0])
        yobs  = float(terms[1])
        try:
            ycal  = float(terms[2])
        except ValueError as err:
            ycal  = 0.0
        try:
            ydif  = float(terms[3])
        except ValueError as err:
            ydif  = 0.0
        listx.append(x)
        listyobs.append(yobs)
        listycal.append(ycal)
        listydif.append(ydif)

    # LOOP-OVER

    # 4. read reflection
    reflections = []
    
    # 4.1 determine start line
    refmode = -1
    # a) search in the diffraction line
    stline = infoline+1
    terms = lines[stline].split("\n")[0].strip().split()
    if len(terms) > 5 and lines[stline].count(")") == 1:
        # good line is found
        refmode = 1
    else:
        stline = stline+patpointnum
        terms = lines[stline].split("\n")[0].strip().split()
        if len(terms) > 5 and lines[stline].count(")") == 1:
            # good line is found
            refmode = 2
    edline = stline+reflpeaknum-1

    # 4.2 read
    if refmode == -1:
        # cannot find reflection
        wmsg = "pcrParser()  Warning:  Reflection List Cannot Be Found" 
        print (wmsg)

    else:
        if refmode == 1:
            stcol = 5
        elif refmode == 2:
            stcol = 0
        else:
            errmsg = "pcrParser()  refmode = %-5s Not Allowed!"% (refmode)
            raise NotImplementedError(errmsg)

        for lineindex in range(stline, edline+1):
            terms = lines[lineindex].split("\n")[0].strip().split()
            refpos = float(terms[stcol])
            reflections.append(refpos)


    # 5.  organize return
    from numpy import array
    diffpatternarray = array([listx, listyobs, listycal, listydif])
    reflectionarray  = array(reflections)

    return ( (patpointnum, reflpeaknum, diffpatternarray, reflectionarray, diffunit, excludedregions) )


def subParser(rootname=None, phaseno=None, filename=None, thmin=None, thmax=None, step=None):
    """
    parse a simulated/calcualted sub file from FullProf

    Arguements:
    - rootname  :   string, file's root name (i.e., before COLFIL)
    - phaseno   :   integer, phase number
    - thmax
    - thmin
    - step

    Return      :   list of 2-tuple (or list) for a phase
    """
    # 1. generate the sub file name and read the file
    if (rootname is not None) and (phaseno is not None) and (filename is None):
        fname = rootname+str(phaseno)+".sub"
    elif filename is not None:
        fname = filename
    else:
        errmsg = "Input as:  filename = %-10s,  rootname = %-10s,  phaseno = %-10s is NOT Allowed"% \
            (filename, rootname, phaseno)
        raise NotImplementedError(errmsg)

    ifile = open(fname, "r")
    lines = ifile.readlines()
    ifile.close()
    numlines = len(lines)

    # 2. get file size information
    terms = lines[0].strip().split()
    if thmin is None:
        thmin = float(terms[0])
        step  = float(terms[1])
        thmax = float(terms[2])
    iphaseno = int(terms[-2])
    if iphaseno != phaseno and phaseno is not None:
        wmsg = "In-file Phase-No = %-5s Is Different From Input %-5s"% (iphaseno, phaseno)
        raise NotImplementedError(wmsg)
    
    # 3. get data pattern
    calpattern = []
    pindex     = 0
    for lindex in range(1, numlines):
        terms = lines[lindex].strip().split()
        for term in terms:
            calX = thmin+step*float(pindex)
            calY = float(term)
            calpattern.append( (calX, calY) )
            pindex += 1

    # 4. return 
    return calpattern


def parseHKLn(fullname, phaseno, singlepattern, patno, hklrange):
    """
    PyFullProf:  parse a FullProf HKL file 

    Idea:  get the parser from viewprf.py

    Arguments:
    hklfname    :   string, hkl file                        -- option 1
    rootname    :   string, root name of FullProf prcr file -- option 2
    phaseno     :   integer, phase number                   -- option 2

    Return      :   dictionary:  key = (h, k, l)    value = (peak position, multiplication)
    """
    import os
    basename = os.path.basename(fullname)
    rootname = os.path.splitext(basename)[0]
    processdir = fullname.split(basename)[0][:-1]
 
    # 1. process input parameters
    ifrootname = rootname + str(phaseno)
    ifname = processdir + "/" + ifrootname
    if singlepattern is True:
        ifname += ".hkl"
    else:
        ifname += "_"+str(patno)+".hkl"
    # END-IF-ELSE

    # 2. import file
    ifile = open(ifname, "r")
    rawlines = ifile.readlines()
    ifile.close()

    lines = []
    for rawline in rawlines:
        line = rawline.strip()
        if line != "":
            lines.append(line)
    # LOOP-OVER: for rawline in rawlines:

    # 3. interpret
    numlines = len(lines)
    reflectdict = {}
    for lindex in range(2, numlines):
        terms = lines[lindex].split()
        # FIXME - Cannot handle the situation when l and m are stuck together
        try:
            h = int(terms[0])
            k = int(terms[1])
            l = int(terms[2])
            m = int(terms[3])
            pos = float(terms[6])
            if hklrange == None:
                reflectdict[(h,k,l)] = (pos, m)
            elif hklrange["min"] <= pos and hklrange["max"] >= pos:
                reflectdict[(h,k,l)] = (pos, m)         
        except IndexError as err:
            pass
        except ValueError as err:
            pass
    # LOOP-OVER:  for lindex in range(2, numlines):

    # 4. return
    return reflectdict


class FPOutFileParser:
    """
    Parser class to read and interpret a Fullprof refine.out file
    """
    FirstblocklineFlag = "CYCLE No.:"
    LastblocklineFlag  = "Global user-weigthed Chi2 (Bragg contrib.):"
    PatternFlag     = "RELIABILITY FACTORS WITH ALL NON-EXCLUDED POINTS FOR PATTERN:"
    ResidueFlag     = "Conventional Rietveld Rp,Rwp,Re and Chi2:" 
    ConvergeFlag    = "Convergence reached at this CYCLE"
    ErrorFlag1      = "Singular matrix"
    ErrorFlag2      = "NO REFLECTIONS FOUND"

    def __init__(self, thisfit, outfilename):
        """
        initialization

        Arguments:
        - thisfit       :   PyFullProf.Fit
        - outfilename   :   str, .out file
        """
        self._myFit = thisfit

        # 2. init
        #xpc change the code begin
        #the raw code is
        #---------------------self._numcycles=thisfit.get("NCY")
        if(thisfit.get("Sho")==False):
            self._numcycles = thisfit.get("NCY")
        else:
            self._numcycles=1
        #xpc change the code end
        self._blocks = {}
        self._error  = False
        self._errmsg = None

        # 3. parse blocks
        self._parseToBlocks(outfilename)

        return

    
    def getStatus(self):
        """
        Report refinement status:  good or not
        """
        self._status = not self._error

        return self._status


    def getErrorReason(self):
        """
        Report the reason for error in Rietveld refinement
        """
        return self._errmsg


    def _parseToBlocks(self, outfilename):
        """
        Parase an out file to blocks for further data retrieval

        Argument:
        - outfilename   :   str

        Return          :   None
        """
        # 1. get file 
        outfile = open(outfilename, "r")
        rlines  = outfile.readlines()
        outfile.seek(0)
        xpc_context=outfile.read()
        XPC_ErrorFlag3="Strong DIVERGENCE"
        outfile.close()

        # 2. filter
        lines = []
        for line in rlines:
            cleanline = line.strip()
            if cleanline != "" and cleanline[0] == "=":
                lines.append(cleanline)
        self._lines = lines

        # 3. check last line: blocks or no blocks
        lastline  = self._lines[-1]
        errorcode = 0
        if lastline.count(self.ErrorFlag1) >= 1 or xpc_context.rfind(self.ErrorFlag1)!=-1:
            # Singular matrix
            self._error  = True
            self._errmsg = "Singular matrix"
            errorcode    = -1
        elif lastline.count(self.ErrorFlag2) >= 1 or xpc_context.rfind(self.ErrorFlag1)!=-1:
            # NO REFLECTIONS FOUND
            self._error   = True
            self._errmsg = "No Reflections Found"
            errorcode    = -3
        elif xpc_context.rfind(XPC_ErrorFlag3)!=-1:
            self._error=True
            self._errmsg= XPC_ErrorFlag3
            errorcode = -11
        # Internal function return
        if errorcode < 0:
            return 

        # 4. Put into block: Successful
        currline  = 0
        prevcycleno = 0
        breakflag = False
        self._goodRefine =  True
        for cindex in range(self._numcycles):
            # 1. search for start
            findFirstBlockLine = False
            noCycleBlock       = False
            numlines           = len(lines)
            while findFirstBlockLine == False and noCycleBlock == False:
                # 2.1 find line with flag 
                if lines[currline].count(self.FirstblocklineFlag) == 1:
                    # 3.1 record
                    firstlineindex = currline
                    cycleno = int(lines[currline].split(self.FirstblocklineFlag)[1])
                    findFirstBlockLine = True

                    # 3.2 judge whether this is a convergence reached
                    if cycleno == prevcycleno and lines[currline+1].count(self.ConvergeFlag) == 1:
                        self._numcycles = prevcycleno
                        breakflag = True

                # 2.2 adjust incremetn
                currline += 1
                if cindex == 0 and currline == numlines and findFirstBlockLine is False:
                    noCycleBlock = True
            # LOOP-OVER  while not findFirstBlockLine:

            if noCycleBlock is False:
                # 2. a convergence return (not refined to pre-determined cycle number)
                if breakflag is True:   
                    break

                # 3. search for last line
                findLastBlockLine = False
                while not findLastBlockLine:
                    if lines[currline].count(self.LastblocklineFlag) == 1:
                        lastlineindex = currline
                        findLastBlockLine = True
                    currline += 1

                # 3. store
                self._blocks[cindex] = (firstlineindex, lastlineindex)

                prevcycleno = cycleno

            else:
                # 2B: Error... 
                self._blocks[0] = (0, numlines-1)
                self._goodRefine =  False
                break

        # LOOP-OVER: for cindex in range(self._numclycles)

        # 5. Error message check
        if self._goodRefine is False:
            for line in lines:
                if line[0] == "=" and line.count("Excessive peak overlap") > 0:
                    self._numcycles = 0
                    self._error  =    True
                    self._errmsg =    "Excessive Peak Overlap"
                    break

        return


    def getNumCycles(self):
        """
        Get the number of least square refinement cycles

        Return  :   int
        """
        return self._numcycles


    def getResidues(self, cycleno):
        """
        Retrieve the residue values in a specific cycle 

        Arguments:
        - cycleno   :   int, 

        Return      :   4-tuple
        """
        if cycleno > self._numcycles:
            errmsg = "Fullprof did not run to cycle %-5s, real cycle number = %-5s"% (cycleno, self._numcycles)
            raise RietConfigurationError(errmsg)

        # 1. prepare infomation
        blockno = cycleno-1
        numpatterns = len(self._myFit.get("Pattern"))
        retlist = []
   
        # 2. get value
        startlineno = self._blocks[blockno][0]
        
   
        # 2.3 parse
        for pindex in range(numpatterns):
            flaglineindex = None
            #2.1 find pattern flag
            for lindex in range(startlineno, self._blocks[blockno][1]+1):
                if self._lines[lindex].count(self.PatternFlag) == 1:
                    flaglineindex = lindex
                    break
 
            # 2.2 find residue values line
            for lindex in range(flaglineindex, self._blocks[blockno][1]+1):
                if self._lines[lindex].count(self.ResidueFlag) == 1:
                    resline = self._lines[lindex]
                    startlineno = lindex
                    break

            digits = resline.split(self.ResidueFlag)[1].strip()
            terms = digits.split()
            if len(terms) == 4:
                Rp   = float(terms[0])
                Rwp  = float(terms[1])
                Re   = float(terms[2])
                Chi2 = float(terms[3])
            else:
                terms = {}
                print(digits, len(digits))
                for i in range(4):
                    terms[i] = ""
                    for j in range(9):
                        try:
                            terms[i] += digits[i*9+j]
                        except:
                            terms[i] += ""
                Rp   = float(terms[0])
                Rwp  = float(terms[1])
                Re   = float(terms[2])
                Chi2 = float(terms[3])

            retlist.append( (Rp, Rwp, Re, Chi2) )
            
        # LOOP-OVER: for pindex in range(numpatterns)

        return retlist

# END-CLASS FPOutFileParser
