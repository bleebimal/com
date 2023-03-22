import os
from datetime import datetime
from relevance import revelance_calculate
from django.http.response import HttpResponse

import pandas
from WebGraph.forms import Login
from analysis import analyze
from django.contrib import auth, messages
from django.contrib.auth import logout
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from graphos.renderers.gchart import ColumnChart
from graphos.sources.simple import SimpleDataSource
from mysql.connector import MySQLConnection
from mysql_dbconfig import read_db_config
from single_domain import single_domain_calculate
from multi_domain import multiple_domain_calculate

classes = ["table", "table-bordered",
           "table-striped", "table-hover", "table-dark"]


def index(request):
    return render(request, "index.html")


def patent_quality(request):
    return render(request, "analyze.html")


def single_domain(request):
    return render(request, "single_domain.html")


def relevance_analyze(request):
    print(request.POST["relevance"])
    val1, val2 = 0, 0
    if(request.POST["val1"]):
        val1 = int(request.POST["val1"])
    if(request.POST["val2"]):
        val2 = int(request.POST["val2"])

    result = revelance_calculate(
        uploadAndGetFileName(request, request.FILES["file"]),
        request.POST["relevance"], val1, val2
    )
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=relevance.csv"

    result.to_csv(
        path_or_buf=response, sep="\t", decimal=",", index=False
    )
    return response


def multiple_domain(request):
    return render(request, "multiple_domain.html")


def relevance(request):
    return render(request, "relevance.html")


def login(request):
    return render(request, "login.html")


def get_data(request):
    table = request.GET.get("table", None)
    value = request.GET.get("value", None)

    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        query = 'SELECT * FROM {} where id="{}"'.format(table, value)
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            data = {"status": "200", "message": str(row[1])}
        else:
            data = {"status": "404"}
        return JsonResponse(data)
    except:
        print("Exception Ocurred")
        return JsonResponse({"status": "404"})


def uploadAndGetFileName(request, uploadedFile):
    folder = "uploads/"
    BASE_PATH = "WebGraph/"

    try:
        os.mkdir(os.path.join(BASE_PATH, folder))
    except:
        pass

    uploaded_filename = uploadedFile.name.split(".")[0]
    uploaded_filename_extension = uploadedFile.name.split(".")[1]

    new_file_name = (
        uploaded_filename
        + "_"
        + str(datetime.now().timestamp())
        + "."
        + uploaded_filename_extension
    )

    full_filename = os.path.join(BASE_PATH, folder, new_file_name)
    fout = open(full_filename, "wb+")

    file_content = ContentFile(uploadedFile.read())

    try:
        for chunk in file_content.chunks():
            fout.write(chunk)
        fout.close()
    except:
        messages.add_message(request, messages.ERROR, "Some Error Occurred!!!")

    return full_filename


def single_domain_analyze(request):
    by_year, by_centrality, final_assignee, final_inventor = single_domain_calculate(
        uploadAndGetFileName(request, request.FILES["file"])
    )

    if (
        by_year is not None
        and by_centrality is not None
        and final_assignee is not None
        and final_inventor is not None
    ):
        by_year_table = by_year.to_html(
            index=False, classes=(*classes, "table-sm"), table_id="by_year"
        )
        by_centrality_table = by_centrality.to_html(
            index=False, classes=classes, table_id="by_centrality"
        )
        final_assignee_table = final_assignee.to_html(
            index=False, classes=classes, table_id="final_assignee"
        )
        final_inventor_table = final_inventor.to_html(
            index=False, classes=classes, table_id="final_inventor"
        )

        by_year_list = by_year.values.tolist()
        final_assignee_list = final_assignee.values.tolist()
        final_inventor_list = final_inventor.values.tolist()

        by_year_list.insert(0, ["PUBLICATION YEAR", "PATENT COUNT"])
        final_assignee_list.insert(0, ["ASSIGNEE", "PATENT COUNT"])
        final_inventor_list.insert(0, ["INVENTORS", "PATENT COUNT"])

        by_year_chart_formatted_data = SimpleDataSource(data=by_year_list)
        final_assignee_chart_formatted_data = SimpleDataSource(
            data=final_assignee_list)
        final_inventor_chart_formatted_data = SimpleDataSource(
            data=final_inventor_list)

        by_year_chart = ColumnChart(
            by_year_chart_formatted_data,
            options={
                "title": "PUBLICATION YEAR and PATENT COUNT",
                "width": 1000,
                "height": 500,
                "legend": "none",
                "hAxis": {
                    "title": "PUBLICATION YEAR",
                    "format": "0000",
                },
                "vAxis": {"title": "PATENT COUNT"},
            },
        )
        final_assignee_chart = ColumnChart(
            final_assignee_chart_formatted_data,
            options={
                "title": "ASSIGNEE and PATENT COUNT",
                "width": 800,
                "height": 500,
                "legend": "none",
                "hAxis": {
                    "title": "ASSIGNEE",
                    "slantedText": "true",
                    "slantedTextAngle": 55,
                    "showTextEvery": 1,
                },
                "vAxis": {
                    "title": "PATENT COUNT",
                },
            },
        )
        final_inventor_chart = ColumnChart(
            final_inventor_chart_formatted_data,
            options={
                "title": "INVENTORS and PATENT COUNT",
                "width": 800,
                "height": 500,
                "legend": "none",
                "hAxis": {
                    "title": "INVENTORS",
                    "slantedText": "true",
                    "slantedTextAngle": 55,
                    "showTextEvery": 1,
                },
                "vAxis": {"title": "PATENT COUNT"},
            },
        )

        context = {
            "by_year_table": by_year_table,
            "by_year_chart": by_year_chart,
            "by_centrality_table": by_centrality_table,
            "final_assignee_table": final_assignee_table,
            "final_assignee_chart": final_assignee_chart,
            "final_inventor_table": final_inventor_table,
            "final_inventor_chart": final_inventor_chart,
        }
        return render(request, "single_domain_result.html", context)
    else:
        messages.add_message(request, messages.ERROR, "Some Error Occurred!!!")
        return redirect("/singleDomain/")


def multiple_domain_analyze(request):
    uploadedFiles = [
        uploadAndGetFileName(request, file) for file in request.FILES.getlist("file[]")
    ]
    technologyNames = request.POST.getlist("technologyName[]")

    k_comp, heatmap, total_patents = multiple_domain_calculate(
        uploadedFiles, technologyNames
    )

    k_comp_table = k_comp.to_html(
        index=False, classes=classes, table_id="k_comp")
    total_patents_table = total_patents.to_html(
        index=False, classes=classes, table_id="total_patents"
    )

    k_comp_list = k_comp.values.tolist()

    k_comp_list.insert(0, ["TECHNOLOGY NAME", "K"])

    k_comp_chart_formatted_data = SimpleDataSource(data=k_comp_list)

    k_comp_chart = ColumnChart(
        k_comp_chart_formatted_data,
        options={
            "title": "TECHNOLOGY NAME and K",
            "width": 800,
            "height": 500,
            "hAxis": {"title": "TECHNOLOGY NAME"},
            "vAxis": {"title": "K Value"},
        },
    )
    context = {
        "k_comp_table": k_comp_table,
        "k_comp_chart": k_comp_chart,
        "heatmap": heatmap,
        "total_patents_table": total_patents_table,
    }
    return render(request, "multiple_domain_result.html", context)

    # print(uploadAndGetFileName(request, request.FILES.getlist("file")[0]))
    # uploaded_filename = request.FILES["file"].name.split(".")[0]
    # uploaded_filename_extension = request.FILES["file"].name.split(".")[1]

    # new_file_name = (
    #     uploaded_filename
    #     + "_"
    #     + str(datetime.now().timestamp())
    #     + "."
    #     + uploaded_filename_extension
    # )

    # BASE_PATH = "WebGraph/"


def analyze_data(request):
    folder = "uploads/"
    uploaded_filename = request.FILES["file"].name
    BASE_PATH = "WebGraph/"

    try:
        os.mkdir(os.path.join(BASE_PATH, folder))
    except:
        pass

    full_filename = os.path.join(BASE_PATH, folder, uploaded_filename)
    fout = open(full_filename, "wb+")

    file_content = ContentFile(request.FILES["file"].read())

    try:
        for chunk in file_content.chunks():
            fout.write(chunk)
        fout.close()
    except:
        messages.add_message(request, messages.ERROR, "Some Error Occurred!!!")

    (
        combination,
        ipc_r,
        ipc_p,
        ipc_m,
        i_mpr,
        cpc_r,
        cpc_p,
        cpc_m,
        c_mpr,
        upc_r,
        upc_p,
        upc_m,
        u_mpr,
    ) = analyze(full_filename)

    # print("VIEWS.PY " + str(combination))

    if combination is not None:

        ipc_r["recall"] = ipc_r["recall"].astype(float)
        ipc_p["precision"] = ipc_p["precision"].astype(float)
        ipc_m["mpr"] = ipc_m["mpr"].astype(float)
        i_mpr["k"] = i_mpr["k"].astype(float)
        cpc_r["recall"] = cpc_r["recall"].astype(float)
        cpc_p["precision"] = cpc_p["precision"].astype(float)
        cpc_m["mpr"] = cpc_m["mpr"].astype(float)
        c_mpr["k"] = c_mpr["k"].astype(float)
        upc_r["recall"] = upc_r["recall"].astype(float)
        upc_p["precision"] = upc_p["precision"].astype(float)
        upc_m["mpr"] = upc_m["mpr"].astype(float)
        u_mpr["k"] = u_mpr["k"].astype(float)

        ipc_r_list = ipc_r.values.tolist()
        ipc_r_list.insert(0, ["IPC", "Recall"])
        ipc_p_list = ipc_p.values.tolist()
        ipc_p_list.insert(0, ["IPC", "PRECISION"])
        ipc_m_list = ipc_m.values.tolist()
        ipc_m_list.insert(0, ["IPC", "MPR"])
        i_mpr_list = i_mpr.values.tolist()  # merge mpr for ipc
        i_mpr_list.insert(0, ["IPC", "MPR", "K"])
        cpc_r_list = cpc_r.values.tolist()
        cpc_r_list.insert(0, ["CPC", "Recall"])
        cpc_p_list = cpc_p.values.tolist()
        cpc_p_list.insert(0, ["CPC", "PRECISION"])
        cpc_m_list = cpc_m.values.tolist()
        cpc_m_list.insert(0, ["CPC", "MPR"])
        c_mpr_list = c_mpr.values.tolist()  # merge mpr for cpc
        c_mpr_list.insert(0, ["CPC", "MPR", "K"])
        upc_r_list = upc_r.values.tolist()
        upc_r_list.insert(0, ["UPC", "Recall"])
        upc_p_list = upc_p.values.tolist()
        upc_p_list.insert(0, ["UPC", "PRECISION"])
        upc_m_list = upc_m.values.tolist()
        upc_m_list.insert(0, ["UPC", "MPR"])
        u_mpr_list = u_mpr.values.tolist()  # merge mpr for upc
        u_mpr_list.insert(0, ["UPC", "MPR", "K"])

        ipc_r_data = SimpleDataSource(data=ipc_r_list)
        ipc_p_data = SimpleDataSource(data=ipc_p_list)
        ipc_m_data = SimpleDataSource(data=ipc_m_list)
        cpc_r_data = SimpleDataSource(data=cpc_r_list)
        cpc_p_data = SimpleDataSource(data=cpc_p_list)
        cpc_m_data = SimpleDataSource(data=cpc_m_list)
        upc_r_data = SimpleDataSource(data=upc_r_list)
        upc_p_data = SimpleDataSource(data=upc_p_list)
        upc_m_data = SimpleDataSource(data=upc_m_list)

        ipc_chart_r = ColumnChart(
            ipc_r_data,
            options={
                "title": "IPC Recall",
                "width": 800,
                "height": 500,
                "hAxis": {
                    "slantedText": "true",
                    "slantedTextAngle": 55,
                    "showTextEvery": 1,
                },
            },
        )
        ipc_chart_p = ColumnChart(
            ipc_p_data,
            options={
                "title": "IPC Precision",
                "width": 800,
                "height": 500,
                "hAxis": {
                    "slantedText": "true",
                    "slantedTextAngle": 55,
                    "showTextEvery": 1,
                },
            },
        )
        ipc_chart_m = ColumnChart(
            ipc_m_data,
            options={
                "title": "IPC MPR",
                "width": 800,
                "height": 500,
                "hAxis": {
                    "slantedText": "true",
                    "slantedTextAngle": 55,
                    "showTextEvery": 1,
                },
            },
        )
        cpc_chart_r = ColumnChart(
            cpc_r_data,
            options={
                "title": "CPC Recall",
                "width": 800,
                "height": 520,
                "hAxis": {
                    "slantedText": "true",
                    "slantedTextAngle": 55,
                    "showTextEvery": 1,
                },
            },
        )
        cpc_chart_p = ColumnChart(
            cpc_p_data,
            options={
                "title": "CPC PRECISION",
                "width": 800,
                "height": 520,
                "hAxis": {
                    "slantedText": "true",
                    "slantedTextAngle": 55,
                    "showTextEvery": 1,
                },
            },
        )
        cpc_chart_m = ColumnChart(
            cpc_m_data,
            options={
                "title": "CPC MPR",
                "width": 800,
                "height": 520,
                "hAxis": {
                    "slantedText": "true",
                    "slantedTextAngle": 55,
                    "showTextEvery": 1,
                },
            },
        )
        upc_chart_r = ColumnChart(
            upc_r_data,
            options={
                "title": "UPC Recall",
                "width": 800,
                "height": 500,
                "hAxis": {
                    "slantedText": "true",
                    "slantedTextAngle": 55,
                    "showTextEvery": 1,
                },
            },
        )
        upc_chart_p = ColumnChart(
            upc_p_data,
            options={
                "title": "UPC PRECISION",
                "width": 800,
                "height": 500,
                "hAxis": {
                    "slantedText": "true",
                    "slantedTextAngle": 55,
                    "showTextEvery": 1,
                },
            },
        )
        upc_chart_m = ColumnChart(
            upc_m_data,
            options={
                "title": "UPC MPR",
                "width": 800,
                "height": 500,
                "hAxis": {
                    "slantedText": "true",
                    "slantedTextAngle": 55,
                    "showTextEvery": 1,
                },
            },
        )

        ipc_table_r = ipc_r.to_html(
            index=False, classes=classes, table_id="ipc_def_final"
        )
        ipc_table_p = ipc_p.to_html(
            index=False, classes=classes, table_id="ipc_def_final"
        )
        # ipc_table_m = ipc_m.to_html(index=False, classes=classes, table_id="ipc_def")
        ipc_table_m = i_mpr.to_html(
            index=False, classes=classes, table_id="ipc_def_final"
        )
        cpc_table_r = cpc_r.to_html(
            index=False, classes=classes, table_id="cpc_def_final"
        )
        cpc_table_p = cpc_p.to_html(
            index=False, classes=classes, table_id="cpc_def_final"
        )
        # cpc_table_m = cpc_m.to_html(index=False, classes=classes, table_id="cpc_def")
        cpc_table_m = c_mpr.to_html(
            index=False, classes=classes, table_id="cpc_def_final"
        )
        upc_table_r = upc_r.to_html(
            index=False, classes=classes, table_id="upc_def_final"
        )
        upc_table_p = upc_p.to_html(
            index=False, classes=classes, table_id="upc_def_final"
        )
        # upc_table_m = upc_m.to_html(index=False, classes=classes, table_id="upc_def")
        upc_table_m = u_mpr.to_html(
            index=False, classes=classes, table_id="upc_def_final"
        )

        combination = pandas.DataFrame(
            combination, columns=["IPC and CPC", "IPC and UPC"]
        )
        combination = combination.to_html(index=False, classes=classes)

        ipc_mpr_chart, cpc_mpr_chart, upc_mpr_chart = mpr_data(
            ipc_m_data, cpc_m_data, upc_m_data
        )

        context = {
            "ipc_chart_r": ipc_chart_r,
            "ipc_chart_p": ipc_chart_p,
            "ipc_chart_m": ipc_chart_m,
            "cpc_chart_r": cpc_chart_r,
            "cpc_chart_p": cpc_chart_p,
            "cpc_chart_m": cpc_chart_m,
            "upc_chart_r": upc_chart_r,
            "upc_chart_p": upc_chart_p,
            "upc_chart_m": upc_chart_m,
            "file_name": uploaded_filename,
            "ipc_table_r": ipc_table_r,
            "ipc_table_p": ipc_table_p,
            "ipc_table_m": ipc_table_m,
            "cpc_table_r": cpc_table_r,
            "cpc_table_p": cpc_table_p,
            "cpc_table_m": cpc_table_m,
            "upc_table_r": upc_table_r,
            "upc_table_p": upc_table_p,
            "upc_table_m": upc_table_m,
            "combination": combination,
            "ipc_mpr_chart": ipc_mpr_chart,
            "cpc_mpr_chart": cpc_mpr_chart,
            "upc_mpr_chart": upc_mpr_chart,
        }
        return render(request, "result.html", context)
    else:
        messages.add_message(request, messages.ERROR, "Some Error Occurred!!!")
        return redirect("/patent/")


def validate_login(request):
    if request.method == "POST":
        # print("Here!!!")
        form = Login(request.POST)

        if form.is_valid():

            username = form["username"].value()
            password = form["password"].value()

            print("Username " + username)
            print("Password " + password)

            user = auth.authenticate(username=username, password=password)

            if user is not None:

                auth.login(request, user)
                return redirect("/main/")
            else:
                messages.add_message(
                    request, messages.ERROR, "INCORRECT USERNAME / PASSWORD"
                )
                return redirect("/")
    else:
        return redirect("/")


def result(request):
    return render(request, "result.html")


def logout_system(request):
    logout(request)
    return redirect("/")


def mpr_data(ipc_m_data, cpc_m_data, upc_m_data):
    ipc_chart_m = ColumnChart(
        ipc_m_data,
        options={
            "title": "IPC MPR",
            "width": 800,
            "height": 500,
            "hAxis": {
                "slantedText": "true",
                "slantedTextAngle": 55,
                "showTextEvery": 1,
            },
        },
    )

    cpc_chart_m = ColumnChart(
        cpc_m_data,
        options={
            "title": "CPC MPR",
            "width": 800,
            "height": 520,
            "hAxis": {
                "slantedText": "true",
                "slantedTextAngle": 55,
                "showTextEvery": 1,
            },
        },
    )

    upc_chart_m = ColumnChart(
        upc_m_data,
        options={
            "title": "UPC MPR",
            "width": 800,
            "height": 500,
            "hAxis": {
                "slantedText": "true",
                "slantedTextAngle": 55,
                "showTextEvery": 1,
            },
        },
    )
    return ipc_chart_m, cpc_chart_m, upc_chart_m
