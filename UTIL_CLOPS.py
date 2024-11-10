import time
import random
from UTIL_DECODER import Q5Processor
from UTIL_MACHINE_CODE import *
import tqdm
import tkinter as tk
import UTIL_SPEC as SPEC

def apply_random_gate(qubit):
    gate_list = ["H", "T", "S", "X", "Y", "Z"]
    gate = random.choice(gate_list)

    if gate == "H":
        return f"H({qubit})"
    
    elif gate == "T":
        return f"T({qubit})"
    
    elif gate == "S":
        return f"S({qubit})"
 
    elif gate == "X":
        return f"X({qubit})"

    elif gate == "Y":
        return f"Y({qubit})"

    elif gate == "Z":
        return f"Z({qubit})"

def generate_circuit(D):
    operations = []

    for _ in range(D):
        for qubit in range(5):
            operations.append(apply_random_gate(qubit))

        for qubit in range(4):
            operations.append(f"CNOT({qubit},{qubit+1})")

    operations.append("MEASURE(0)")
    operations.append("MEASURE(1)")
    operations.append("MEASURE(2)")
    operations.append("MEASURE(3)")
    operations.append("MEASURE(4)")

    return operations

def returnCLOPS(D=100, N=5, S=10, M=10, K=1):
    total_time = 0
    root = tk.Tk()
    root.title("Benchmarking")
    # Window size increase
    root.geometry("500x300")
    # Display a message "Benchmarking in progress" in a pop-up window
    label = tk.Label(root, text="Benchmarking in progress")
    label.pack()
    root.update()


    for i in tqdm.tqdm(range(M)):
        operations = generate_circuit(D)
        operations = "\n".join(operations)
        start_time = time.time()
        for _ in range(S):
            P = ConvertProgram(operations)
            QP = Q5Processor(P)
            QP.run()
        end_time = time.time()
        total_time += end_time - start_time

    CLOPS = M * S * D * K / total_time
    Spec = SPEC.SPEC_bm()
    # Open a new window writing that "THE CLOPS RATING IS {CLOPS}"

    # Remove the previous message
    label.destroy()
    label = tk.Label(root, text=f"\n\nThe CLOPS Rating is {CLOPS}\n\nThe SPEC Rating is {Spec}. \nThe Reference Processor is IBM Eagle R3 QPU (IBM_Kyiv).")

    label.pack()
    root.update()
    root.mainloop()
    return CLOPS
