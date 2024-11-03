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
def __(data_filtered, mo):
    n_accidents = mo.stat(
        label="Anzahl Unfälle",
        bordered=True,
        value=len(data_filtered),
    )

    n_severe_accidents = mo.stat(
        label="Anzahl Unfälle mit Schwerverletzten",
        bordered=True,
        value=len(data_filtered[data_filtered["SeverityCategory"] == "Unfall mit Schwerverletzten"]),
    )

    n_death_accidents = mo.stat(
        label="Anzahl Unfälle mit Toten",
        bordered=True,
        value=len(data_filtered[data_filtered["SeverityCategory"] == "Unfall mit Getöteten"]),
    )

    mo.hstack([n_accidents, n_severe_accidents, n_death_accidents],
        widths="equal",
        gap=1,)
    return n_accidents, n_death_accidents, n_severe_accidents


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
        start=int(data["Year"].min()), 
        stop=int(data["Year"].max()), 
        show_value=True, 
        label="Zeitspanne: ",
    )

    list_cantons = data["Canton"].unique()
    canton_filter = mo.ui.multiselect(
        options=sorted(list_cantons), 
        #value=list_cantons,
        value=["ZH",], 
        label="Kanton: ",
    )

    list_roadtypes = data["RoadType"].unique()
    roadtype_filter = mo.ui.multiselect(
        options=sorted(list_roadtypes),
        value=list_roadtypes,
        label="Strassentyp: ",
    )

    list_accidenttypes = data["Type"].unique()
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
    data_filtered = data_filtered[data_filtered["Year"].astype(int) >= date_range.value[0]]
    data_filtered = data_filtered[data_filtered["Year"].astype(int) <= date_range.value[1]]
    data_filtered = data_filtered[data_filtered["RoadType"].isin(selected_roadtypes)]
    data_filtered = data_filtered[data_filtered["Type"].isin(selected_accidenttypes)]
    data_filtered = data_filtered[data_filtered["Canton"].isin(selected_cantons)]
    data_filtered = data_filtered.sort_values(["Year", "Canton", "Type", "RoadType", "SeverityCategory"])
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
        result2 = mo.ui.table(data_filtered.loc[:, ['latitude', 'longitude', 'Type', 'SeverityCategory','RoadType', 'Canton', 'Year']], selection=None)
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
    map_data = map_data.sort_values(by=["Year", "Month"], ascending=[False, False])
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
    color_column=""
    match color_filter.value:
        case "Unfalltyp":
            color_column="Type"
        case "Strassentyp":
            color_column="RoadType"
        case "Schweregrad":
            color_column="SeverityCategory"

    fig = px.scatter_mapbox(
        map_data,
        lat="latitude",
        lon="longitude",
        color=color_column,
        hover_data=["Type", "RoadType", "SeverityCategory", "Month", "Year", "Canton"],
        zoom=8.6,
        labels={"Type": "Unfalltyp", "RoadType": "Strassentyp", "SeverityCategory": "Schweregrad"}
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
    return color_column, fig, map


@app.cell
def __(color_filter, map, mo, pd):
    try:
        table = pd.DataFrame(map.value).loc[:, [color_filter.value]].value_counts().to_frame()
        table.columns = ["Anzahl"]
        result3 = mo.ui.table(table, selection=None, pagination=False)
    except (KeyError):
        result3 = mo.md("Selektiere eine Region auf der Karte um eine Statistik zu erhalten.")

    try:
        table2 = pd.DataFrame(map.value).loc[:, ["Jahr"]].value_counts().to_frame()
        table2.columns = ["Anzahl"]
        result4 = mo.ui.table(table2, selection=None, pagination=False)
    except (KeyError):
        result4 = mo.md("")

    mo.hstack([result3, result4],
        widths="equal",
        gap=1,)
    return result3, result4, table, table2


if __name__ == "__main__":
    app.run()
