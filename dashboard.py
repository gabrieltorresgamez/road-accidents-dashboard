import marimo

__generated_with = "0.9.14"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    import pandas as pd
    import geopandas as gpd
    import altair as alt
    import plotly.express as px
    return alt, gpd, mo, pd, px


@app.cell
def __(gpd):
    data = gpd.read_parquet("accidents.parquet")
    data['latitude'] = data['geometry'].apply(lambda geom: geom.y)
    data['longitude'] = data['geometry'].apply(lambda geom: geom.x)
    data = data.rename(columns={
        "Type": "Unfalltyp",
        "SeverityCategory": "Schweregrad",
        "RoadType": "Strassentyp",
        "Canton": "Kanton",
        "Year": "Jahr",
        "Month": "Monat"
    })
    return (data,)


@app.cell
def __(mo):
    mo.md("""# Visualisierung der Autounfälle in der Schweiz""")
    return


@app.cell
def __(mo):
    mo.md("""---""")
    return


@app.cell
def __(mo):
    mo.md("""## Zusammenfassung des Datensatzes""")
    return


@app.cell
def __(data_filtered, map, mo, pd):
    statistics_data = pd.DataFrame(map.value) if len(pd.DataFrame(map.value)) > 0 else data_filtered
    n_accidents = mo.stat(
        label="Anzahl Unfälle",
        bordered=True,
        value=len(statistics_data),
    )

    n_severe_accidents = mo.stat(
        label="Anzahl Unfälle mit Schwerverletzten",
        bordered=True,
        value=len(statistics_data[statistics_data["Schweregrad"] == "Unfall mit Schwerverletzten"]),
    )

    n_death_accidents = mo.stat(
        label="Anzahl Unfälle mit Toten",
        bordered=True,
        value=len(statistics_data[statistics_data["Schweregrad"] == "Unfall mit Getöteten"]),
    )

    mo.hstack([n_accidents, n_severe_accidents, n_death_accidents],
        widths="equal",
        gap=1,)
    return (
        n_accidents,
        n_death_accidents,
        n_severe_accidents,
        statistics_data,
    )


@app.cell
def __(mo):
    toggle_filters_btn = mo.ui.button(
        value=False, on_click=lambda value: not value, label="Filter ein/ausblenden"
    )
    toggle_filters_btn
    return (toggle_filters_btn,)


@app.cell
def __(data, mo, toggle_filters_btn):
    date_range = mo.ui.range_slider(
        start=int(data["Jahr"].min()), 
        stop=int(data["Jahr"].max()), 
        show_value=True, 
        label="Zeitspanne: ",
    )

    list_cantons = data["Kanton"].unique()
    canton_filter = mo.ui.multiselect(
        options=sorted(list_cantons), 
        #value=list_cantons,
        value=["ZH",], 
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
def __(
    accidenttype_filter,
    canton_filter,
    data,
    date_range,
    roadtype_filter,
):
    selected_roadtypes = roadtype_filter.value
    selected_accidenttypes = accidenttype_filter.value
    selected_cantons = canton_filter.value

    data_filtered = data.copy()
    data_filtered = data_filtered[data_filtered["Jahr"].astype(int) >= date_range.value[0]]
    data_filtered = data_filtered[data_filtered["Jahr"].astype(int) <= date_range.value[1]]
    data_filtered = data_filtered[data_filtered["Strassentyp"].isin(selected_roadtypes)]
    data_filtered = data_filtered[data_filtered["Unfalltyp"].isin(selected_accidenttypes)]
    data_filtered = data_filtered[data_filtered["Kanton"].isin(selected_cantons)]
    data_filtered = data_filtered.sort_values(["Jahr", "Kanton", "Unfalltyp", "Strassentyp", "Schweregrad"])
    data_filtered = data_filtered.reset_index()
    return (
        data_filtered,
        selected_accidenttypes,
        selected_cantons,
        selected_roadtypes,
    )


@app.cell
def __(mo):
    toggle_dataset_btn = mo.ui.button(
        value=False, on_click=lambda value: not value, label="Datensatz ein/ausblenden"
    )
    toggle_dataset_btn
    return (toggle_dataset_btn,)


@app.cell
def __(data_filtered, mo, toggle_dataset_btn):
    result2 = None
    if toggle_dataset_btn.value:
        result2 = mo.ui.table(data_filtered.loc[:, ['latitude', 'longitude', 'Unfalltyp', 'Schweregrad','Strassentyp', 'Kanton', 'Jahr', 'Monat']], selection=None)
    result2
    return (result2,)


@app.cell
def __(mo):
    mo.md("""---""")
    return


@app.cell
def __(anzahl_unfälle, mo):
    mo.md(f"## Visualisierung der Karte mit den letzten {anzahl_unfälle.value} Unfällen")
    return


@app.cell
def __(data_filtered, mo):
    default_anzahl_unfälle = 5_000
    anzahl_unfälle = mo.ui.slider(0, len(data_filtered), value=min(default_anzahl_unfälle, len(data_filtered)), label="Anzahl Datenpunkte" , show_value=True,)
    anzahl_unfälle
    return anzahl_unfälle, default_anzahl_unfälle


@app.cell
def __(anzahl_unfälle, data_filtered):
    map_data = data_filtered.copy()
    map_data = map_data.sort_values(by=["Jahr", "Monat"], ascending=[False, False])
    map_data = map_data.head(anzahl_unfälle.value)
    return (map_data,)


@app.cell
def __(mo):
    color_filter = mo.ui.dropdown(
        options=["Unfalltyp", "Strassentyp", "Schweregrad"],
        value="Unfalltyp", 
        label="Einfärbung der Punkte: ",
    )
    color_filter
    return (color_filter,)


@app.cell
def __(mo):
    mo.md("""#### Unfallkarte""")
    return


@app.cell
def __(color_filter, map_data, mo, px):
    fig = px.scatter_mapbox(
        map_data,
        lat="latitude",
        lon="longitude",
        color=color_filter.value,
        hover_data=["Unfalltyp", "Strassentyp", "Schweregrad", "Monat", "Jahr", "Kanton"],
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
        )
    )

    # Customize map settings
    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r":0,"t":0,"l":0,"b":0},
        #showlegend=False
    )

    map = mo.ui.plotly(fig)
    map
    return fig, map


@app.cell
def __(mo):
    mo.md("""## Statistiken""")
    return


@app.cell
def __(mo):
    mo.md("""#### Simple Statistiken""")
    return


@app.cell
def __(mo, statistics_data):
    table = statistics_data.loc[:, ["Unfalltyp"]].value_counts().to_frame()
    table.columns = ["Anzahl"]
    result3 = mo.ui.table(table, selection=None, pagination=False)

    table2 = statistics_data.loc[:, ["Strassentyp"]].value_counts().to_frame()
    table2.columns = ["Anzahl"]
    result4 = mo.ui.table(table2, selection=None, pagination=False)

    table3 = statistics_data.loc[:, ["Schweregrad"]].value_counts().to_frame()
    table3.columns = ["Anzahl"]
    result5 = mo.ui.table(table3, selection=None, pagination=False)


    result345 = mo.hstack(
        [result3, result4, result5],
        widths="equal",
        gap=1,
    )

    result345
    return result3, result345, result4, result5, table, table2, table3


@app.cell
def __(mo):
    mo.md(r"""#### Monatliche Statistiken""")
    return


@app.cell
def __(mo):
    month_column_filter = mo.ui.dropdown(
        options=["Unfalltyp", "Strassentyp", "Schweregrad"],
        value="Unfalltyp", 
        label="Variable für die monatliche Statistik: ",
    )
    month_column_filter
    return (month_column_filter,)


@app.cell
def __(alt, mo, month_column_filter, statistics_data):
    bars = alt.Chart(statistics_data).mark_bar().encode(
        y=alt.Y(f'count({month_column_filter.value})').stack('zero').title(f"Anzahl Unfälle"),
        x=alt.X('Monat').title("Monat"),
        color=alt.Color(f'{month_column_filter.value}'),
    )

    text = alt.Chart(statistics_data).mark_text(dy=-10).encode(
        y=alt.Y(f'count({month_column_filter.value})').stack('zero'),
        x=alt.X('Monat'),
        text=alt.Text(f"count({month_column_filter.value}):Q")
    )
    month_plot = mo.ui.altair_chart(bars + text)
    month_plot
    return bars, month_plot, text


if __name__ == "__main__":
    app.run()
