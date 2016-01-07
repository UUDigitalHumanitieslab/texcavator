// FL-11-May-2012 Created
// FL-04-Apr-2013 Changed

/*
var storeCloudData = function( cloudType, cloudData )
var getCloudSrc = function()
var getCloudTermCount = function()
var getCloudGridLayout = function()
var showCloudDlg = function()
var createCloudDlg = function()
var createCloudTableData = function()
var fillCloudTable = function()
function exportCloudData( filename )
*/


dojo.require( "dojo.data.ItemFileWriteStore" );
//dojo.require( "dojo.io.iframe" );			// obsolete in 1.8, use: dojo/request/iframe
dojo.require( "dojo.request.iframe" );		// Dojo-1.8
dojo.require( "dojo.request.xhr" );			// Dojo-1.8

dojo.require( "dijit.form.Form" );

dojo.require( "dojox.grid.EnhancedGrid" );
dojo.require( "dojox.grid.enhanced.plugins.exporter.CSVWriter" );


var cloud_src  = "";
var cloud_data = [];
var cloud_data_elems = 0;

var grid_3layout = [
	{ field: "id",    width: "25%" },
	{ field: "term", width: "50%" },
	{ field: "count",  width: "25%" },
];

var grid_4layout = [
	{ field: "id",    width: "20%" },
	{ field: "term",  width: "40%" },
	{ field: "count", width: "20%" },
	{ field: "tfidf",  width: "20%" }
];


var storeCloudData = function( cloudType, cloudData )
{
	console.log( "storeCloudData() " + cloudType );
	// This can be either the normal cloud data, or the burst cloud data

	cloud_data = cloudData;
	cloud_src  = cloudType;
	cloud_data_elems = getConfig().cloud.NER || getConfig().cloud.idf ? 3 : 2;
};

var getCloudSrc = function()
{
	return cloud_src;
};

var getCloudTermCount = function()
{
	return cloud_data.length;
};


var getCloudGridLayout = function()
{
	var grid_layout;
	// 3 columns without NER/idf (including # column)
	// 4 columns with NER/idf (including # column)
	if( typeof( cloud_data_elems ) === "undefined" )
	{ grid_layout = grid_3layout; }			// 3 columns (+id)
	else
	{
		if( cloud_data_elems === 0 || cloud_data_elems === 2 )
		{ grid_layout = grid_3layout; }		// 3 columns (+id)
		else if( cloud_data_elems === 3 ) 
		{ grid_layout = grid_4layout; }		// 4 columns (+id)
		else
		{ grid_layout = grid_3layout; }		// 3 columns (+id)
	}
	return grid_layout;
};


var showCloudDlg = function()
{
//	fillCloudTable();
	dlg_cloud = dijit.byId( "dlg-cloud" );
	if( dlg_cloud == null ) { createCloudDlg(); }	// create an new one
	dijit.byId( "dlg-cloud" ).show();
};

var createCloudDlg = function()
{
	console.log( "createCloudDlg()");

	var grid_layout = getCloudGridLayout();

	var dlgCloud = new dijit.Dialog({
		id: "dlg-cloud",
		title: "Word Cloud Data"
	});

	dojo.style( dlgCloud.closeButtonNode, "visibility", "hidden" );	// hide the ordinary close button

	var container = dlgCloud.containerNode;

	var tcdiv = dojo.create( "div", { id: "tc-div-cloud" }, container );

	var tabCont = new dijit.layout.TabContainer({
		style: "background-color: white; width: 410px; height: 320px; line-height: 18pt"
	}, "tc-div-cloud" );

	/*
	var form = new dijit.form.Form({
		id: "frm-cloud-table",
		method: "post"
	});
	tabCont.addChild( form );
	*/

	var term_src = getCloudSrc();
	if( cloud_src === "article" )
	{ var content_html = "<b>Single Article "; }
	else if( cloud_src === "date range" )
	{ var content_html = "<b>Date range "; }
	else if( cloud_src === "burst" )
	{ var content_html = "<b>Burst "; }
	else
	{ var content_html = "<b>"; }	// full range, or date_range

	var term_count = getCloudTermCount();
	content_html += "Word Cloud Data: " + term_count + " terms</b><br/>";
	console.log( content_html );

	// word cloud data tab
	var cp_grid_cloud = new dijit.layout.ContentPane({
		id:     "cp-grid-cloud",
		title:  "Cloud Data",
		width:  "100%",
		height: "100%",
		content: content_html
	});
	tabCont.addChild( cp_grid_cloud );
//	cp_grid_cloud.placeAt( "form" );

	var cloud_store = new dojo.data.ItemFileWriteStore({ data: createCloudTableData() });


	var divWData = dojo.create( "div", {
		id: "div-grid-cloud"		// for the grid
	}, cp_grid_cloud.domNode );

	var grid = new dojox.grid.EnhancedGrid({
		id: 'grid-cloud',
		store: cloud_store,
		structure: grid_layout,
		rowSelector: '20px',
	//	style: 'font-size 8pt',		// no effect
		width: '45em',				// required
		height: '33ex',				// required
		plugins: { exporter: true }
	});
	grid.placeAt( dojo.byId( "div-grid-cloud" ) );
	grid.startup();


	var actionBar = dojo.create( "div", {
		className: "dijitDialogPaneActionBar",
		style: "height: 30px"
	}, container );

	var bCancel = new dijit.form.Button({
		label: "<img src='/static/image/icon/Tango/16/actions/dialog-cancel.png'/> Cancel",
		showLabel: true,
		role: "presentation",
		onClick: function() { dijit.byId( "dlg-cloud" ).destroyRecursive(); }
	//	onClick: function() { dijit.byId( "dlg-cloud" ).hide(); }
	});
	actionBar.appendChild( bCancel.domNode );

	if( term_count == 0 )
	{ var export_disabled = true; }
	else
	{ var export_disabled = false; }
	var bExport = new dijit.form.Button(
	{
		id: "btn-cloud-export",
		label: "<img src='/static/image/icon/Tango/16/actions/dialog-ok.png'/> Export",
		showLabel: true,
		disabled: export_disabled,
		role: "presentation",
		onClick: function()
		{
			console.log( "Exporting Cloud Data..." );
			var filename = "cloud.csv";
			exportCloudData( filename );
			dijit.byId( "dlg-cloud" ).destroyRecursive();
		//	dijit.byId( "dlg-cloud" ).hide();
		}
	});
	actionBar.appendChild( bExport.domNode );
}; // createCloudDlg



var createCloudTableData = function()
{
	console.log( "createCloudTableData()" );
	// using global cloud_data

	var config = getConfig();

	var table_data = 
	{
		identifier: 'id',
		label: 'id',
		items: []
	};

	var ner_cloud = cloud_data_elems == 3;

	for( var i = 0; i < cloud_data.length; ++i ) 
	{
		var cloud_line = cloud_data[ i ];

		// NER terms 
		var term = cloud_line.term;

		if( ner_cloud && config.cloudexport.normalize_ws )
		{
			// replace any (multiple) whitespace by a single space
			var term_new = term.replace( /\s+/g, " " );
			if( term != term_new )
			{
			//	console.warn( (i+1) + ": " + term_new );
				cloud_line.term = term_new;
			}
			term = term_new;
		}

		if( ner_cloud && config.cloudexport.comma2semicolon )
		{
			// a comma splits the term by (some?) spreadsheets, notwithstanding ""
			// a semicolon seems fine
			var pos_comma = term.indexOf( "," );
			if( pos_comma !== -1 )
			{
			//	console.warn( (i+1) + ": " + term );
				var term_new = term.replace( ',', ';' );		// comma -> semicolon
			//	console.log( term_new );
				cloud_line.term = term_new;
			}
		}

		table_data.items.push( dojo.mixin( { 'id': i + 1 }, cloud_line ) );
	}

	return table_data;
}



var fillCloudTable = function()
{
	console.log( "fillCloudTable()" );

	var grid_layout = getCloudGridLayout();

	var cloud_store = new dojo.data.ItemFileWriteStore({ data: createCloudTableData() });
//	dojo.forEach( data.items, function( item )
//	{ cloud_store.loadItem( item ); });


	var term_count = getCloudTermCount();
	console.log( "term_count: " + term_count );
//	dijit.byId( "cp-grid-cloud" ).set( "content", "<b>Word Cloud Data: " + term_count + " terms</b><br/>" );

	if( term_count == 0 )
	{ var export_disabled = true; }
	else
	{ var export_disabled = false; }
	dijit.byId( "btn-cloud-export" ).set( "disabled", export_disabled );


	var divWData = dojo.create( "div", {
		id: "div-grid-cloud"		// for the grid
	}, dijit.byId( "cp-grid-cloud" ).domNode );


//	dijit.byId( "grid-cloud" ).destroyRecursive();
	var grid = dijit.byId( "grid-cloud" );
	if( grid )
	{ grid.destroy(); }

	var grid = new dojox.grid.EnhancedGrid({
		id:          "grid-cloud",
		store:        cloud_store,
		structure:    grid_layout,
		rowSelector: "20px",
	//	style:       "font-size 8pt",		// no effect
	//	rowHeight:   "20px",				// no effect
		autoHeight:   true,					// no effect
	//	width:       "45em",				// required
	//	height:      "33ex",				// required
		width:       "100%",
		height:      "100%",
		plugins:    { exporter: true }
	});
	grid.placeAt( dojo.byId( "div-grid-cloud" ) );
	grid.startup();

	/*
	var div_grid = dojo.byId( "div-grid-cloud" );
	if( div_grid )
	{
		grid.placeAt( div_grid );
		grid.startup();
	}
	else
	{ console.log( "No div-grid-cloud !" ); }
	*/
};



function exportCloudData( filename )
{
	console.log( "exportCloudData()" );

	var config = getConfig();

	dijit.byId( "grid-cloud" ).exportGrid( "csv", function( str )
	{
		var url = "services/export_cloud/";
		var cdata = {
			"clouddata": str,				// the cloud data
			"filename": filename,
			"separator": config.cloudexport.separator,
			"zipped": '0',					// {0|1} compression
		};
		var options = {
			handleAs: "text",
			data: cdata,			// clouddata
			timeout: 30000			// 30 sec		REQUIRED, otherwise it only works once
		};

		// Dojo expects the response in a <textarea> element of a html document
		// we sent a text/csv file
		// So Dojo does not know when the response is done, and waits forever
		// a timeout fixes that

		dojo.request.iframe( url, options ).then( function( resp )		// iframe uses POST
		{
			// with xhr we get the clouddata, with iframe we see nothing
		//	console.log( "resp: " + resp );
		//	console( "dojo.request: got response" );
		}),
		function( err ) { console.error( err ); return err; }
    });
}

/*
function exportCloudDataSelected()
{
	console.log( "exportCloudDataSelected()" );
	var str = dijit.byId( "grid-cloud" ).exportSelected( "csv" );
//	console.log( "str: " + str );
	dojo.byId( "output" ).value = str;
};
*/



// [eof]
