function showHeatmap(query_id, year) {
    $('#cal-heatmap').empty();

    var cal = new CalHeatMap();
    cal.init({
        data: 'services/heatmap/' + query_id + '/' + year,
        domain: "month",
        subDomain: "day",
        start: new Date(year, 0),
        minDate: new Date(year - 5, 0),
        maxDate: new Date(year + 5, 0),
        range: 12,
        previousSelector: "#cal-heatmap-prev",
        nextSelector: "#cal-heatmap-next",
        legendHorizontalPosition: "center",
        onClick: function(d) {
            beginDate = d;

            // Sets enddate to the day after the clicked date
            // Code copied from http://stackoverflow.com/a/3674550/3710392
            var tomorrow = new Date(d);
            tomorrow.setDate(tomorrow.getDate() + 1);
            endDate = tomorrow;
            
            dijit.byId("begindate").set("value", beginDate);
            dijit.byId("enddate").set("value", endDate);
            if (beginDate2 !== undefined) {
                toggleSecondDateFilter();
            }
            accordionSelectChild("searchPane");
            searchSubmit();
        },
    });
}
