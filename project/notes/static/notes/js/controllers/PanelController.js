var PanelController = function($cookies) {

    this.tab = parseInt($cookies.get('panelTab')) || 2;

    this.selectTab = function(numTab) {
        this.tab = numTab;
        $cookies.put('panelTab', numTab);
    };

    this.isSelected = function(numTab) {
        return this.tab === numTab;
    };
}
