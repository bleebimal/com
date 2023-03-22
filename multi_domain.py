import os
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import seaborn as sns
import cufflinks as cf
from functools import reduce
from datetime import datetime

# init_notebook_mode(connected=True)
cf.go_offline()

# Function to find common patents between two technologies
def common_patents(df1, df2):
    if df1.empty is False and df2.empty is False:
        return list(
            reduce(
                np.intersect1d, [df1["Publication Number"], df2["Publication Number"]]
            )
        )
    else:
        return []


def getFileName():
    folder = "media/"
    BASE_PATH = os.getcwd()
    try:
        os.mkdir(os.path.join(BASE_PATH, folder))
    except:
        pass
    return "media/" + "heatmap" + "_" + str(datetime.now().timestamp()) + ".png"


def multiple_domain_calculate(files, technology_name):
    technology_name = technology_name[0 : len(files)]
    files = [pd.read_csv(file) for file in files]
    files.extend([pd.DataFrame()] * (7 - len(files)))
    df1, df2, df3, df4, df5, df6, df7 = files

    # df1 = pd.read_csv(files[0])
    # df2 = pd.read_csv(files[1])
    # df3 = pd.read_csv(files[2])
    # df4 = pd.read_csv(files[3])
    # df5 = pd.read_csv(files[4])

    # k_temp = [average_cent(pd.read_csv(file)) for file in files]

    # technology_name = ["Coronavirus", "Cough", "Bacteria", "Virus", "Polio"]

    while True:
        try:

            def average_cent(df):
                if df.empty is False:
                    cent_val = list(df["Centrality"])
                    cent_vals = [float(i) for i in cent_val if i != " "]
                    average_c = sum(cent_vals) / len(cent_vals)
                    k = math.exp((average_c * 6.15987) - 5.01885) * 100
                    return k
                    # average_centrality = sum(pd.to_numeric(df['Centrality'], errors='coerce').dropna()) / df.shape[0]
                    # k = math.exp((average_centrality * 6.15987) - 5.01885) * 100
                    # return k

            k1 = average_cent(df1)
            k2 = average_cent(df2)
            k3 = average_cent(df3)
            k4 = average_cent(df4)
            k5 = average_cent(df5)
            k6 = average_cent(df6)
            k7 = average_cent(df7)

            k_temp = [k1, k2, k3, k4, k5, k6, k7]
            # # k_final = [x for x in k_temp if x is not None]
            # print(k_temp)
            # print(k_final)
            k_comb = []
            k_comb = pd.DataFrame(k_temp)  # Converting into DataFrame
            k_comb.columns = ["k"]

            k_comb = k_comb.dropna()
            k_comb["Technology Name"] = technology_name
            k_columns_titles = ["Technology Name", "k"]
            k_comb = k_comb.reindex(columns=k_columns_titles)
            k_comb = k_comb.sort_values(by="k", ascending=False)
            print(k_comb)
            # k_comb.index = technology_name
            # fig = px.bar(k_comb, x=k_comb.index, y="k")
            # fig.update_layout(xaxis_title="Technologies", yaxis_title="K (%)")
            # fig.show()
            break
        except NameError as e:
            name = str(e).split()[1].strip("'")
            globals()[name] = pd.DataFrame()

    A = df1.shape[0]
    B = df2.shape[0]
    each_patent = [A, B]

    while True:
        try:

            if df3.empty is False:
                C = df3.shape[0]
                each_patent.append(C)
            if df4.empty is False:
                D = df4.shape[0]
                each_patent.append(D)
            if df5.empty is False:
                E = df5.shape[0]
                each_patent.append(E)
            if df6.empty is False:
                F = df6.shape[0]
                each_patent.append(F)
            if df7.empty is False:
                G = df7.shape[0]
                each_patent.append(G)

            each_patents = pd.DataFrame(
                each_patent
            )  # Number of Patents from each Technology
            each_patents.index = technology_name
            each_patents.columns = ["Total Patents"]
            print(each_patents)  # -------------------

            note = dict(zip(technology_name, each_patent))
            total_patents = pd.DataFrame(
                list(note.items()), columns=["Technology", "Patent Count"]
            )
            # ----------------- As a table along side Heatmap.

            # Finding common patents between two technologies at a time
            com_ab = common_patents(df1, df2)
            ab = len(com_ab)
            com_ac = common_patents(df1, df3)
            ac = len(com_ac)
            com_ad = common_patents(df1, df4)
            ad = len(com_ad)
            com_ae = common_patents(df1, df5)
            ae = len(com_ae)
            com_af = common_patents(df1, df6)
            af = len(com_af)
            com_ag = common_patents(df1, df7)
            ag = len(com_ag)

            # Patents exclusive to one technology
            only_a = df1.shape[0] - len(
                set(com_ab + com_ac + com_ad + com_ae + com_af + com_ag)
            )

            com_bc = common_patents(df2, df3)
            bc = len(com_bc)
            com_bd = common_patents(df2, df4)
            bd = len(com_bd)
            com_be = common_patents(df2, df5)
            be = len(com_be)
            com_bf = common_patents(df2, df6)
            bf = len(com_bf)
            com_bg = common_patents(df2, df7)
            bg = len(com_bg)
            only_b = df2.shape[0] - len(
                set(com_ab + com_bc + com_bd + com_be + com_bf + com_bg)
            )

            com_cd = common_patents(df3, df4)
            cd = len(com_cd)
            com_ce = common_patents(df3, df5)
            ce = len(com_ce)
            com_cf = common_patents(df3, df6)
            cf = len(com_cf)
            com_cg = common_patents(df3, df7)
            cg = len(com_cg)
            only_c = df3.shape[0] - len(
                set(com_ac + com_bc + com_cd + com_ce + com_cf + com_cg)
            )

            com_de = common_patents(df4, df5)
            de = len(com_de)
            com_df = common_patents(df4, df6)
            df = len(com_df)
            com_dg = common_patents(df4, df7)
            dg = len(com_dg)
            only_d = df4.shape[0] - len(
                set(com_ad + com_bd + com_cd + com_de + com_df + com_dg)
            )

            com_ef = common_patents(df5, df6)
            ef = len(com_ef)
            com_eg = common_patents(df5, df7)
            eg = len(com_eg)
            only_e = df5.shape[0] - len(
                set(com_ae + com_be + com_ce + com_de + com_ef + com_eg)
            )

            com_fg = common_patents(df6, df7)
            fg = len(com_fg)
            only_f = df6.shape[0] - len(
                set(com_af + com_bf + com_cf + com_df + com_ef + com_fg)
            )

            only_g = df7.shape[0] - len(
                set(com_ag + com_bg + com_cg + com_dg + com_eg + com_fg)
            )

            final_combined = {
                "a": [only_a, ab, ac, ad, ae, af, ag],
                "b": [ab, only_b, bc, bd, be, bf, bg],
                "c": [ac, bc, only_c, cd, ce, cf, cg],
                "d": [ad, bd, cd, only_d, de, df, dg],
                "e": [ae, be, ce, de, only_e, ef, eg],
                "f": [af, bf, cf, df, ef, only_f, fg],
                "g": [ag, bg, cg, dg, eg, fg, only_g],
            }

            # print(final_combined)

            pd.options.display.max_columns = None
            multi_comb = pd.DataFrame(final_combined)
            print(multi_comb)
            #
            multi_comb = multi_comb[(multi_comb.T != 0).any()]  # remove empty rows
            # print(multi_comb)

            multi_comb.index = technology_name
            # print(multi_comb)
            multi_comb = multi_comb.loc[
                :, (multi_comb != 0).any(axis=0)
            ]  # remove empty columns
            multi_comb.columns = technology_name  # Assigning Technology Name
            print(multi_comb)  # --------------------

            # Heatmap                 -----------------------
            plt.figure(figsize=(10, 5))
            sns.heatmap(
                multi_comb,
                annot=True,
                fmt="d",
                cmap="Blues_r",
                linewidths=0.5,
                linecolor="Red",
            )
            # plugins.clear(fig)

            # plt.show()
            filePath = getFileName()
            plt.savefig(filePath, transparent=True)
            break
        except NameError as e:
            name = str(e).split()[1].strip("'")
            globals()[name] = pd.DataFrame()
    # return k_comb, mpld3.fig_to_html(fig)
    return k_comb, filePath, total_patents
