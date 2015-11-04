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

__id__ = "$Id: stringop.py 6843 2013-01-09 22:14:20Z juhas $"
from diffpy.pyfullprof.exception import RietPCRError
    
_WARNINGOUTPUT = False
_DEBUGOUTPUT = False

class StringOP:
    """ Some operations on string
    Applied to parse Fullprof pcr files
    """
    def __init__(self):
        """ Initialization of StringOP
        """
        pass

    def SplitString(s, c):
        """ Split a string s by character c, ' ', '\n' and '\t'

        return a list of terms which are either string, string for valid integer, 
        or string for valid float

        Argument:
        - s:  string to split
        - c:  special character
        """
        try:
            list1 = s.split(c)  
        except Exception, err:
            raise RietPCRError(str(err))
        """
        print "step 1"
        for word in list1: 
            print word
        """

        list2 = []
        for word in list1:
            try:
                templist = word.split()
            except Exception, err:
                raise RietPCRError(s)
            for subw in templist:
                # check subw
                if isValidDataOrString(subw):
                    # append
                    list2.append(subw)
                else:
                    # split subw
                    subwords = Split2GluedNumerical(subw)
                    for subsubw in subwords:
                        list2.append(subsubw)

        return list2

    SplitString = staticmethod(SplitString)


"""
External Function
"""
def allNumericalCharacter(tstring):
    """
    return True if string only contains
    (1) '0' - '9'
    (2) .
    (3) +
    (4) -

    tstring:    string to test
    """
    notnumerical = False

    # general scan
    for c in tstring:
        if (c < '0' or c > '9') and c != '+' and c != '-' and c != '.' and c != 'E':
            notnumerical = True
            break;

    # check E
    if not notnumerical:
        for pos in xrange(len(tstring)):
            if tstring[pos] == 'E':
                if pos < len(tstring)-1:  # not last position
                    if tstring[pos+1] != '+' and tstring[pos+1] != '-':
                        notnumerical = False
                        break
                else:
                    notnumerical = False

    if notnumerical:
        return False
    else:
        return True


def isValidDataOrString(tstring):
    """
    return True if string tstring is a valid string for 
    (1) string (with letters)
    (2) integer
    (3) float

    tstring:    a string to test
    """

    # exception case 1:  tstring is composed of '0-9','+','-',and '.' only and
    # (1) '+' or '-' are not at the beginning or
    # (2) has >= 2 '.'

    if allNumericalCharacter(tstring):
        # 1. check last position of +, -, number of '.'
        posplus  = -1
        posminus = -1
        numdot   = 0
        numE     = 0
        for p in xrange(len(tstring)):
            if tstring[p] == '+':
                posplus = p
            elif tstring[p] == '-':
                posminus = p
            elif tstring[p] == '.':
                numdot += 1
            elif tstring[p] == 'E':
                numE   += 1

        # validate
        valid = True
        if posplus > 0:
            if tstring[posplus-1] != 'E':
                valid = False

        if posminus > 0:
            if tstring[posminus-1] != 'E':
                valid = False
        
        if numdot > 1 or numE > 1:
            valid = False

        if not valid:
            if _DEBUGOUTPUT:
                print "Find the bastard.... " + tstring
            return False
        
    return True


def Split2GluedNumerical(tstring):
    """
    split N 'glued' numerical (integer or float) (such that they are stuck together)

    Example: 0.74735E-03-0.23554E-04-0.60930E-06

    return  --

    tstring --  string, two numerical stuck together  
    """
    numE = tstring.count("E")
    rlist = []

    if numE <= 2:
        # Split 2 glued numerical

        # 1. use internal "+", "-" sign to split
        posplus  = -1
        posminus = -1

        for pos in xrange(len(tstring)):
            if tstring[pos] == '-' and pos != 0:
                if tstring[pos-1] != 'E':
                    posminus = pos
            elif tstring[pos] == '+' and pos != 0:
                if tstring[pos-1] != 'E':
                    posplus = pos

        if posplus > 0:

            s1 = ""
            s2 = ""
            for pos in xrange(0, posplus):
                s1 += tstring[pos]
            for pos in xrange(posplus, len(tstring)):
                s2 += tstring[pos]

            rlist.append(s1)
            rlist.append(s2)

        elif posminus > 0:
            s1 = ""
            s2 = ""
            for pos in xrange(0, posminus):
                s1 += tstring[pos]
            for pos in xrange(posminus, len(tstring)):
                s2 += tstring[pos]

            rlist.append(s1)
            rlist.append(s2)  
            
        else:
            # use the heuristic that in FullProf the digit is either 5 or 6: say x.xxxxxx.xxx
            if tstring.count(".") == 2:
                # split the string, split the middle string to 5-.. or 6-...
                substring = tstring.split(".")
                if substring[1][5] != '0':
                    spoint = 5
                else:
                    spoint = 6
                # split middle string according spoint
                s1 = ""
                for i in xrange(0, spoint):
                    s1 += substring[1][i]
                s2 = ""
                for i in xrange(spoint, len(substring[1])):
                    s2 += substring[1][i]
                #except Exception, err:
                #    print str(err)
                #    for s in substring:
                #        print s
                #    print "i = " + str(i)
                # combine string 
                t1 = substring[0]+"."+s1
                t2 = s2+"."+substring[1]

                rlist = []
                rlist.append(t1)
                rlist.append(t2)

                mstring = "Split string ' %-30s ' to ' %-30s ' and ' %-30s '"%(tstring, t1, t2)
                print mstring

            else:
                emsg = ("Cannot deal with glued string " + tstring +
                        " in stringop.Split2GluedNumerical.")
                raise RietPCRError(emsg)

    else:
        # more than 2 numerics stuck together
        # they are in scientific representation, i.e., num(E) = num(.)
        # Example: 0.74735E-03-0.23554E-04-0.60930E-06
        terms   = tstring.split(".")
        preterm = terms[0]
        for n in xrange(numE):
            numpm = terms[n+1].count("+")+terms[n+1].count("-")
            if numpm == 2:
                lenstring = len(terms[n+1])
                # find position of last + or -
                for i in xrange(1, lenstring+1):
                    if not terms[n+1][lenstring-i].isdigit():
                        seppos = lenstring-i
                        break
                part2 = terms[n+1][0:seppos]
                nextterm = terms[n+1][seppos:lenstring]
            else:
                part2 = terms[n+1]
            floatstring = preterm+"."+part2
            preterm = nextterm

            rlist.append(floatstring)

        # LOOP-OVER for n in xrange(numE)
         
    # END-IF-ELSE

    if _WARNINGOUTPUT is True:
        msg = "Floats Stick Together: %-10s --> " % ( tstring )
        for r in rlist:
            msg += "%-10s  " % (r)
        print msg

    return rlist


def parseLineToDict(line, seplist, startflag = None):
    """ Parse a line with key word and value and to a dictionary. 

    Argument
      - line        :   str
      - seplist     :   list of string
      - startflag   :   str.  If not none, the line must start with this

    Return  :   list
    """
    # 1. Remove start-flag
    if startflag is not None:
        pline = line.split(startflag)[1]
    else:
        pline = line

    # 2. Separate line with all separation flag
    terms = [pline]
    for sepflag in seplist:
        newterms = []
        for origterm in terms:
            septerms = origterm.split(sepflag)
            newterms.extend(septerms)
        terms = newterms
    # LOOP-OVER

    # 3. Conver to key and value
    valuelist = []
    for i in range( 1, len(terms) ):
        newval = parseValue( terms[i], ["(", ")"] )
        valuelist.append( newval )

    return valuelist


def parseValue( interm, uncertaintyflag = None ):
    """ Read a value out of a string 
    The string starts with this value, and the value can be 
      - xxx
      - xxx (yyy)

    Argument:
      - interm  :   str
      - uncertaintyflag :   list nor None

    Return  :   2-tuple
    """
    # 1. Get value term and uncertainty term (possible)
    if uncertaintyflag is not None:
        terms = interm.split(uncertaintyflag[0])
        valueterm = terms[0].strip()
        testterm = interm.split()[0].strip()

        # print "3:51  ", valueterm, len(valueterm), testterm, len(testterm)
        # print "3:58  ", str(terms)

        if len( terms ) == 1:
            # a) no such flag exits
            nouncertainty = True
            valueterm = testterm

        else:
            # b) with uncertainty-flag existing
            if len(valueterm) <= len(testterm):
                # b1. term before flag is shorter than term before space
                #     this means that the term before flag is a value
                #     and there is uncertainty given 
                nouncertainty = False
                try:
                    uncertaintyterm = terms[1].split( uncertaintyflag[1] )[0].strip()
                except IndexError, err:
                    errmsg = "Terms = %-20s   No flag %-5s Inside" % \
                            (terms, uncertaintyflag[0])
                    raise NotImplementedError, errmsg
                # END-TRY-EXCEPT

            else:
                # b2. term before flag is longer than term before space
                #     this means that the term before flag contains more than a simple value
                #     it is not within pattern defined.  so no uncertainty is given
                nouncertainty = True
                valueterm = testterm

            # END-IF-ELSE
        # END-IF-ELSE

    else:
        valueterm = interm.split()[0]
        nouncertainty = True

    # END-IF-ELSE
        
    try:
        newvalue = float( valueterm )
        if nouncertainty is False:
            newuncert = float( uncertaintyterm )
        else:
            newuncert = None
    except ValueError, err:
        errmsg = "value term = %-10s   test term = %-10s" % \
                (valueterm, testterm)
        raise RietPCRError(errmsg)
        
    return ( (newvalue, newuncert) )
