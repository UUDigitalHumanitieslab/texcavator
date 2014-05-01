// FL-24-Sep-2013 Created
// FL-30-Sep-2013 Changed

/*
var genDialog = function( title, message, buttons )
var genDialogCallback = function( title, message, buttons, call_func, boundFunction )
*/


// general purpose dialog
var genDialog = function( title, message, buttons )
{
	var answer = "";

	var dialog = new dijit.Dialog({
		title: title
	});

	dojo.style( dialog.closeButtonNode, "visibility", "hidden" ); // hide the ordinary close button

	var container = dialog.containerNode;

	var dialogContainer = new dijit.layout.ContentPane({
		title: "Dialog",
		style: "width: 275px; height: 125px; text-align: left; line-height: 18px; margin: 5px;"
	});
	dialogContainer.placeAt( container );

	var msgNode = dojo.create( "div",
	{
		innerHTML: message,
		style: "clear: both;"
	}, dialogContainer.domNode );

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
			//	dijit.byId( dialogId ).destroyRecursive();
				dialog.destroyRecursive();
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
		//	dijit.byId( dialogId ).destroyRecursive();
			dialog.destroyRecursive();
		}
	});
	actionBar.appendChild( bOK.domNode );

	dialog.show();
	return answer;
} // genDialog()



// general purpose dialog with callbackfunction on OK
var genDialogCallback = function( title, message, buttons, call_func, boundFunction )
{
	var answer = "";

	var dialog = new dijit.Dialog({
		title: title
	});

	dojo.style( dialog.closeButtonNode, "visibility", "hidden" ); // hide the ordinary close button

	var container = dialog.containerNode;

	var dialogContainer = new dijit.layout.ContentPane({
		title: "Dialog",
		style: "width: 275px; height: 125px; text-align: left; line-height: 18px; margin: 5px;"
	});
	dialogContainer.placeAt( container );

	var msgNode = dojo.create( "div",
	{
		innerHTML: message,
		style: "clear: both;"
	}, dialogContainer.domNode );

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
			//	dijit.byId( dialogId ).destroyRecursive();
				dialog.destroyRecursive();
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
		//	dijit.byId( dialogId ).destroyRecursive();
			dialog.destroyRecursive();
			if( call_func ) { boundFunction(); }
		}
	});
	actionBar.appendChild( bOK.domNode );

	dialog.show();
	return answer;
} // genDialogCallback()

// [eof]
 
