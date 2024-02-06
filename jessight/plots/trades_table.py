from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode

from jessight.plots.renderers import checkbox_renderer


def draw_grid(
    df,
    formatter: dict = None,
    fit_columns=False,
    theme="streamlit",
    max_height: int = 400,
    wrap_text: bool = False,
    grid_options: dict = None,
    key=None,
    css: dict = None,
) -> AgGrid:
    formatter = formatter or {}

    gb = GridOptionsBuilder.from_dataframe(df, enableRowGroup=True, enableValue=True, enablePivot=True)

    gb.configure_column("Viewed", editable=True, cellRenderer=checkbox_renderer)
    gb.configure_default_column(
        editable=False,
        groupable=False,
        filterable=True,
        enableValue=True,
        enablePivot=True,
        wrapText=wrap_text,
        enableRowGroup=True,
    )

    if grid_options is not None:
        gb.configure_grid_options(**grid_options)

    for latin_name, (cyr_name, style_dict) in formatter.items():
        gb.configure_column(latin_name, header_name=cyr_name, **style_dict)

    gb.configure_side_bar()
    gb.configure_selection("single")
    return AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.VALUE_CHANGED,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=fit_columns,
        height=min(max_height, (1 + len(df.index)) * 29),
        theme=theme,
        key=key,
        custom_css=css,
    )
