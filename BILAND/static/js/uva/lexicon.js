// FL-07-Nov-2012 Created
// FL-10-Jan-2013 Changed

//var fetchDataDialog = function( lexiconID, lexiconTitle, metadata_count, ocrdata_count )
var fetchDataDialog = function( item )
{
//	console.log( "fetchDataDialog()" );

	var lexiconID      = item.pk;
	var lexiconTitle   = item[ "fields" ][ "title" ];
	var metadata_count = item[ "fields" ][ "metadata_count" ];
	var ocrdata_count  = item[ "fields" ][ "ocrdata_count" ];
//	console.log( "lexiconID: ", + lexiconID );
//	console.log( "lexiconTitle: ", + lexiconTitle );
//	console.log( "metadata count: " + metadata_count );
//	console.log( "ocrdata count: " + ocrdata_count );


	var dialog = new dijit.Dialog({
		id: "fetch-data",
		title: "Fetch OCR + Metadata for articles"
	});

	dojo.style( dialog.closeButtonNode, "visibility", "hidden" ); // hide the ordinary close button

	var container = dialog.containerNode;

	var cpdiv = dojo.create( "div", { id: "div-fetchdata" }, container );

	var contentpane = new dijit.layout.ContentPane({
		title: "Fetch article data",
		style: "width: 300px; height: 150px; text-align: left; line-height: 18px; margin: 5px;"
	}, "div-fetchdata" );


	var divLexicon = dojo.create( "div", {
		id: "div-lexicon"
	}, contentpane.domNode );

	var labelLexicon = dojo.create( "label", {
		id: "label-lexicon",
		for: "div-lexicon",
		innerHTML: "Query # " + lexiconID + "<br/>" + lexiconTitle + "<br/>"
	}, contentpane.domNode );


	dojo.create( "label", {
		innerHTML: "<br/>Fetching the KB articles may take a while.<br/>Do you want to continue?<br/><br/>"
	}, contentpane.domNode );


//	if( !(metadata_count == 0 && ocrdata_count == 0) )
//	{ var timestamp_refresh = false; }
//	else
//	{ var timestamp_refresh = true; }
	var timestamp_refresh = true;		// let's always show the option

	if( timestamp_refresh == true )
	{
		var divTimestamp = dojo.create( "div", {
			id: "div-timestamp"
		}, contentpane.domNode );

		var timestamp_refresh = false
		var cbTimestamp = new dijit.form.CheckBox({
			id: "cb-timestamp",
			checked: false,
			onChange: function( btn ) { timestamp_refresh = btn; }
		}, divTimestamp );

		var labelTimestamp = dojo.create( "label", {
			id: "label-timestamp",
			for: "cb-timestamp",
			innerHTML: "&nbsp;Also update query timestamp<br/>"
		}, contentpane.domNode );
	}

	var actionBar = dojo.create( "div", {
		className: "dijitDialogPaneActionBar",
		style: "height: 30px"
	}, container );

	var bCancel = new dijit.form.Button({
		label: "<img src='/static/image/icon/Tango/16/actions/dialog-cancel.png'/> Cancel",
		showLabel: true,
		role: "presentation",
		onClick: function() {
			dialog.hide();
			dijit.byId( "fetch-data" ).destroyRecursive();
		}
	});
	actionBar.appendChild( bCancel.domNode );

	var bOK = new dijit.form.Button(
	{
		label: "<img src='/static/image/icon/Tango/16/actions/dialog-ok.png'/> OK",
		showLabel: true,
		role: "presentation",
		onClick: function() {
			dialog.hide();
			if( timestamp_refresh == true )
			{
			//	console.log( "timestamp refresh" );
				timestampRefresh( lexiconID );
			}
		//	else { console.log( "No timestamp refresh" ); }
			dijit.byId( "fetch-data" ).destroyRecursive();
		//	console.log( "onClick: lexiconID: ", + lexiconID );
			var config = getConfig();
			console.log( "datastore: " + config[ "datastore" ] );
			onClickLoadData( lexiconID, config[ "datastore" ] );
		}
	});
	actionBar.appendChild( bOK.domNode );

	dialog.show();
}
var showDialog = function() { dijit.byId( "fetch-data" ).show(); }
var hideDialog = function() { dijit.byId( "fetch-data" ).hide(); }


var timestampRefresh = function( lexiconID )
{
	dojo.xhrGet({
		url: SUB_SITE + "lexicon/timestamp",
		handleAs: "text",
		content: {
			username:  glob_username,
			password:  glob_password,
			lexiconID: lexiconID
		},
		load: function( data )
		{
			var resp = JSON.parse( data );
			var status = resp[ "status" ];

			if( status === "SUCCESS" )
			{
				var timestamp = resp[ "timestamp" ];
			//	console.log( "timestamp: " + timestamp );
			}
			else
			{
				console.log( status );
				var msg = resp[ "msg" ];
				console.log( msg );
			}
		},
		error: function( err ) {
			console.error( err );
			return err;
		}
	});
}

// [eof]
