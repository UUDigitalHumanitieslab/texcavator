// FL-12-Nov-2012 Created
// FL-13-Dec-2013 Changed

/*
function storeLexiconID( lexicon_id )
function retrieveLexiconID()
function storeLexiconTitle( lexicon_title )
function retrieveLexiconTitle()
function storeLexiconQuery( lexicon_query )
function retrieveLexiconQuery()
function createQueryDlg()
function okDownload( query_title )
*/

dojo.require("dijit.form.Button");
dojo.require("dijit.form.CheckBox");
dojo.require("dijit.form.ComboBox");
dojo.require("dijit.form.Textarea");
dojo.require("dijit.layout.TabContainer");
dojo.require("dijit.ProgressBar");


var lexiconID = null; // file global
var lexiconTitle = null; // file global
var lexiconQuery = null; // file global


// Getters and setters for global variables above
function storeLexiconID(lexicon_id) {
	lexiconID = lexicon_id;
}

function retrieveLexiconID() {
	return lexiconID;
}


function storeLexiconTitle(lexicon_title) {
	lexiconTitle = lexicon_title;
}

function retrieveLexiconTitle() {
	return lexiconTitle;
}


function storeLexiconQuery(lexicon_query) {
	lexiconQuery = lexicon_query;
}

function retrieveLexiconQuery() {
	return lexiconQuery;
}


// Starts the download dialog
function downloadQueryDialog(item) {
	console.log("downloadQueryDialog()");

	var cpQData = new dijit.layout.ContentPane({
		id: "cp-data",
		content: "<strong>Download options</strong>",
	});

	// Output formats (json, xml, csv)
	dojo.create("div", {
		id: "div-qdata-format"
	}, cpQData.domNode);

	var textQDataFormat = dojo.create("label", {
		id: "text-qdata-format",
		for: "div-qdata-format",
		innerHTML: "Export format: <br/>"
	}, cpQData.domNode);

	var formats = {
		'json': 'JSON (native format)',
		'xml': 'XML (slow! conversion)',
		'csv': 'CSV (TAB delimited)',
	};
	$.each(formats, function(key, value) {
		var rb = new dijit.form.RadioButton({
			id: "rb-qdata-" + key,
			checked: getConfig().querydataexport.format === key,
			onChange: function(btn) {
				if (btn) {
					getConfig().querydataexport.format = key;
				}
			},
		});
		rb.placeAt(cpQData.domNode);

		var label = dojo.create("label", {
			id: "label-qdata-" + key,
			for: "rb-qdata-" + key,
			innerHTML: "&nbsp;" + value + "<br />",
		}, cpQData.domNode);
	});

	// Simplified export
	var hrSimplifiedExport = dojo.create("hr", {
		id: "hr-simplified-export",
	}, cpQData.domNode);

	var divSimplifiedExport = dojo.create("div", {
		id: "div-simplified-export",
	}, cpQData.domNode);

	var cbSimplifiedExport = new dijit.form.CheckBox({
		id: "cb-simplified-export",
		checked: getConfig().querydataexport.simplified,
		onChange: function(btn) {
			getConfig().querydataexport.simplified = btn;
		}
	}, divSimplifiedExport);

	var labelSimplifiedExport = dojo.create("label", {
		id: "label-simplified-export",
		for: "cb-simplified-export",
		innerHTML: "&nbsp;Simplified export (only article title and full text)<br/>"
	}, cpQData.domNode);

	var title = "Download the query data (OCR and metadata)";
	var buttons = { "OK": true, "Cancel": true };
	genDialog(title, cpQData.domNode, buttons, function() { okDownload(item); });
}


// Starts the download of a query
function okDownload(item) {
	console.log("okDownload() : " + item.pk);

	var config = getConfig();
	var params = {
		pk: item.pk,
		format: config.querydataexport.format, // "json", "xml" or "csv"
		simplified: config.querydataexport.simplified
	};

	dojo.xhrGet({
		url: "query/download/prepare/",
		content: params,
		handleAs: "json",
		load: function(result) {
			var title = "Preparing download failed";
			if (result.status === "SUCCESS") {
				title = "Download finished";
			}

			var buttons = {
				"OK": true,
				"Cancel": false
			};
			answer = genDialog(title, result.msg, buttons);
		},
		error: function(err) {
			console.error(err);
			return err;
		}
	});

	genDialog("Preparing download",
		"Your download is being prepared. This might take a while. When the download is finished, a message box will pop up.", {
			"OK": true
		});
};


// Save a created or modified query
function saveQuery(item, url) {
	console.log("saveQuery() title: " + item.title + ", query: " + item.query);
	console.log("url: " + url);

	dojo.xhrPost({
		url: url,
		handleAs: "json",
		content: item,
		load: function(result) {
			if (result.status !== "SUCCESS") {
				var msg = "The query could not be saved:<br/>" + result.msg;
				var dialog = new dijit.Dialog({
					title: "Save query",
					style: "width: 300px",
					content: msg
				});
				dialog.show();
			}

			createQueryList();

			var successDialog = new dijit.Dialog({
				title: "Save query",
				style: "width: 300px",
				content: "Query saved successfully",
			});
			successDialog.show();

			accordionSelectChild("lexicon");
		},
		error: function(err) {
			console.error(err);
		}
	});
}


// Return the current query as the kind of 'item' that is used everywhere
function itemFromCurrentQuery() {
	var params = getSearchParameters();
	params.title = dojo.byId("queryTitle").value;
	params.comment = dojo.byId("queryComment").value;
	params.query = dojo.byId("query").value;
	return params;
}


// button Save query
function queryToLexicon()
{
	var dialog = new dijit.Dialog({
		title: "Save query",
		style: "width: 300px",
	});

	var item = itemFromCurrentQuery();

	if( isWhitespaceOrEmpty( item.query ) == true )        // utils.js
	{
		var title = "Save query";
		var buttons = { "OK": true };
		genDialog( title, "Your query is empty", buttons );
		return;
	}
	
	if (!validateQuery(item.query)) return;  // sanitize_query.js
	
	// optionally overwrite an existing query
	var formerItem = $('#queryTitle').data('activeItem');
	if (formerItem && item.title == formerItem.title) {
		var title = 'Overwrite query';
		var message = 'You changed the query but not the title. Do you want to replace the query?';
		var buttons = {'OK': true, 'Cancel': true};
		genDialog(title, message, buttons, function () {
			saveQuery(item, 'query/' + formerItem.pk + '/update');
		});
		$('#queryTitle').focus();
		return;
	}

	// validate CQL -> ES; when valid, stores query
	saveQuery(item, "query/create");     // query.js
} // queryToLexicon


// button Uitvoeren: metadata graphics + query word cloud
function onClickExecute(item)
{
	queryID = item.pk;
	query = item.query;

	console.log( "onClickExecute() queryID: " + queryID + " : " + query );
	console.log(item);

	storeLexiconID( queryID );            // query.js

	setQueryMetadata(item);

	// Cloud
	var config = getConfig();
	var params = {
		queryID    : queryID,
		dateRange  : getDateRangeString()
	}
	params = getCloudParameters( params );

//	console.log( params );
	dojo.xhrGet({
		url: "services/doc_count/",
		handleAs: "json",
		content: params,
		load: function( data )
		{
			if( data.status !== "ok" )
			{
				var title = "Request failed";
				var buttons = { "OK": true };
				genDialog( title, data.msg, buttons );
				return;
			}
			else
			{
				onClickExecuteCloud( queryID );
			} 
		}
	});
} // onClickExecute


var retrieveRecord = function( record_id )
{
	console.log("retrieveRecord: " + record_id);

	var ocr_pane = "record";
	var cloud_pane = "cloudPane";

	// Select OCR tab
	dijit.byId("articleContainer").selectChild(dijit.byId(ocr_pane));
	
	// Cause the selected article to be highlighted
	$('#search-result ol li').removeClass('active-article');
	// Using the [id="value"] construct because jQuery will choke on the
	// colons in the id otherwise.
	$('[id="' + record_id + '"]').addClass('active-article');
	
	dojo.place( new dijit.ProgressBar( { indeterminate: true } ).domNode, dojo.byId( cloud_pane ), "only" );

	dojo.xhrGet({
		url: "services/retrieve/" + record_id,
		failOk: false,            // true: No dojo console error message
		handleAs: "json",
		load: function( resp )
		{
			dojo.empty( dojo.byId( cloud_pane ) );          // remove ProgressBar

			if( resp.status === "SUCCESS" )
			{
				processRecord(record_id, resp.article_dc_title, resp.text_content);
			}
			else
			{
				console.error( resp.msg );
				var title = "Request failed";
				var buttons = { "OK": true };
				genDialog( title, resp.msg, buttons );
				return;
			}
		},
		error: function( err ) { console.error( err ); }
	});
}

// Process a record: write the OCR, retrieve the scan and create the single article cloud
var processRecord = function(record_id, article_title, ocr_text)
{
	console.log("processRecord: " + record_id);
	writeTextview(article_title, ocr_text);         // update article in Text tab
	scanImages(record_id);                          // scan_images.js : scan[s] + View at KB tab
	retrieveRecordCloudData(record_id);             // create word cloud
}


function setQueryMetadata(item) {
	var query = item.query;
	console.log( "query: " + query );
	dojo.byId( "query" ).value = query;        // display query in Search textBox

	// set query meta data
	// set query title and comment
	$('#queryTitle').data('activeItem', item);

	dojo.byId("queryTitle").value = item.title;
	dojo.byId("queryComment").value = item.comment;

	// Daterange
	beginDate = stringToDate(item.dates[0].lower);
	endDate = stringToDate(item.dates[0].upper);
	console.log("Date range: " + beginDate + " - " + endDate);

	dijit.byId( "begindate" ).set( "value", beginDate );
	dijit.byId( "enddate"   ).set( "value", endDate );

	// Set the second search date
	if (item.dates[1]) {
		if (beginDate2 == undefined) {
			toggleSecondDateFilter();
		}

		beginDate2 = stringToDate(item.dates[1].lower);
		endDate2 = stringToDate(item.dates[1].upper);
		console.log("Date range 2: " + beginDate2 + " - " + endDate2);

		dijit.byId( "begindate-2" ).set( "value", beginDate2 );
		dijit.byId( "enddate-2"   ).set( "value", endDate2 );
	}
	// Or set it to null
	else if (beginDate2 !== undefined) {
		toggleSecondDateFilter();
	}
	
	require(["dojo/_base/array"], function(arrayUtil) {
		// Distributions
		var excl_dist = item.exclude_distributions;
		console.log("Exclude distributions: "+excl_dist);

		var val_sd_national = true;
		var val_sd_regional = true;
		var val_sd_antilles = true;
		var val_sd_surinam = true;
		var val_sd_indonesia = true;

		if(arrayUtil.indexOf(excl_dist, "sd_national") != -1){
			val_sd_national = false;
		}

		if(dijit.byId("cb-distrib-national-nl")){
			dijit.byId("cb-distrib-national-nl").set("checked", val_sd_national);
		}
		config["search"]["distrib"]["national"] = val_sd_national;

		if(arrayUtil.indexOf(excl_dist, "sd_regional") != -1){
			val_sd_regional = false;
		}

		if(dijit.byId("cb-distrib-regional")){
			dijit.byId("cb-distrib-regional").set("checked", val_sd_regional);
		}
		config["search"]["distrib"]["regional"] = val_sd_regional;

		if(arrayUtil.indexOf(excl_dist, "sd_antilles") != -1){
			val_sd_antilles = false;
		}

		if(dijit.byId("cb-distrib-antilles")){
			dijit.byId("cb-distrib-antilles").set("checked", val_sd_antilles);
		}
		config["search"]["distrib"]["antilles"] = val_sd_antilles;

		if(arrayUtil.indexOf(excl_dist, "sd_surinam") != -1){
			val_sd_surinam = false;
		}

		if(dijit.byId("cb-distrib-surinam")){
			dijit.byId("cb-distrib-surinam").set("checked", val_sd_surinam);
		}
		config["search"]["distrib"]["surinam"] = val_sd_surinam;

		if(arrayUtil.indexOf(excl_dist, "sd_indonesia") != -1){
			val_sd_indonesia = false;
		}

		if(dijit.byId("cb-distrib-indonesia")){
			dijit.byId("cb-distrib-indonesia").set("checked", val_sd_indonesia);
		}
		config["search"]["distrib"]["indonesia"] = val_sd_indonesia;

		// article types
		var excl_art_types = item.exclude_article_types;
		console.log("Exclude article types: "+excl_art_types);

		var val_st_article = true;
		var val_st_advert = true;
		var val_st_illust = true;
		var val_st_family = true;

		if(arrayUtil.indexOf(excl_art_types, "st_article") != -1){
			val_st_article = false;
		}

		if(dijit.byId("cb-type-article")){
			dijit.byId("cb-type-article").set("checked", val_st_article);
		}
		config["search"]["type"]["article"] = val_st_article;

		if(arrayUtil.indexOf(excl_art_types, "st_advert") != -1){
			val_st_advert = false;
		}

		if(dijit.byId("cb-type-advert")){
			dijit.byId("cb-type-advert").set("checked", val_st_advert);
		}
		config["search"]["type"]["advert"] = val_st_advert;

		if(arrayUtil.indexOf(excl_art_types, "st_illust") != -1){
			val_st_illust = false;
		}

		if(dijit.byId("cb-type-illust")){
			dijit.byId("cb-type-illust").set("checked", val_st_illust);
		}
		config["search"]["type"]["illust"] = val_st_illust;

		if(arrayUtil.indexOf(excl_art_types, "st_family") != -1){
			val_st_family = false;
		}

		if(dijit.byId("cb-type-family")){
			dijit.byId("cb-type-family").set("checked", val_st_family);
		}
		config["search"]["type"]["family"] = val_st_family;
	});

	// Set pillars as selected
	getToolbarConfig();     // ensure checkboxes exist
	var selected_pillars = item.selected_pillars;
	$('.pillar input').each(function(i) {
		var checked = selected_pillars.indexOf(parseInt($(this).val())) != -1;
		dijit.byId($(this).attr('id')).set("checked", checked);
	});

	console.log(getSearchParameters());
}