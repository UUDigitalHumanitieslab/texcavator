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

glob_username  = "";		// global


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
		dijit.byId( "dlg-login" ).hide();

		glob_username = dijit.byId( "tb-username" ).get( "value" );
		var password = dijit.byId( "tb-password" ).get( "value" );
		var next = location.search.split('next=')[1]; // TODO: dirty way to retrieve next url

		// Empty the username and password fields
		dijit.byId( "tb-username" ).set( "value", "" );
		dijit.byId( "tb-password" ).set( "value", "" );

		dojo.xhrPost({
			url: "login",
			handleAs: "json",
			content: {
				"username" : glob_username,
				"password" : password,
				"next_url" : next
			},
			load: function(response)
			{
				var status = response.status;
				var msg = response.msg;
				var next_url = response.next_url;

				if ( status === "SUCCESS" )
				{
					createQueryList();		// using username to filter the Saved queries
					$('#query').focus();

					if ( next_url )
					{
						window.location.href = next_url;
					}
				}
				else
				{
					var retry = true;
					createResponse( msg, retry );
					showResponse();
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
	actionBar.appendChild( bSubmit.domNode );
};

var showLogin = function()
{
	if( dijit.byId( "dlg-login" ) === undefined )
	{ console.log( "showLogin: dlg-login is undefined" ); }

	dijit.byId( "dlg-login" ).show();
};

var hideLogin = function() { dijit.byId( "dlg-login" ).hide(); };

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
		style: "width: 275px; height: 125px; text-align: right; line-height: 24px; margin: 5px;"
	}, "logout-div" );

//	if( retry )
//	{ var icon = "<img src='/static/image/icon/Tango/48/status/dialog-warning.png' height='50' align='left' />"; }
//	else
//	{ var icon = "<img src='/static/image/icon/Tango/48/status/dialog-information.png' height='50' align='left' />"; }

	dojo.create( "div", {
		innerHTML: "<img src='/static/image/icon/Tango/48/apps/preferences-users.png' height='50' align='left' />",
		style: "clear: both"
	}, logoutContainer.domNode );

	var msg = "Goodbye " + glob_username;
	var msgNode = dojo.create( "div",
	{
		innerHTML: msg,
		style: "text-align: left"
	}, logoutContainer.domNode );

	var actionBar = dojo.create( "div", {
		className: "dijitDialogPaneActionBar",
		style: "height: 30px"
	}, container );

	var bClose = new dijit.form.Button({
		label: "<img src='/static/image/icon/Tango/16/actions/dialog-cancel.png'/>&nbsp;Cancel",
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
			        dijit.byId( "dlg-logout" ).hide();
			        glob_username = "";
			        clearGui();		// cloud, article, lexicons...
			        showLogin();
			    },
			    error: function( err ) {
				    console.error( err );
				    dijit.byId( "dlg-login" ).destroyRecursive();
				    return err;
                }
			});
        }
	});
	actionBar.appendChild( bLogout.domNode );
};

var showLogout = function() { dijit.byId( "dlg-logout" ).show(); };
var hideLogout = function() { dijit.byId( "dlg-logout" ).hide(); };

var createResponse = function( msg, retry )
{
	var dlgResponse = new dijit.Dialog({
		id: "message",
		title: "Login"
	});

	dojo.style( dlgResponse.closeButtonNode, "visibility", "hidden" );   // hide the ordinary close button

	var container = dlgResponse.containerNode;

	var loginrespdiv = dojo.create( "div", { id: "login-resp-div" }, container );

	var style = "width: 275px; height: 125px; text-align: right; line-height: 24px; margin: 5px;";
//	if( retry )
//	{ style += "background-color: LightPink"; }
//	else
//	{ style += "background-color: LightYellow"; }

	var respContainer = new dijit.layout.ContentPane({
		title: "Resp",
		style: style
	}, "login-resp-div" );

	var icon = "<img src='/static/image/icon/Tango/48/status/dialog-information.png' height='50' align='left' />";
	if( retry )
	{ icon = "<img src='/static/image/icon/Tango/48/status/dialog-warning.png' height='50' align='left' />"; }

	dojo.create( "div", {
		innerHTML: icon,
		style: "clear: both"
	}, respContainer.domNode );

	var msgNode = dojo.create( "div",
	{
		innerHTML: msg,
		style: "text-align: left"
	}, respContainer.domNode );

	var actionBar = dojo.create( "div", {
		className: "dijitDialogPaneActionBar",
		style: "height: 30px"
	}, container );

	var bOK = new dijit.form.Button({
		label: "<img src='/static/image/icon/Tango/16/actions/dialog-ok.png'/>&nbsp;OK",
		title: "OK",
		text: "OK",
		showLabel: true,
		role: "presentation",
		retry: retry,
		onClick: function( ev ) {
			dijit.byId( "message" ).destroyRecursive();
			if( retry )
			{ showLogin(); }
		}
	});
	actionBar.appendChild( bOK.domNode );
};

var showResponse = function() { dijit.byId( "message" ).show(); };