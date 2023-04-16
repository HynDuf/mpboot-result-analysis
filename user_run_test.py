import os
from datetime import datetime

num_runs = int(input("Num runs each test: "))
seeds = [0] * num_runs
print("Please enter " + str(num_runs) + " seeds below on each line:")
for i in range(num_runs):
    seeds[i] = int(input())
spr_cmds = input("SPR additional options (usually empty): ")
tbr_cmds = input("TBR additional options (Ex: \"-tbr_maxtrav 6\"): ")
ant_cmds = input("ANT additional options (Ex: \"-tbr_maxtrav 7\"): ")
result_file_name = input(
    "Result file's name: ") + "_" + datetime.now().strftime("%d-%m-%Y_%Hh%M")
desc = input("Description: ")

PATH = "/home/diepht/hynduf"
os.makedirs(PATH + "/test/inp", exist_ok=True)
os.makedirs(PATH + "/test/debug", exist_ok=True)
INPUT_FILE = PATH + "/test/inp/" + result_file_name + ".inp"
DEBUG_FILE = PATH + "/test/debug/" + result_file_name + ".out"
with open(INPUT_FILE, "w+") as f:
    f.write(str(num_runs) + '\n')
    for i in range(num_runs):
        f.write(str(seeds[i]) + '\n')
    f.write(str(spr_cmds) + '\n')
    f.write(str(tbr_cmds) + '\n')
    f.write(str(ant_cmds) + '\n')
    f.write(str(result_file_name) + '\n')
    f.write(str(desc) + '\n')

base_cmd = '"python ' + PATH + '/test/run_test.py < ' + INPUT_FILE + ' > ' + DEBUG_FILE + '"'
print(base_cmd)
cmd = 'bsub -J ' + result_file_name + ' -q normal ' + base_cmd
# print(cmd)
os.system(cmd)
