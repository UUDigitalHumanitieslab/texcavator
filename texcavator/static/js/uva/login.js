// FL-13-Feb-2012 Created
// FL-24-Oct-2013 Changed

dojo.require( "dijit.Dialog" );
dojo.require( "dijit.form.Button" );
dojo.require( "dijit.form.TextBox" );
dojo.require( "dijit.layout.ContentPane" );

/*
var createLogin = function( projectname )
var showLogin = function()
var hideLogin = function()
var createLogout = function()
var showLogout = function()
var hideLogout = function()
var createResponse = function( msg, retry )
var showResponse = function()
*/

glob_username  = "";	// global variable that saves the username
is_guest = true;		// global variable that signals whether this user is a guest


var createLogin = function( projectname )
{
	var checkSubmit = function()
	{
		var curr_username = dijit.byId( "tb-username" ).get( "value" );
		var curr_password = dijit.byId( "tb-password" ).get( "value" );
		var curr_projectn = dijit.byId( "cb-projectn" ).get( "value" );

		var disabled = curr_username === "" || curr_password === "" || curr_projectn === ""; // user must supply values
		bSubmit.set( "disabled", disabled );
		return disabled;
	};

	var dlgLogin = new dijit.Dialog({
		id: "dlg-login",
		title: "Login"
	});

	dojo.style( dlgLogin.closeButtonNode, "visibility", "hidden" ); // hide the ordinary close button

	var container = dlgLogin.containerNode;

	var cpdiv = dojo.create( "div", { id: "login-div" }, container );
	var loginContainer = new dijit.layout.ContentPane({
		title: "Login",
		style: "width: 275px; height: 125px; text-align: right; line-height: 24px; margin: 5px;"
	}, "login-div" );

	dojo.create( "div", {
		innerHTML: "<img src='/static/image/icon/Tango/48/status/dialog-password.png' height='50' align='left' />",
		style: "clear: both"
	}, loginContainer.domNode );

	var usrNode = dojo.create( "div",
	{
		innerHTML: " Username: ",
		style: "clear: both;"
	}, loginContainer.domNode );

	dojo.place(( new dijit.form.TextBox({
		id: "tb-username",
		label: "Username",
		title: "Username",
		onChange: function() { checkSubmit(); },
		onKeyPress: function( ev ) {
			if( ev.charCode === 0 && ev.keyCode == dojo.keys.ENTER )
			{
				if( !checkSubmit() ) { fSubmit(); }
			}
		}
	})).domNode, usrNode );


	var pwdNode = dojo.create( "div",
	{
		innerHTML: "Password: ",
		style: "clear: both"
	}, loginContainer.domNode );

	dojo.place(( new dijit.form.TextBox({
		id: "tb-password",
		label: "Password",
		title: "Password",
		type: "password",
		onChange: function() { checkSubmit(); },
		onKeyPress: function( ev ) {
			if( ev.charCode === 0 && ev.keyCode == dojo.keys.ENTER )
			{
				if( !checkSubmit() ) { fSubmit(); }
			}
		}
	})).domNode, pwdNode );


	var projNode = dojo.create( "div",
	{
		innerHTML: "Project: ",
		style: "clear: both"
	}, loginContainer.domNode );

    var projectData = [
        { id: 1, name: projectname },
    ];

	var projectListStore = new dojo.store.Memory({ data: projectData });
	dojo.place(( new dijit.form.ComboBox({
		id: "cb-projectn",
		name: "cbProject",
		displayedValue: "Select project",
		store: projectListStore,
		value: projectname,			// initial selection
		searchAttr: "name",
		onChange: function() { checkSubmit(); }
	})).domNode, projNode );


	var actionBar = dojo.create( "div", {
		className: "dijitDialogPaneActionBar",
		style: "height: 30px"
	}, container );

	var fSubmit = function()
	{
		hideLogin();

		var username = dijit.byId( "tb-username" ).get( "value" );
		var password = dijit.byId( "tb-password" ).get( "value" );
		var next = location.search.split('next=')[1]; // TODO: dirty way to retrieve next url

		// Empty the username and password fields
		dijit.byId( "tb-username" ).set( "value", "" );
		dijit.byId( "tb-password" ).set( "value", "" );

		dojo.xhrPost({
			url: "login",
			handleAs: "json",
			content: {
				"username" : username,
				"password" : password,
				"next_url" : next
			},
			load: function(response)
			{
				if ( response.status === "SUCCESS" )
				{
					is_guest = false;
					createUserEnv(username);

					var next_url = response.next_url;
					if ( next_url )
					{
						window.location.href = next_url;
					}
				}
				else
				{
					genDialog("Login failed", response.msg, {"OK": true}, showLogin);
				}
			},
			error: function( err ) {
				console.error( err );
				dijit.byId( "dlg-login" ).destroyRecursive();
				return err;
			}
		});
	};

	var bSubmit = new dijit.form.Button({
		disabled: true,
		label: "Login",
		iconClass: "dijitIconUsers",
		title: "Login",
		text: "Login",
		showLabel: true,
		role: "presentation",
		onClick: fSubmit
	});

	var bCancel = new dijit.form.Button({
		label: "<img src='/static/image/icon/Tango/16/actions/dialog-cancel.png'/> Cancel",
		title: "Cancel",
		text: "Cancel",
		showLabel: true,
		role: "presentation",
		onClick: function() {
			hideLogin();
			showStart();
		}
	});

	actionBar.appendChild( bSubmit.domNode );
	actionBar.appendChild( bCancel.domNode );
};


function doGuestLogin() {
	dojo.xhrPost({
		url: "guest_login",
		handleAs: "json",
		load: function(response)
		{
			if ( response.status === "SUCCESS" )
			{
				createUserEnv(response.username);
			}
			else
			{
				genDialog("Login failed", response.msg, {"OK": true});
			}
		},
		error: function( err ) {
			console.error( err );
			return err;
		}
	});
}


var createLogout = function()
{
	var dlgLogout = new dijit.Dialog({
		id: "dlg-logout",
		title: "Logout"
	});

	dojo.style( dlgLogout.closeButtonNode, "visibility", "hidden" ); // hide the ordinary close button

	var container = dlgLogout.containerNode;

	var cpdiv = dojo.create( "div", { id: "logout-div" }, container );
	var logoutContainer = new dijit.layout.ContentPane({
		title: "Logout",
		style: "width: 275px; height: 125px; margin: 5px;"
	}, "logout-div" );

	var msg = "Thanks for using Texcavator. " +
		"Clicking the logout button below will end your session. " +
		"Click the cancel button to continue using Texcavator.";
	var msgNode = dojo.create( "div",
	{
		innerHTML: msg,
	}, logoutContainer.domNode );

	var actionBar = dojo.create( "div", {
		className: "dijitDialogPaneActionBar",
		style: "height: 30px"
	}, container );

	var bClose = new dijit.form.Button({
		label: "<img src='/static/image/icon/Tango/16/actions/dialog-cancel.png'/> Cancel",
		title: "Cancel",
		text: "Cancel",
		showLabel: true,
		role: "presentation",
		onClick: function() { dijit.byId( "dlg-logout" ).destroyRecursive(); }
	});
	actionBar.appendChild( bClose.domNode );

	var bLogout = new dijit.form.Button({
		label: "Logout",
		iconClass: "dijitIconUsers",
		title: "Logout",
		text: "Logout",
		showLabel: true,
		role: "presentation",
		onClick: function() {
		    dojo.xhrPost({
			    url: "logout",
			    handleAs: "json",
			    load: function(response)
			    {
			        clearUserEnv();		// cloud, article, lexicons...
			    },
			    error: function( err ) {
				    console.error( err );
				    dijit.byId( "dlg-logout" ).destroyRecursive();
				    return err;
                }
			});
        }
	});
	actionBar.appendChild( bLogout.domNode );
};


// Create the user environment
function createUserEnv(username) {
	glob_username = username; 			// Set the global username
	createQueryList();					// Use username to filter the Saved queries
	$("#toolbar-logout").show();		// Show log-out button
	$("#toolbar-start").hide();			// Hide start button
	$("#query").focus();				// Set focus on the query text

	// Add a warning that queries for guest users will be deleted.
	if (is_guest) {
		var msg = "Queries saved by guests will be deleted <strong>every day</strong>.";
		var msg_div = "<p class='alert alert-warning alert-warning-guest'>" + msg + "</p>";
		$("#saveQueryPane").append(msg_div);
		$("#lexicon").append(msg_div);
	}
}


// called after logout: glob_username = ""
function clearUserEnv()
{
	// Reset global variables
	glob_username = "";
	is_guest = true;

	hideLogout();						// Hide log-out dialog
	$("#toolbar-logout").hide();		// Hide log-out button
	$("#toolbar-start").show();			// Show start button
	showStart();						// Show start dialog

	// Remove warnings for guests
	$(".alert-warning-guest").remove();

	// Remove query results and query
	dojo.byId( "search-result" ).innerHTML = "Search for newspaper articles at the KB.";
	dijit.byId( "query" ).set( "value", "" );

	// Empty the saved queries
	dojo.empty( dojo.byId( "lexiconItems" ) );

	// Clear the tabs
	$("#metadata svg").empty();			// Metadata
	clearCloud();						// Cloud, in cloud_view.js
	clearTextview();					// OCR text, in ocr.js

	// Clear timeline
	$("#timeline-advert-warning").hide();
	dojo.empty(dojo.byId("chartDiv"));
	dojo.empty(dojo.byId("cloud"));
	dojo.empty(dojo.byId("cal-heatmap"));
}


var showLogin = function() { dijit.byId( "dlg-login" ).show(); };
var hideLogin = function() { dijit.byId( "dlg-login" ).hide(); };
var showLogout = function() { dijit.byId( "dlg-logout" ).show(); };
var hideLogout = function() { dijit.byId( "dlg-logout" ).hide(); };
