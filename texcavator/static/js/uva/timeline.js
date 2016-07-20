dojo.require("dijit.TitlePane");

/*
function loadGraphData( queryId )
function findValue(start, end, data, startIndex)
function getDataForInterval( queryId, intervalIndex, callback )
function getData( queryId, field, interval, callback )
function getEndOfInterval( date, interval )
function createGraph() {
	function filterFunction( d )
	function redraw() {
		function nrOfBins( data )
		function burstUpdateFunction( burst )
	}
}
function burstClicked( data, index, element )
function burstCloud( params )
*/

var intervals = ['year']; // since zooming is broken, only query the year instead of ["year", "month", "day"];

var zoomLimit = 8 * 24 * 3600000; // Eight days
var zoomLimit = 10 * 60000; // Ten minutes //24*3600000; // One days

var detectBursts = true;


var showTimeline = function(item) {
	queryId = item.pk;
	queryTitle = item.title;
	queryString = item.query;
	console.log("showTimeline() queryId: " + queryId + ", queryTitle: " + queryTitle);

	setQueryMetadata(item);

	storeLexiconID(queryId); // query.js
	storeLexiconTitle(queryTitle); // query.js
	storeLexiconQuery(queryString); // query.js

	// select the tab containing the timeline
	var tc = dijit.byId("articleContainer");
	tc.selectChild(dijit.byId("timeline"));

	loadGraphData(queryId);

	// Toggle warning for advertisements
	$("#timeline-advert-warning").toggle(getConfig().search.type.advert);
};


function loadGraphData(queryId) {
	burstData = {};
	burstIntervalIndex = 0;
	burstAnimation = false;

	getDataForInterval(queryId, 0, function() {
		createGraph();

		var intervalIndex = 0;

		var continueFunction = function() {
			if (++intervalIndex < intervals.length) {
				getDataForInterval(queryId, intervalIndex, continueFunction);
			}
		};

		continueFunction();
	});
}


function findValue(start, end, data, startIndex) {
	if (data[0].start > end) return [0, 0];
	if (data[data.length - 1].end < start) return [0, data.length];
	for (indx = startIndex; indx < data.length; indx++) {
		if (data[indx].end < start) continue;
		return [data[indx].value, indx];
	}
	return [0, data.length];
}


function getDataForInterval(queryId, intervalIndex, callback) {
	var interval = intervals[intervalIndex];

	getData(queryId, interval, function(data) {
		// Detect bursts (mean + 2 * stddev)
		var mean = d3.mean(data, function(d) {
			return d.value;
		});
		var stddev = Math.sqrt(d3.mean(data, function(d) {
			return Math.pow(d.value - mean, 2);
		}));

		var burstLimit = mean + 2 * stddev;

		if (detectBursts) $.each(data, function(index, entry) {
			entry.burst = entry.value > burstLimit;
		});

		// Set the data, range and statistics
		burstData[intervalIndex] = {
			data: data,
			range: [0, d3.max(data, function(d) {
				return d.value;
			})],

			// Compute the extent of the data set for dates
			dateRange: [d3.min(data, function(d) {
					return d.start;
				}),
				d3.max(data, function(d) {
					return d.end;
				})
			],
			mean: mean,
			stddev: stddev
		};
		console.log("Loaded " + data.length + " data points for burst with interval " + interval + ".");

		// Set data for animation
		if (intervalIndex > 0) {
			var originalData = burstData[intervalIndex - 1].data;

			burstData[intervalIndex].animationData = [];
			var startIndex = 0;
			for (index = 0; index < burstData[intervalIndex].data.length; index++) {
				var result = findValue(burstData[intervalIndex].data[index].start,
					burstData[intervalIndex].data[index].end, originalData, startIndex);
				// Copy original data
				var newDatum = {};
				$.extend(newDatum, burstData[intervalIndex].data[index]);
				newDatum.value = result[0];
				burstData[intervalIndex].animationData.push(newDatum);
				startIndex = result[1];
			}
		}

		// Retrieve the data for the next interval
		callback(burstData[interval]);
	});
}


function getData(queryId, interval, callback) {
	var timeline_url = "query/timeline/" + queryId + "/" + interval;

	if (getConfig().timeline.normalize) {
		timeline_url += "?normalize=1";
	} else {
		timeline_url += "?normalize=0";
	}

	console.log("timeline_url: " + timeline_url);

	$.ajax({
		url: timeline_url,
		type: 'GET',
		dataType: 'json',
		processData: false,
		success: function(rawData) {
			// Prepare data
			var data = [];

			$.each(rawData.result, function(key, value) {
				data.push({
					start: new Date(key),
					end: getEndOfInterval(new Date(key), interval),
					value: value[0],
					count: value[1], // doc count shown in tooltip
					docs: value[2] // doc ids
				});
			});

			data = data.sort(function(a, b) {
				return a.start - b.start;
			});

			callback(data);
		},
		error: function(xhr, message, error) {
			console.error(message);
			genDialog("Error while loading timeline data", message, { "OK": true });
		}
	});
}


function getEndOfInterval(date, interval) {
	if (interval == "year") {
		var d = new Date(date.getTime());
		d.setFullYear(date.getFullYear() + 1);
		return d;
	}

	if (interval == "month") {
		return new Date(date.getFullYear(), date.getMonth() + 1, date.getDate(),
			date.getHours(), date.getMinutes(), date.getSeconds(), date.getMilliseconds());
	}

	if (interval == "week") {
		return new Date(date.getTime() + 7 * 24 * 3600000 - 1);
	}

	if (interval == "day") {
		return new Date(date.getTime() + 24 * 3600000 - 1);
	}

	if (interval == "hour") {
		return new Date(date.getTime() + 3600000 - 1);
	}

	if (interval == "10m") {
		return new Date(date.getTime() + 10 * 60000 - 1);
	}

	if (interval == "5m") {
		return new Date(date.getTime() + 5 * 60000 - 1);
	}

	if (interval == "minute") {
		return new Date(date.getTime() + 60000 - 1);
	}
}


function createGraph() {
	var config = getConfig();

	// Clear existing destination
	dojo.byId("chartDiv").innerHTML = "";

	// This follows the margin convention (http://bl.ocks.org/mbostock/3019563)
	var margin = {top: 30, right: 30, bottom: 30, left: 50},
		w = $("#chartDiv").width() - margin.left - margin.right,
		h = $("#chartDiv").height() - margin.top - margin.bottom;

	var x = d3.time.scale().range([0, w]);
	var y = d3.scale.linear().range([h, 0]);

	console.log("createGraph() w=" + w + ", h=" + h); // debug: sometimes the graph is compressed to a small width

	var xAxis = d3.svg.axis()
		.scale(x)
		.orient("bottom")
		.ticks(d3.time.years, 10);

	var yAxis = d3.svg.axis()
		.scale(y)
		.orient("left")
		.ticks(10);

	// Update the scale domains
	x.domain(burstData[burstIntervalIndex].dateRange);
	y.domain(burstData[burstIntervalIndex].range);

	// Create the SVG element of the chart
	var svg = d3.select("#chartDiv").append("svg:svg")
		.attr("width", w + margin.left + margin.right)
		.attr("height", h + margin.top + margin.bottom)
		.attr("pointer-events", "all");

	var body = svg.append("svg:g")
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")")
		.call(d3.behavior.zoom().on("zoom", redraw));

	function filterFunction(d) {
		if (d.end.getTime() < x.domain()[0])
			return false;
		if ((d.start.getTime() - (d.end.getTime() - d.start.getTime())) > x.domain()[1])
			return false;
		return true;
	}

	function redraw() {
		console.log("redraw()");

		if (burstAnimation) {
			return;
		} // Should only update X scale. Separate that from y scale? Can we do even that for area?

		// Use behavior instead of transform: 
		// https://github.com/mbostock/d3/blob/master/examples/zoom-pan/zoom-pan.html
		var previousXdomain = x.domain();
		if (d3.event) {
			d3.event.transform(x);
		}

		// Limit zooming in range
		var dateRange = burstData[burstIntervalIndex].dateRange;
		if (x.domain()[0] < dateRange[0]) {
			x.domain([dateRange[0], x.domain()[1]]);
		}
		if (x.domain()[1] > dateRange[1]) {
			x.domain([x.domain()[0], dateRange[1]]);
		}

		// Limit zooming to zoomLimit
		if ((x.domain()[1].getTime() - x.domain()[0].getTime()) < zoomLimit) {
			x.domain(previousXdomain);
		}

		// Prevent zooming out of Date range
		if (isNaN(x.domain()[0].getTime()) || isNaN(x.domain()[1].getTime())) {
			x.domain(previousXdomain);
		}
		
		body.append("g")
			.attr("class", "x axis")
			.attr("transform", "translate(0," + h + ")")
			.call(xAxis);

		body.append("g")
			.attr("class", "y axis")
			.call(yAxis);

		var newData;
		filteredData = burstData[burstIntervalIndex].data.filter(filterFunction);


		function nrOfBins(data) {
			var bins = data.length;
			if (bins > 1) {
				var binSize = data[0].end - data[0].start;
				if (binSize > 0) {
					bins = (data[data.length - 1].end - data[0].start) / binSize;
				}
				// else return the data.length
			}
			return bins;
		}

		if (nrOfBins(filteredData) < 10 && burstIntervalIndex < (intervals.length - 1) &&
			burstData[burstIntervalIndex + 1] !== undefined) {
			// Zoom in
			burstIntervalIndex += 1;
			console.log("Zooming in to interval " + intervals[burstIntervalIndex]);
			newData = burstData[burstIntervalIndex].data.filter(filterFunction);
			filteredData = burstData[burstIntervalIndex].animationData.filter(filterFunction);
		} else if (nrOfBins(filteredData) > 20 && burstIntervalIndex > 0 &&
			burstData[burstIntervalIndex - 1] !== undefined) {
			// Zoom out
			var zoomOutData = burstData[burstIntervalIndex - 1].data.filter(filterFunction);
			if (nrOfBins(zoomOutData) > 10) {
				burstIntervalIndex -= 1;
				console.log("Zooming out to interval " + intervals[burstIntervalIndex]);
				newData = burstData[burstIntervalIndex + 1].animationData.filter(filterFunction);
				filteredData = burstData[burstIntervalIndex + 1].data.filter(filterFunction);
			}
		}

		// Select all bursts
		var bursts = body.selectAll("rect.bursts")
			.data(filteredData);

		// Create new burst when needed
		// 'd' is the data, 'i' is the bar index: 0, 1, ..., 'this' is a svg rect class
		bursts.enter().append("svg:rect")
			.attr("class", "bursts")
			.attr("y", h)
			.on("mouseover", function(d, i) {
				d3.select(this).transition().duration(300).style("opacity", 0.5);
			})
			.on("mouseout", function(d, i) {
				d3.select(this).transition().duration(300).style("opacity", 1.0);
			})
			.on("mouseup", function(d) {
				burstClicked(d);
			})
			.transition()
			.duration(1000)
			.attr("y", function(d) {
				return y(d.value);
			})
			.attr("height", function(d) {
				return h - y(d.value);
			});

		// Delete unneeded bursts and path
		bursts.exit().remove(); //call(exitTransition(burstUpdateFunction, 2500));

		function burstUpdateFunction(burst) {
			burst
				.attr("x", function(d) {
					return x(d.start);
				})
				.attr("width", function(d) {
					return Math.max(4, x(d.end) - x(d.start) + 1);
				})
				.style("opacity", 1)
				.style("fill", function(d) {
					if (config.timeline.burst_detect) {
						return (d.burst) ? "red" : "steelblue";
					} else {
						return "steelblue";
					}
				});
		}

		// Place bursts at right spot
		bursts.call(burstUpdateFunction);

		// Update tooltip document count
		body.selectAll("title").remove();
		bursts.append("svg:title")
			.text(function(d, i) {
				s = d.count + " document" + ((d.count == 1) ? "" : "s");
				if (getConfig().timeline.normalize) {
					s += " (relative frequency: " + d.value + "%)";
				}
				return s;
			});

		// Update period
		svg.selectAll("text.period")
			.data([0])
			.enter().append("svg:text")
			.attr("class", "period")
			.attr("fill", "#555")
			.attr("x", 50)
			.attr("y", 0)
			.attr("dy", "1em")
			.attr("text-anchor", "left");

		var title = "Period: " + toDateString(beginDate) + " - " + toDateString(endDate); 
		if (beginDate2) {
			title += " & " + toDateString(beginDate2) + " - " + toDateString(endDate2);
		}
		title += ", Query title: " + retrieveLexiconTitle();

		svg.selectAll("text.period").text(title);

		// If we have newData, set up animation
		if (newData !== undefined) {
			burstAnimation = true;

			y.domain(burstData[burstIntervalIndex].range);

			body.selectAll("rect.bursts")
				.data(newData)
				.transition()
				.duration(2500)
				.call(burstUpdateFunction);
		}
	}
	redraw();


	// Raise the bars
	y.range([h, 0]);
} // createGraph()


function burstClicked(d) {
	console.log("burstClicked(): " + d.docs.length + " records");

	// Show articles in search accordion; set timeline values in filters
	var query_id = retrieveLexiconID();
	var query = retrieveLexiconQuery();
	dijit.byId("query").set("value", query);
	setDateFilters(d.start, d.end);
	accordionSelectChild("searchPane");
	searchSubmit();

	// Set the title for the cloud
	var template = "{burst} from {start} to {end} ({count} document{plural})";
	var content = {
		burst: (d.burst) ? "Burst cloud" : "Cloud",
		start: d.start.toString().substr(4, 11),
		end: d.end.toString().substr(4, 11),
		count: d.count,
		plural: d.count > 1 ? "s" : "",
	};
	var cloudContainer = dijit.byId("cloudContainer");
	cloudContainer.set("title", dojo.replace(template, content));

	// Create the cloud
	burstCloud(query_id);

	// Create the heat map
	showHeatmap(query_id, d.start.getFullYear());
} // burstClicked()


function burstCloud(query_id) {
	console.log("burstCloud()");

	dojo.place(new dijit.ProgressBar({
		indeterminate: true
	}).domNode, dojo.byId("cloud"), "only");

	var params = {
		queryID: query_id,
		is_timeline: true,
		date_range: getDateRangeString()
	};

	params = getCloudParameters(params); // add user-changeable parameters from config

	dojo.xhrGet({
		url: "services/cloud",
		content: params,
		failOk: false, // true: No dojo console error message
		handleAs: "json",
	}).then(function(resp) {
		console.log("requesting task id for burstcloud");
		console.log(resp);

		if (resp.status != "ok") {
			console.error(resp.msg);
			closePopup();
			var title = "Cloud request failed";
			var buttons = {
				"OK": true
			};
			genDialog(title, resp.msg, buttons);
			return;
		} else if (resp.result) {
			// this will be the case for single documents
			createCloud("burst", resp, "cloud");
			return;
		} else {
			console.log("Retrieved task_id: " + resp.task);
			return resp.task;
		}
	}, function(err) {
		console.error(err);
	}).then(function(task_id) {
		if (task_id) {
			console.log("Start polling!");
			console.log("task_id: " + task_id);
			check_status(task_id);
		} else {
			console.log('No task_id returned');
		}
	});
} // burstCloud()


function switchTimelineNormalize() {
	// Switch between normalizations
	var newValue = !getConfig().timeline.normalize;
	getConfig().timeline.normalize = newValue;
	dijit.byId('cb-normalize').set('checked', newValue);

	// Reload the timeline graph
	dojo.xhrGet({
		url: 'query/' + retrieveLexiconID(),
		handleAs: 'json',
		sync: true,
		load: function(response) {
			if (response.status === "OK") {
				showTimeline(response.query);
			}
		},
		error: function(err) {
			console.error(err);
		}
	});
} // switchTimelineNormalize()