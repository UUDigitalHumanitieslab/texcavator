// FL-20-Jun-2012 Created
// FL-28-Feb-2013 Check celery process owner
// FL-27-Mar-2013 Changed


// Celery processes dialog
var celeryDialog = function( title, message, buttons )
{
	var answer = "";

	var dialog = new dijit.Dialog({
		id: "celery-dialog",
		title: title
	});

	dojo.style( dialog.closeButtonNode, "visibility", "hidden" ); // hide the ordinary close button

	var container = dialog.containerNode;

	var cpdiv = dojo.create( "div", { id: "dialog-div" }, container );
	var dialogContainer = new dijit.layout.ContentPane({
		title: "Dialog",
		style: "width: 800px; height: 160px; text-align: left; line-height: 18px; margin: 5px;"	// textarea
	}, "dialog-div" );


	var msgNode = dojo.create( "div",
	{
		style: "clear: both;"
	}, dialogContainer.domNode );

	var output = "";
	dojo.forEach( message, function( amessage ) {
		output += amessage + "\n";
	});

	var textarea = new dijit.form.SimpleTextarea({
		name: "message",
		rows: message.length,
		cols: "110",
		style: "width:auto;"
	}, msgNode );
	textarea.set( "value", output );

	var actionBar = dojo.create( "div", {
		className: "dijitDialogPaneActionBar",
		style: "height: 30px"
	}, container );

	if( buttons[ "Cancel" ] )
	{
		var bCancel = new dijit.form.Button({
			label: "<img src='/static/image/icon/Tango/16/actions/dialog-cancel.png'/> Cancel",
			showLabel: true,
			role: "presentation",
			onClick: function() {
				answer = "Cancel";
				dijit.byId( "celery-dialog" ).destroyRecursive();
			}
		});
		actionBar.appendChild( bCancel.domNode );
	}

	var bOK = new dijit.form.Button(
	{
		label: "<img src='/static/image/icon/Tango/16/actions/dialog-ok.png'/> OK",
		showLabel: true,
		role: "presentation",
		onClick: function() {
			answer = "OK";
			dijit.byId( "celery-dialog" ).destroyRecursive();
		}
	});
	actionBar.appendChild( bOK.domNode );

	dialog.show();
	return answer;
}
var showCeleryDialog = function() { dijit.byId( "celery-dialog" ).show(); }
var hideCeleryDialog = function() { dijit.byId( "celery-dialog" ).hide(); }

var celery_only_failure = true;			// show only failure
var celeryCheckFailure = function( celery_owner )
{
	storeCeleryOwner( celery_owner );	// config.js
	if( celery_owner == "None" ) { return; }

	celeryCheck( celery_owner );
	celery_only_failure = false;		// show success + failure
}

var celeryCheck = function( celery_owner )
{
	if( celery_owner == "None" )
	{
		var title = "Celery task queue status";
		var message = "Celery is currently not used";
		var buttons = { "OK": true, "Cancel": false };
		genDialog( title, message, buttons );
		return;
	}

	dojo.xhrGet({
		url: "services/celery/",
		sync: true,
		handleAs: "json",
		load: function( resp )
		{
		//	console.log( resp );
			if( resp.status === "OK" )
			{
				// check the owner of the processes
				var process_count = 0;		// of the app owner only
				var app_data = [];
				dojo.forEach( resp.data, function( entry, i ) {
					var process_owner = entry.split( " " )[ 0 ]; 
					if( celery_owner === process_owner ) {
						process_count += 1;
						app_data.push( entry );
					}
				});

				var message = process_count + " Celery processes found for owner " + celery_owner;
				console.debug( message );

				if( process_count > 0 )
				{
					if( celery_only_failure )
					{ return; }
					message = message.fontcolor( "green" );
				}
				else
				{ message = message.fontcolor( "red" ); }
			}
			else
			{ var message = "Unknown"; }

			var title = "Celery task queue status";
			var buttons = { "OK": true, "Cancel": false };

			//celeryDialog( title, app_data, buttons );		// using the textarea
			genDialog( title, message, buttons );			// single text line
		},
		error: function( err ) { console.error( err ); return err; }
	});
}

// [eof]
