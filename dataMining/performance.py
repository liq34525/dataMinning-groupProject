import os
import sys
sys.path.append(os.getcwd())
from dataMining.aprioriDataMining import load_data_set, generate_L
import dataMining.aprioriDataMining as ap
import time
import multiprocessing as mp


def run_apriori():
    data_set = load_data_set()
    L, support_data = generate_L(data_set, k=6, min_support=0.02)
    # big_rules_list = generate_big_rules(L, support_data, min_conf=0.7)

    # if len(list(L)) > 0:
    #     for Lk in L:
    #         print("=" * 50)
    #         if len(list(Lk)) > 0:
    #             print("frequent " + str(len(list(Lk)[0])) + "-itemsets\t\tsupport")
    #             print("=" * 50)
    #             for freq_set in Lk:
    #                 print(freq_set, support_data[freq_set])
    #         else:
    #             print("Null")


def parallel_Performance():
    i=2

    ap.is_multiprocessing = False
    timer_sequential = time.time()
    run_apriori()
    timer_sequential = time.time() - timer_sequential
    while i <= mp.cpu_count():

        ap.is_multiprocessing = True
        ap.num_processor = i
        timer_parallel = time.time()
        run_apriori()
        timer_parallel = time.time() - timer_parallel
        print('****************************')
        print('Execution time for sequential computing:')
        print('{0} second '.format(timer_sequential))
        print('number of processor: {0}'.format(i))
        print('Execution time for parallel computing:')
        print('{0} second '.format(timer_parallel))
        print('speedup:')
        print('{0} %:'.format(timer_sequential/timer_parallel*100))
        print('***************************************/')
        i*=2
parallel_Performance()