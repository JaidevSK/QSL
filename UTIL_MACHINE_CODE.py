QG = {
    "RESET":    "0000",
    "H":        "0001",
    "T":        "0010",
    "X":        "0011",
    "Y":        "0100",
    "Z":        "0101",
    "S":        "0110",
    "MEASURE":  "0111",
    "CNOT":     "1000",
    "CZ":       "1001",
    "SWAP":     "1010",
}

CG = {
    "AND":      "000",
    "IOR":      "001",
    "XOR":      "010",
    "NOT":      "011",
    "NOR":      "100",
    "MOV":      "101",
    "SET":      "110",
    "CLR":      "111",
}

def BIN(x:int,n:int):
    if x<0:x=2**n +x
    assert x>=0
    assert x<=2**n
    x = bin(x)[2:]
    x ="0"*(n-len(x)) + x
    return x

def isNumeric(s:str):
    for x in s:
        if x not in "0123456789":
            return False
    return True

def SingleQubit(inst,PC,LABEL):
    """
    Example inputs :
    - ["H","0"]
    - ["MEASURE","1"]
    """
    gate,qb = inst
    func = QG[gate]
    assert isNumeric(qb)
    qs = BIN(int(qb),3)
    qt = "111"
    return "000" + qs + "000" + qt + "00" +func

def MultiQubit(inst,PC,LABEL):
    """
    Examples:
    ["CNOT","0","1"]
    """
    gate,qb1,qb2 = inst
    func = QG[gate]
    assert isNumeric(qb1)
    assert isNumeric(qb2)
    qs = BIN(int(qb1),3)
    qt = BIN(int(qb2),3)
    return "000" + qs + "000" + qt + "00" +func

def Classical(inst,PC,LABEL):
    """
    Examples:
    ["AND","0","0","0","0"]
    """
    gate,rs,sb,rt,tb = inst
    rs = BIN(int(rs),3)
    sb = BIN(int(sb),3)
    rt = BIN(int(rt),3)
    tb = BIN(int(tb),3)
    func = CG[gate]
    return "001" + rs + sb + rt + tb + func

def JPN(inst,PC,LABEL):
    """
    Example :["JPN",'0','0','label_to_go_to']
    """
    _,rs,sb,label = inst
    rs = BIN(int(rs),3)
    sb = BIN(int(sb),3)
    imm = LABEL[label]
    imm = imm #- (PC +1)
    imm = BIN(imm,9)
    return "010" + rs + sb +imm

def JPP(inst,PC,LABEL):
    """
    Example :["JPP",'0','0','label_to_go_to']
    """
    _,rs,sb,label = inst
    rs = BIN(int(rs),3)
    sb = BIN(int(sb),3)
    imm = LABEL[label]
    imm = imm #- (PC +1)
    imm = BIN(imm,9)
    return "011" + rs + sb +imm

def JMP(inst,PC,LABEL):
    """
    Example :["JMP",'label_to_go_to']
    """
    _,label = inst
    imm = LABEL[label]
    imm = BIN(imm,15)
    return "100" +imm

def LDB(inst,PC=None,LABEL=None):
    """
    Example : ["LDB",'0','0','1','13']
    """
    _,rs,sb,rt,imm = inst
    rs = BIN(int(rs),3)
    sb = BIN(int(sb),3)
    rt = BIN(int(rt),3)
    imm = BIN(int(imm),6)
    return "101" + rs + sb + rt + imm

def STB(inst,PC=None,LABEL=None):
    """
    Example : ["STB",'0','0','1','13']
    """
    _,rs,sb,rt,imm = inst
    rs = BIN(int(rs),3)
    sb = BIN(int(sb),3)
    rt = BIN(int(rt),3)
    imm = BIN(int(imm),6)
    return "110" + rs + sb + rt + imm

def NOP(inst,PC=None,LABEL=None):
    return "111" + "0"*15


FUNCTION = {
    #Q type
    "RESET":    SingleQubit,
    "H":        SingleQubit,
    "T":        SingleQubit,
    "X":        SingleQubit,
    "Y":        SingleQubit,
    "Z":        SingleQubit,
    "S":        SingleQubit,
    "MEASURE":  SingleQubit,
    "CNOT":     MultiQubit,
    "CZ":       MultiQubit,
    "SWAP":     MultiQubit,
    #R type
    "AND":      Classical,
    "IOR":      Classical,
    "XOR":      Classical,
    "NOT":      Classical,
    "NOR":      Classical,
    "MOV":      Classical,
    "SET":      Classical,
    "CLR":      Classical,
    #Control flow
    "JPN":      JPN,
    "JPP":      JPP,
    "JMP":      JMP,
    "LDB":      LDB,
    "STB":      STB,
    #Special
    "NOP":      NOP,
}

def ConvertToMachineCode(inst:str,PC:int,LABEL:dict):
    """
    Example:
    MOV(0,3,1,0)
    """
    inst = inst.strip()
    if inst[0]=="#":return ""
    inst = inst.split("(")
    assert len(inst)==2
    inst,arg = inst
    assert len(arg)>0
    assert arg[-1]==")"
    arg = arg[:-1]
    arg = [x.strip() for x in arg.split(",")]
    f = FUNCTION[inst]
    inst = [inst] + arg
    inst = f(inst,PC,LABEL)
    return inst

def ConvertInstructions(instructions:list[str]):
    return [ConvertToMachineCode(inst) for inst in instructions]

def ConvertProgram(P:str,fancy=False):
    P =P.split("\n")
    P = [inst.split("#")[0].strip() for inst in P]
    P = [
        [x.strip() for x in line.split(":")]
        for line in P
    ]
    labels = []
    newP = []
    for line in P:
        if line[-1]:
            newP.append(labels + line)
            labels = []
        else: labels.extend(line[:-1])
    if labels:newP.append(labels+["NOP()"])
    P = newP
    LABEL = {}
    for i,line in enumerate(P):
        inst = line[-1]
        labels = line[:-1]
        for lb in labels:
            assert lb not in LABEL
            LABEL[lb] = i
    newP = []
    M = []
    for PC,line in enumerate(P):
        inst = line[-1]
        labels = line[:-1]
        if not inst:continue
        ins = ConvertToMachineCode(inst,PC,LABEL)
        M.append(ins)
        newP.append(ins + f"\t[{inst.split('(')[0]}]("+ ",".join(labels) + ")")
    P = newP
    P = [f"{i}:{x}" for i,x in enumerate(P)]
    if fancy: return P
    else: return M

if __name__=="__main__":
    P ="""
    ok:   f:AND(0,0,1,1)
    label1: IOR(0,0,1,1)
    not ok: #stuff..
    abort mission: JPP(0,0,idgaf)
    more labels.. :
    """
    M = ConvertProgram(P,True)
    #for x in M:print(x)
    print(M)
