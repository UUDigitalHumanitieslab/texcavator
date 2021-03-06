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

	var term_src = getCloudSrc();
	var term_count = getCloudTermCount();
	var content_html = "<b>";
	if ( cloud_src === "article" ) { 
		content_html += "Single Article"; 
	}
	else if ( cloud_src === "date range" ) { 
		content_html += "Date range";
	}
	else if ( cloud_src === "burst" ) { 
		content_html += "Burst"; 
	}
	content_html += " Word Cloud Data: " + term_count + " terms</b><br/>";

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
	});
	actionBar.appendChild( bCancel.domNode );

	var bExport = new dijit.form.Button(
	{
		id: "btn-cloud-export",
		label: "<img src='/static/image/icon/Tango/16/actions/dialog-ok.png'/> Export",
		showLabel: true,
		disabled: term_count === 0,
		role: "presentation",
		onClick: function()
		{
			console.log( "Exporting Cloud Data..." );
			var filename = "cloud.csv";
			exportCloudData( filename );
			dijit.byId( "dlg-cloud" ).destroyRecursive();
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
};


var fillCloudTable = function()
{
	console.log( "fillCloudTable()" );

	var grid_layout = getCloudGridLayout();

	var cloud_store = new dojo.data.ItemFileWriteStore({ data: createCloudTableData() });

	var term_count = getCloudTermCount();
	console.log( "term_count: " + term_count );

	dijit.byId( "btn-cloud-export" ).set( "disabled", term_count === 0 );

	var divWData = dojo.create( "div", {
		id: "div-grid-cloud"		// for the grid
	}, dijit.byId( "cp-grid-cloud" ).domNode );

	if( dijit.byId( "grid-cloud" ) )
	{ dijit.byId( "grid-cloud" ).destroy(); }

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
};


function exportCloudData( filename )
{
	console.log( "exportCloudData()" );

	var config = getConfig();

	dijit.byId( "grid-cloud" ).exportGrid( "csv", function( str )
	{
		// Copy the data to a form and then export
		// TODO: yes, this is ugly; but I'm not sure of an alternative to send POST data and to return a .csv-response
		$("input[name='separator']").val(config.cloudexport.separator);
		$("input[name='filename']").val(filename);
		$("input[name='zipped']").val(0);  // 0 or 1 for zipped (TODO: magic number)
		$("input[name='clouddata']").val(str);
		$("input[name='export_cloud']").click();
    });
}