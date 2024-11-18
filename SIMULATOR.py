from UTIL_MACHINE_CODE import *
from UTIL_DECODER import *
import tkinter as tk
from tkinter import filedialog
from sympy import preview
import traceback
import UTIL_CLOPS as CLOPS

if __name__ == "__main__":
    parent = tk.Tk()
    parent.title("QSL Simulator")
    QP = Q5Processor()
    PVerbose = "0:halt"

    def ThrowError():
        # rep = traceback.format_exc()
        rep = "YOU HAVE COME OUT OF THE MEMORY\nPLEASE RESTART THE SIMULATOR"
        output.delete("1.0",'end')
        output.insert("end",rep)
        output.configure(bg='red')
        output.bg = 'red'

    def Render(S):
        output.delete("1.0",'end')
        output.insert('end',S)
        output.configure(bg='grey')
        output.bg = 'grey'

    def compute():
        global stage,H,PVerbose,line
        try:
            compiled_program.delete("1.0",'end')
            S = og_program.get("1.0","end-1c")
            P = ConvertProgram(S,False)
            QP.burn(P)
            PVerbose = ConvertProgram(S,True)
            PVerbose.extend([f"{len(PVerbose)}:111111111111111111 [HLT]()"]+[f"{len(PVerbose)+1+i}:" for i in range(5)])
            P = PVerbose.copy()
            if QP.PC < len(P):P[QP.PC] = "CURR→" + P[QP.PC]
            P = "\n".join(P)
            compiled_program.insert("end",P)
            S = QP.__repr__(False)
            Render(S)
            output.configure(bg='grey')
            output.bg = 'grey'
            stage = 0
            line = 0
            H = [(S,0)]

        except:
            ThrowError()
            stage = 0
            line = 0
            H = []

    def step():
        global stage,H,PVerbose,line
        try:
            if stage < len(H)-1:
                stage += 1
                S,line = H[stage]
                Render(S)
            else:
                QP.step()
                line = QP.PC
                S = QP.__repr__(False)
                H.append((S,line))
                Render(S)
                stage+=1
            P = PVerbose.copy()
            if line < len(P): P[line] = "CURR→" + P[line]
            P = "\n".join(P)
            compiled_program.delete("1.0",'end')
            compiled_program.insert("end",P)
            output.configure(bg='grey')
            output.bg = 'grey'
        except:ThrowError()

    def run():
        global stage,H,PVerbose,line
        try:
            H = QP.RunAtoZ()
            stage = len(H)-1
            S,line = H[stage]
            Render(S)
            P = PVerbose.copy()
            if line < len(P): P[line] = "CURR→" + P[line]
            P = "\n".join(P)
            compiled_program.delete("1.0",'end')
            compiled_program.insert("end",P)
            output.configure(bg='grey')
            output.bg = 'grey'
        except:ThrowError()

    def prev():
        global stage,H,PVerbose,line
        try:
            if stage > 0:
                stage -= 1
                S,line = H[stage]
                Render(S)
            else:raise ValueError("Cannot go back from initial stage")
            P = PVerbose.copy()
            if line < len(P): P[line] = "CURR→" + P[line]
            P = "\n".join(P)
            compiled_program.delete("1.0",'end')
            compiled_program.insert("end",P)
            output.configure(bg='grey')
            output.bg = 'grey'
        except:ThrowError()

    def open_file():
        try:
            file_path = filedialog.askopenfilename(
                title="Select a Text File", filetypes=[("QSL Files", "*.qsl")])
            if file_path:
                with open(file_path, 'r') as file:
                    content = file.read()
                    og_program.delete("1.0",'end')
                    og_program.insert("end",content)
                Render(f"Opened:\n {file_path}\n Press 'Burn' to compile the program.")
        except:ThrowError()

    og_program_label = tk.Label(parent,text="Program")
    compiled_program_label = tk.Label(parent,text="Compiled Program")
    output_label = tk.Label(parent,text="States and Memory")
    output = tk.Text(parent,bg='grey',width=40,height=40,borderwidth=3,relief='solid')
    og_program = tk.Text(parent,bg='light yellow',width=40,height=40,borderwidth=3,relief='solid')
    compiled_program = tk.Text(parent,bg='light green',width=40,height=40,borderwidth=3,relief='solid')
    compile_button=tk.Button(command = compute, text = "Burn",borderwidth=3,width=40) ###
    step_button=tk.Button(command = step, text = "Step",borderwidth=3,width=40) ###
    run_button=tk.Button(command = run, text = "Run",borderwidth=3,width=40) ###
    prev_button=tk.Button(command = prev, text = "Prev",borderwidth=3,width=40) ###
    open_button=tk.Button(command = open_file, text = "Open",borderwidth=3,width=40) ###
    clops_button=tk.Button(command = CLOPS.returnCLOPS, text = "Benchmark",borderwidth=3,width=40) ###

    og_program_label.grid(row=0,column=0,rowspan=1,sticky='nswe')
    compiled_program_label.grid(row=0,column=1,rowspan=1,sticky='nswe')
    output_label.grid(row=0,column=2,rowspan=1,sticky='nswe')
    og_program.grid(row=1,column=0,rowspan=3,columnspan=1,sticky='nswe')
    compiled_program.grid(row=1,column=1,rowspan=3,columnspan=1,sticky='nswe')
    output.grid(row=1,column=2,rowspan=3,columnspan=2,sticky='nswe')
    compile_button.grid(row=4,column=0,columnspan=1,sticky='nswe')
    step_button.grid(row=4,column=2,columnspan=1,sticky='nswe')
    prev_button.grid(row=5,column=2,columnspan=1,sticky='nswe')
    run_button.grid(row=5,column=0,columnspan=1,sticky='nswe')
    open_button.grid(row=4,column=1,columnspan=1,rowspan=1,sticky='nswe')
    clops_button.grid(row=5,column=1,columnspan=1,rowspan=1,sticky='nswe')

    n_rows =7
    n_columns =3
    for i in range(n_rows):
        parent.grid_rowconfigure(i,  weight =1)
    for i in range(n_columns):
        parent.grid_columnconfigure(i,  weight =1)
    stage = 0
    line = 0
    Initial_Text =open("Initial.txt",'r').read()
    H = [(Initial_Text,0)]
    Render(H[0][0])
    parent.mainloop()