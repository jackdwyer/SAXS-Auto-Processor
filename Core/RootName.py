def changeInRootName(current, previous):
    current = current.split('_') #Spilts name in respective parts, and removes image number
    del current[-1] #Remove extension and image number
    
    previous = previous.split('_')
    del previous[-1]
    
    if (previous == current):
        return False
    else:
        return True
    

if __name__ == "__main__":
    changeInRootName("1A10_C1_BFIB_HMP_PH3_20_NACL_0363.dat", "1A10_C1_BFIB_HMP_PH3_20_NACL_0363.dat")
    result = 0
    """
    P1A1_WATER_0005.tif
    P1A1_WATER_0004.tif
    """ 
    print changeInRootName("P1A1_WATER_0005.tif", "P1A1_WATER_0004.tif")

    #Unit Tests
    
    #TEST 1 - Same Root Names
    #Expected Result - True
    test = changeInRootName("1A10_C1_BFIB_HMP_PH3_20_NACL_0363.dat", "1A10_C1_BFIB_HMP_PH3_20_NACL_0363.dat")
    #Should return False as tehre is no change
    if (test):
        print "TEST 1 - FAILED - SAME ROOT NAMES"
        result = result + 1

    else:
        print "TEST 1 - True - SAME ROOT NAMES"


    #TEST 2 - Different Root Names
    #Expected Result - False
    test = changeInRootName("P1A12_C2_BFIB_HMP_PH3_20_NACL_0433.dat", "water_cap2_0004.dat")
    if (test):
        print "TEST 2 - PASSED - DIFFERENT ROOT NAMES"
    else:
        print "TEST 2 - FAILED - DIFFERENT ROOT NAMES"
        result = result + 1



    l = ["P1A10_C1_BFIB_HMP_PH3_20_NACL_0363.dat", 
    "P1A10_C1_BFIB_HMP_PH3_20_NACL_0364.dat",
    "P1A10_C1_BFIB_HMP_PH3_20_NACL_0365.dat",
    "P1A10_C1_BFIB_HMP_PH3_20_NACL_0366.dat",
    "P1A11_HCL_PH3_20_NACL_0391.dat",
    "P1A11_HCL_PH3_20_NACL_0392.dat", 
    "P1A11_HCL_PH3_20_NACL_0393.dat", 
    "P1A11_HCL_PH3_20_NACL_0394.dat",
    "P1A12_C2_BFIB_HMP_PH3_20_NACL_0430.dat", 
    "P1A12_C2_BFIB_HMP_PH3_20_NACL_0431.dat",
    "P1A12_C2_BFIB_HMP_PH3_20_NACL_0432.dat",
    "P1A12_C2_BFIB_HMP_PH3_20_NACL_0433.dat",
    "P1A1_WATER_0023.dat",
    "P1A1_WATER_0024.dat",
    "P1A1_WATER_0025.dat",
    "P1A1_WATER_0146.dat",
    "P1A3_HCL_PH3_0196.dat",
    "P1A3_HCL_PH3_0197.dat",
    "P1A3_HCL_PH3_0198.dat",
    "P1A3_HCL_PH3_0199.dat",
    "water_cap2_0001.dat",
    "water_cap2_0002.dat",
    "water_cap2_0003.dat",
    "water_cap2_0004.dat"]
    
    #Test 3 - Blocks of 4 Root names that change
    v = 0
    n = 0
    for i in range(len(l)):
        #Should get 3 True then a False
        try:
            if (changeInRootName(l[i], l[i+1])):
                v = v + 1
            else:
                n = n + 1
                if (v == 3):
                    print "TEST 4 - Pass -> " + str(n)
                v = 0
                
        except:
            pass        

    if (n == 5):
        print "TEST 4 - PASSED"
    
    
    if (result > 0 and n != 5):
        print "SOME OR ALL TEST FAILED"


"""
String names for testing root name change

P1A10_C1_BFIB_HMP_PH3_20_NACL_0363.dat
P1A10_C1_BFIB_HMP_PH3_20_NACL_0364.dat
P1A10_C1_BFIB_HMP_PH3_20_NACL_0365.dat
P1A10_C1_BFIB_HMP_PH3_20_NACL_0366.dat

P1A11_HCL_PH3_20_NACL_0391.dat
P1A11_HCL_PH3_20_NACL_0392.dat
P1A11_HCL_PH3_20_NACL_0393.dat
P1A11_HCL_PH3_20_NACL_0394.dat

P1A12_C2_BFIB_HMP_PH3_20_NACL_0430.dat
P1A12_C2_BFIB_HMP_PH3_20_NACL_0431.dat
P1A12_C2_BFIB_HMP_PH3_20_NACL_0432.dat
P1A12_C2_BFIB_HMP_PH3_20_NACL_0433.dat

P1A1_WATER_0023.dat
P1A1_WATER_0024.dat
P1A1_WATER_0025.dat
P1A1_WATER_0146.dat

P1A3_HCL_PH3_0196.dat
P1A3_HCL_PH3_0197.dat
P1A3_HCL_PH3_0198.dat
P1A3_HCL_PH3_0199.dat

water_cap2_0001.dat
water_cap2_0002.dat
water_cap2_0003.dat
water_cap2_0004.dat
"""