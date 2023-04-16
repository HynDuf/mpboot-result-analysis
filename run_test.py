import glob
import os
import shutil
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xlsxwriter


class ResultAnalyser():

    def __init__(self, num_runs, seeds, result_file_name, desc):
        self.num_runs = num_runs
        self.seeds = seeds
        self.result_file_name = result_file_name
        self.desc = desc
        self.table = [[], [], []]
        self.num_operations_ant = []

    def get_last_iteration_better_tree_found(content):
        key = "BETTER TREE FOUND at iteration "
        idx = content.rfind(key)
        if idx == -1:
            return "-1"
        sp = content.find(" ", idx + len(key))
        return content[idx + len(key):sp - 1]

    def get_last_iteration(content):
        key = "RATCHET Iteration "
        idx = content.rfind(key)

        sp = content.find(" ", idx + len(key))
        return content[idx + len(key):sp]

    def get_best_score(content):
        key = "BEST SCORE FOUND : "
        idx = content.rfind(key)

        sp = content.find("\n", idx + len(key))
        return content[idx + len(key):sp]

    def get_cpu_time(content):
        key = "Total CPU time used: "
        idx = content.rfind(key)

        sp = content.find(" ", idx + len(key))
        return content[idx + len(key):sp]

    # Ant specifics
    def get_num_nnis(content):
        key = "Num NNIs: "
        idx = content.rfind(key)

        sp = content.find("\n", idx + len(key))
        return content[idx + len(key):sp]

    def get_num_sprs(content):
        key = "Num SPRs: "
        idx = content.rfind(key)

        sp = content.find("\n", idx + len(key))
        return content[idx + len(key):sp]

    def get_num_tbrs(content):
        key = "Num TBRs: "
        idx = content.rfind(key)

        sp = content.find("\n", idx + len(key))
        return content[idx + len(key):sp]
    # 0: SPR
    # 1: TBR
    # 2: ANT
    LOCAL_PATH = "/home/diepht/hynduf/test"
    SUFFIXES = ["_SPR", "_TBR", "_RATFULL"]
    FEATURES = [
        "best_score", "cpu_time", 'num_iter', 'time_per_iter',
        'last_iteration_better'
    ]
    COL_NAMES = [
        "Score", "Time (s)", "Num Iters", "Time/Iteration (ms)",
        "Last BETTER iter"
    ]
    def single_analyse(self, filename):
        sum = {}
        for i in range(len(ResultAnalyser.SUFFIXES)):
            for f in ResultAnalyser.FEATURES:
                sum[f] = 0.0
            sum_nnis = 0
            sum_sprs = 0
            sum_tbrs = 0
            for id_run in range(self.num_runs):
                final_filename = ResultAnalyser.LOCAL_PATH + "/log/" + self.result_file_name + "/" + filename + ResultAnalyser.SUFFIXES[
                    i] + '_' + str(seeds[id_run]) + ".log"
                with open(final_filename, "r") as f:
                    content = f.read()
                    try:
                        last_iteration_better = int(
                            ResultAnalyser.
                            get_last_iteration_better_tree_found(content))
                        num_iter = int(ResultAnalyser.get_last_iteration(content)) + \
                            (int(last_iteration_better) % 10)
                        best_score = int(
                            ResultAnalyser.get_best_score(content))
                        cpu_time = float(ResultAnalyser.get_cpu_time(content))
                        time_per_iter = float(cpu_time) / float(
                            num_iter) * 1000
                        if ResultAnalyser.SUFFIXES[i] == "_ANT":
                            num_nnis = int(ResultAnalyser.get_num_nnis(content))
                            num_sprs = int(ResultAnalyser.get_num_sprs(content))
                            num_tbrs = int(ResultAnalyser.get_num_tbrs(content))
                            sum_nnis += num_nnis
                            sum_sprs += num_sprs
                            sum_tbrs += num_tbrs
                    except Exception as e:
                        print(e)
                        print("Error read " + final_filename)
                        exit(0)

                    if last_iteration_better == -1:
                        last_iteration_better = 0

                    sum['best_score'] += best_score
                    sum['cpu_time'] += cpu_time
                    sum['num_iter'] += num_iter
                    sum['time_per_iter'] += time_per_iter
                    sum['last_iteration_better'] += last_iteration_better
            for f in ResultAnalyser.FEATURES:
                sum[f] /= self.num_runs
                print(f, ": ", sum[f])
            if ResultAnalyser.SUFFIXES[i] == "_ANT":
                sum_nnis /= self.num_runs
                sum_sprs /= self.num_runs
                sum_tbrs /= self.num_runs
                print("nnis: ", sum_nnis)
                print("sprs: ", sum_sprs)
                print("tbrs: ", sum_tbrs)
                self.num_operations_ant.append([sum_nnis, sum_sprs, sum_tbrs])

            
            self.table[i].append(sum.copy())

    def plot_bar(Y, y_label, title):
        X = np.arange(1, len(Y) + 1)
        fig = plt.figure(figsize=(12, 5))
        plt.bar(X, Y, color='g', width=0.4)
        plt.xticks(np.arange(1, len(Y) + 1, 5))
        plt.xlabel("ID of testcases")
        plt.ylabel(y_label)
        plt.title(title)
        plt.axhline(y=0, color='r', linestyle='-')
        plt.savefig('img/' + title.replace(' ', '_') + ".png")

    def run_analysis(self):
        filenames = []
        for file_name in list_of_files_desc_size:
            filenames.append(file_name)
            print(file_name)
            self.single_analyse(file_name)
        print("Finished analyzed all the logs files")
        df = []
        for i in range(3):
            df.append(pd.DataFrame(self.table[i]))
            print(df[i].head)

        ## Create Workbook ##
        print("Creating sheets");
        workbook = xlsxwriter.Workbook(self.result_file_name + '.xlsx')
        worksheet = workbook.add_worksheet()

        worksheet.write(0, 0, "Seeds (" + str(self.num_runs) + ")")
        for i in range(self.num_runs):
            worksheet.write(0, i + 1, self.seeds[i])

        num_tests = len(filenames)
        worksheet.write(1, 0, "Tests")
        for i in range(num_tests):
            worksheet.write(i + 2, 0, filenames[i])

        for i in range(len(ResultAnalyser.COL_NAMES)):
            idx = 3 * i + 1
            worksheet.write(1, idx, ResultAnalyser.COL_NAMES[i] + " (SPR)")
            worksheet.write(1, idx + 1, ResultAnalyser.COL_NAMES[i] + " (TBR)")
            worksheet.write(1, idx + 2, ResultAnalyser.COL_NAMES[i] + " (ANT)")
        worksheet.write(1, len(ResultAnalyser.COL_NAMES) * 3 + 1, "BEST SCORE")
        if "_ANT" in ResultAnalyser.SUFFIXES:
            worksheet.write(1, len(ResultAnalyser.COL_NAMES) * 3 + 2, "NUM NNIS ANT")
            worksheet.write(1, len(ResultAnalyser.COL_NAMES) * 3 + 3, "NUM SPRS ANT")
            worksheet.write(1, len(ResultAnalyser.COL_NAMES) * 3 + 4, "NUM TBRS ANT")
        print("Finished headers")
        for i in range(3):
            values = df[i].values.tolist()
            for idxRow, row in enumerate(values):
                for j in range(len(row)):
                    idxCol = j * 3 + 1 + i
                    worksheet.write(idxRow + 2, idxCol, row[j])
                if i == 2:
                    worksheet.write(idxRow + 2,
                                len(row) * 3 + 1,
                                f'=MIN(B{idxRow + 3}:D{idxRow + 3})')
        if "_ANT" in ResultAnalyser.SUFFIXES:
            print('Add ant num operations')
            for idxRow in range(len(self.num_operations_ant)):
                # print('Row: ', idxRow)
                # print(self.num_operations_ant[idxRow][0])
                # print(self.num_operations_ant[idxRow][1])
                # print(self.num_operations_ant[idxRow][2])
                worksheet.write(idxRow + 2, len(ResultAnalyser.COL_NAMES) * 3 + 2, self.num_operations_ant[idxRow][0])
                worksheet.write(idxRow + 2, len(ResultAnalyser.COL_NAMES) * 3 + 3, self.num_operations_ant[idxRow][1])
                worksheet.write(idxRow + 2, len(ResultAnalyser.COL_NAMES) * 3 + 4, self.num_operations_ant[idxRow][2])
        idxRow = len(filenames) + 3
        END_ROW = len(filenames) + 2
        print("Adding summrization")
        worksheet.write(idxRow, 2, "SPR")
        worksheet.write(idxRow, 3, "TBR")
        worksheet.write(idxRow, 4, "ANT")
        worksheet.write(idxRow + 1, 0, "Tổng thời gian (phút)")
        worksheet.write(idxRow + 2, 0, "Số lần đạt BEST SCORE")
        worksheet.write(idxRow + 3, 0, "Số test điểm SPR tốt hơn")
        worksheet.write(idxRow + 4, 0, "Số test điểm TBR tốt hơn")
        worksheet.write(idxRow + 5, 0, "Số test điểm ANT tốt hơn")
        worksheet.write(idxRow + 7, 0, "Description")
        worksheet.write(idxRow + 7, 2, self.desc)

        worksheet.write(idxRow + 1, 2, f"=SUM(E3:E{END_ROW})/60")
        worksheet.write(idxRow + 1, 3, f"=SUM(F3:F{END_ROW})/60")
        worksheet.write(idxRow + 1, 4, f"=SUM(G3:G{END_ROW})/60")
        worksheet.write(idxRow + 2, 2,
                        f"=SUMPRODUCT(--(B3:B{END_ROW}=Q3:Q{END_ROW}))")
        worksheet.write(idxRow + 2, 3,
                        f"=SUMPRODUCT(--(C3:C{END_ROW}=Q3:Q{END_ROW}))")
        worksheet.write(idxRow + 2, 4,
                        f"=SUMPRODUCT(--(D3:D{END_ROW}=Q3:Q{END_ROW}))")
        worksheet.write(idxRow + 3, 2,
                        f"=SUMPRODUCT(--(B3:B{END_ROW}<B3:B{END_ROW}))")
        worksheet.write(idxRow + 3, 3,
                        f"=SUMPRODUCT(--(B3:B{END_ROW}<C3:C{END_ROW}))")
        worksheet.write(idxRow + 3, 4,
                        f"=SUMPRODUCT(--(B3:B{END_ROW}<D3:D{END_ROW}))")
        worksheet.write(idxRow + 4, 2,
                        f"=SUMPRODUCT(--(C3:C{END_ROW}<B3:B{END_ROW}))")
        worksheet.write(idxRow + 4, 3,
                        f"=SUMPRODUCT(--(C3:C{END_ROW}<C3:C{END_ROW}))")
        worksheet.write(idxRow + 4, 4,
                        f"=SUMPRODUCT(--(C3:C{END_ROW}<D3:D{END_ROW}))")
        worksheet.write(idxRow + 5, 2,
                        f"=SUMPRODUCT(--(D3:D{END_ROW}<B3:B{END_ROW}))")
        worksheet.write(idxRow + 5, 3,
                        f"=SUMPRODUCT(--(D3:D{END_ROW}<C3:C{END_ROW}))")
        worksheet.write(idxRow + 5, 4,
                        f"=SUMPRODUCT(--(D3:D{END_ROW}<D3:D{END_ROW}))")

        # Format all the columns.
        my_format = workbook.add_format()
        my_format.set_align('center')
        my_format.set_align('vcenter')
        my_format.set_text_wrap()
        worksheet.set_row(idxRow + 7, 200, my_format)
        COLUMN_WIDTHS = [
            33, 14, 14, 14, 17, 17, 17, 17, 17, 17, 25, 25, 25, 23, 23, 23, 12, 17, 17, 17
        ]
        for i in range(len(COLUMN_WIDTHS)):
            worksheet.set_column(i, i, COLUMN_WIDTHS[i], my_format)
        print("Drawing plots")
        score_diff = df[0]['best_score'] - df[2]['best_score']
        ResultAnalyser.plot_bar(score_diff, "Score diff", "Score: SPR vs ANT")
        score_diff = df[1]['best_score'] - df[2]['best_score']
        ResultAnalyser.plot_bar(score_diff, "Score diff", "Score: TBR vs ANT")
        score_diff = df[0]['best_score'] - df[1]['best_score']
        ResultAnalyser.plot_bar(score_diff, "Score diff", "Score: SPR vs TBR")
        time_speed_up_factor = np.log(df[0]['cpu_time'] / df[2]['cpu_time'])
        ResultAnalyser.plot_bar(time_speed_up_factor, "Ln(CPU Time ratio)",
                                "CPU Time: SPR vs ANT")
        time_speed_up_factor = np.log(df[1]['cpu_time'] / df[2]['cpu_time'])
        ResultAnalyser.plot_bar(time_speed_up_factor, "Ln(CPU Time ratio)",
                                "CPU Time: TBR vs ANT")
        num_iter = np.log(df[0]['num_iter'] / df[2]['num_iter'])
        ResultAnalyser.plot_bar(num_iter, "Ln(Num iter ratio)",
                                "Num Iter: SPR vs ANT")
        num_iter = np.log(df[1]['num_iter'] / df[2]['num_iter'])
        ResultAnalyser.plot_bar(num_iter, "Ln(Num iter ratio)",
                                "Num Iter: TBR vs ANT")
        tpi_speed_up_facter = np.log(df[0]['time_per_iter'] /
                                     df[2]['time_per_iter'])
        ResultAnalyser.plot_bar(tpi_speed_up_facter, "Ln(Time per iter ratio)",
                                "TimePerIter: SPR vs ANT")
        tpi_speed_up_facter = np.log(df[1]['time_per_iter'] /
                                     df[2]['time_per_iter'])
        ResultAnalyser.plot_bar(tpi_speed_up_facter, "Ln(Time per iter ratio)",
                                "TimePerIter: TBR vs ANT")

        sheetGraphs = workbook.add_worksheet()
        directoryImg = ResultAnalyser.LOCAL_PATH + "/img"
        filenames = []
        idxCol = 1
        soDirImg = sorted(os.listdir(directoryImg))
        for i in range(0, len(soDirImg), 2):
            im = soDirImg[i]
            print(ResultAnalyser.LOCAL_PATH + "/img/" + im)
            sheetGraphs.insert_image(f'A{idxCol}',
                                     ResultAnalyser.LOCAL_PATH + "/img/" + im,
                                     {
                                         'x_scale': 0.65,
                                         'y_scale': 0.65
                                     })
            if i + 1 == len(soDirImg):
                break
            im = soDirImg[i + 1]
            sheetGraphs.insert_image(f'M{idxCol}',
                                     ResultAnalyser.LOCAL_PATH + "/img/" + im,
                                     {
                                         'x_scale': 0.65,
                                         'y_scale': 0.65
                                     })
            idxCol += 17
        print("Finished creating sheets")
        workbook.close()


## ------------------------------ MAIN ------------------------------ ##

## --------------- USER INPUT --------------- ##
num_runs = int(input("Num runs each test: "))
seeds = [0] * num_runs
print("Please enter " + str(num_runs) + " seeds below on each line:")
for i in range(num_runs):
    seeds[i] = int(input())
spr_cmds = input("SPR additional options (usually empty): ")
tbr_cmds = input("TBR additional options (Ex: \"-tbr_maxtrav 6\"): ")
ant_cmds = input("ANT additional options (Ex: \"-tbr_maxtrav 7\"): ")
result_file_name = input("Result file's name: ")
desc = input("Description: ")
## ------------------------------------------ ##
PATH = "/home/diepht/hynduf"
DATA_PATH = PATH + "/test/data"
commands = [
    PATH + "/build/mpboot-avx-normal -s " + DATA_PATH + "/? " + spr_cmds + " -pre " +
    PATH + "/test/log/" + result_file_name + "/?" + ResultAnalyser.SUFFIXES[0],
    PATH + "/build/mpboot-avx-normal -s " + DATA_PATH + "/? " + tbr_cmds +
    " -tbr_pars -pre " + PATH + "/test/log/" + result_file_name + "/?" + ResultAnalyser.SUFFIXES[1],
    PATH + "/build/mpboot-avx-ratfull -s " + DATA_PATH + "/? " + ant_cmds +
    " -pre " + PATH + "/test/log/" + result_file_name + "/?" + ResultAnalyser.SUFFIXES[2]
]

# Remove files if exists in the result folder
shutil.rmtree(PATH + "/test/log/" + result_file_name, ignore_errors=True)
os.makedirs(PATH + "/test/log/" + result_file_name, exist_ok=True)

# Get list of all files only in the given directory
list_of_files_desc_size = filter(
    lambda x: os.path.isfile(os.path.join(DATA_PATH, x)) and x.endswith(".phy"
                                                                        ),
    os.listdir(DATA_PATH))

# Sort list of file names by size
list_of_files_desc_size = sorted(
    list_of_files_desc_size,
    key=lambda x: os.stat(os.path.join(DATA_PATH, x)).st_size)
list_of_files_desc_size.reverse()
NAMES = ['spr', 'tbr', 'ant']


def bsub_commands_generator(filename):
    for i in range(num_runs):
        for id in range(len(commands)):
            c = 'bsub -J ' + NAMES[id] + '_' + filename + '_' + str(seeds[i]) + ' -q normal "' + \
                commands[id].replace("?", filename) + '_' + str(seeds[i]) + ' -seed ' + str(seeds[i]) + ' >/dev/null 2>&1"'
            os.system(c)
        time.sleep(2)


for file_name in list_of_files_desc_size:
  bsub_commands_generator(file_name)

NUM_FILES = len(list_of_files_desc_size)
while (True):
    num_mpboot_files = len(
        glob.glob1(PATH + "/test/log/" + result_file_name + "/", "*.mpboot"))
    print("num: ", num_mpboot_files)
    if num_mpboot_files == 3 * num_runs * NUM_FILES:
        result_analyser = ResultAnalyser(num_runs, seeds, result_file_name,
                                         desc)
        result_analyser.run_analysis()
        print("DONE!")
        exit(0)
    # Wait for 5 minutes
    time.sleep(10)
