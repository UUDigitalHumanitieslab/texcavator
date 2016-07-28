// Create metadata graphics for a query
function metadataGraphics(item) {
    console.log("metadataGraphics()");

    dojo.xhrGet({
        url: "services/metadata/",
        handleAs: "json",
        // TODO: it's better not to pass the search parameters here. See also TODO in backend.
        content: item,
    }).then(function(response) {
        // Describe what is being visualised
        $('#metadata_help').text('Metadata for query "' + item.query + '".');

        // Add pie charts
        var filtered = {
            types: !(item.st_advert && item.st_article &&
                     item.st_family && item.st_illust),
            distrib: !(item.sd_antilles && item.sd_indonesia &&
                       item.sd_national && item.sd_regional && item.sd_surinam),
            pillars: !!(item.pillars.length)
        };
        addPieChart(
            filtered.types, 
            response.articletype.buckets, 
            "#chart_articletype"
        );
        addPieChart(
            filtered.distrib, 
            response.distribution.buckets, 
            "#chart_distribution"
        );
        addPieChart(
            filtered.pillars, 
            response.pillar, 
            "#chart_pillar"
        );

        // Create newspapers bar chart
        data_newspapers = [{
            "key": "Newspapers",
            "values": response.newspapers.buckets
        }];

        nv.addGraph(function() {
            var chart = nv.models.multiBarHorizontalChart()
                .x(function(d) {
                    return d.key;
                })
                .y(function(d) {
                    return d.doc_count;
                })
                .margin({
                    top: 30,
                    right: 20,
                    bottom: 50,
                    left: 250
                })
                .valueFormat(d3.format(",d"))
                .showValues(true)
                .showControls(false)
                .tooltips(false);

            chart.yAxis
                .tickFormat(d3.format(",d"));

            d3.select("#chart_newspapers svg")
                .datum(data_newspapers)
                .call(chart);

            nv.utils.windowResize(chart.update);

            return chart;
        });
    }, function(err) {
        console.error(err);
    });
}

// Create a pie chart for a set of data points
function addPieChart(filtered, data, id) {
    nv.addGraph(function() {
        var chart = nv.models.pieChart()
            .x(function(d) {
                return d.key;
            })
            .y(function(d) {
                return d.doc_count;
            })
            .valueFormat(d3.format(",d"))
            .showLabels(true);
        
        if (filtered) {
            $(id).find('.filter-reset-btn').show();
        } else {
            chart.pie.dispatch.on('elementClick', filterSearch(id));
            $(id).find('.filter-reset-btn').hide();
        }

        d3.select(id + " svg")
            .datum(data)
            .transition().duration(1200)
            .call(chart);

        return chart;
    });
}

// Issue a new search when a pie segment is clicked, filtered by the segment
function filterSearch(id) {
    if (id === "#chart_articletype") return function(segmentData) {
        var selected = ES_REVERSE_MAPPING.st[segmentData.label].slice(3);
        for (var key in config.search.type) {
            if (key === selected) {
                config.search.type[key] = true;
            } else {
                config.search.type[key] = false;
            }
        }
        searchSubmit();
    }; else if (id === "#chart_distribution") return function(segmentData) {
        var selected = ES_REVERSE_MAPPING.sd[segmentData.label].slice(3);
        for (var key in config.search.distrib) {
            if (key === selected) {
                config.search.distrib[key] = true;
            } else {
                config.search.distrib[key] = false;
            }
        }
        searchSubmit();
    }; else /* id === "#chart_pillar" */ return function(segmentData) {
        getToolbarConfig();  // ensure that the checkboxes exist
        var selectedID = 'cb-pillar-' + segmentData.label;
        $('.pillar input').each(function(i) {
            var elem = $(this);
            if (elem.attr('id') === selectedID) {
                elem.prop('checked', true);
            } else {
                elem.prop('checked', false);
            }
        });
        searchSubmit();
    };
}
