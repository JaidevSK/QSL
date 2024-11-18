import numpy as np
from UTIL_MACHINE_CODE import *

class Q5Processor():
    def __init__(self, instrMem=[]):
        self.q = 5
        self.instrMem = instrMem
        self.dataMem = np.zeros(1024,dtype=bool)
        self.PC = 0
        self.IR = 0
        self.opcode = 0
        self.second3 = 0
        self.third3 = 0
        self.fourth3 = 0
        self.fifth3 = 0
        self.sixth3 = 0
        self.psi = np.zeros(2**self.q,dtype=np.complex128)
        self.psi[0] = 1+0j
        self.measure_bit = 0

    def burn(self,instrMem=[]):
        self.instrMem = instrMem
        for i in range(1024): self.dataMem[i] = 0
        self.PC = 0
        self.IR = 0
        self.opcode = 0
        self.second3 = 0
        self.third3 = 0
        self.fourth3 = 0
        self.fifth3 = 0
        self.sixth3 = 0
        self.psi = np.zeros(2**self.q,dtype=np.complex128)
        self.psi[0] = 1+0j
        self.measure_bit = 0

    def fetch(self):
        self.IR = self.instrMem[self.PC]
        self.opcode = self.IR[0:3]
        self.second3 = self.IR[3:6]
        self.third3 = self.IR[6:9]
        self.fourth3 = self.IR[9:12]
        self.fifth3 = self.IR[12:15]
        self.sixth3 = self.IR[15:18]
        self.PC += 1

    def decode_and_execute(self):
        if self.opcode == "000":
            self.Q_Type(self.second3, self.fourth3, self.fifth3+self.sixth3)
        elif self.opcode == "001":
            self.R_Type(self.second3, self.third3, self.fourth3, self.fifth3, self.sixth3)
        elif self.opcode == "010":
            self.JPN(self.second3, self.third3, self.fourth3+self.fifth3+self.sixth3)
        elif self.opcode == "011":
            self.JPP(self.second3, self.third3, self.fourth3+self.fifth3+self.sixth3)
        elif self.opcode == "100":
            self.JMP(self.second3+self.third3+self.fourth3+self.fifth3+self.sixth3)
        elif self.opcode == "101":
            self.LDB(self.second3, self.third3, self.fourth3, self.fifth3+self.sixth3)
        elif self.opcode == "110":
            self.STB(self.second3, self.third3, self.fourth3, self.fifth3+self.sixth3)
        else:self.NOP()

    def Q_Type(self, qs, qt, funct):
        QG = [
            self.RESET,         #0
            self.H,             #1
            self.T,             #2
            self.X,             #3
            self.Y,             #4
            self.Z,             #5
            self.S,             #6
            self.MEASURE,       #7
            self.CNOT,          #8
            self.CZ,            #9
            self.SWAP,          #10
        ]
        funct = int(funct,2)
        qs = int(qs,2)
        qt = int(qt,2)
        funct = QG[funct]
        funct(qs=qs,qt=qt)
        return
    
    def RESET(self,qs:int,qt=0):
        #ignore qt. Just measure qs
        self.MEASURE(qs,qt)
        if self.dataMem[self.measure_bit]:self.X(qs,qt)
        #psi0 = np.zeros(2**self.q,dtype=np.complex128)
        #psi1 = np.zeros(2**self.q,dtype=np.complex128)
        #for ps in range(2**self.q):
        #    PS = bin(ps)[2:]
        #    PS = "0"*(self.q - len(PS)) + PS
        #    coeff = self.psi[ps]
        #    if      PS[self.q - 1 - qs] == "0": psi0[ps] = coeff
        #    elif    PS[self.q - 1 - qs] == "1": psi1[ps] = coeff
        #    else: raise ValueError("ERRO in Measure")
        #prob0 = np.sum(np.abs(psi0)**2)
        #prob1 = np.sum(np.abs(psi1)**2)
        #psi0Norm = prob0**0.5
        #psi1Norm = prob1**0.5
        #psi0 = psi0/psi0Norm
        #psi1 = psi1/psi1Norm
        #self.psi = psi0

    def H(self,qs:int,qt=0):
        Gate = [
            [2**-0.5,2**-0.5],
            [2**-0.5,-2**-0.5],
            ]
        self.SingleQubitGate(qs,Gate)

    def T(self,qs:int,qt=0):
        Gate = [
            [1,0],
            [0,np.cos(np.pi/4)+1j*np.sin(np.pi/4)],
            ]
        self.SingleQubitGate(qs,Gate)

    def X(self,qs:int,qt=0):
        Gate = [
            [0,1],
            [1,0],
            ]
        self.SingleQubitGate(qs,Gate)

    def Y(self,qs:int,qt=0):
        Gate = [
            [0+0j,0-1j],
            [0+1j,0+0j],
            ]
        self.SingleQubitGate(qs,Gate)

    def Z(self,qs:int,qt=0):
        Gate = [
            [1+0j,0-0j],
            [0+0j,-1+0j],
            ]
        self.SingleQubitGate(qs,Gate)

    def S(self,qs:int,qt=0):
        Gate = [
            [1,0],
            [0,1j],
            ]
        self.SingleQubitGate(qs,Gate)

    def MEASURE(self,qs:int,qt=0):
        #ignore qt. Just measure qs
        psi0 = np.zeros(2**self.q,dtype=np.complex128)
        psi1 = np.zeros(2**self.q,dtype=np.complex128)
        for ps in range(2**self.q):
            PS = bin(ps)[2:]
            PS = "0"*(self.q - len(PS)) + PS
            coeff = self.psi[ps]
            if      PS[self.q - 1 - qs] == "0": psi0[ps] = coeff
            elif    PS[self.q - 1 - qs] == "1": psi1[ps] = coeff
            else: raise ValueError("ERRO in Measure")
        prob0 = np.sum(np.abs(psi0)**2)
        prob1 = np.sum(np.abs(psi1)**2)
        psi0Norm = prob0**0.5
        psi1Norm = prob1**0.5
        if psi0Norm == 0:
            self.psi =psi1/psi1Norm
            self.dataMem[self.measure_bit] = 1
            return
        elif psi1Norm == 0:
            self.psi =psi0/psi0Norm
            self.dataMem[self.measure_bit] = 0
            return
        psi0 = psi0/psi0Norm
        psi1 = psi1/psi1Norm
        x = np.random.random()
        if x < prob0 :
            self.psi =psi0
            self.dataMem[self.measure_bit] = 0
        else:
            self.psi =psi1
            self.dataMem[self.measure_bit] = 1

    def CX(self,qs:int,qt:int):
        Gate = [
            [1,0,0,0],
            [0,1,0,0],
            [0,0,0,1],
            [0,0,1,0],
        ]
        self.DoubleQubitGate(qs,qt,Gate)

    def CNOT(self,qs:int,qt:int):
        self.CX(qs,qt)

    def CZ(self,qs:int,qt:int):
        Gate = [
            [1,0,0,0],
            [0,1,0,0],
            [0,0,1,0],
            [0,0,0,-1],
        ]
        self.DoubleQubitGate(qs,qt,Gate)

    def SWAP(self,qs:int,qt:int):
        Gate = [
            [1,0,0,0],
            [0,0,1,0],
            [0,1,0,0],
            [0,0,0,0],
        ]
        self.DoubleQubitGate(qs,qt,Gate)

    def DoubleQubitGate(self,qs:int,qt:int,Gate):
        psid = np.zeros(2**self.q,dtype=np.complex128)
        for ps in range(2**self.q):
            PS = bin(ps)[2:]
            PS = "0"*(self.q - len(PS)) + PS
            #This is in big endian notation (MSB on left)
            coeff = self.psi[ps]
            #State_qt_qs
            State_00 = list(PS)
            State_01 = list(PS)
            State_10 = list(PS)
            State_11 = list(PS)

            State_00[self.q-1-qs]="0"
            State_01[self.q-1-qs]="1"
            State_10[self.q-1-qs]="0"
            State_11[self.q-1-qs]="1"

            State_00[self.q-1-qt]="0"
            State_01[self.q-1-qt]="0"
            State_10[self.q-1-qt]="1"
            State_11[self.q-1-qt]="1"

            State_00=int("".join(State_00),2)
            State_01=int("".join(State_01),2)
            State_10=int("".join(State_10),2)
            State_11=int("".join(State_11),2)

            qs_val = int(PS[self.q-1-qs])
            qt_val = int(PS[self.q-1-qt])
            ps2_val = qt_val*2 + qs_val
            out2_val = [Gate[i][ps2_val] for i in range(len(Gate))]
            psid[State_00] = psid[State_00] + coeff * out2_val[0]
            psid[State_01] = psid[State_01] + coeff * out2_val[1]
            psid[State_10] = psid[State_10] + coeff * out2_val[2]
            psid[State_11] = psid[State_11] + coeff * out2_val[3]
        self.psi = psid

    def SingleQubitGate(self,qs:int,Gate):
        #ignore qt. Just do H qs
        psid = np.zeros(2**self.q,dtype=np.complex128)
        for ps in range(2**self.q):
            PS = bin(ps)[2:]
            PS = "0"*(self.q - len(PS)) + PS
            #This is in big endian notation (MSB on left)
            coeff = self.psi[ps]
            up = list(PS)
            down = list(PS)
            up[self.q-1-qs] = '1'
            down[self.q-1-qs] = '0'
            up = "".join(up)
            down = "".join(down)
            up = int(up,2)
            down = int(down,2)
            if PS[self.q-1-qs]  == "0":
                psid[down] = psid[down] + coeff * Gate[0][0]
                psid[up]   = psid[up]   + coeff * Gate[1][0]
            elif PS[self.q-1-qs]  == "1":
                psid[down] = psid[down] + coeff * Gate[0][1]
                psid[up]   = psid[up]   + coeff * Gate[1][1]
            else:
                raise ValueError("ERROR in SingleQubitGate")
        self.psi = psid

    def R_Type(self, rs, sb, rt, tb, funct):
        funct = int(funct,2)
        rs = int(rs,2)
        rt = int(rt,2)
        sb = int(sb,2)
        tb = int(tb,2)
        assert 0 <= rs and rs < 32
        assert 0 <= rt and rt < 32
        assert 0 <= sb and sb < 32
        assert 0 <= tb and tb < 32
        x =32*rs + sb
        y =32*rt + tb
        X = self.dataMem[x]
        Y = self.dataMem[y]
        CG = [
            (X and Y), #AND,
            (X or Y), #IOR,
            (X and (not Y)) or ((not X) and Y), #XOR,
            not X, #NOT,
            not (X or Y), #NOR,
            Y, #MOV,
            True, #SET,
            False, #CLR,
        ]
        self.dataMem[x] = CG[funct]

    def AND(self,rs,rt,sb,tb):
        x = rs*32 #register
        x = x + sb #bit
        y = rt*32 +tb
        self.dataMem[x] = (self.dataMem[x] and self.dataMem[y])

    def IOR(self,rs,rt,sb,tb):
        x = rs*32 #register
        x = x + sb #bit
        y = rt*32 +tb
        self.dataMem[x] = (self.dataMem[x] or self.dataMem[y])

    def NOR(self,rs,rt,sb,tb):
        x = rs*32 #register
        x = x + sb #bit
        y = rt*32 +tb
        self.dataMem[x] = not (self.dataMem[x] or self.dataMem[y])

    def XOR(self,rs,rt,sb,tb):
        x = rs*32 #register
        x = x + sb #bit
        y = rt*32 +tb
        self.dataMem[x] = (self.dataMem[x] and not self.dataMem[y]) or (not self.dataMem[x] and self.dataMem[y])

    def MOV(self,rs,rt,sb=0,tb=0):
        x = rs*32 #register
        x = x + sb #bit
        y = rt*32 +tb
        self.dataMem[x] = self.dataMem[y]

    def SET(self,rs,rt,sb=0,tb=0):
        x = rs*32 #register
        x = x + sb #bit
        self.dataMem[x] = True

    def CLR(self,rs,rt,sb=0,tb=0):
        x = rs*32 #register
        x = x + sb #bit
        self.dataMem[x] = False

    def JPN(self, rs, sb, imm):
        rs = int(rs,2)
        sb = int(sb,2)
        x = 32*rs + sb
        X = self.dataMem[x]
        if not X:self.PC = int(imm,2)

    def JPP(self, rs, sb, imm):
        rs = int(rs,2)
        sb = int(sb,2)
        x = 32*rs + sb
        X = self.dataMem[x]
        if X:self.PC = int(imm,2)

    def JMP(self, imm):
        self.PC = int(imm,2)

    def LDB(self, rs, sb, rt, imm):
        rs = int(rs,2)
        rt = int(rt,2)
        sb = int(sb,2)
        imm = int(imm,2)
        if imm >= 2**5:imm = 2**6 - imm
        p = 1
        for i in range(32):
            if self.dataMem[32*rt + i]: imm +=p
            p = p*2
        x = 32*rs + sb
        self.dataMem[x] = self.dataMem[imm]

    def STB(self, rs, sb, rt, imm):
        rs = int(rs,2)
        rt = int(rt,2)
        sb = int(sb,2)
        imm = int(imm,2)
        if imm >= 2**5:imm = 2**6 - imm
        p = 1
        for i in range(32):
            if self.dataMem[32*rt + i]: imm +=p
            p = p*2
        x = 32*rs + sb
        self.dataMem[imm] = self.dataMem[x]

    def NOP(self):
        pass
    
    def step(self):
        self.fetch()
        self.decode_and_execute()

    def run(self):
        while self.PC < len(self.instrMem):
            self.step()
            # print(self)

    def __repr__(self,include_imem=True):
        S = ""
        #S = "-"*50
        sv = []
        for i,x in enumerate(self.psi):
            if x==0+0j:continue
            X = f"{np.around(x,2)}|{i}⟩"
            sv.append(X)
        sv = " + ".join(sv)
        S += "  ψ = " +  sv
        S += f"\n\n  PC : {self.PC}"
        if include_imem:
            S += "\n\n Instruction Memory:"
            IM = [f"{i} : {x}" for i,x in enumerate(self.instrMem)]
            S += "\n" + "\n".join(IM)
        DM = [['1' if self.dataMem[x] else '0' for x in range(32*y,32*y+32)] for y in range(32)]
        # DM = [f"${i}\t: " + "".join(x)[::-1] for i,x in enumerate(DM)]
        DM1 = []
        for i,x in enumerate(DM):
            if i == 0: 
                DM1.append(f"MEASUREMENT BUFFER ($0): " + "".join(x)[::-1])
                DM1.append("-"*50)
                DM1.append("\nREGISTER FILE:")
            elif i<8:
                DM1.append(f"${i}\t: " + "".join(x)[::-1])
            else:
                if i == 8:
                   DM1.append("-"*50)
                   DM1.append("\nDATA MEMORY:")
                DM1.append(f"s{i}\t: " + "".join(x)[::-1])


        DM = DM1
        DM = "\n  ".join(DM)
        S += "\n  " + DM
        S += "\n" + '-'*50
        S += "\n\nInstruction Memory:"
        # IM = [f" {i} : {x}" for i,x in enumerate(self.instrMem)]
        IM = []
        for i,x in enumerate(self.instrMem):
            IM.append(f"{i}\t: {x}")
        IM.append(f"{len(self.instrMem)}\t: "+"1"*18)
        S += "\n" + "\n".join(IM)

        # S += "\n\n Data Memory:\n  " + DM
        #S += "\n" + '-'*50
        return S

    def latex(self):
        S = []
        sv = []
        for i,x in enumerate(self.psi):
            if x==0+0j:continue
            X = f"{np.around(x,2)}|{i}" + r"\rangle"
            sv.append(X)
        sv = " + ".join(sv)
        S.append(r"\Psi = " +  sv)
        S.append(r"\kappa = " + str(self.PC))
        #IM = [f"{i} & [{x}]" for i,x in enumerate(self.instrMem)]
        #IM.append(r"\text{halt}")
        #IM = (r"\\" + "\n").join(IM)
        #S.append(r"P = \begin{bmatrix}" + "\n" + IM + "\n" + r"\end{bmatrix}")
        DM = [['1' if self.dataMem[x] else '0' for x in range(32*y,32*y+32)] for y in range(32)]
        DM = [f"s{i} & [" + "".join(x)[::-1] + "]" for i,x in enumerate(DM)]
        DM =(r"\\" + "\n").join(DM)
        S.append("C = \n"+r" \begin{bmatrix}" + DM +r"\end{bmatrix}")
        S = ["-"*10] + S + ["-"*10]
        S = r"$$ \begin{bmatrix}"+ (r"\\"+"\n").join(S) +r"\end{bmatrix} $$"
        return S

    def RunAtoZ(self,use_latex=False,limit=1000000):
        self.burn(self.instrMem)
        if use_latex:H = [(self.latex(),self.PC)]
        else: H = [(self.__repr__(False),self.PC)]
        i = 0
        while self.PC < len(self.instrMem):
            if i > limit:raise ValueError(f"The program has more than {limit} steps!!")
            self.step()
            i += 1
            if use_latex:H.append((self.latex(),self.PC))
            else:H.append((self.__repr__(False),self.PC))
        return H
            
if __name__=="__main__":
    #P =[
    #    "001000000001001000",
    #    "001000000001001001",
    #    "011000000111111110",
    #    "111000000000000000",
    #]
    P ="""
    SET(0,0,0,2)
    SET(1,1,0,2)
    ok:   f:AND(0,0,1,1)
    label1: XOR(0,0,1,1)
    not ok: #stuff..
    abort mission: JPN(0,0,idgaf)
    """
    P = ConvertProgram(P)
    print(P)
    QP = Q5Processor(P)
    #QP.H(0,0)
    #QP.CNOT(0,1)
    #QP.MEASURE(0,0)
    print(QP)
    QP.run()
    print(QP)
