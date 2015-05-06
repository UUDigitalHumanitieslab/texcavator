// FL-27-Jan-2012 Created
// FL-29-Nov-2013 Changed

dojo.require( "dojo.data.ItemFileWriteStore" );
//dojo.require("dojo.date");
dojo.require( "dojo.date.locale" );
dojo.require( "dojo.i18n" );
dojo.require( "dojo.store.Memory" );

dojo.require( "dijit.Calendar" );
dojo.require( "dijit.Dialog" );
dojo.require( "dijit.Toolbar" );
dojo.require( "dijit.ToolbarSeparator" );
dojo.require( "dijit.Tooltip" );
dojo.require( "dijit.form.Button" );
dojo.require( "dijit.form.DateTextBox" );
dojo.require( "dijit.form.CheckBox" );
dojo.require( "dijit.form.ComboBox" );
dojo.require( "dijit.form.NumberSpinner" );
dojo.require( "dijit.form.RadioButton" );
dojo.require( "dijit.form.SimpleTextarea" );
dojo.require( "dijit.form.TextBox" );
dojo.require( "dijit.layout.ContentPane" );
dojo.require( "dijit.layout.TabContainer" );

dojo.require( "dojox.widget.Dialog" );

/*
var storeDateLimits = function( SRU_DATE_LIMITS )
var toDateString = function( date )
var getDateBeginStr = function()
var getDateEndStr   = function()
var getDateRangeString = function()
var getBeginDate = function()
var getEndDate = function()
var createToolbar = function()
var toolbarSearch = function()
var toolbarQuery = function()
var toolbarAbout = function()
var showAbout = function()
var createAbout = function()
*/

// Project Date range
// Notice: these are just the initial values. 
// At startup they are already overwritten with the values taken from settings.py
// WAHSP
//var minDate = new Date( 1900,  0,  1 );		// month 0...11
//var maxDate = new Date( 1945, 11, 31 );		// month 0...11
// BiLand
//var minDate = new Date( 1850,  0,  1 );		// month 0...11
//var maxDate = new Date( 1945, 11, 31 );		// month 0...11
// Horizon
//var minDate = new Date( 1850,  0,  1 );		// month 0...11
//var maxDate = new Date( 1990, 11, 31 );		// month 0...11

var minDate;			// fixed for project
var maxDate;			// fixed for project
var beginDateMax;		// changeable
var endDateMin;			// changeable
var beginDate = minDate;
var endDate   = maxDate;


var storeDateLimits = function( SRU_DATE_LIMITS )
{
//	console.log( "storeDateLimits()" );
//	console.log( "SRU_DATE_LIMITS: " + SRU_DATE_LIMITS );

	var min_date = SRU_DATE_LIMITS[ 0 ].toString();
	var max_date = SRU_DATE_LIMITS[ 1 ].toString();

	// parseInt with radix 10 to prevent trouble with leading 0's (octal, hex)
	// substring: from index is included, to index is not included
	var min_year  = parseInt( min_date.substring( 0, 4 ), 10 );
	var max_year  = parseInt( max_date.substring( 0, 4 ), 10 );

	var min_month = parseInt( min_date.substring( 4, 6 ), 10 ) -1;	// month 0...11
	var max_month = parseInt( max_date.substring( 4, 6 ), 10 ) -1;	// month 0...11

	var min_day   = parseInt( min_date.substring( 6, 8 ), 10 );
	var max_day   = parseInt( max_date.substring( 6, 8 ), 10 );

	minDate = new Date( min_year, min_month, min_day );
	maxDate = new Date( max_year, max_month, max_day );
	beginDate = minDate;
	endDate   = maxDate;

//	console.log( min_year + " " + min_month + " " + min_day );
//	console.log( max_year + " " + max_month + " " + max_day );
//	console.log( minDate );
//	console.log( maxDate );

	// update widget contents
	dijit.byId( "begindate" ).set( "constraints", { min: minDate, max: maxDate } );
	dijit.byId( "enddate"   ).set( "constraints", { min: minDate, max: maxDate } );
	dijit.byId( "begindate" ).set( "value", minDate );
	dijit.byId( "enddate"   ).set( "value", maxDate );

	var min_date = dijit.byId( "begindate" ).get( "value" );
	var max_date = dijit.byId( "enddate"   ).get( "value" );
//	console.log( "from: " + min_date + ", to: " + max_date );
} // storeDateLimits()

function stringToDate(strDate){
    /* 
     * Return a JavaScript Date object representing the date in date_string.
     * date_string format: yyyy-mm-dd
     */
    var dateParts = strDate.split("-");
    return new Date(dateParts[0], (dateParts[1]-1), dateParts[2]);
}

var toDateString = function( date )
{
	// Date -> yyyymmdd
	// e.g. 01-Jan-1900 -> "19000101"
	// e.g. 31-Dec-1945 -> "19451231"

//	console.log( "Date: " + date );

	var year = date.getFullYear();		// four digits
	var yearStr = year.toString();

	var month = date.getMonth() + 1;	// 0...11 -> 1...12
	if( month > 9 )
	{ var monthStr = month.toString(); }
	else
	{ var monthStr = "0" + month.toString(); }

	var day = date.getDate();			// 1...31		// getDay() is weekday number: 0...6
	if( day > 9 )
	{ var dayStr = day.toString(); }
	else
	{ var dayStr = "0" + day.toString(); }

	var dateStr = yearStr + monthStr + dayStr;
//	console.log( dateStr );

	return dateStr;
} // toDateString()


var getDate_Begin_Str = function()
{
	var bds = toDateString( beginDate );
	return bds.substring(0,4) + '-' + bds.substring(4,6) + '-' + bds.substring(6,8);
}

var getDate_End_Str = function()
{
	var eds = toDateString( endDate );
	return eds.substring(0,4) + '-' + eds.substring(4,6) + '-' + eds.substring(6,8);
}

var getDateBeginStr = function() { return toDateString( beginDate ); }
var getDateEndStr   = function() { return toDateString( endDate ); }

var getDateRangeString = function()
{
	return getDateBeginStr() + ',' + getDateEndStr();
}

var getBeginDate = function()
{
	return beginDate;
}

var getEndDate = function()
{
	return endDate;
}



var createToolbar = function()
{
	var toolbar = new dijit.Toolbar({
		style: "height: 26px;"
	}, "span-toolbar");		// id="span-toolbar" in base.html

	require( [ "dojo/date" ], function( date ) {
		beginDateMax = date.add( maxDate, "day", -1 );
	//	console.log( "beginDateMax: " + beginDateMax );

		endDateMin = date.add( minDate, "day", 1 );
	//	console.log( "endDateMin: " + endDateMin );
	});

	var btnDateFilterBegin = new dijit.form.Button({
		label: "<img src = '/static/image/icon/Tango/22/apps/office-calendar.png')/>Search period: from",
		showLabel: true,
		disabled: true
	//	onClick: toolbarDateFilter
	});
	toolbar.addChild( btnDateFilterBegin );

	var beginDateTB = new dijit.form.DateTextBox( {
		id: "begindate",
		style: "width: 90px;",
		value: minDate,
		constraints: { min: minDate, max: beginDateMax },
		onChange: function() {
			beginDate = beginDateTB.get( "value" );

			// set new min constraint for endDate
			var constraints = endDateTB.get( "constraints" );
			var min = constraints[ "min" ];
			var max = constraints[ "max" ];
		//	console.log( "endDateMin old: " + min );
		//	console.log( "endDateMax: " + max );
			require( [ "dojo/date" ], function( date ) {
				var value = beginDateTB.get( "value" );
				min = date.add( value, "day", 1 );
			});
		//	console.log( "endDateMin new: " + min );
			constraints[ "min" ] = min;		// update
			endDateTB.set( "constraints", constraints );

			updateYearSlider( dijit.byId( "begindate" ).get( "value" ), dijit.byId( "enddate" ).get( "value" ) );
		}
	} );
	toolbar.addChild( beginDateTB );

	var btnDateFilterEnd = new dijit.form.Button({
		label: "to",
		showLabel: true,
		disabled: true
	});
	toolbar.addChild( btnDateFilterEnd );


	var endDateTB = new dijit.form.DateTextBox( {
		id: "enddate",
		style: "width: 90px;",
		value: maxDate,
		constraints: { min: endDateMin, max: maxDate },
		onChange: function() {
			endDate = endDateTB.get( "value" );

			// set new max constraint for beginDate
			var constraints = beginDateTB.get( "constraints" );
			var min = constraints[ "min" ];
			var max = constraints[ "max" ];
		//	console.log( "beginDateMin: " + min );
		//	console.log( "beginDateMax old: " + max );
			require( [ "dojo/date" ], function( date ) {
				var value = endDateTB.get( "value" );
				max = date.add( value, "day", -1 );
			});
		//	console.log( "beginDateMax new: " + max );
			constraints[ "max" ] = max;		// update
			beginDateTB.set( "constraints", constraints );

			updateYearSlider( dijit.byId( "begindate" ).get( "value" ), dijit.byId( "enddate" ).get( "value" ) );
		}
	} );
	toolbar.addChild( endDateTB );

	toolbar.addChild( new dijit.ToolbarSeparator() );


	var btnSearch = new dijit.form.Button({
		label: "<img src = '/static/image/icon/Tango/22/actions/system-search.png')/>Search",
		showLabel: true,
		onClick: toolbarSearch
	});
//	toolbar.addChild( btnSearch );	// New Search widget for BILAND, not WAHSP

	var btnQuery = new dijit.form.Button({
		label: "<img src = '/static/image/icon/Tango/22/apps/utilities-dictionary.png')/>Query",
		showLabel: true,
		onClick: toolbarQuery
	});
	toolbar.addChild( btnQuery );

	var btnCloud = new dijit.form.Button({
		label: "<img src = '/static/image/icon/Tango/22/actions/check-spelling.png')/>Cloud Data",
		showLabel: true,
		onClick: showCloudDlg
	});
	toolbar.addChild( btnCloud );

	/*
	var btnTimeline = new dijit.form.Button({
		label: "<img src = '/static/image/icon/Tango/22/apps/office-chart.png')/>Timeline",
		showLabel: true,
		onClick: showTimeline
	});
	toolbar.addChild( btnTimeline );
	*/


	// remaining icons style: "float:right"

	var btnAbout = new dijit.form.Button({
		label: "<img src='/static/image/icon/gnome/22/actions/help-about.png'/>About",
		showLabel: true,
		style: "float:right",
		onClick: toolbarAbout
	});
	toolbar.addChild( btnAbout );


	var btnConfig = new dijit.form.Button({
		label: "<img src = '/static/image/icon/Tango/22/categories/utilities.png')/>Config",
		showLabel: true,
		style: "float:right",
		onClick: toolbarConfig		// config.js
	});
	toolbar.addChild( btnConfig );


	var btnUser = new dijit.form.Button({
		id: "toolbar-user",
		label: "<img src = '/static/image/icon/Tango/22/apps/preferences-users.png')/>",
		showLabel: true,
		style: "float:right",
		onClick: function() {
			if( dijit.byId( "dlg-logout" ) != undefined )
			{ dijit.byId( "dlg-logout" ).destroyRecursive(); }
			createLogout();
			showLogout();
		}
	});
	toolbar.addChild( btnUser );
} // createToolbar()

dojo.addOnLoad( createToolbar );

/*
var toolbarDateFilter = function()
{
	createDateFilter();
	showDateFilter();
}

var showDateFilter = function()
{
	dijit.byId( "datefilter" ).show();
}

var createDateFilter = function()
{
	var datefilterDlg = new dijit.Dialog({
		id: "datefilter",
		title: "Date period filter",
		style: "background-color: white;"
	});

	//hide the ordinary close button from the user...
  //dojo.style( datefilterDlg.closeButtonNode, "visibility", "hidden" );

	var datefilterContainer = dojo.create( "div", {
	//	style: "width: 410px; height: 290px; text-align: right; line-height: 24px; margin: 5px;"
		style: "width: 410px; height: 290px; clear: both; line-height: 24px; margin: 5px;"
	}, dojo.byId( "datefilter" ) );

	dojo.create( "div", { innerHTML: "Begin datum", style: "text-align: left" }, datefilterContainer );

	dojo.create( "div", { id: "begindatehook", style: "text-align: left" }, datefilterContainer );
	var beginvalue = dojo.date.locale.format( new Date( 1900, 0, 1 ), 
		{ selector: "date", format: "MMM dd, yyyy", locale: "nl" } );
	console.log( "beginvalue: " + beginvalue );
	var beginDate = new dijit.form.DateTextBox( {
		id: "begindate",
		value: new Date( 1900, 0, 1 )
	//	value: beginvalue
	}, dojo.byId( "begindatehook" ) );

	dojo.create( "div", { innerHTML: "<p>" }, datefilterContainer );

	dojo.create( "div", { innerHTML: "Eind datum", style: "text-align: left" }, datefilterContainer );

	dojo.create( "div", { id: "enddatehook", style: "text-align: left" }, datefilterContainer );
	var endDate = new dijit.form.DateTextBox( {
		id: "enddate",
		value: new Date( 1945, 11, 31 )
	}, dojo.byId( "enddatehook" ) );

	dojo.create( "div", { innerHTML: "<hr>", style: "clear: both" }, datefilterContainer );

	var buttonsNode = dojo.create( "div", {
		style: "text-align: right"
	}, datefilterContainer );

	dojo.place(( new dijit.form.Button({
	//  iconClass: "dijitEditorIcon dijitEditorIconCancel",
	//  label: "Close", 
		label: "<img src='/static/image/icon/Tango/16/actions/dialog-close.png'/>Close",
		title: "Close",
		text: "Close",
		showLabel: true,
		onClick: function() {
		//  dijit.byId( "datefilter" ).hide();
			dijit.byId( "datefilter" ).destroyRecursive();
		}
	})).domNode, buttonsNode );
}
*/

var toolbarSearch = function()
{
	createSearch();
	showSearch();
}


var toolbarQuery = function()
{
	createQueryDlg();		// query.js : this fills the querylistStore
//	updateQueryDlg();		// query.js : this fills the querylistStore
	dijit.byId( "dlg-query" ).show();
}


var toolbarAbout = function()
{
	createAbout();
	showAbout();
}

var showAbout = function()
{
	dijit.byId( "about" ).show();
}

var createAbout = function()
{
    var title =  "Texcavator - Collaborating Institutes";
    var style = "width: 420px; height: 420px; text-align: right; line-height: 24px; margin: 5px;"

	var dlgAbout = new dijit.Dialog({
		id: "about",
		title:title
	});

	dojo.style( dlgAbout.closeButtonNode, "visibility", "hidden" );	// hide the ordinary close button

	var container = dlgAbout.containerNode;

	var cpdiv = dojo.create( "div", { id: "cp-div" }, container );
	var aboutContainer = new dijit.layout.ContentPane({
		title: "About",
		style: style
	}, "cp-div" );

	dojo.create( "div", {
		innerHTML: "<a href='http://wahsp.nl' target='_blank'><img src='/static/image/logos/WAHSPlogo.png' height='48' align='left' /></a>",
		style: "clear: both"
	}, aboutContainer.domNode );

	// var innerHTML = "<a href='/static/BiLand_manual.pdf' target='_blank'>BiLand Manual</a>";
	var innerHTML = "<a href='/static/WAHSP_manual.pdf' target='_blank'>WAHSP/BiLand Manual</a>";

	dojo.create( "div", {
		innerHTML: innerHTML,
		style: "clear: both"
	}, aboutContainer.domNode );

	var client_timestamp = getClientTimestamp();		// timestamp.js
	var server_timestamp = getServerTimestamp();		// timestamp.js

	dojo.create( "div", { innerHTML: "Client timestamp: " + client_timestamp, style: "clear: both" }, aboutContainer.domNode );
	dojo.create( "div", { innerHTML: "Server timestamp: " + server_timestamp, style: "clear: both" }, aboutContainer.domNode );
	dojo.create( "div", { innerHTML: "<hr>", style: "clear: both" }, aboutContainer.domNode );

	dojo.create( "div", {
		innerHTML: "<a href='http://www.uva.nl' target='_blank'><img src='/static/image/logos/UvA.gif' height='50' align='left' /></a>",
		style: "clear: both"
	}, aboutContainer.domNode );
	dojo.create( "div", { innerHTML: "<hr>", style: "clear: both" }, aboutContainer.domNode );

	dojo.create( "div", {
		innerHTML: "<a href='http://www.uu.nl' target='_blank'><img src='/static/image/logos/UniversiteitUtrecht.gif' height='50' align='left' /></a>",
		style: "clear: both"
	}, aboutContainer.domNode );
	dojo.create( "div", { innerHTML: "<hr>", style: "clear: both" }, aboutContainer.domNode );

	dojo.create( "div", {
		innerHTML: "<a href='http://www.kb.nl' target='_blank'><img src='/static/image/logos/KB.gif' height='40' align='left' /></a>",
		style: "clear: both"
	}, aboutContainer.domNode );
	dojo.create( "div", { innerHTML: "<hr>", style: "clear: both" }, aboutContainer.domNode );

	dojo.create( "div", {
		innerHTML: "<a href='http://huygensinstituut.knaw.nl' target='_blank'><img src='/static/image/logos/HuygensInstituut.gif' height='30' align='left' /></a>",
		style: "clear: both"
	}, aboutContainer.domNode );

    dojo.create( "div", { innerHTML: "<hr>", style: "clear: both" }, aboutContainer.domNode );
    dojo.create( "div", {
        innerHTML: "<a href='http://staatsbibliothek-berlin.de/' target='_blank'><img src='/static/image/logos/StaatsbibliothekBerlin.png' height='40' align='left' /></a>",
        style: "clear: both"
    }, aboutContainer.domNode );

	var actionBar = dojo.create( "div", {
		className: "dijitDialogPaneActionBar",
		style: "height: 30px"
	}, container );

	var bClose = new dijit.form.Button({
		label: "<img src='/static/image/icon/Tango/16/actions/dialog-close.png'/> Close",
		showLabel: true,
		role: "presentation",
		onClick: function() { dijit.byId( "about" ).destroyRecursive(); }
	});
	actionBar.appendChild( bClose.domNode );
} // createAbout

// [eof]
