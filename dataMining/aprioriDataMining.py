import pandas as pd
import numpy as np
from _pytest import logging
import multiprocessing as mp
import os
import math
import time

import test
# 'True' for parallel computing
# 'False' for sequential computing
is_multiprocessing = True

num_processor = mp.cpu_count()      #default:parallel computing with max num of proessor

def load_data_set():
    data_set =None

    data_set = pd.read_csv("rawData/allInfo.csv",
                               usecols=["Route", "Time", "Day", "Location", "Location", "Incident", "Min Delay Range",
                                        "Direction", "Weather", "YesterdayWeather"])

    return data_set


def create_C1(data_set):
    # Create frequent candidate 1-itemset C1 by scaning data set.
    c1 = set()
    data = data_set.values.tolist()
    for t in data:
        for item in t:
            if type(item) is str or (type(item) is not str and not math.isnan(item)):
                item_set = frozenset([item])
                c1.add(item_set)


    return c1


def is_apriori(Ck_item, Lksub1):
    # Judge whether a frequent candidate k-itemset satisfy Apriori property.
    for item in Ck_item:
        sub_ck = Ck_item - frozenset([item])
        if sub_ck not in Lksub1:
            return False
    return True


def create_Ck(Lksub1, k):
    # Create Ck, a set which contains all all frequent candidate k-itemsets
    # by Lk-1's own connection operation.
    ck = set()
    len_Lksub1 = len(Lksub1)
    list_Lksub1 = list(Lksub1)
    for i in range(len_Lksub1):
        for j in range(1, len_Lksub1):
            l1 = list(list_Lksub1[i])
            l2 = list(list_Lksub1[j])
            # l1.sort()
            # l2.sort()
            if l1[0:k - 2] == l2[0:k - 2]:
                ck_item = list_Lksub1[i] | list_Lksub1[j]
                # pruning
                if is_apriori(ck_item, Lksub1):
                    ck.add(ck_item)
    return ck



#multiprocessing function for item counting
def count_item( Ck, item_count,data_set,lock=None):
    index = 0
    count = {}

    #get the size of item-set for the log
    if len(Ck)!=0:item_set_size = len(next(iter(Ck)))
    else: item_set_size=None

    for t in data_set:
        for item in Ck:
            if item.issubset(t):

                if item not in count:
                    count[item] = 1
                else:
                    count[item] += 1

        index += 1
        progress = round((index / len(data_set)) * 100)

        #progressing bar
        print("\rgenerate {0}-item set: [{1}{2}]: {3}\t %\tfrom process".format(item_set_size, "#" * progress, " " * (100 - progress),
                                                                (index / len(data_set)) * 100), os.getpid(),
              end='', flush=True)

    #add the count number to the shared memory(item_count)
    if is_multiprocessing:
        lock.acquire()
        for key in count:
            if key in item_count:
                item_count[key] = item_count[key] + count[key]
            else:
                item_count[key] = count[key]

        lock.release()
    else:
        item_count.update(count)






def generate_Lk_by_Ck(data_set, Ck, min_support, support_data):
    Lk = set()
    item_count = {}
    data_np = np.array(data_set)

    if is_multiprocessing:
        procs = []
        pipe_list = []
        lock = mp.Lock()

        sub_array = np.array_split(data_np, num_processor)             #split the data set

        #create shared memory
        manager = mp.Manager()
        item_count = manager.dict()


        #create thread
        for sub_data in sub_array:
            # tesing pipe methon for data transfer
            # recv_end, send_end = multiprocessing.Pipe(False)
            proc = mp.Process(target=count_item, args=(Ck,  item_count, sub_data, lock))
            procs.append(proc)
            proc.start()
            # pipe_list.append(recv_end)

        #synchronization
        for proc in procs:
            proc.join()

    else:
        count_item(Ck, item_count, data_np)

    t_num = len(data_np) * 1.0

    print("\ndone scanning")
    for item in item_count:


        if (item_count[item]/t_num) >= min_support:
            Lk.add(item)
            support_data[item] = item_count[item]/t_num
    return Lk


def generate_L(data_set, k, min_support):
    support_data = {}
    print("process C1")
    C1 = create_C1(data_set)
    print("generate C1 rules")
    L1 = generate_Lk_by_Ck(data_set, C1, min_support, support_data)
    Lksub1 = L1.copy()
    L = []
    L.append(Lksub1)

    for i in range(2, k + 1):
        Ci = create_Ck(Lksub1, i)
        Li = generate_Lk_by_Ck(data_set, Ci, min_support, support_data)
        Lksub1 = Li.copy()
        L.append(Lksub1)

        progress = (i//(k-1))*100

        print("generate L: [{0}{1}]: {2}\t %".format("#"*progress, " "*(10-progress), (i/(k))*100),end='\r',flush=True)
    print()
    return L, support_data


if __name__ == '__main__':
    data_set = load_data_set()
    L, support_data = generate_L(data_set, k=6, min_support=0.005)


    if len(list(L)) > 0:
        for Lk in L:
            print("=" * 50)
            if len(list(Lk)) > 0:
                print("frequent " + str(len(list(Lk)[0])) + "-itemsets\t\tsupport")
                print("=" * 50)
                for freq_set in Lk:
                    print(freq_set, support_data[freq_set])
            else:
                print("Null")



