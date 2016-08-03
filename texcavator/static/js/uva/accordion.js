// FL-27-Mar-2013 Created
// FL-10-Sep-2013 Changed

/*
	function accordionSelectChild( id )
	function createQueryLine( item )
	function createQueryList()
	function updateQueryDocCounts( item )
*/

dojo.require("dojo.store.JsonRest");
dojo.require("dijit.ProgressBar");


function accordionSelectChild(id) {
	dijit.byId("leftAccordion").selectChild(id);
} // accordionSelectChild()


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
			showTimeline(item); // timeline.js
		}
	})).domNode, buttonsNode);


	// Add a download button if downloading is allowed.
	if (QUERY_DATA_DOWNLOAD && !is_guest) {
		btn = dijit.byId("btn-sq-download-" + item.pk);
		if (btn !== undefined) {
			if (debug_destroy) {
				console.error("btn-sq-download button already exists");
			}
			btn.destroy();
		}

		dojo.place((new dijit.form.Button({
			id: "btn-sq-download-" + item.pk,
			title: "Export your query results to .json, .xml or .csv",
			iconClass: "dijitIconSave",
			showLabel: false,
			onClick: function() {
				downloadQueryDialog(item); // query.js
			}
		})).domNode, buttonsNode);
	}

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
		title: "Re-save your query, using the current filter settings",
		iconClass: "dijitIconEditTask",
		showLabel: false,
		onClick: function() {
			var newItem = itemFromCurrentQuery();
			// Only modify the query when it has some data
			if (newItem.title && newItem.query) {
				saveQuery(newItem, "query/" + item.pk + "/update");
				createQueryList();
			}
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