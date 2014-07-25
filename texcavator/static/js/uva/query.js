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
function okCombine( comb_operator, query1Name, query2Name, querySaveName )
function okEdit( querySaveName, querySaveQuery )
function okCreate( querySaveName )
function okDownload( query_title )
*/

dojo.require( "dijit.form.Button" );
dojo.require( "dijit.form.CheckBox" );
dojo.require( "dijit.form.ComboBox" );
dojo.require( "dijit.form.Textarea" );
dojo.require( "dijit.layout.TabContainer" );

dojo.require( "dojox.widget.Dialog" );


var lexiconID      = null;	// file global
var lexiconTitle   = null;	// file global
var lexiconQuey    = null;	// file global
var collectionUsed = null;	// file global

/*
var cloud_data = [
	{"count": 42, "term": "jaar"}, 
	{"count": 34, "term": "alle"}, 
	{"count": 30, "term": "onder"}, 
	{"count": 29, "term": "jeugd"}, 
	{"count": 25, "term": "daarvan"}, 
	{"count": 24, "term": "wordt"}
];
*/

var grid_3layout = [
	{ field: "id",    width: "25%" },
	{ field: "count", width: "25%" },
	{ field: "term",  width: "50%" },
];



function storeLexiconID( lexicon_id )
{
//	console.log( "storeLexiconID(): " + lexicon_id );
	lexiconID = lexicon_id;
}

function retrieveLexiconID()
{
//	console.log( "retrieveLexiconID(): " + lexiconID );
	return lexiconID;
}


function storeLexiconTitle( lexicon_title )
{
//	console.log( "storeLexiconTitle(): " + lexicon_title );
	lexiconTitle = lexicon_title;
}

function retrieveLexiconTitle()
{
//	console.log( "retrieveLexiconTitle(): " + lexiconTitle );
	return lexiconTitle;
}


function storeLexiconQuery( lexicon_query )
{
//	console.log( "storeLexiconQuery(): " + lexicon_query );
	lexiconQuery = lexicon_query;
}

function retrieveLexiconQuery()
{
//	console.log( "retrieveLexiconQuery(): " + lexiconQuery );
	return lexiconQuery;
}


function storeCollectionUsed( collection_used )
{
//	console.log( "storeCollectionUsed(): " + collection_used );
	collectionUsed = collection_used;
}

function retrieveCollectionUsed()
{
//	console.log( "retriveCollectionUsed(): " + collection_used );
	return collectionUsed;
}


function queryFromName( queryName )
{
	var query_content = "";

	dojo.forEach( glob_lexiconData, function( item )		// glob_lexiconData: index.html
	{
		var query_title = item[ "fields" ][ "title" ];
		if( query_title === queryName  && ! query_title.endsWith( "_daterange" ) )
		{ query_content = item[ "fields" ][ "query" ]; }
	});

	return query_content;
}


function getQueryList()
{
	var queryList = [];
	dojo.forEach( glob_lexiconData, function( item )	// glob_lexiconData: index.html
	{
		var query_title = item[ "fields" ][ "title" ];
		var id = item[ "pk" ];
		if( ! query_title.endsWith( "_daterange" ) )	// do not show queries with *_daterange names
		{ queryList.push( { name: query_title, id: id } ); }
	});

	return queryList;
}


function updateQueryDlg()
{
	console.log( "updateQueryDlg()" );

	// update the query list
	var querylistStore = new dojo.store.Memory({ data: getQueryList() });

	// update the Combine query lists
	dijit.byId( "cb-que1" ).set( "store", querylistStore );
	dijit.byId( "cb-que2" ).set( "store", querylistStore );

	// update the Edit query list
	dijit.byId( "cb-query-edit" ).set( "store", querylistStore );

	// update the Data query list
	dijit.byId( "cb-query-data" ).set( "store", querylistStore );
}


//dojo.addOnLoad( createQueryDlg );
function createQueryDlg()
{
	console.log( "createQueryDlg()" );

	var dlgQuery = new dijit.Dialog({
		id: "dlg-query",
		title: "Query"
	});

	dojo.style( dlgQuery.closeButtonNode, "visibility", "hidden" );	// hide the ordinary close button

	var container = dlgQuery.containerNode;

	var tcdiv = dojo.create( "div", { id: "tc-div-query" }, container );
	var tabCont = new dijit.layout.TabContainer({
		id: "tc-query",
		style: "background-color: white; width: 410px; height: 320px; line-height: 18pt"
	}, "tc-div-query" );


	// Combine 2 queries
//	console.log( "cpQCombine" );
	var cpQCombine = new dijit.layout.ContentPane({
		id: "cp-combine",
		title: "Combine",
		content: "<b>Combine 2 saved queries</b>"
	});
	tabCont.addChild( cpQCombine );

	var query1Name = "";
	var query2Name = "";
	var querySaveName = "";


	dojo.create( "label", {
		innerHTML: "<br/>Boolean CQL operator:<br/>"
	}, cpQCombine.domNode );


	var comb_operator = "AND";

	var rbAND = new dijit.form.RadioButton({
		id: "rb-AND",
		checked: true,
		onChange: function( btn ) { if( btn ) { comb_operator = "AND"; } }
	});
	rbAND.placeAt( cpQCombine.domNode );

	var labelAND = dojo.create( "label", {
		id: "label-AND",
		for: "rb-AND",
		innerHTML: "&nbsp;AND&nbsp;&nbsp;"
	}, cpQCombine.domNode );


	var rbOR = new dijit.form.RadioButton({
		id: "rb-OR",
		checked: false,
		onChange: function( btn ) { if( btn ) { comb_operator = "OR" }; }
	});
	rbOR.placeAt( cpQCombine.domNode );

	var labelOR = dojo.create( "label", {
		id: "label-OR",
		for: "rb-OR",
		innerHTML: "&nbsp;OR&nbsp;&nbsp;"
	}, cpQCombine.domNode );


	var rbNOT = new dijit.form.RadioButton({
		id: "rb-NOT",
		checked: false,
		onChange: function( btn ) { if( btn ) { comb_operator = "NOT" }; }
	});
	rbNOT.placeAt( cpQCombine.domNode );

	var labelNOT = dojo.create( "label", {
		id: "label-NOT",
		for: "rb-NOT",
		innerHTML: "&nbsp;NOT&nbsp;&nbsp;"
	}, cpQCombine.domNode );

	/*
	// PROX probably not implemented
	var rbPROX = new dijit.form.RadioButton({
		id: "rb-PROX",
		disabled: true,				// needs additional syntax
		checked: false,
		onChange: function( btn ) { if( btn ) { comb_operator = "PROX" }; }
	}, dojo.byId( "div-op-prox" ) );

	var labelPROX = dojo.create( "label", {
		id: "label-PROX",
		style: "color: DarkGrey",	// 'disabled'
		for: "rb-PROX",
		innerHTML: "&nbsp;PROX<br/><br/>"
	});
	rbPROX.placeAt( cpQCombine.domNode );

	*/

	// fill the query list
	var stateStore = new dojo.store.Memory({ data: getQueryList() });

	dojo.create( "div", { id: "div-query1" }, cpQCombine.domNode );
	var cbQue1 = new dijit.form.ComboBox(
	{
		id: "cb-que1",
		name: "cbQue1",
		style: "width: 100%",
		displayedValue: "Select query 1",
		store: stateStore,
		searchAttr: "name",
		onChange: function() { combine_check(); }
	});
	cbQue1.placeAt( cpQCombine.domNode );

	dojo.create( "div", { id: "div-query2" }, cpQCombine.domNode );
	var cbQue2 = new dijit.form.ComboBox(
	{
		id: "cb-que2",
		name: "cbQue2",
		style: "width: 100%",
		displayedValue: "Select query 2",
		store: stateStore,
		searchAttr: "name",
		onChange: function() { combine_check(); }
	});
	cbQue2.placeAt( cpQCombine.domNode );

	var combine_check = function()
	{
		query1Name = cbQue1.get( "value" );
		query2Name = cbQue2.get( "value" );
	//	console.log( "query 1: " + query1Name );
	//	console.log( "query 2: " + query2Name );
		if( query1Name !== "Select query 1" && query2Name !== "Select query 2" 
			&&  query1Name !== query2Name )
		{
			querySaveName = query1Name + "_" + comb_operator + "_" + query2Name;
			tbQueName.set( "value", querySaveName );
			bOK.set( "disabled", false );
		}
		else
		{
			tbQueName.set( "value", "" );
			bOK.set( "disabled", true );
		}
	}

	dojo.create( "label", {
		innerHTML: "<br/>Save result as:"
	}, cpQCombine.domNode );

	dojo.create( "div", { id: "div-query2" }, cpQCombine.domNode );
	var divQueName = dojo.create( "div", { id: "div-quename" }, cpQCombine.domNode );
	var tbQueName = new dijit.form.TextBox({
		id: "tb-quename",
		style: "width: 100%"
	});
	tbQueName.placeAt( divQueName );


	// Edit a query
//	console.log( "cpQEdit" );
	var cpQEdit = new dijit.layout.ContentPane({
		id: "cp-edit",
		title: "Edit",
		content: "<b>Edit a query</b>"
	});

	// fill the query list
	var queryListStoreEdit = new dojo.store.Memory({ data: getQueryList() });

	var queryNameEdit = "";
	dojo.create( "div", { id: "div-query-edit" }, cpQCombine.domNode );
	var cbQueryEdit = new dijit.form.ComboBox(
	{
		id: "cb-query-edit",
		name: "cbQueryEdit",
		style: "width: 100%",
		displayedValue: "Select query to edit",
		store: queryListStoreEdit,
		searchAttr: "name",
		onChange: function() {
			bOK.set( "disabled", false );
			bValidate.set( "disabled", false );
			queryNameEdit = cbQueryEdit.get( "value" );
			console.log( "Query name: " + queryNameEdit );

			dojo.forEach( glob_lexiconData, function( item )		// glob_lexiconData: index.html
			{
				var query_title = item[ "fields" ][ "title" ];
				if( query_title === queryNameEdit  && ! query_title.endsWith( "_daterange" ) )	// do not show queries with *_daterange names
				{ taQuery.set( "value", item[ "fields" ][ "query" ] ); }
			});
		}
	});
	cbQueryEdit.placeAt( cpQEdit.domNode );


	var taQuery = new dijit.form.Textarea({
		name: "myarea",
		value: "",
		style: "width: 100%; height: 100%;"
	});
	taQuery.placeAt( cpQEdit.domNode );


	// Create a new query
//	console.log( "cpQCreate" );
	/*
	var cpQCreate = new dijit.layout.ContentPane({
		id: "cp-create",
		title: "Create",
		content: "<b>Create a query</b>"
	});
	*/

	/*
	dojo.create( "div", { id: "div-grid" }, cpQCreate.domNode );

	// set up data store
	var data = {
		identifier: 'id',
		items: []
	};

	var data_list = [
		{ col1: "normal",    col2: false, col3: 'But are not followed by two hexadecimal', col4: 29.91},
		{ col1: "important", col2: false, col3: 'Because a % sign always indicates',       col4: 9.33},
		{ col1: "important", col2: false, col3: 'Signs can be selectively',                col4: 19.34}
	];

//	var rows = 60;
	var rows = 3;
	for( var i = 0, l = data_list.length; i <rows; i++ ) {
		data.items.push( dojo.mixin( { id: i+1 }, data_list[ i%l ] ) );
	}
	var store = new dojo.data.ItemFileWriteStore( { data: data } );

	// grid layout
	var layout = [[
		{'name': 'Column 1', 'field': 'id'},
		{'name': 'Column 2', 'field': 'col2'},
		{'name': 'Column 3', 'field': 'col3', 'width': '230px'},
		{'name': 'Column 4', 'field': 'col4', 'width': '230px'}
	]];

	// create a new grid
//	var grid = new dojox.grid.EnhancedGrid({
	var grid = new dojox.grid.DataGrid({
		id: 'grid',
	//	style: "width: 45em; height: 20em;",
		style: "width: 100%; height: 100%;",
		store: store,
		structure: layout,
		rowSelector: '20px'
	}, dojo.byId( "div-grid" ) );
//	}, document.createElement( 'div' ) );

	// append the new grid to the div
//	dojo.byId( "div-grid" ).appendChild( grid.domNode );

	// Grid need a explicit width/height by default
//	#grid { width: 45em; height: 20em; }
	*/

	/*
	var layout = [
		{name : "MyFirstColumnHeader", field : 'someColumnNameInMyData', width : "180px;"}, 
		{name : "MySecondColumnHeader", field : 'someOtherColumnName', width : "180px;"}
	];

	var emptyData = { identifier : 'uniqueIdOfEachItem', label : 'displayName', items : [] };
	var store = new dojo.data.ItemFileWriteStore( { data : emptyData } );
	var grid = new dojox.grid.DataGrid({
		id : 'grid',
		query : { uniqueIdOfEachItem: '*' },
		store : store,
		structure : layout
	},  dojo.byId( "div-grid" ) );

	// grid.startup();
	*/


	// Download query data
//	console.log( "cpQData" );
	var cpQData = new dijit.layout.ContentPane({
		id: "cp-data",
		title: "Data",
		content: "<b>Download the query Data (OCR and Metadata)</b>"
	});


	dojo.create( "div", { id: "div-qdata-format" }, cpQData.domNode );

	var textQDataFormat = dojo.create( "label", {
		id: "text-qdata-format",
		for: "div-qdata-format",
		innerHTML: "Export format: <br/>"
	}, cpQData.domNode );


	if( config[ "querydataexport" ][ "format" ] === "json" )
	{ var jsonformat_val = true; }
	else
	{ var jsonformat_val = false; }

	var rbQDataJSON = new dijit.form.RadioButton({
		id: "rb-qdata-json",
		checked: jsonformat_val,
		onChange: function( btn )
		{
			if( btn == true )
			{ config[ "querydataexport" ][ "format" ] = "json"; }
		},
	});
	rbQDataJSON.placeAt( cpQData.domNode );

	var labelQDataJSON = dojo.create( "label", {
		id: "label-qdata-json",
		for: "rb-qdata-json",
		innerHTML: "&nbsp;JSON (native format)<br/>"
	}, cpQData.domNode );


	if( config[ "querydataexport" ][ "format" ] === "xml" )
	{ var xmlformat_val = true; }
	else
	{ var xmlformat_val = false; }

	var rbQDataXML = new dijit.form.RadioButton({
		id: "rb-qdata-xml",
		checked: xmlformat_val,
		onChange: function( btn )
		{
			if( btn == true )
			{ config[ "querydataexport" ][ "format" ] = "xml"; }
		},
	});
	rbQDataXML.placeAt( cpQData.domNode );

	var labelQueryDataFormatXML = dojo.create( "label", {
		id: "label-qdata-xml",
		for: "rb-qdata-xml",
		innerHTML: "&nbsp;XML (slow! conversion)<br/>"
	}, cpQData.domNode );


	if( config[ "querydataexport" ][ "format" ] === "csv" )
	{ var csvformat_val = true; }
	else
	{ var csvformat_val = false; }

	var rbQDataCSV = new dijit.form.RadioButton({
		id: "rb-qdata-csv",
		checked: csvformat_val,
		onChange: function( btn )
		{
			if( btn == true )
			{ config[ "querydataexport" ][ "format" ] = "csv"; }
		},
	});
	rbQDataCSV.placeAt( cpQData.domNode );

	var labelQueryDataFormatCSV = dojo.create( "label", {
		id: "label-qdata-csv",
		for: "rb-qdata-csv",
		innerHTML: "&nbsp;CSV (TAB delimited)<br/>"
	}, cpQData.domNode );


	// fill the query list
	var queryListStoreData = new dojo.store.Memory({ data: getQueryList() });

	var queryNameData = "";
	dojo.create( "div", { id: "div-query-data" }, cpQData.domNode );

	var cbQueryData = new dijit.form.ComboBox(
	{
		id: "cb-query-data",
		name: "cbQueryData",
		style: "width: 100%",
		displayedValue: "Select query",
		store: queryListStoreData,
		searchAttr: "name",
		onChange: function() {
			bOK.set( "disabled", false );
			bValidate.set( "disabled", false );
			queryNameData = cbQueryData.get( "value" );
			console.log( "Query name: " + queryNameData );

			dojo.forEach( glob_lexiconData, function( item )		// glob_lexiconData: index.html
			{
				var query_title = item[ "fields" ][ "title" ];
				if( query_title === queryNameEdit  && ! query_title.endsWith( "_daterange" ) )	// do not show queries with *_daterange names
				{ downloadQueryData( query_title ); }
			});
		}
	});
	cbQueryData.placeAt( cpQData.domNode );


	var actionBar = dojo.create( "div", {
		className: "dijitDialogPaneActionBar",
		style: "height: 30px"
	}, container );

	var bCancel = new dijit.form.Button({
		label: "<img src='/static/image/icon/Tango/16/actions/dialog-cancel.png'/> Cancel",
		showLabel: true,
		role: "presentation",
		onClick: function() { dijit.byId( "dlg-query" ).destroyRecursive(); }
	});
	actionBar.appendChild( bCancel.domNode );

	var bValidate = new dijit.form.Button(
	{
		label: "<img src='/static/image/icon/Tango/16/categories/system.png'/> Validate",
	//	label: "<img src='/static/image/icon/Tango/16/mimetypes/executable.png'/> Validate",
		disabled: true,
		showLabel: true,
		role: "presentation",
		onClick: function() { dijit.byId( "dlg-query" ).destroyRecursive(); }
	});
//	actionBar.appendChild( bValidate.domNode );

	var bOK = new dijit.form.Button(
	{
	//	label: "<img src='/static/image/icon/Tango/16/actions/dialog-ok.png'/> OK",
		label: " OK",
		iconClass: "dijitIconSave",
		disabled: true,
		showLabel: true,
		role: "presentation",
		onClick: function()
		{
			var selectedTab = dijit.byId( "tc-query" ).get( "selectedChildWidget" );
		//	console.log( selectedTab.title );

			if( selectedTab.id === "cp-combine" )
			{ okCombine( comb_operator, query1Name, query2Name, querySaveName ); }
			else if( selectedTab.id === "cp-edit" )
			{ okEdit( queryNameEdit, taQuery.get( "value" ) ); }
			else if( selectedTab.id === "cp-create" )
			{ okCreate( queryNameCreate ); }
			else if( selectedTab.id === "cp-data" )
			{ okDownload( queryNameData ); }
		}
	});
	actionBar.appendChild( bOK.domNode );


	// choose the order in which the tabs appear
	tabCont.addChild( cpQCombine );
	tabCont.addChild( cpQEdit );
//	tabCont.addChild( cpQCreate );

	if( glob_username != "guest" && QUERY_DATA_DOWNLOAD == true ) 
	{ tabCont.addChild( cpQData ); }		// guest has no email
};



function okCombine( comb_operator, query1Name, query2Name, querySaveName )
{
	console.log( "okCombine" );
//	console.log( "Query 1 name: " + query1Name );
//	console.log( "Query 2 name: " + query2Name );

	dijit.byId( "dlg-query" ).destroyRecursive();

	var query1Query = "";
	var query2Query = "";
	dojo.forEach( glob_lexiconData, function( item )		// lexiconData: global {} in index.html
	{
		var query_title = item[ "fields" ][ "title" ];
		if( query_title === query1Name )
		{ query1Query = item[ "fields" ][ "query" ]; }
		if( query_title === query2Name )
		{ query2Query = item[ "fields" ][ "query" ]; }
	});

	querySaveQuery = "(" + query1Query + " " + comb_operator + " " + query2Query + ")";

//	console.log( "Query: " + querySaveQuery );
//	console.log( "Saving as " + querySaveName );

	// lexicon is the django app name; lexiconitem could be renamed to query
	var data = { 
		"model": "lexicon.lexiconitem",
		"fields": {
			"overwrite": false,
			"user": glob_username,
			"title": querySaveName,
			"query": querySaveQuery
		} 
	};

	lexiconStore.put( data ).then( function( result )			// HTTP POST
	{
		var status = result[ "status" ];
		if( status === "SUCCESS" )
		{
			console.log( "Query was saved" );
			dijit.byId( "leftAccordion" ).selectChild( "lexicon" );
			createQueryList();		// fill the Saved queries panel (in index.html)
		}
		else
		{
			var msg = "The query could not be saved:<br/>" + result[ "msg" ];
			var dialog = new dijit.Dialog({
				title: "Save query",
				style: "width: 300px",
				content: msg
			});
			dialog.show();
		}
	});
}


function okEdit( querySaveName, querySaveQuery )
{
	console.log( "okEdit" );
	console.log( "Query name: " + querySaveName );
	console.log( "Query: " + querySaveQuery );

	dijit.byId( "dlg-query" ).destroyRecursive();

	dojo.forEach( glob_lexiconData, function( item )		// lexiconData: global {} in index.html
	{
		var query_title = item[ "fields" ][ "title" ];
		if( query_title === querySaveName )
		{
			item[ "fields" ][ "query" ] = querySaveQuery;
		}
	});

	if( querySaveQuery === "" )
	{ console.log( "empty query?" ); }
	else
	{
		// lexicon is the django app name; lexiconitem could be renamed to query
		var data = {
			"model": "lexicon.lexiconitem", 
			"fields": {
				"overwrite": true,
				"removetags": true,		// remove existing Lexicon* tags; docs must be reloaded
				"user":  glob_username,
				"title": querySaveName,
				"query": querySaveQuery
			}
		};

		lexiconStore.put( data ).then( function( result )			// HTTP POST
		{
			var status = result[ "status" ];
			if( status === "SUCCESS" )
			{
				console.log( "Query was saved" );
				dijit.byId( "leftAccordion" ).selectChild( "lexicon" );
				refreshQueriesDocCounts()();		// update the lexicon container (in index.html)
			}
			else
			{
				var title = "Save query";
				var msg = "The query could not be saved:<br/>" + result[ "msg" ];
				var buttons = { "OK": true, "Cancel": false };
				genDialog( title, msg, buttons );
			}
		});
	}
}


function okCreate( querySaveName )
{
	console.log( "okCreate" );
	console.log( "Query name: " + querySaveName );

	dijit.byId( "dlg-query" ).destroyRecursive();
}



function okDownload( query_title )
{
	console.log( "okDownload() : " + query_title );

	dijit.byId( "dlg-query" ).destroyRecursive();

	// 'raw' query, without extras
	var query_content = queryFromName( query_title );
	console.log( "query_content: " + query_content );

	// add date range to the query
	var min_date_str = getDate_Begin_Str();
	var max_date_str = getDate_End_Str();
	console.log( "date range: [" + min_date_str + ',' +  max_date_str + ']');

	var params = getSearchParameters();			// from config
	params[ "username" ]    = glob_username;
	params[ "password" ]    = glob_password;
	params[ "collection" ]  = ES_INDEX;
	params[ "query_title" ] = query_title;
	params[ "query" ]       = query_content;

	config = getConfig();
	params[ "format" ] = config[ "querydataexport" ][ "format" ]	// "json" or "xml"

	dojo.xhrGet({
		url: "lexicon/download/prepare/",
		content: params,
		handleAs: "json",
		load: function( result ) {
			var status = result[ "status" ];
			if( status === "SUCCESS" )
			{ var title = "Preparing download"; }
			else
			{ var title = "Preparing download failed"; }

			var message = result[ "msg" ];
			var buttons = { "OK": true, "Cancel": false };
			answer = genDialog( title, message, buttons );
		},
		error: function( err ) { console.error( err ); return err; }
	});
}


function saveQuery( title, query )
{
	console.log( "saveQuery() title: "  + title + ", query: " + query )
	var data = { 
		"model": "lexicon.lexiconitem", 
		"fields": { 
			"overwrite": false,
			"user":  glob_username, 
			"title": title, 
			"query": query
		} 
	};

	lexiconStore.put( data ).then( function( result )		// HTTP POST
	{
		var status = result[ "status" ];
		if( status !== "SUCCESS" )
		{
			var msg = "The query could not be saved:<br/>" + result[ "msg" ];
			var dialog = new dijit.Dialog({
				title: "Save query",
				style: "width: 300px",
				content: msg
			});
			dialog.show();
		}

		createQueryList();
		return true;
	});
}

// [eof]
