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

dojo.require("dojox.widget.Dialog");


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
			checked: config.querydataexport.format === key,
			onChange: function(btn) {
				if (btn) {
					config.querydataexport.format = key;
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
		checked: config.querydataexport.simplified,
		onChange: function(btn) {
			config.querydataexport.simplified = btn;
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