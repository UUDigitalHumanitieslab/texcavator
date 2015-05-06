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

var default_username = "";
var default_password = "";
// FL-24-Oct-2013 the KB forbids the use of a guest account
//var default_username = "guest";		// for auto-login
//var default_password = "guest";		// for auto-login

var default_projectn = "";	// WAHSP, BiLand, Horizon

glob_username  = "";		// global
glob_password  = "";		// global
glob_userid    = null;		// global

glob_projectn  = "";		// global: project related
glob_begindate = "";		// global: project related
glob_enddate   = "";		// global: project related

glob_sessionId = "";		// global


var createLogin = function( projectname )
{
//	console.log( "createLogin()" );
//	console.log( "projectname: " + projectname );

	default_projectn = projectname;

	var checkSubmit = function()
	{
	//	console.log( "checkSubmit()" );

		var curr_username = dijit.byId( "tb-username" ).get( "value" );
		var curr_password = dijit.byId( "tb-password" ).get( "value" );
		var curr_projectn = dijit.byId( "cb-projectn" ).get( "value" );

		if(curr_username  == "" || curr_password == "" || curr_projectn == "" )
		{ var disabled = true; }
		else
		{ var disabled = false; }		// user must supply values

		bSubmit.set( "disabled", disabled );

		return disabled;
	}

	if( default_username == "" || default_password == "" || default_projectn == "" )
	{ var submit_disabled = true; }		// user must supply values
	else
	{ var submit_disabled = false; }

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
		value: default_username,
		onChange: function() { checkSubmit(); },
		onKeyPress: function( ev ) {
			if( ev.charCode == 0 && ev.keyCode == dojo.keys.ENTER )
			{
				var disabled = checkSubmit();
				if( disabled == false ) { fSubmit(); }
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
		value: default_password,
		onChange: function() { checkSubmit(); },
		onKeyPress: function( ev ) {
			if( ev.charCode == 0 && ev.keyCode == dojo.keys.ENTER )
			{
				var disabled = checkSubmit();
				if( disabled == false ) { fSubmit(); }
			}
		}
	})).domNode, pwdNode );


	var projNode = dojo.create( "div",
	{
		innerHTML: "Project: ",
		style: "clear: both"
	}, loginContainer.domNode );

    var projectData = [
        { id:1, name : "WAHSP" },
        { id:2, name : "BiLand" },
        { id:3, name : "Horizon" },
        { id:4, name : "All KB" }
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
		glob_password = dijit.byId( "tb-password" ).get( "value" );
		glob_projectn = dijit.byId( "cb-projectn" ).get( "value" );

		dijit.byId( "tb-username" ).set( "value", default_username );
		dijit.byId( "tb-password" ).set( "value", default_password );
		dijit.byId( "cb-projectn" ).set( "value", default_projectn );

		dojo.xhrPost({
			url: "login",
			handleAs: "json",
			content: {
				"username" : glob_username,
				"password" : glob_password,
				"projectname" : glob_projectn
			},
			load: function(response)
			{
			//	console.log( data );
				var status = response["status"];
				var msg = response["msg"];

				if( status === "SUCCESS" )
				{
					glob_server_timestamp = response[ "timestamp" ];
					setServerTimestamp( glob_server_timestamp );		// timestamp.js
					var client_timestamp = getClientTimestamp();		// timestamp.js
					if( glob_server_timestamp == client_timestamp )
					{ console.log( "timestamp: " + server_timestamp ); }
					else
					{ console.warn( "server: " + glob_server_timestamp + ", client: " + client_timestamp ); }

					var daterange = response[ "daterange" ];
					glob_begindate = daterange[ 0 ].toString();		// store as string (could contain '-')
					glob_enddate   = daterange[ 1 ].toString();		// store as string (could contain '-')
					storeDateLimits( daterange );					// set date widgets on toolbar
					sessionId = response[ "session_id" ];
					var btnUser = dijit.byId( "toolbar-user" );
					var label = "<img src = '/static/image/icon/Tango/22/apps/preferences-users.png')/>" + glob_username;
					btnUser.set( "label", label );
					createQueryList();		// using username to filter the Saved queries

					if( ILPS_LOGGING )
					{
						glob_userid = response[ "user_id" ];
						var user_info = { username: response[ "user_name" ] };
						var login_event = false;					// avoid generating multiple login events 
						// when login_event = false, only the user_id is logged, but not the user_info
						console.log( "ILPSLogging.userLogin()" );
						ILPSLogging.userLogin( glob_userid, user_info, login_event );
					}

					if( glob_username === "guest" && glob_password === "guest" )
					{
						var retry = false;
						createResponse( msg, retry );
						showResponse();
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
	}

	var bSubmit = new dijit.form.Button({
		disabled: submit_disabled,
		label: "Login",
		iconClass: "dijitIconUsers",
		title: "Login",
		text: "Login",
		showLabel: true,
		role: "presentation",
		onClick: fSubmit
	});
	actionBar.appendChild( bSubmit.domNode );
}

var showLogin = function()
{
	if( dijit.byId( "dlg-login" ) == undefined )
	{ console.log( "showLogin: dlg-login is undefined" ); }

	dijit.byId( "dlg-login" ).show();
}

var hideLogin = function() { dijit.byId( "dlg-login" ).hide(); }


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
			console.log( "bLogout: " + glob_userid + " (" + glob_username + ")" );

		    dojo.xhrPost({
			    url: "logout",
			    handleAs: "json",
			    content: {
				    "username" : glob_username,
				    "password" : glob_password,
				    "projectname" : glob_projectn
			    },
			    load: function(response)
			    {
			        if( ILPS_LOGGING )
			        {
			            console.log( "ILPSLogging.userLogout()" );
			            ILPSLogging.userLogout();
			        }

			        dijit.byId( "dlg-logout" ).hide();
			        glob_username = "";
			        var btnUser = dijit.byId( "toolbar-user" );
			        var label = "<img src = '/static/image/icon/Tango/22/apps/preferences-users.png')/>";
			        btnUser.set( "label", label );
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
}

var showLogout = function() { dijit.byId( "dlg-logout" ).show(); }
var hideLogout = function() { dijit.byId( "dlg-logout" ).hide(); }


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

	if( retry )
	{ var icon = "<img src='/static/image/icon/Tango/48/status/dialog-warning.png' height='50' align='left' />"; }
	else
	{ var icon = "<img src='/static/image/icon/Tango/48/status/dialog-information.png' height='50' align='left' />"; }

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
}

var showResponse = function() { dijit.byId( "message" ).show(); }

// [eof]
