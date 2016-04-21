function showHeatmap(query_id, year) {
    $('#cal-heatmap').empty();

    var cal = new CalHeatMap();
    cal.init({
        data: 'services/heatmap/' + query_id + '/' + year,
        domain: "month",
        subDomain: "x_day",
        start: new Date(year, 0),
        minDate: new Date(year - 5, 0),
        maxDate: new Date(year + 5, 0),
        range: 12,
        previousSelector: "#cal-heatmap-prev",
        nextSelector: "#cal-heatmap-next",
    });
}
