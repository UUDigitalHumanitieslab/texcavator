// FL-12-Nov-2012 Created
// FL-13-Dec-2013 Changed

/*
function storeLexiconID( lexicon_id )
function retrieveLexiconID()
function storeLexiconTitle( lexicon_title )
function retrieveLexiconTitle()
function storeLexiconQuery( lexicon_query )
function retrieveLexiconQuery()
function storeCollectionUsed( collection_used )
function retrieveCollectionUsed()
function getQueryList()
function updateQueryDlg()
function createQueryDlg()
function okEdit( querySaveName, querySaveQuery )
function okCreate( querySaveName )
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
var lexiconQuey = null; // file global
var collectionUsed = null; // file global

var grid_3layout = [{
	field: "id",
	width: "25%"
}, {
	field: "count",
	width: "25%"
}, {
	field: "term",
	width: "50%"
}, ];


function storeLexiconID(lexicon_id) {
	//	console.log( "storeLexiconID(): " + lexicon_id );
	lexiconID = lexicon_id;
}

function retrieveLexiconID() {
	//	console.log( "retrieveLexiconID(): " + lexiconID );
	return lexiconID;
}


function storeLexiconTitle(lexicon_title) {
	//	console.log( "storeLexiconTitle(): " + lexicon_title );
	lexiconTitle = lexicon_title;
}

function retrieveLexiconTitle() {
	//	console.log( "retrieveLexiconTitle(): " + lexiconTitle );
	return lexiconTitle;
}


function storeLexiconQuery(lexicon_query) {
	//	console.log( "storeLexiconQuery(): " + lexicon_query );
	lexiconQuery = lexicon_query;
}

function retrieveLexiconQuery() {
	//	console.log( "retrieveLexiconQuery(): " + lexiconQuery );
	return lexiconQuery;
}


function storeCollectionUsed(collection_used) {
	//	console.log( "storeCollectionUsed(): " + collection_used );
	collectionUsed = collection_used;
}

function retrieveCollectionUsed() {
	//	console.log( "retriveCollectionUsed(): " + collection_used );
	return collectionUsed;
}


function queryFromName(queryName) {
	var query_content = "";

	dojo.forEach(glob_lexiconData, function(item) {
		var query_title = item.title;
		// TODO: magic string "_daterange"
		if (query_title === queryName && !query_title.endsWith("_daterange")) {
			query_content = item.query;
		}
	});

	return query_content;
}


function getQueryList() {
	var queryList = [];
	dojo.forEach(glob_lexiconData, function(item) {
		var query_title = item.title;
		var id = item.pk;
		// do not show queries with *_daterange names TODO: magic string
		if (!query_title.endsWith("_daterange")) {
			queryList.push({
				name: query_title,
				id: id
			});
		}
	});

	return queryList;
}


function updateQueryDlg() {
	console.log("updateQueryDlg()");

	// update the query list
	var querylistStore = new dojo.store.Memory({
		data: getQueryList()
	});

	// update the Edit query list
	dijit.byId("cb-query-edit").set("store", querylistStore);

	// update the Data query list
	dijit.byId("cb-query-data").set("store", querylistStore);
}


//dojo.addOnLoad( createQueryDlg );
function createQueryDlg() {
	console.log("createQueryDlg()");

	var dlgQuery = new dijit.Dialog({
		id: "dlg-query",
		title: "Query"
	});

	dojo.style(dlgQuery.closeButtonNode, "visibility", "hidden"); // hide the ordinary close button

	var container = dlgQuery.containerNode;

	var tcdiv = dojo.create("div", {
		id: "tc-div-query"
	}, container);
	var tabCont = new dijit.layout.TabContainer({
		id: "tc-query",
		style: "background-color: white; width: 410px; height: 320px; line-height: 18pt"
	}, "tc-div-query");


	// Edit a query
	//	console.log( "cpQEdit" );
	var cpQEdit = new dijit.layout.ContentPane({
		id: "cp-edit",
		title: "Edit",
		content: "<b>Edit a query</b>"
	});

	// fill the query list
	var queryListStoreEdit = new dojo.store.Memory({
		data: getQueryList()
	});

	var queryNameEdit = "";
	dojo.create("div", {
		id: "div-query-edit"
	}, cpQEdit.domNode);
	var cbQueryEdit = new dijit.form.ComboBox({
		id: "cb-query-edit",
		name: "cbQueryEdit",
		style: "width: 100%",
		displayedValue: "Select query to edit",
		store: queryListStoreEdit,
		searchAttr: "name",
		onChange: function() {
			bOK.set("disabled", false);
			bValidate.set("disabled", false);
			queryNameEdit = cbQueryEdit.get("value");
			console.log("Query name: " + queryNameEdit);

			dojo.forEach(glob_lexiconData, function(item) {
				var query_title = item.title;
				if (query_title === queryNameEdit && !query_title.endsWith("_daterange")) // do not show queries with *_daterange names
				{
					taQuery.set("value", item.query);
				}
			});
		}
	});
	cbQueryEdit.placeAt(cpQEdit.domNode);


	var taQuery = new dijit.form.Textarea({
		name: "myarea",
		value: "",
		style: "width: 100%; height: 100%;"
	});
	taQuery.placeAt(cpQEdit.domNode);


	// Download query data
	//	console.log( "cpQData" );
	var cpQData = new dijit.layout.ContentPane({
		id: "cp-data",
		title: "Data",
		content: "<b>Download the query data (OCR and metadata)</b>"
	});


	dojo.create("div", {
		id: "div-qdata-format"
	}, cpQData.domNode);

	var textQDataFormat = dojo.create("label", {
		id: "text-qdata-format",
		for: "div-qdata-format",
		innerHTML: "Export format: <br/>"
	}, cpQData.domNode);

	var jsonformat_val = config.querydataexport.format === "json";

	var rbQDataJSON = new dijit.form.RadioButton({
		id: "rb-qdata-json",
		checked: jsonformat_val,
		onChange: function(btn) {
			if (btn) {
				config.querydataexport.format = "json";
			}
		},
	});
	rbQDataJSON.placeAt(cpQData.domNode);

	var labelQDataJSON = dojo.create("label", {
		id: "label-qdata-json",
		for: "rb-qdata-json",
		innerHTML: "&nbsp;JSON (native format)<br/>"
	}, cpQData.domNode);


	var xmlformat_val = config.querydataexport.format === "xml";

	var rbQDataXML = new dijit.form.RadioButton({
		id: "rb-qdata-xml",
		checked: xmlformat_val,
		onChange: function(btn) {
			if (btn) {
				config.querydataexport.format = "xml";
			}
		},
	});
	rbQDataXML.placeAt(cpQData.domNode);

	var labelQueryDataFormatXML = dojo.create("label", {
		id: "label-qdata-xml",
		for: "rb-qdata-xml",
		innerHTML: "&nbsp;XML (slow! conversion)<br/>"
	}, cpQData.domNode);

	var csvformat_val = config.querydataexport.format === "csv";

	var rbQDataCSV = new dijit.form.RadioButton({
		id: "rb-qdata-csv",
		checked: csvformat_val,
		onChange: function(btn) {
			if (btn) {
				config.querydataexport.format = "csv";
			}
		},
	});
	rbQDataCSV.placeAt(cpQData.domNode);

	var labelQueryDataFormatCSV = dojo.create("label", {
		id: "label-qdata-csv",
		for: "rb-qdata-csv",
		innerHTML: "&nbsp;CSV (TAB delimited)<br/>"
	}, cpQData.domNode);

	// Simplified export
	var divSimplifiedExport = dojo.create("div", {
		id: "div-simplified-export"
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


	// fill the query list
	var queryListStoreData = new dojo.store.Memory({
		data: getQueryList()
	});

	var queryNameData = "";
	var queryID = -1;
	dojo.create("div", {
		id: "div-query-data"
	}, cpQData.domNode);

	var cbQueryData = new dijit.form.ComboBox({
		id: "cb-query-data",
		name: "cbQueryData",
		style: "width: 100%",
		displayedValue: "Select query",
		store: queryListStoreData,
		searchAttr: "name",
		onChange: function() {
			bOK.set("disabled", false);
			bValidate.set("disabled", false);
			queryNameData = cbQueryData.get("value");
			console.log("Query name: " + queryNameData);

			dojo.forEach(glob_lexiconData, function(item) {
				var query_title = item.title;
				if (query_title === queryNameEdit && !query_title.endsWith("_daterange")) // do not show queries with *_daterange names
				{
					downloadQueryData(query_title);
				}
			});
		}
	});
	cbQueryData.placeAt(cpQData.domNode);


	var actionBar = dojo.create("div", {
		className: "dijitDialogPaneActionBar",
		style: "height: 30px"
	}, container);

	var bCancel = new dijit.form.Button({
		label: "<img src='/static/image/icon/Tango/16/actions/dialog-cancel.png'/> Cancel",
		showLabel: true,
		role: "presentation",
		onClick: function() {
			dijit.byId("dlg-query").destroyRecursive();
		}
	});
	actionBar.appendChild(bCancel.domNode);

	var bValidate = new dijit.form.Button({
		label: "<img src='/static/image/icon/Tango/16/categories/system.png'/> Validate",
		disabled: true,
		showLabel: true,
		role: "presentation",
		onClick: function() {
			dijit.byId("dlg-query").destroyRecursive();
		}
	});
	//	actionBar.appendChild( bValidate.domNode );

	var bOK = new dijit.form.Button({
		//	label: "<img src='/static/image/icon/Tango/16/actions/dialog-ok.png'/> OK",
		label: " OK",
		iconClass: "dijitIconSave",
		disabled: true,
		showLabel: true,
		role: "presentation",
		onClick: function() {
			var selectedTab = dijit.byId("tc-query").get("selectedChildWidget");
			//	console.log( selectedTab.title );

			if (selectedTab.id === "cp-edit") {
				okEdit(queryNameEdit, taQuery.get("value"));
			} else if (selectedTab.id === "cp-create") {
				okCreate(queryNameCreate);
			} else if (selectedTab.id === "cp-data") {
				okDownload(queryNameData);
			}
		}
	});
	actionBar.appendChild(bOK.domNode);


	// choose the order in which the tabs appear
	tabCont.addChild(cpQEdit);
	//	tabCont.addChild( cpQCreate );

	if (QUERY_DATA_DOWNLOAD) {
		tabCont.addChild(cpQData);
	} // guest has no email
}


function okEdit(querySaveName, querySaveQuery) {
	console.log("okEdit");
	console.log("Query name: " + querySaveName);
	console.log("Query: " + querySaveQuery);

	dijit.byId("dlg-query").destroyRecursive();

	dojo.forEach(glob_lexiconData, function(item) // lexiconData: global {} in index.html
		{
			var query_title = item.title;
			if (query_title === querySaveName) {
				item.query = querySaveQuery;
			}
		});

	if (querySaveQuery === "") {
		console.log("empty query?");
	} else {
		// lexicon is the django app name; lexiconitem could be renamed to query
		var data = {
			"model": "lexicon.lexiconitem",
			"fields": {
				"overwrite": true,
				"removetags": true, // remove existing Lexicon* tags; docs must be reloaded
				"user": glob_username,
				"title": querySaveName,
				"query": querySaveQuery
			}
		};

		lexiconStore.put(data).then(function(result) // HTTP POST
			{
				var status = result.status;
				if (status === "SUCCESS") {
					console.log("Query was saved");
					dijit.byId("leftAccordion").selectChild("lexicon");
					// update the lexicon container (in index.html)
					createQueryList();
				} else {
					var title = "Save query";
					var msg = "The query could not be saved:<br/>" + result.msg;
					var buttons = {
						"OK": true,
						"Cancel": false
					};
					genDialog(title, msg, buttons);
				}
			});
	}
}


// TODO: remove, deprecated functionality
function okCreate(querySaveName) {
	console.log("okCreate");
	console.log("Query name: " + querySaveName);

	dijit.byId("dlg-query").destroyRecursive();
}


// Starts the download of a query
function okDownload(query_title) {
	console.log("okDownload() : " + query_title);

	dijit.byId("dlg-query").destroyRecursive();

	var config = getConfig();
	var params = {
		collection: ES_INDEX,
		query_title: query_title,
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
}


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
		},
		error: function(err) {
			console.error(err);
		}
	});
}