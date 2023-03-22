from collections import Counter
import matplotlib

import matplotlib.pyplot as plt

import pandas as pd
from mysql.connector import MySQLConnection, Error

from mysql_dbconfig import read_db_config

matplotlib.use('agg')


def analyze(file_path):
    file = pd.read_csv(file_path)
    # file = pd.read_csv('/Users/blee/PycharmProjects/WebGraph/input.csv')
    dbconfig = read_db_config()
    con = MySQLConnection(**dbconfig)
    cur = con.cursor()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()
    newcursor = conn.cursor()

    # IPC
    # take ipc class, drop empty class and split on the basis of '|'

    def ipc_read():
        column = file.columns.tolist()

        if 'IPC(s)' in column:
            ipc = file['IPC(s)'].dropna().str.split('|')
        else:
            ipc = file['IPC'].dropna().str.split('|')
        ipc_c = []

        for items in ipc:
            ipc_c += items

        ipc_combine = list(filter(lambda x: x != ' ', ipc_c))  # removing empty ipc class
        ipc_combines = [x.strip(' ') for x in ipc_combine]  # trimming spaces
        ipc_length = len(ipc_combines)
        # print(ipc_combines)

        key_ipc = Counter(ipc_combines).keys()
        value_ipc = Counter(ipc_combines).values()
        recall_ipc = list('%.6f' % (i / ipc_length) for i in value_ipc)  # recall for ipc to 3 decimal point
        # print(recall_ipc)

        # list1 = pd.DataFrame({'code': key_ipc, 'count': value_ipc})
        tuple_ipc = list(zip(key_ipc, value_ipc))
        # print(data_tuple)
        # Storing the final code and respective count in data frame
        seed_ipc = pd.DataFrame(tuple_ipc, columns=['Code', 'Count']).sort_values('Count', ascending=False).head(30)
        print("SEED LINE 44")
        # print(seed_ipc)

        tuple_ipc_recall = list(zip(key_ipc, recall_ipc))
        # print(tuple_ipc_recall)

        dataframe_ipc_recall = pd.DataFrame(tuple_ipc_recall, columns=['ipc', 'recall']).sort_values('recall',
                                                                                                     ascending=False).head(
            30)  # ipc recall to data frame
        print("dataframe_ipc_recall  LINE 53")

        print(dataframe_ipc_recall)

        try:

            cursor.execute("SELECT * FROM ipc_class")
            row = cursor.fetchall()
            newcursor.execute("SELECT * FROM ipc_k")
            newrow = newcursor.fetchall()

            ipc_data = pd.DataFrame(row, columns=['ipc', 'total'])  # for main ipc
            ipc_k_data = pd.DataFrame(newrow, columns=['ipc', 'k'])  # for k value
            # print(ipc_k_data)

            # new = upc_data['upc'].isin(upc_check)
            # print(upc_data.loc[upc_data['upc'].isin(upc_check)])

            new = ipc_data.query("ipc in @seed_ipc.Code")  # filtering database equal to seed set to reduce calculation

            print('Total Row(s):', cursor.rowcount)
            ipc_precision = {}  # precision calculation for ipc

            for sindex, srow in seed_ipc.iterrows():
                for dindex, drow in new.iterrows():
                    if srow['Code'] == drow['ipc']:
                        ipc_precision.update({srow['Code']: ('%.6f' % (srow['Count'] / drow['total']))})
            print("IPC_PRECISION------------------------------------------")
            print(ipc_precision)
            ipc_precision_final = pd.DataFrame.from_dict(ipc_precision, orient='index', columns=['IPC_Precision'],
                                                         dtype='float64').sort_values('IPC_Precision',
                                                                                      ascending=False).head(10)

            seed_ipc_show = seed_ipc.copy()
            seed_ipc_show.plot.bar(x='Code')
            # plt.show

            names = list(ipc_precision.keys())
            quant = list(ipc_precision.values())

            tuple_ipc_precision = list(zip(names, quant))
            dataframe_ipc_precision = pd.DataFrame(tuple_ipc_precision, columns=['ipc', 'precision']).sort_values(by=
                                                                                                                  [
                                                                                                                      'precision'],
                                                                                                                  ascending=False).head(
                30)

            # dataframe_upc_precision.upc = pd.to_numeric(upc_precision_dataframe.upc)
            # dataframe_upc_precision.precision = pd.to_numeric(upc_precision_dataframe.precision)

            print("IPC PRECISION DATAFRAME")
            print(dataframe_ipc_precision)

            # plt.bar(range(len(upc_precision)), quant, tick_label=names)
            # plt.savefig('bar.png')
            # plt.show()

            # index = np.arange(len(names))
            # plt.bar(names, quant)
            # plt.xlabel('Codes', fontsize=5)
            # plt.ylabel('Values', fontsize=5)
            # plt.xticks(index, names, fontsize=5, rotation=30)
            # plt.title('Precision Table')
            # plt.show()

            # dataframe_upc_precision.plot.bar(x='upc', y='precision', rot=0)
            # ipc_precision_final.plot.bar()
            # plt.show()
            #
            # plt.show()

            ipc_mpr = {}

            for rindex, rvalue in dataframe_ipc_recall.iterrows():
                for pindex, pvalue in dataframe_ipc_precision.iterrows():
                    if rvalue['ipc'] == pvalue['ipc']:
                        ipc_mpr.update(
                            {rvalue['ipc']: ('%.6f' % ((float(rvalue['recall']) + float(pvalue['precision'])) / 2))})

            # print(ipc_mpr)

            mpr_keys = list(ipc_mpr.keys())
            mpr_values = list(ipc_mpr.values())

            tuple_ipc_mpr = list(zip(mpr_keys, mpr_values))
            ipc_mpr_show = pd.DataFrame(tuple_ipc_mpr, columns=['ipc', 'mpr']).sort_values('mpr', ascending=False).head(
                10)

            ipc_mpr_final = pd.DataFrame.from_dict(ipc_mpr, orient='index', columns=['IPC_MPR'],
                                                   dtype='float64').sort_values('IPC_MPR', ascending=False).head(10)

            print("MPR FInalllllllllllllllllllllllllllll")
            print(ipc_mpr_final)

            # merging ipc mpr and ipc K value

            merge_mpr = pd.merge(ipc_mpr_show, ipc_k_data, on='ipc', how='left')

            print("MERGEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
            print(merge_mpr)

            ipc_read.ipc_top5 = ipc_mpr_show.head(5)
            print(ipc_read.ipc_top5)

            ipc_mpr_final.plot.bar()
            plt.show()
            return dataframe_ipc_recall.head(10), dataframe_ipc_precision.head(10), ipc_mpr_show.head(
                10), merge_mpr.head(10)

        except Error as e:
            print(e)

        finally:
            cursor.close()
            newcursor.close()
            conn.close()

    ipc_recall, ipc_precisions, ipc_mpr, i_mpr = ipc_read()

    # CPC
    def cpc_read():

        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        newcursor = conn.cursor()

        column = file.columns.tolist()

        if 'CPC(s)' in column:
            cpc = file['CPC(s)'].dropna().str.split('|')
        else:
            cpc = file['CPC'].dropna().str.split('|')  # removing pipe(|) from a single CPC cell for a patent

        cpc_c = []

        for items in cpc:
            cpc_c += items  # combining all the cpc classes
        cpc_combine = [x.strip(' ') for x in cpc_c]  # trimming spaces

        cpc_length = len(cpc_combine)
        print(cpc_length)

        key_cpc = Counter(cpc_combine).keys()
        value_cpc = Counter(cpc_combine).values()

        recall_cpc = list('%.6f' % (i / cpc_length) for i in value_cpc)  # recall for cpc to 3 decimal point
        # print(recall_cpc)

        # list1 = pd.DataFrame({'code': key_cpc, 'count': value_cpc})
        tuple_cpc = list(zip(key_cpc, value_cpc))
        # print(data_tuple)
        # Storing the final code and respective count in data frame
        seed_cpc = pd.DataFrame(tuple_cpc, columns=['Code', 'Count']).sort_values('Count', ascending=False).head(30)
        # ranking done
        print(seed_cpc)
        tuple_cpc_recall = list(zip(key_cpc, recall_cpc))
        dataframe_cpc_recall = pd.DataFrame(tuple_cpc_recall, columns=['cpc', 'recall']).sort_values('recall',
                                                                                                     ascending=False).head(
            30)  # cpc recall to data frame
        print(dataframe_cpc_recall)

        try:

            cur.execute("SELECT * FROM cpc_class")
            ro = cur.fetchall()
            newcursor.execute("SELECT * FROM cpc_k")
            newrow = newcursor.fetchall()

            cpc_data = pd.DataFrame(ro, columns=['cpc', 'total'])
            cpc_k_data = pd.DataFrame(newrow, columns=['cpc', 'k'])  # for k value

            # new = upc_data['upc'].isin(upc_check)
            # print(upc_data.loc[upc_data['upc'].isin(upc_check)])
            print(dataframe_cpc_recall)
            new = cpc_data.query("cpc in @seed_cpc.Code")  # filtering database equal to seed set
            print("NEWWWWWWWWWWWWWWWWWWWWWW")

            print('Total Row(s):', cursor.rowcount)
            cpc_precision = {}  # precision calculate for cpc

            for sindex, srow in seed_cpc.iterrows():
                for dindex, drow in new.iterrows():
                    if srow['Code'] == drow['cpc']:
                        cpc_precision.update({srow['Code']: ('%.6f' % (srow['Count'] / drow['total']))})

            cpc_precision_final = pd.DataFrame.from_dict(cpc_precision, orient='index', columns=['CPC_Precision'],
                                                         dtype='float64').sort_values('CPC_Precision',
                                                                                      ascending=False).head(10)

            names = list(cpc_precision.keys())
            quant = list(cpc_precision.values())

            tuple_cpc_precision = list(zip(names, quant))
            dataframe_cpc_precision = pd.DataFrame(tuple_cpc_precision, columns=['cpc', 'precision']).sort_values(
                by=['precision'], ascending=False).head(30)

            # dataframe_upc_precision.upc = pd.to_numeric(upc_precision_dataframe.upc)
            # dataframe_upc_precision.precision = pd.to_numeric(upc_precision_dataframe.precision)

            print("CPC PRECISION DATAFRAME")
            print(dataframe_cpc_precision)

            # plt.bar(range(len(upc_precision)), quant, tick_label=names)
            # plt.savefig('bar.png')
            # plt.show()

            # index = np.arange(len(names))
            # plt.bar(names, quant)
            # plt.xlabel('Codes', fontsize=5)
            # plt.ylabel('Values', fontsize=5)
            # plt.xticks(index, names, fontsize=5, rotation=30)
            # plt.title('Precision Table')
            # plt.show()

            # dataframe_upc_precision.plot.bar(x='upc', y='precision', rot=0)
            # seed_ipc_show = seed_cpc.copy()
            # seed_ipc_show.plot.bar(x='Code')
            # # plt.show
            #
            # cpc_precision_final.plot.bar()
            # plt.show()
            #
            # plt.show()

            cpc_mpr = {}

            for rindex, rvalue in dataframe_cpc_recall.iterrows():
                for pindex, pvalue in dataframe_cpc_precision.iterrows():
                    if rvalue['cpc'] == pvalue['cpc']:
                        cpc_mpr.update(
                            {rvalue['cpc']: ('%.6f' % ((float(rvalue['recall']) + float(pvalue['precision'])) / 2))})

            print(cpc_mpr)
            mpr_keys = list(cpc_mpr.keys())
            mpr_values = list(cpc_mpr.values())

            tuple_cpc_mpr = list(zip(mpr_keys, mpr_values))
            cpc_mpr_show = pd.DataFrame(tuple_cpc_mpr, columns=['cpc', 'mpr']).sort_values('mpr', ascending=False).head(
                10)

            cpc_mpr_final = pd.DataFrame.from_dict(cpc_mpr, orient='index', columns=['CPC_MPR'],
                                                   dtype='float64').sort_values('CPC_MPR', ascending=False).head(10)

            # merging cpc mpr and cpc K value
            m_mpr = pd.merge(cpc_mpr_show, cpc_k_data, on='cpc', how='left')

            cpc_read.cpc_top5 = cpc_mpr_show.head(5)
            # print(cpc_read.cpc_top5)
            cpc_mpr_final.plot.bar()
            plt.show()

            return dataframe_cpc_recall.head(10), dataframe_cpc_precision.head(10), cpc_mpr_show.head(10), m_mpr.head(
                10)
        except Error as e:
            print(e)

        finally:
            cur.close()
            newcursor.close()
            con.close()

    cpc_recall, cpc_precisions, cpc_mpr, c_mpr = cpc_read()

    # UPC
    # def upc_read():
    #     upc = file['UPC(s)'].dropna().str.split('|')
    #
    #     upc_c = []
    #
    #     for items in upc:
    #         upc_c += items
    #
    #     upc_combine = [x.strip(' ') for x in upc_c]  # trimming spaces
    #     print(upc_combine)
    #     upc_length = len(upc_combine)
    #     print(upc_length)
    #
    #     key_upc = Counter(upc_combine).keys()
    #     value_upc = Counter(upc_combine).values()
    #
    #     recall_upc = list('%.3f' % (i / upc_length) for i in value_upc)  # recall for cpc to 3 decimal point
    #     #print(recall_upc)
    #
    #     # list1 = pd.DataFrame({'code': key_upc, 'count': value_upc})
    #     tuple_upc = list(zip(key_upc, value_upc))
    #     print(tuple_upc)
    #     # Storing the final code and respective count in data frame
    #     seed_upc = pd.DataFrame(tuple_upc, columns=['Code', 'Count']).head(30).sort_values('Count', ascending=False)
    #     print(seed_upc)
    #
    #     tuple_upc_recall = list(zip(key_upc, recall_upc))
    #     dataframe_upc_recall = pd.DataFrame(tuple_upc_recall, columns=['upc', 'recall']).head(30).sort_values('recall',ascending=False)  # upc recall to data frame
    #     print(dataframe_upc_recall)
    #
    # upc_read()

    # dict = {'key': value}
    #
    # for key, value in dict.items():
    #     print(dict[key])

    def upc_read():
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        newcursor = conn.cursor()

        column = file.columns.tolist()

        if 'UPC(s)' in column:  # making compatible with patsnap as well
            upc = file['UPC(s)'].dropna().str.split('|')
        else:
            upc = file['UPC'].dropna().str.split('|')  # removing pipe(|) from a single UPC cell for a patent

        upc_c = []

        for items in upc:
            upc_c += items

        upc_combine = [x.strip(' ') for x in upc_c]  # trimming spaces
        # print(upc_combine)
        upc_length = len(upc_combine)
        # print(upc_length)

        key_upc = Counter(upc_combine).keys()
        value_upc = Counter(upc_combine).values()
        print("Values")
        upc_check = list(key_upc)
        # print(upc_check)

        recall_upc = list('%.6f' % (i / upc_length) for i in value_upc)  # recall for upc to 3 decimal point
        # print(recall_upc)

        # list1 = pd.DataFrame({'code': key_upc, 'count': value_upc})
        tuple_upc = list(zip(key_upc, value_upc))
        # print(tuple_upc)
        # Storing the final code and respective count in data frame
        seed_upc = pd.DataFrame(tuple_upc, columns=['Code', 'Count']).sort_values('Count', ascending=False).head(30)
        print("SEEEDDDDDDDDDDDDDDDDDDDDDDDD")
        # print(seed_upc)

        tuple_upc_recall = list(zip(key_upc, recall_upc))
        dataframe_upc_recall = pd.DataFrame(tuple_upc_recall, columns=['upc', 'recall']).sort_values('recall',
                                                                                                     ascending=False).head(
            30)

        # removind 'No longer' and empty upc class
        dataframe_upc_recall = dataframe_upc_recall[dataframe_upc_recall.upc != 'No longer']
        dataframe_upc_recall = dataframe_upc_recall[dataframe_upc_recall.upc != '']
        print(dataframe_upc_recall)

        try:

            cursor.execute("SELECT * FROM uspc_class")
            rows = cursor.fetchall()

            newcursor.execute("SELECT * FROM upc_k")
            newrow = newcursor.fetchall()

            upc_data = pd.DataFrame(rows, columns=['upc', 'total'])
            upc_k_data = pd.DataFrame(newrow, columns=['upc', 'k'])  # for k value

            # new = upc_data['upc'].isin(upc_check)
            # print(upc_data.loc[upc_data['upc'].isin(upc_check)])
            # print(dataframe_upc_recall)
            new = upc_data.query("upc in @seed_upc.Code")  # filtering database equal to seed set
            print("NEWWWWWWWWWWWWWWWWWWWWWW")
            # print(new)

            print('Total Row(s):', cursor.rowcount)
            upc_precision = {}  # precision calculate for upc

            for sindex, srow in seed_upc.iterrows():
                for dindex, drow in new.iterrows():
                    if srow['Code'] == drow['upc']:
                        upc_precision.update({srow['Code']: ('%.6f' % (srow['Count'] / drow['total']))})

            upc_precision_final = pd.DataFrame.from_dict(upc_precision, orient='index', columns=['UPC_Precision'],
                                                         dtype='float64').sort_values('UPC_Precision',
                                                                                      ascending=False).head(10)

            names = list(upc_precision.keys())
            quant = list(upc_precision.values())

            tuple_upc_precision = list(zip(names, quant))
            dataframe_upc_precision = pd.DataFrame(tuple_upc_precision, columns=['upc', 'precision']).sort_values(
                'precision', ascending=False).head(30)

            # dataframe_upc_precision.upc = pd.to_numeric(upc_precision_dataframe.upc)
            # dataframe_upc_precision.precision = pd.to_numeric(upc_precision_dataframe.precision)

            print("UPC PRECISION DATAFRAME")
            # print(dataframe_upc_precision)

            # plt.bar(range(len(upc_precision)), quant, tick_label=names)
            # plt.savefig('bar.png')
            # plt.show()

            # index = np.arange(len(names))
            # plt.bar(names, quant)
            # plt.xlabel('Codes', fontsize=5)
            # plt.ylabel('Values', fontsize=5)
            # plt.xticks(index, names, fontsize=5, rotation=30)
            # plt.title('Precision Table')
            # plt.show()

            # dataframe_upc_precision.plot.bar(x='upc', y='precision', rot=0)
            # seed_ipc_show = seed_upc.copy()
            # seed_ipc_show.plot.bar(x='Code')
            # plt.show

            upc_precision_final.plot.bar()
            plt.show()
            #
            # plt.show()

            upc_mpr = {}

            for rindex, rvalue in dataframe_upc_recall.iterrows():
                for pindex, pvalue in dataframe_upc_precision.iterrows():
                    if rvalue['upc'] == pvalue['upc']:
                        upc_mpr.update(
                            {rvalue['upc']: ('%.6f' % ((float(rvalue['recall']) + float(pvalue['precision'])) / 2))})

            # print(upc_mpr)

            mpr_keys = list(upc_mpr.keys())
            mpr_values = list(upc_mpr.values())

            tuple_upc_mpr = list(zip(mpr_keys, mpr_values))
            upc_mpr_show = pd.DataFrame(tuple_upc_mpr, columns=['upc', 'mpr']).sort_values('mpr',
                                                                                           ascending=False).head(10)

            upc_mpr_final = pd.DataFrame.from_dict(upc_mpr, orient='index', columns=['UPC_MPR'],
                                                   dtype='float64').sort_values('UPC_MPR', ascending=False).head(10)

            # merging upc mpr and upc K value
            me_mpr = pd.merge(upc_mpr_show, upc_k_data, on='upc', how='left')

            upc_read.upc_top5 = upc_mpr_show.head(5)
            # print(upc_read.upc_top5)

            upc_mpr_final.plot.bar()
            plt.show()
            print(
                "================================================================================================================")

            # print(upc_mpr_show)

            print(
                "================================================================================================================")
            return dataframe_upc_recall.head(10), dataframe_upc_precision.head(10), upc_mpr_show.head(10), me_mpr.head(
                10)

        except Error as e:
            print(e)

        finally:
            cursor.close()
            newcursor.close()
            conn.close()

    upc_recall, upc_precisions, upc_mpr, u_mpr = upc_read()

    comb_IPC_CPC = []
    comb_IPC_UPC = []
    # print("\nIPC and CPC Combination\n")
    for a, ipc_items in ipc_read.ipc_top5.iterrows():
        for b, cpc_items in cpc_read.cpc_top5.iterrows():
            data = '(IPC: (' + ipc_items['ipc'] + ')' + ' and ' + 'CPC: (' + cpc_items['cpc'] + '))'
            comb_IPC_CPC.append(data)
            # print(ipc_items['ipc'] + ' and ' + cpc_items['cpc'])

    print("\nIPC and UPC Combination\n")
    for a, ipc_items in ipc_read.ipc_top5.iterrows():
        for b, cpc_items in upc_read.upc_top5.iterrows():
            data = '(IPC: (' + ipc_items['ipc'] + ')' + ' and ' + 'UPC: (' + cpc_items['upc'] + '))'
            comb_IPC_UPC.append(data)
            # print(ipc_items['ipc'] + ' and ' + cpc_items['upc'])
    # print(comb_IPC_UPC)
    print("============")
    # print(comb_IPC_CPC)
    combination = list(map(list, zip(comb_IPC_CPC, comb_IPC_UPC)))
    print(combination)
    return combination, ipc_recall, ipc_precisions, ipc_mpr, i_mpr, cpc_recall, cpc_precisions, cpc_mpr, c_mpr, upc_recall, upc_precisions, upc_mpr, u_mpr

# analyze("WebGraph/uploads/input.csv")
