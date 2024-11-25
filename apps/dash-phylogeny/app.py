# -*- coding: utf-8 -*-
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output
from utils import (
    create_paths_file,
    min_max_date,
    slicer,
    create_tree,
    create_map_bubble_year,
    create_curve_line,
)

app = dash.Dash(__name__)
app.title = "Phylogeny Tree Explorer"
server = app.server

virus_name = "measles"
species = ["Avian", "Ebola"]
tree_fig = {}
# mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"  # needed for what?

tree_file, metadata_file, metadata_file_stat = create_paths_file(
    virus_name, level1="", level2="", level3=""
)

# To know the minimum and the maximum values of date for slicer
df_stat_metadata = pd.read_csv(metadata_file_stat)
min_date, max_date = min_max_date(df_stat_metadata)

# create the dictionary of slider
marks_data = slicer(min_date, max_date)
min_max_date_value = [min_date, max_date]

fig = create_tree(virus_name, tree_file, metadata_file, "Country")
tree_fig[tree_file] = fig

# fig_map_bubble = create_map_bubble_year(
#     virus_name, metadata_file_stat, 2, min_date, max_date
# )

# fig_curve_line = create_curve_line(df_stat_metadata, virus_name, min_date, max_date)

######################################### MAIN APP #########################################
app.layout = html.Div(
    [
        # Banner display
        html.Div(
            className="header-title",
            children=[
                html.H2(
                    id="title",
                    children="Phylogeny trees and global spread of 6 viruses",
                ),
                html.Div(
                    id="learn_more",
                    children=[
                        html.Img(className="logo", src=app.get_asset_url("logo.png"))
                    ],
                ),
            ],
        ),
        html.Div(
            id="grid",
            children=[
                html.Div(
                    id="controls",
                    className="row div-row div-card",
                    children=[
                        html.Div(
                            id="dataset-picker",
                            children=[
                                html.Div(
                                    className="six columns",
                                    children=[
                                        html.H6(children="Dataset"),
                                        dcc.Dropdown(
                                            id="d_virus-name",
                                            options=[
                                                {
                                                    "label": species[i],
                                                    "value": species[i],
                                                }
                                                for i in range(len(species))
                                            ],
                                            value="Avian",
                                        ),
                                        html.Div(id="output-container"),
                                    ],
                                ),
                                # Strain dropdown picker
                                html.Div(
                                    className="row",
                                    children=[
                                        html.Div(
                                            className="four columns",
                                            children=[
                                                html.Div(
                                                    children=[
                                                        html.Div(
                                                            id="controls-container_avian",
                                                            children=[
                                                                dcc.Dropdown(
                                                                    id="d_avian_opt1",
                                                                    options=[
                                                                        {
                                                                            "label": i,
                                                                            "value": i,
                                                                        }
                                                                        for i in [
                                                                            "h7n9"
                                                                        ]
                                                                    ],
                                                                    value="h7n9",
                                                                ),
                                                                dcc.Dropdown(
                                                                    id="d_avian_opt2",
                                                                    options=[
                                                                        {
                                                                            "label": i,
                                                                            "value": i,
                                                                        }
                                                                        for i in [
                                                                            "ha",
                                                                            "mp",
                                                                            "na",
                                                                            "ns",
                                                                            "np",
                                                                            "pa",
                                                                            "pb2",
                                                                            "pb1",
                                                                        ]
                                                                    ],
                                                                    value="ha",
                                                                ),
                                                            ],
                                                            style={"display": "none"},
                                                        ),
                                                    ]
                                                )
                                            ],
                                        )
                                    ],
                                ),
                            ],
                        ),
                        html.Div(
                            className="six columns",
                            children=[
                                html.H6(children="Data Range"),
                                html.Div(
                                    id="id-slicer",
                                    children=[
                                        dcc.RangeSlider(
                                            id="id-year",
                                            min=min_date,
                                            max=max_date,
                                            step=1,
                                            marks=marks_data,
                                            value=min_max_date_value,
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                # dcc.Graph(
                #     id="curve-line-graph", className="div-card", figure=fig_curve_line
                # ),
                dcc.Graph(id="phylogeny-graph", className="div-card", figure=fig),
                # dcc.Graph(id="map-graph", className="div-card", figure=fig_map_bubble),
                dcc.Graph(id="histo-graph", className="div-card"),
            ],
        ),
    ]
)


######################################### UPDATING FIGURES #########################################
@app.callback(Output("output-container", "children"), [Input("d_virus-name", "value")])
def _update_legend_gene(virus_name):
    return 'You have selected "{}" virus'.format(virus_name)


@app.callback(
    Output("controls-container_mumps", "style"), [Input("d_virus-name", "value")]
)
@app.callback(
    Output("controls-container_avian", "style"), [Input("d_virus-name", "value")]
)
def _update_avian_option(virus_name):
    if virus_name == "Avian":
        return {"display": "block"}
    else:
        return {"display": "none"}

@app.callback(
    Output("phylogeny-graph", "figure"),
    [
        Input("d_virus-name", "value"),
        Input("d_avian_opt1", "value"),
        Input("d_avian_opt2", "value"),
    ],
)
def update_phylogeny_tree(
    virus_name,
    avian_opt1,
    avian_opt2,
):
    virus_name = virus_name.lower()
    ord_by_elt = "Country"
    if virus_name == "ebola" or virus_name == "zika" or virus_name == "measles":
        (
            tree_file_filtred,
            metadata_file_filtred,
            metadata_file_stat_filtred,
        ) = create_paths_file(virus_name, level1="", level2="", level3="")
    elif virus_name == "avian":
        (
            tree_file_filtred,
            metadata_file_filtred,
            metadata_file_stat_filtred,
        ) = create_paths_file(
            virus_name, level1=avian_opt1, level2=avian_opt2, level3=""
        )

    if tree_file_filtred in tree_fig:
        fig = tree_fig[tree_file_filtred]
    else:
        if ord_by_elt == "Country" or ord_by_elt == "Division" or ord_by_elt == "Date":
            fig = create_tree(
                virus_name, tree_file_filtred, metadata_file_filtred, ord_by_elt
            )

        tree_fig[tree_file_filtred] = fig

    return fig


@app.callback(
    Output("map-graph", "figure"),
    [
        Input("d_virus-name", "value"),
        Input("d_avian_opt1", "value"),
        Input("d_avian_opt2", "value"),
        Input("id-year", "value"),
    ],
)
def _update_map(
    virus_name,
    avian_opt1,
    avian_opt2,
    id_year,
):
    virus_name = virus_name.lower()
    if virus_name == "ebola" or virus_name == "zika" or virus_name == "measles":
        (
            tree_file_filtred,
            metadata_file_filtred,
            metadata_file_stat_filtred,
        ) = create_paths_file(virus_name, level1="", level2="", level3="")
    elif virus_name == "avian":
        (
            tree_file_filtred,
            metadata_file_filtred,
            metadata_file_stat_filtred,
        ) = create_paths_file(
            virus_name, level1=avian_opt1, level2=avian_opt2, level3=""
        )
    df = pd.read_csv(metadata_file_stat_filtred)

    min_date, max_date = id_year
    # To select only the data between min_date and max_date
    df = df[df["Year"] >= min_date]
    df = df[df["Year"] <= max_date]
    return create_map_bubble_year(
        virus_name, metadata_file_stat_filtred, 2, min_date, max_date
    )


@app.callback(
    Output("id-slicer", "children"),
    [
        Input("d_virus-name", "value"),
        Input("d_avian_opt1", "value"),
        Input("d_avian_opt2", "value"),
    ],
)
def _update_slicer(
    virus_name,
    avian_opt1,
    avian_opt2,
):
    virus_name = virus_name.lower()
    if virus_name == "ebola" or virus_name == "zika" or virus_name == "measles":
        (
            tree_file_filtred,
            metadata_file_filtred,
            metadata_file_stat_filtred,
        ) = create_paths_file(virus_name, level1="", level2="", level3="")
    elif virus_name == "avian":
        (
            tree_file_filtred,
            metadata_file_filtred,
            metadata_file_stat_filtred,
        ) = create_paths_file(
            virus_name, level1=avian_opt1, level2=avian_opt2, level3=""
        )
    df = pd.read_csv(metadata_file_stat_filtred)
    min_date, max_date = min_max_date(df)
    # create the dictionary of slider
    marks_data = slicer(min_date, max_date)
    min_max_date_value = [min_date, max_date]

    # To select only the data between min_date and max_date
    df = df[df["Year"] >= min_date]
    df = df[df["Year"] <= max_date]
    return dcc.RangeSlider(
        id="id-year",
        min=min_date,
        max=max_date,
        step=1,
        marks=marks_data,
        value=min_max_date_value,
    )


@app.callback(
    Output("curve-line-graph", "figure"),
    [
        Input("d_virus-name", "value"),
        Input("d_avian_opt1", "value"),
        Input("d_avian_opt2", "value"),
        Input("id-year", "value"),
    ],
)
def _update_curve(
    virus_name,
    avian_opt1,
    avian_opt2,
    id_year,
):
    virus_name = virus_name.lower()
    if virus_name == "ebola" or virus_name == "zika" or virus_name == "measles":
        (
            tree_file_filtred,
            metadata_file_filtred,
            metadata_file_stat_filtred,
        ) = create_paths_file(virus_name, level1="", level2="", level3="")
    elif virus_name == "avian":
        (
            tree_file_filtred,
            metadata_file_filtred,
            metadata_file_stat_filtred,
        ) = create_paths_file(
            virus_name, level1=avian_opt1, level2=avian_opt2, level3=""
        )
    df = pd.read_csv(metadata_file_stat_filtred)
    min_date, max_date = id_year

    # To select only the data between min_date and max_date
    df = df[df["Year"] >= min_date]
    df = df[df["Year"] <= max_date]

    return create_curve_line(df, virus_name, min_date, max_date)


@app.callback(
    Output("histo-graph", "figure"),
    [
        Input("d_virus-name", "value"),
        Input("d_avian_opt1", "value"),
        Input("d_avian_opt2", "value"),
        Input("id-year", "value"),
    ],
)
def _update_histo(
    virus_name,
    avian_opt1,
    avian_opt2,
    id_year,
):
    virus_name = virus_name.lower()
    if virus_name == "ebola" or virus_name == "zika" or virus_name == "measles":
        (
            tree_file_filtred,
            metadata_file_filtred,
            metadata_file_stat_filtred,
        ) = create_paths_file(virus_name, level1="", level2="", level3="")
    elif virus_name == "avian":
        (
            tree_file_filtred,
            metadata_file_filtred,
            metadata_file_stat_filtred,
        ) = create_paths_file(
            virus_name, level1=avian_opt1, level2=avian_opt2, level3=""
        )
    df = pd.read_csv(metadata_file_stat_filtred)
    min_date, max_date = id_year

    # To select only the data between min_date and max_date
    df = df[df["Year"] >= min_date]
    df = df[df["Year"] <= max_date]

    # Count the number of viruses by Country
    df_group_by_country = df.groupby(["Country"])["Value"].sum()
    # Translate groupby object in dataframe
    df_group_by_country = df_group_by_country.to_frame()
    # Rename the first column in Value
    df_group_by_country.columns = ["Value"]
    # Move the index values (i.e. Country column) in column and reset index
    df_group_by_country = df_group_by_country.reset_index()

    return {
        "data": [
            {
                "x": df_group_by_country["Country"],
                "y": df_group_by_country["Value"],
                "type": "bar",
                "marker": dict(color="#8380ff"),
            }
        ],
        "layout": {
            "autosize": True,
            "margin": dict(l=30, r=30, b=70, t=40),
            "title": "<br>Distribution of {} <br>Between {} and {}".format(
                virus_name.title(), min_date, max_date
            ),
            "font": dict(family="Open Sans"),
        },
    }


# Running the server
if __name__ == "__main__":
    app.run_server(debug=True)
