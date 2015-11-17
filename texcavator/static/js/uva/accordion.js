// FL-27-Mar-2013 Created
// FL-10-Sep-2013 Changed

/*
	function collection_fromradio()
	function accordionSelectChild( id )
	function createQueryLine( item )
	function createQueryList()
	function updateQueryDocCounts( item )
*/

dojo.require("dojo.store.JsonRest");
dojo.require("dojox.form.RangeSlider");


function collection_fromradio() {
	return ES_INDEX;
}


function accordionSelectChild(id) {
	// how to select accordion child?
	var accordion = dijit.byId("leftAccordion");
	var selected_child = accordion.get("selectedChildWidget");
	if (selected_child.id !== id) {
		accordion.back();
	} // show Search pane
} // accordionSelectChild()


function createYearSlider(min, max, n) {
	// default value for n
	n = typeof n !== 'undefined' ? n : "";

	//	console.log( "createYearSlider()" );
	storeDateLimits(min, max);

	var min_year = beginDate.getFullYear();
	var max_year = endDate.getFullYear();
	//	console.log( "from: " + min_year  + " to: " + max_year );

	var discrete_values = max_year - min_year + 1;
	//	console.log( "discrete_values: " + discrete_values );

	var rangeSlider = new dojox.form.HorizontalRangeSlider({
		id: "year-range-slider" + n,
		value: [min_year, max_year],
		minimum: min_year,
		maximum: max_year,
		intermediateChanges: false,
		discreteValues: discrete_values,
		style: (n ? "display: none;" : ""),
		onChange: function(value) {
			//	console.log( "value:" + value );

			var new_min_year = Math.ceil(value[0]);
			var new_max_year = Math.floor(value[1]);
			//	console.log( "from: " + new_min_year  + " to: " + new_max_year );

			var old_min_date = n ? beginDate2 : beginDate;
			var old_max_date = n ? endDate2 : endDate;
			//	console.log( "old from: " + old_min_date + ", to: " + old_max_date );

			var min_month = old_min_date.getMonth();
			var max_month = old_max_date.getMonth();

			var min_day = old_min_date.getDate();
			var max_day = old_max_date.getDate();

			//	console.log( "from: year: " + old_min_year + ", month: " + min_month + ", day: " + min_day );
			//	console.log( "to: year:   " + old_max_year + ", month: " + max_month + ", day: " + max_day );

			var new_min_date = new Date(new_min_year, min_month, min_day);
			var new_max_date = new Date(new_max_year, max_month, max_day);

			// update date widgets in toolbar
			dijit.byId("begindate" + n).set("value", new_min_date);
			dijit.byId("enddate" + n).set("value", new_max_date);
		}
	}, "div-year-range-slider" + n);

	// create legend for year slider range
	// parseInt with radix 10 to prevent trouble with leading 0's (octal, hex)
	// substring: from index is included, to index is not included
	var min_y = parseInt(min.substring(0, 4), 10);
	var max_y = parseInt(max.substring(0, 4), 10);

	var legend = '<span style="float:left">' + min_y + '</span>';
	legend += '<span style="float:center">' + "search period" + '</span>';
	legend += '<span style="float:right">' + max_y + '</span><hr>';

	dojo.create("label", {
		innerHTML: legend
	}, "div-year-range-legend" + n);
} // createYearSlider()


function updateYearSlider(min_date, max_date, n) {
	// default value for n
	n = typeof n !== 'undefined' ? n : "";
	// we get here from the toolbar date widgets
	var min_year = min_date.getFullYear();
	var max_year = max_date.getFullYear();
	//	console.log( "from: " + min_year  + " to: " + max_year );
	dijit.byId("year-range-slider" + n).set("value", [min_year, max_year]);
}


// Update the number of results for a Query, synchronically.
function updateResults(query_id) {
	var result = 'unknown';
	dojo.xhrGet({
		url: 'query/' + query_id + '/update_nr_results',
		handleAs: 'json',
		sync: true,
		load: function(response) {
			if (response.status === "SUCCESS") {
				result = response.count;
			}
		},
		error: function(err) {
			console.error(err);
		}
	});
	return result; 
}


// the "btn-sq-fetch-" button becomes dead with Dojo-1.9.0
// strangely, the other queryline buttons do work with Dojo-1.9.0
function createQueryLine(item) {
	var title = item.title;
	var pk = item.pk;
	var date_created = item.date_created.slice(0, 16);
	var results = item.nr_results;

	// If the number of results is invalidated, retrieve the count. 
	if (!results)
	{
		results = updateResults(pk);
	}

	var string = '<span title="' + item.comment + '">' + title + ' [' + results + '] <em>' + date_created + '</em></span>';
	var params = {
		style: 'clear: both;'
	};
	var itemNode = dojo.byId("query-" + item.pk);
	dojo.html.set(itemNode, string, params);
	var buttonsNode = dojo.create('span', {
		style: 'float:right;'
	}, itemNode);

	var btn = null;
	var debug_destroy = false;
	
	var articleContainer = dijit.byId('articleContainer');

	//	console.log( "Button re-search" );
	btn = dijit.byId("btn-sq-fetch-" + item.pk);
	if (btn !== undefined) {
		if (debug_destroy) {
			console.error("btn-sq-fetch button already exists");
		}
		btn.destroy();
	}

	dojo.place((new dijit.form.Button({
		id: "btn-sq-fetch-" + item.pk,
		title: "Fetch results and visualise metadata",
		iconClass: "dijitIconSearch",
		showLabel: false,
		onClick: function() {
			console.log("Fetch " + title);
			researchSubmit(item);
			articleContainer.selectChild(dijit.byId('metadata'));
		}
	})).domNode, buttonsNode);

	//	console.log( "Button cloud for lexicon item" );
	btn = dijit.byId("btn-sq-cloud-" + item.pk);
	if (btn !== undefined) {
		if (debug_destroy) {
			console.error("btn-sq-cloud button already exists");
		}
		btn.destroy();
	}

	dojo.place((new dijit.form.Button({
		id: "btn-sq-cloud-" + item.pk,
		title: "Generate wordcloud",
		iconClass: "dijitEditorIcon dijitEditorIconJustifyCenter",
		showLabel: false,
		onClick: function() {
			onClickExecute(item);
		}
	})).domNode, buttonsNode);


	//	console.log( "Button timeline for lexicon item" );
	btn = dijit.byId("btn-sq-timeline-" + item.pk);
	if (btn !== undefined) {
		if (debug_destroy) {
			console.error("btn-sq-timeline button already exists");
		}
		btn.destroy();
	}

	// timeline for lexicon item
	dojo.place((new dijit.form.Button({
		id: "btn-sq-timeline-" + item.pk,
		title: "Timeline",
		iconClass: "dijitIconChart",
		showLabel: false,
		onClick: function() {
			var collection = collection_fromradio();
			showTimeline(item, collection); // timeline.js
		}
	})).domNode, buttonsNode);

	//	console.log( "Button update for lexicon item" );
	btn = dijit.byId("btn-sq-modify-" + item.pk);
	if (btn !== undefined) {
		if (debug_destroy) {
			console.error("btn-sq-modify button already exists");
		}
		btn.destroy();
	}

	dojo.place((new dijit.form.Button({
		id: "btn-sq-modify-" + item.pk,
		title: "Modify",
		iconClass: "dijitIconSave",
		showLabel: false,
		onClick: function() {
			var newItem = itemFromCurrentQuery();
			saveQuery(newItem, "query/" + item.pk + "/update");
			createQueryList();
		}
	})).domNode, buttonsNode);

	//	console.log( "Button delete for lexicon item" );
	btn = dijit.byId("btn-sq-delete-" + item.pk);
	if (btn !== undefined) {
		if (debug_destroy) {
			console.error("btn-sq-delete button already exists");
		}
		btn.destroy();
	}

	dojo.place((new dijit.form.Button({
		id: "btn-sq-delete-" + item.pk,
		title: "Delete",
		iconClass: "dijitIconDelete",
		showLabel: false,
		onClick: function() {
			genDialog(
				"Delete query",
				"Are you sure you want to delete this query?", {
					"OK": true,
					"Cancel": true
				},
				function() {
					require(["dojo/request/xhr"], function(xhr) {
						xhr.post("query/" + item.pk + "/delete", {
							handleAs: "json"
						}).then(function(result) {
							var buttons = {
								"OK": true
							};
							genDialog("Delete query", result.msg, buttons);
							createQueryList();
						}, function(error) {
							var buttons = {
								"OK": true
							};
							genDialog("Delete query", error.response.text, buttons);
						});
					});
				});
		}
	})).domNode, buttonsNode);
} // createQueryLine()


function createQueryList() {
	console.log("createQueryList()");

	dojo.place(new dijit.ProgressBar({
		indeterminate: true
	}).domNode, dojo.byId("lexiconItems"), "only");

	dojo.xhrGet({
		url: "query/",
		handleAs: "json",
		load: function(response) {
			if (response.status != "OK") {
				var msg = "We could not read the lexicons:<br/>" + response.msg;
				var buttons = {
					"OK": true
				};
				genDialog(title, msg, buttons);
			} else {
				dojo.empty(dojo.byId("lexiconItems")); // this does not delete the buttons!, memory leak: 
				// see: http://higginsforpresident.net/2010/01/widgets-within-widgets/

				var items = response.queries;
				// TODO: delete this global variable
				glob_lexiconData = items;

				dojo.forEach(items, function(item) {
					// create the divs for the saved queries
					var itemNode = dojo.create('div', {
						id: "query-" + item.pk,
						innerHTML: "", // title, counts & date are added later
						style: 'clear: both;'
					}, dojo.byId("lexiconItems"));
				});

				dojo.forEach(items, function(item) {
					createQueryLine(item); // add title, date, buttons
				});
			}
		},
		error: function(err) {
			console.error(err);
			var title = "createQueryList failed";
			var buttons = {
				"OK": true
			};
			genDialog(title, err, buttons);
			return err;
		}
	});
} // createQueryList()