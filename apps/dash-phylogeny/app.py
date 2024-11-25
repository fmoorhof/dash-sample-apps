# -*- coding: utf-8 -*-
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output
from utils import (
    create_paths_file,
    create_tree,
)

app = dash.Dash(__name__)
app.title = "Phylogeny Tree Explorer"
server = app.server

virus_name = "ebola"
species = ["Avian", "Ebola"]
tree_fig = {}

tree_file, metadata_file, metadata_file_stat = create_paths_file(
    virus_name, level1="", level2="", level3=""
)

fig = create_tree(virus_name, tree_file, metadata_file, "Country")
tree_fig[tree_file] = fig


######################################### MAIN APP #########################################
app.layout = html.Div(
    [
        # Banner display
        html.Div(
            className="header-title",
            children=[
                html.H2(
                    id="title",
                    children="Phylogeny trees",
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
                    ],
                ),
                dcc.Graph(id="phylogeny-graph", className="div-card", figure=fig),
            ],
        ),
    ]
)


######################################### UPDATING FIGURES #########################################
@app.callback(Output("output-container", "children"), [Input("d_virus-name", "value")])
def _update_legend_gene(virus_name):
    return 'You have selected "{}" virus'.format(virus_name)



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


# Running the server
if __name__ == "__main__":
    app.run_server(debug=True)
