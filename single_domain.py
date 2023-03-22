import math
from collections import Counter

import cufflinks as cf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns

# init_notebook_mode(connected=True)
cf.go_offline()


def single_domain_calculate(filename):
    df = pd.read_csv(filename)  # Read CSV
    year = df["Publication Year"].value_counts()
    year_dict = dict(year)

    by_year = pd.DataFrame.from_dict(year_dict, orient="index").reset_index()
    by_year.columns = ["Publication Year", "Patent Count"]
    by_year.sort_values(
        by="Publication Year", ascending=False, inplace=True
    )  # year wise patents  ----------
    # print(by_year)

    # plt.figure(figsize=(20, 5))
    # sns.barplot(x="Publication Year", y="Patent Count", data=by_year)
    # plt.show()

    # px.bar(by_year, x="Publication Year", y="Patent Count")

    # Year = by_year["Publication Year"]  # Year Values
    # Patent_Count = by_year["Patent Count"]  # Patent Count Values
    # fig = go.Figure()
    # fig.add_trace(go.Scatter(x=Year, y=Patent_Count, mode="lines+markers"))

    # fig.update_layout(xaxis_title="Year", yaxis_title="Patent Count")
    # fig.show()

    # Top 10 Central Patents
    # print("")
    df = df[df.columns].replace({'"': ""}, regex=True)
    cen_temp = df.sort_values(by="Centrality", ascending=False).head(10).reset_index()
    by_centrality = cen_temp[
        ["Publication Number", "Title", "Assignee(s)", "Centrality"]
    ]
    by_centrality.index = np.arange(
        1, len(by_centrality) + 1
    )  # Top central patents  -----------
    # by_centrality = df[df.columns].replace({'"': ""}, regex=True)
    # print(by_centrality)

    # Top 10 Assignees
    assignees = []
    as_list = (
        df["Assignee(s)"].dropna().str.split("|")
    )  # taking assignee column and separating the '|'
    for items in as_list:
        assignees += items  # storing all the assignees in a single list
    assignees = [s.strip('"') for s in assignees]  # removing quotes from the strings
    assignees = [s for s in assignees if s != " "]  # removing null values
    as_temp_dict = Counter(assignees)

    by_assignees = pd.DataFrame.from_dict(as_temp_dict, orient="index").reset_index()
    by_assignees.columns = ["Assignee", "Patent Count"]
    final_assignee = by_assignees.sort_values(by="Patent Count", ascending=False).head(
        10
    )
    final_assignee.index = np.arange(
        1, len(final_assignee) + 1
    )  # Top Assignees      --------------

    # print(final_assignee)
    # px.bar(final_assignee, x="Assignee", y="Patent Count")

    # Top 10 inventors
    inventors = []
    as_list = (
        df["Inventor(s)"].dropna().str.split("|")
    )  # taking inventor column and separating the '|'
    for items in as_list:
        inventors += items  # storing all the assignees in a single list
    inventors = [s.strip('"') for s in inventors]  # removing quotes from the strings
    inventors = [s for s in inventors if s != " "]  # removing null values
    in_temp_dict = Counter(inventors)

    by_inventors = pd.DataFrame.from_dict(in_temp_dict, orient="index").reset_index()
    by_inventors.columns = ["Inventors", "Patent Count"]
    final_inventor = by_inventors.sort_values(by="Patent Count", ascending=False).head(
        10
    )
    final_inventor.index = np.arange(
        1, len(final_inventor) + 1
    )  # Top inventors         ---------------

    # print(final_inventor)
    # px.bar(final_inventor, x="Inventors", y="Patent Count")

    # K value of the whole technology
    average_cent = (
        sum(pd.to_numeric(df["Centrality"], errors="coerce").dropna()) / df.shape[0]
    )
    k = math.exp((average_cent * 6.15987) - 5.01885)
    print("The Rate of Improvement for this technology is " + str(k))

    # K value of the whole technology discarding NULL VALUES
    # using list comprehension
    cent_val = list(df["Centrality"])
    cent_vals = [float(i) for i in cent_val if i != " " and str(i) != "nan"]
    average_c = sum(cent_vals) / len(cent_vals)
    k = math.exp((average_c * 6.15987) - 5.01885)
    print(
        "The Rate of Improvement for this technology is " + str(k)
    )  # K  -----------------

    return by_year, by_centrality, final_assignee, final_inventor
