var PanelController = function() {
    this.tab = 1;

    this.selectTab = function(numTab) {
        this.tab = numTab;
    };

    this.isSelected = function(numTab) {
        return this.tab === numTab;
    };
}
