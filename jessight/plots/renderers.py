from st_aggrid import JsCode

# TODO: Add documentation about this file if it is not redundant, otherwise remove it

checkbox_renderer = JsCode(
    """
    class CheckboxRenderer{
    init(params) {
        this.params = params;
        this.eGui = document.createElement('input');
        this.eGui.type = 'checkbox';
        this.eGui.checked = params.value;
        this.checkedHandler = this.checkedHandler.bind(this);
        this.eGui.addEventListener('click', this.checkedHandler);
    }
    checkedHandler(e) {
        let checked = e.target.checked;
        let colId = this.params.column.colId;
        this.params.node.setDataValue(colId, checked);
    }
    getGui(params) {
        return this.eGui;
    }
    destroy(params) {
    this.eGui.removeEventListener('click', this.checkedHandler);
    }
    }//end class
    """
)
