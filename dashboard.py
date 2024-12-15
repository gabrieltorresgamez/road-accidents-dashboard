import marimo

__generated_with = "0.10.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import altair as alt
    import geopandas as gpd
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    return alt, gpd, mo, pd, px


@app.cell
def _(gpd):
    data = gpd.read_parquet("accidents.parquet")
    data["latitude"] = data["geometry"].apply(lambda geom: geom.y)
    data["longitude"] = data["geometry"].apply(lambda geom: geom.x)
    data = data.rename(
        columns={
            "Type": "Unfalltyp",
            "SeverityCategory": "Schweregrad",
            "RoadType": "Strassentyp",
            "Canton": "Kanton",
            "Year": "Jahr",
            "Month": "Monat",
            "Hour": "Stunde",
            "InvolvingBicycle": "VeloInvolviert",
            "InvolvingMotorcycle": "MotorradInvolviert",
            "InvolvingPedestrian": "FussgängerInvolviert",
        },
    )
    data["VeloInvolviert"] = data["VeloInvolviert"].replace(
        {"false": "False", "true": "True"},
    )
    data["MotorradInvolviert"] = data["MotorradInvolviert"].replace(
        {"false": "False", "true": "True"},
    )
    data["FussgängerInvolviert"] = data["FussgängerInvolviert"].replace(
        {"false": "False", "true": "True"},
    )
    return (data,)


@app.cell
def _(mo):
    mo.md("""# Visualisierung der Autounfälle in der Schweiz""")


@app.cell
def _(mo):
    mo.md("""---""")


@app.cell
def _(mo):
    mo.md("""## Zusammenfassung des Datensatzes""")


@app.cell
def _(data_filtered, map, mo, pd):
    statistics_data = (
        pd.DataFrame(map.value) if len(pd.DataFrame(map.value)) > 0 else data_filtered
    )
    n_accidents = mo.stat(
        label="Anzahl Unfälle",
        bordered=True,
        value=len(statistics_data),
    )

    n_severe_accidents = mo.stat(
        label="Anzahl Unfälle mit Schwerverletzten",
        bordered=True,
        value=len(
            statistics_data[
                statistics_data["Schweregrad"] == "Unfall mit Schwerverletzten"
            ],
        ),
    )

    n_death_accidents = mo.stat(
        label="Anzahl Unfälle mit Toten",
        bordered=True,
        value=len(
            statistics_data[statistics_data["Schweregrad"] == "Unfall mit Getöteten"],
        ),
    )

    mo.hstack(
        [n_accidents, n_severe_accidents, n_death_accidents],
        widths="equal",
        gap=1,
    )
    return (
        n_accidents,
        n_death_accidents,
        n_severe_accidents,
        statistics_data,
    )


@app.cell
def _(mo):
    toggle_filters_btn = mo.ui.button(
        value=False, on_click=lambda value: not value, label="Filter ein/ausblenden",
    )
    toggle_filters_btn
    return (toggle_filters_btn,)


@app.cell
def _(data, mo, toggle_filters_btn):
    date_range = mo.ui.range_slider(
        start=int(data["Jahr"].min()),
        stop=int(data["Jahr"].max()),
        show_value=True,
        label="Zeitspanne: ",
    )

    list_cantons = data["Kanton"].unique()
    canton_filter = mo.ui.multiselect(
        options=sorted(list_cantons),
        # value=list_cantons,
        value=[
            "ZH",
        ],
        label="Kanton: ",
    )

    list_roadtypes = data["Strassentyp"].unique()
    roadtype_filter = mo.ui.multiselect(
        options=sorted(list_roadtypes),
        value=list_roadtypes,
        label="Strassentyp: ",
    )

    list_accidenttypes = data["Unfalltyp"].unique()
    accidenttype_filter = mo.ui.multiselect(
        options=sorted(list_accidenttypes),
        value=list_accidenttypes,
        label="Unfalltyp: ",
    )
    result = None
    if toggle_filters_btn.value:
        result = mo.hstack(
            [date_range, canton_filter, roadtype_filter, accidenttype_filter],
            widths="equal",
            gap=2,
        )
    result
    return (
        accidenttype_filter,
        canton_filter,
        date_range,
        list_accidenttypes,
        list_cantons,
        list_roadtypes,
        result,
        roadtype_filter,
    )


@app.cell
def _(mo, toggle_filters_btn):
    show_accidents_bike = mo.ui.checkbox(
        value=True, label="Unfälle mit Velo einblenden",
    )
    show_accidents_motorcycle = mo.ui.checkbox(
        value=True, label="Unfälle mit Motorrad einblenden",
    )
    show_accidents_pedestrian = mo.ui.checkbox(
        value=True, label="Unfälle mit Fussgänger einblenden",
    )
    show_other_accidents = mo.ui.checkbox(
        value=True, label="Restliche Unfälle einblenden",
    )

    result6 = None
    if toggle_filters_btn.value:
        result6 = mo.hstack(
            [
                show_accidents_bike,
                show_accidents_motorcycle,
                show_accidents_pedestrian,
                show_other_accidents,
            ],
            widths="equal",
            gap=0,
        )
    result6
    return (
        result6,
        show_accidents_bike,
        show_accidents_motorcycle,
        show_accidents_pedestrian,
        show_other_accidents,
    )


@app.cell
def _(
    accidenttype_filter,
    canton_filter,
    data,
    date_range,
    roadtype_filter,
    show_accidents_bike,
    show_accidents_motorcycle,
    show_accidents_pedestrian,
    show_other_accidents,
):
    selected_roadtypes = roadtype_filter.value
    selected_accidenttypes = accidenttype_filter.value
    selected_cantons = canton_filter.value

    data_filtered = data.copy()
    data_filtered = data_filtered[
        data_filtered["Jahr"].astype(int) >= date_range.value[0]
    ]
    data_filtered = data_filtered[
        data_filtered["Jahr"].astype(int) <= date_range.value[1]
    ]
    data_filtered = data_filtered[data_filtered["Strassentyp"].isin(selected_roadtypes)]
    data_filtered = data_filtered[
        data_filtered["Unfalltyp"].isin(selected_accidenttypes)
    ]
    data_filtered = data_filtered[data_filtered["Kanton"].isin(selected_cantons)]

    if not show_accidents_bike.value:
        data_filtered = data_filtered[data_filtered["VeloInvolviert"] == "False"]

    if not show_accidents_motorcycle.value:
        data_filtered = data_filtered[data_filtered["MotorradInvolviert"] == "False"]

    if not show_accidents_pedestrian.value:
        data_filtered = data_filtered[data_filtered["FussgängerInvolviert"] == "False"]

    if not show_other_accidents.value:
        data_filtered = data_filtered[
            (
                (data_filtered["VeloInvolviert"] == "True")
                | (data_filtered["MotorradInvolviert"] == "True")
                | (data_filtered["FussgängerInvolviert"] == "True")
            )
        ]

    data_filtered = data_filtered.sort_values(
        ["Jahr", "Monat", "Stunde", "Kanton", "Unfalltyp", "Strassentyp", "Schweregrad"],
    )
    data_filtered = data_filtered.reset_index()
    return (
        data_filtered,
        selected_accidenttypes,
        selected_cantons,
        selected_roadtypes,
    )


@app.cell
def _(mo):
    toggle_dataset_btn = mo.ui.button(
        value=False,
        on_click=lambda value: not value,
        label="Datensatz ein/ausblenden",
        disabled=False,
    )
    toggle_dataset_btn
    return (toggle_dataset_btn,)


@app.cell
def _(data_filtered, mo, toggle_dataset_btn):
    result2 = None
    if toggle_dataset_btn.value:
        result2 = mo.ui.table(
            data_filtered.loc[
                :,
                [
                    "latitude",
                    "longitude",
                    "Unfalltyp",
                    "Schweregrad",
                    "Strassentyp",
                    "Kanton",
                    "Jahr",
                    "Monat",
                    "Stunde",
                    "VeloInvolviert",
                    "MotorradInvolviert",
                    "FussgängerInvolviert",
                ],
            ],
            selection=None,
        )
    result2
    return (result2,)


@app.cell
def _(mo):
    mo.md("""---""")


@app.cell
def _(anzahl_unfälle, mo):
    mo.md(
        f"## Visualisierung der Karte mit den letzten {anzahl_unfälle.value} Unfällen",
    )


@app.cell
def _(data_filtered, mo):
    default_anzahl_unfälle = 5_000
    anzahl_unfälle = mo.ui.slider(
        0,
        len(data_filtered),
        value=min(default_anzahl_unfälle, len(data_filtered)),
        label="Anzahl Datenpunkte",
        show_value=True,
    )
    anzahl_unfälle
    return anzahl_unfälle, default_anzahl_unfälle


@app.cell
def _(anzahl_unfälle, data_filtered):
    map_data = data_filtered.copy()
    map_data = map_data.sort_values(by=["Jahr", "Monat"], ascending=[False, False])
    map_data = map_data.head(anzahl_unfälle.value)
    return (map_data,)


@app.cell
def _(mo):
    color_filter = mo.ui.dropdown(
        options=["Unfalltyp", "Strassentyp", "Schweregrad"],
        value="Unfalltyp",
        label="Einfärbung der Punkte: ",
    )
    color_filter
    return (color_filter,)


@app.cell
def _(mo):
    mo.md("""### Unfallkarte""")


@app.cell
def _(color_filter, map_data, mo, px):
    fig = px.scatter_mapbox(
        map_data,
        lat="latitude",
        lon="longitude",
        color=color_filter.value,
        hover_data=[
            "Unfalltyp",
            "Strassentyp",
            "Schweregrad",
            "Monat",
            "Jahr",
            "Stunde",
        ],
        zoom=8.6,
    )

    fig.update_traces(
        hovertemplate=(
            "<extra></extra>"
            "Unfalltyp=%{customdata[0]}<br>"
            "Strassentyp=%{customdata[1]}<br>"
            "Schweregrad=%{customdata[2]}<br>"
            "Jahr=%{customdata[4]}<br>"
            "Monat=%{customdata[3]}<br>"
            "Stunde=%{customdata[5]}"
        ),
    )

    # Customize map settings
    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        # showlegend=False
    )

    map = mo.ui.plotly(fig)
    map
    return fig, map


@app.cell
def _(mo):
    mo.md("""---""")


@app.cell
def _(mo):
    mo.md("""## Statistiken""")


@app.cell
def _(mo):
    mo.md("""### Simple Statistiken""")


@app.cell
def _(mo, statistics_data):
    table = statistics_data.loc[:, ["Unfalltyp"]].value_counts().to_frame()
    table.columns = ["Anzahl Unfälle"]
    result3 = mo.ui.table(
        table, selection=None, pagination=False, show_column_summaries=False,
    )

    table2 = statistics_data.loc[:, ["Strassentyp"]].value_counts().to_frame()
    table2.columns = ["Anzahl Unfälle"]
    result4 = mo.ui.table(
        table2, selection=None, pagination=False, show_column_summaries=False,
    )

    table3 = statistics_data.loc[:, ["Schweregrad"]].value_counts().to_frame()
    table3.columns = ["Anzahl Unfälle"]
    result5 = mo.ui.table(
        table3, selection=None, pagination=False, show_column_summaries=False,
    )

    result345 = mo.hstack(
        [result3, result4, result5],
        widths="equal",
        gap=1,
    )

    result345
    return result3, result345, result4, result5, table, table2, table3


@app.cell
def _(mo):
    mo.md("""### Jährliche Statistiken""")


@app.cell
def _(mo):
    year_column_filter = mo.ui.dropdown(
        options=["Unfalltyp", "Strassentyp", "Schweregrad"],
        value="Unfalltyp",
        label="Variable für die jährliche Statistik: ",
    )
    year_column_filter
    return (year_column_filter,)


@app.cell
def _(mo, year_column_filter):
    mo.Html(f"Jährliche Unfallhäufigkeit nach {year_column_filter.value}").center()


@app.cell
def _(alt, mo, statistics_data, year_column_filter):
    bars2 = (
        alt.Chart(statistics_data)
        .mark_bar()
        .encode(
            y=alt.Y("count()").stack("zero").title("Anzahl Unfälle"),
            x=alt.X(
                "Jahr",
                scale=alt.Scale(
                    domain=list(
                        range(
                            int(statistics_data["Jahr"].min()),
                            int(statistics_data["Jahr"].max()) + 1,
                        ),
                    ),
                ),
            ),
            color=alt.Color(f"{year_column_filter.value}"),
        )
    )

    text2 = (
        alt.Chart(statistics_data)
        .mark_text(dy=-10)
        .encode(
            y=alt.Y("count()").stack("zero"),
            x=alt.X("Jahr"),
            text=alt.Text("count():Q"),
        )
    )
    jahr_plot = mo.ui.altair_chart(bars2 + text2)
    jahr_plot
    return bars2, jahr_plot, text2


@app.cell
def _(mo):
    mo.md(r"""### Monatliche Statistiken""")


@app.cell
def _(mo):
    month_column_filter = mo.ui.dropdown(
        options=["Unfalltyp", "Strassentyp", "Schweregrad"],
        value="Unfalltyp",
        label="Variable für die monatliche Statistik: ",
    )
    month_column_filter
    return (month_column_filter,)


@app.cell
def _(mo, month_column_filter):
    mo.Html(
        f"Durchschnittliche monatliche Unfallhäufigkeit nach {month_column_filter.value}",
    ).center()


@app.cell
def _(alt, mo, month_column_filter, statistics_data):
    bars = (
        alt.Chart(statistics_data)
        .mark_bar()
        .encode(
            y=alt.Y("count()").stack("zero").title("Anzahl Unfälle"),
            x=alt.X("Monat", scale=alt.Scale(domain=list(range(1, 13)))),
            color=alt.Color(f"{month_column_filter.value}"),
        )
    )

    text = (
        alt.Chart(statistics_data)
        .mark_text(dy=-10)
        .encode(
            y=alt.Y("count()").stack("zero"),
            x=alt.X("Monat"),
            text=alt.Text("count():Q"),
        )
    )
    month_plot = mo.ui.altair_chart(bars + text)
    month_plot
    return bars, month_plot, text


@app.cell
def _(mo):
    mo.md(r"""### Stündliche Statistiken""")


@app.cell
def _(mo):
    hour_column_filter = mo.ui.dropdown(
        options=["Unfalltyp", "Strassentyp", "Schweregrad"],
        value="Unfalltyp",
        label="Variable für die stündliche Statistik: ",
    )
    hour_column_filter
    return (hour_column_filter,)


@app.cell
def _(hour_column_filter, mo):
    mo.Html(
        f"Durchschnittliche stündliche Unfallhäufigkeit nach {hour_column_filter.value}",
    ).center()


@app.cell
def _(alt, hour_column_filter, mo, statistics_data):
    bars3 = (
        alt.Chart(statistics_data)
        .mark_bar()
        .encode(
            y=alt.Y("count()").stack("zero").title("Anzahl Unfälle"),
            x=alt.X("Stunde", scale=alt.Scale(domain=list(range(24)))),
            color=alt.Color(f"{hour_column_filter.value}"),
        )
    )

    text3 = (
        alt.Chart(statistics_data)
        .mark_text(dy=-10)
        .encode(
            y=alt.Y("count()").stack("zero"),
            x=alt.X("Stunde"),
            text=alt.Text("count():Q"),
        )
    )
    hour_plot = mo.ui.altair_chart(bars3 + text3)
    hour_plot
    return bars3, hour_plot, text3


if __name__ == "__main__":
    app.run()
