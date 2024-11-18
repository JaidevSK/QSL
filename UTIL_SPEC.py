import os
import time
from UTIL_DECODER import Q5Processor
from UTIL_MACHINE_CODE import *
from functools import reduce
import math
import pandas as pd

def SPEC_bm():
    simulator_dict = {}
    for filename in os.listdir("Benchmarks"):
        if filename.endswith(".qsl"):
            with open(f"Benchmarks/{filename}", "r") as f:
                operations = f.read()
                start_time = time.time()
                for _ in range(100):
                    P = ConvertProgram(operations)
                    QP = Q5Processor(P)
                    QP.run()
                end_time = time.time()
                mean_time = (end_time - start_time)
                simulator_dict[filename.split(".")[0]] = mean_time

    ibm_dict = {}
    df = pd.read_csv("Benchmarks/IBMOutput.csv")
    for index, row in df.iterrows():
        ibm_dict[row["program"]] = row["usage(s)"]
    speedup_dict = {}
    for key in ibm_dict:
        speedup_dict[key] = ibm_dict[key] / simulator_dict[key]
    gm = reduce(lambda x, y: x*y, speedup_dict.values())
    gm = math.pow(gm, 1/len(speedup_dict))
    return gm

if __name__ == "__main__":
    print(SPEC_bm())
