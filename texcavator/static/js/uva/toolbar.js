// FL-27-Jan-2012 Created
// FL-29-Nov-2013 Changed

dojo.require("dojo.data.ItemFileWriteStore");
dojo.require("dojo.date.locale");
dojo.require("dojo.i18n");
dojo.require("dojo.store.Memory");

dojo.require("dijit.Calendar");
dojo.require("dijit.Dialog");
dojo.require("dijit.Toolbar");
dojo.require("dijit.ToolbarSeparator");
dojo.require("dijit.Tooltip");
dojo.require("dijit.form.Button");
dojo.require("dijit.form.DateTextBox");
dojo.require("dijit.form.CheckBox");
dojo.require("dijit.form.ComboBox");
dojo.require("dijit.form.NumberSpinner");
dojo.require("dijit.form.RadioButton");
dojo.require("dijit.form.SimpleTextarea");
dojo.require("dijit.form.TextBox");
dojo.require("dijit.layout.ContentPane");
dojo.require("dijit.layout.TabContainer");

dojo.require("dojox.widget.Dialog");

/*
var storeDateLimits = function( min, max )
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

var minDate; // fixed minDate for project
var maxDate; // fixed maxDate for project
var beginDate; // changable beginDate (via filters/slider)
var endDate; // changable endDate (via filters/slider)
var beginDate2; // changable, optional beginDate2 (via filters/slider)
var endDate2; // changable, optional endDate2 (via filters/slider)


// Stores project min/max date in global variables, sets constraints/defaults on filters
var storeDateLimits = function(min, max) {
	// Set global variables
	minDate = new Date(min);
	maxDate = new Date(max);
	beginDate = minDate;
	endDate = maxDate;

	// Update filter constraints/defaults
	dijit.byId("begindate").set("constraints", {
		min: minDate,
		max: maxDate
	});
	dijit.byId("enddate").set("constraints", {
		min: minDate,
		max: maxDate
	});
	dijit.byId("begindate-2").set("constraints", {
		min: minDate,
		max: maxDate
	});
	dijit.byId("enddate-2").set("constraints", {
		min: minDate,
		max: maxDate
	});
	dijit.byId("begindate").set("value", minDate);
	dijit.byId("enddate").set("value", maxDate);
}; // storeDateLimits()


// Converts a string (YYYY-MM-DD) into a Date
function stringToDate(strDate) {
	var dateParts = strDate.split("-");
	return new Date(dateParts[0], (dateParts[1] - 1), dateParts[2]);
}

// Converts a Date into YYYYMMDD (from http://stackoverflow.com/a/3067896/3710392)
var toDateString = function(date) {
	var yyyy = date.getFullYear().toString();
	var mm = (date.getMonth() + 1).toString(); // getMonth() is zero-based
	var dd = date.getDate().toString();
	return yyyy + (mm[1] ? mm : "0" + mm[0]) + (dd[1] ? dd : "0" + dd[0]); // padding
}; // toDateString()


var getDate_Begin_Str = function() {
	var bds = toDateString(beginDate);
	return bds.substring(0, 4) + '-' + bds.substring(4, 6) + '-' + bds.substring(6, 8);
};


var getDate_End_Str = function() {
	var eds = toDateString(endDate);
	return eds.substring(0, 4) + '-' + eds.substring(4, 6) + '-' + eds.substring(6, 8);
};


var getDateBeginStr = function() {
	return toDateString(beginDate);
};


var getDateEndStr = function() {
	return toDateString(endDate);
};


var getDateRangeString = function() {
	return getDateBeginStr() + ',' + getDateEndStr();
};


var getBeginDate = function() {
	return beginDate;
};


var getEndDate = function() {
	return endDate;
};


var createToolbar = function() {
	var toolbar = new dijit.Toolbar({
		style: "height: 26px;"
	}, "span-toolbar"); // id="span-toolbar" in base.html

	// Search dates
	var btnDateFilterBegin = new dijit.form.Button({
		label: "<img src = '/static/image/icon/Tango/22/apps/office-calendar.png')/>Search period: from",
		showLabel: true,
		disabled: true
	});

	var beginDateTB = new dijit.form.DateTextBox({
		id: "begindate",
		style: "width: 90px;",
		onChange: function() {
			if (beginDateTB.value !== undefined && endDateTB.value !== undefined)
			{
				// Set the global beginDate variable
				beginDate = beginDateTB.value;

				// set new min constraint for endDateTB
				require(["dojo/date"], function(date) {
					endDateTB.constraints.min = date.add(beginDateTB.value, "day", 1);
				});

				// Update the slider
				updateYearSlider(beginDateTB.value, endDateTB.value);
			}
		}
	});

	var btnDateFilterEnd = new dijit.form.Button({
		label: "to",
		showLabel: true,
		disabled: true
	});

	var endDateTB = new dijit.form.DateTextBox({
		id: "enddate",
		style: "width: 90px;",
		onChange: function() {
			if (beginDateTB.value !== undefined && endDateTB.value !== undefined)
			{
				// Set the global endDate variable
				endDate = endDateTB.value;

				// Set new max constraint for beginDateTB
				require(["dojo/date"], function(date) {
					beginDateTB.constraints.max = date.add(endDateTB.value, "day", -1);
				});

				// Update the slider
				updateYearSlider(beginDateTB.value, endDateTB.value);
			}
		}
	});

	// Optional second search date
	var btnDateFilterBegin2 = new dijit.form.Button({
		label: "and from",
		style: "display: none;",
		showLabel: true,
		disabled: true
	});

	var beginDateTB2 = new dijit.form.DateTextBox({
		id: "begindate-2",
		style: "width: 90px; display: none;",
		onChange: function(value) {
			if (beginDateTB2.value !== undefined && endDateTB2.value !== undefined)
			{
				// Set the global beginDate2 variable
				beginDate2 = value;

				// set new min constraint for endDateTB2
				require(["dojo/date"], function(date) {
					endDateTB2.constraints.min = date.add(value, "day", 1);
				});

				// Update the slider
				updateYearSlider(value, endDateTB2.value, "-2");
			}
		}
	});

	var btnDateFilterEnd2 = new dijit.form.Button({
		label: "to",
		style: "display: none;",
		showLabel: true,
		disabled: true
	});

	var endDateTB2 = new dijit.form.DateTextBox({
		id: "enddate-2",
		style: "width: 90px; display: none;",
		onChange: function(value) {
			if (beginDateTB2.value !== undefined && endDateTB2.value !== undefined)
			{
				// Set the global endDate2 variable
				endDate2 = value;

				// Set new max constraint for beginDateTB2
				require(["dojo/date"], function(date) {
					beginDateTB2.constraints.max = date.add(value, "day", -1);
				});

				// Update the slider
				updateYearSlider(beginDateTB2.value, value, "-2");
			}
		}
	});

	var toggleBtn = new dijit.form.Button({
		id: "toggleBtn",
		label: "<img src='/static/image/icon/Tango/22/actions/list-add.png')/>",
		// On click, toggle the second date selection filters and the slider
		onClick: toggleSecondDateFilter
	});

	toolbar.addChild(btnDateFilterBegin);
	toolbar.addChild(beginDateTB);
	toolbar.addChild(btnDateFilterEnd);
	toolbar.addChild(endDateTB);

	toolbar.addChild(toggleBtn);
	toolbar.addChild(btnDateFilterBegin2);
	toolbar.addChild(beginDateTB2);
	toolbar.addChild(btnDateFilterEnd2);
	toolbar.addChild(endDateTB2);

	toolbar.addChild(new dijit.ToolbarSeparator({
		id: "sep"
	}));

	var btnQuery = new dijit.form.Button({
		label: "<img src='/static/image/icon/Tango/22/actions/document-save.png')/>Export",
		showLabel: true,
		onClick: toolbarQuery
	});

	var btnCloud = new dijit.form.Button({
		label: "<img src='/static/image/icon/Tango/22/actions/check-spelling.png')/>Cloud Data",
		showLabel: true,
		onClick: showCloudDlg
	});

	// remaining icons style: "float:right"

	var btnAbout = new dijit.form.Button({
		label: "<img src='/static/image/icon/gnome/22/actions/help-about.png' />About",
		showLabel: true,
		style: "float:right",
		onClick: toolbarAbout
	});

	var btnConfig = new dijit.form.Button({
		label: "<img src='/static/image/icon/Tango/22/categories/system.png' />Config",
		showLabel: true,
		style: "float:right",
		onClick: showConfig // config.js
	});

	var btnUser = new dijit.form.Button({
		id: "toolbar-user",
		label: "<img src='/static/image/icon/Tango/22/actions/application-exit.png' />Logout",
		showLabel: true,
		style: "float:right",
		onClick: function() {
			if (dijit.byId("dlg-logout") !== undefined) {
				dijit.byId("dlg-logout").destroyRecursive();
			}
			createLogout();
			showLogout();
		}
	});

	toolbar.addChild(btnQuery);
	toolbar.addChild(btnCloud);
	// The order below is in reverse because of the "float:right" style above (probably).
	toolbar.addChild(btnUser);
	toolbar.addChild(btnAbout);
	toolbar.addChild(btnConfig);
}; // createToolbar()

dojo.addOnLoad(createToolbar);


var toggleSecondDateFilter = function() {
	// On click, toggle the second date selection filters and the slider
	// TODO: This uses jQuery... as that's far more easy.
	var toggleDiv = $("#toggleBtn").parent().parent();
	toggleDiv.nextUntil($("#sep")).toggle();
	$("#year-range-slider-2").toggle();

	// If toggled hidden, set variables to undefined  
	if (beginDate2) {
		beginDate2 = undefined;
		endDate2 = undefined;
		dijit.byId("toggleBtn").set("label", "<img src='/static/image/icon/Tango/22/actions/list-add.png')/>");
	}
	// If toggled visible, set default min/max values
	else {
		beginDate2 = minDate;
		endDate2 = maxDate;
		dijit.byId("begindate-2").set("value", minDate);
		dijit.byId("enddate-2").set("value", maxDate);
		dijit.byId("toggleBtn").set("label", "<img src='/static/image/icon/Tango/22/actions/list-remove.png')/>");
	}
}


var toolbarQuery = function() {
	createQueryDlg(); // query.js : this fills the querylistStore
	dijit.byId("dlg-query").show();
};


var toolbarAbout = function() {
	createAbout();
	showAbout();
};


var showAbout = function() {
	dijit.byId("about").show();
};


var createAbout = function() {
	var title = "Texcavator - Collaborating Institutes";
	var style = "width: 420px; height: 420px; text-align: right; line-height: 24px; margin: 5px;";

	var dlgAbout = new dijit.Dialog({
		id: "about",
		title: title
	});

	dojo.style(dlgAbout.closeButtonNode, "visibility", "hidden"); // hide the ordinary close button

	var container = dlgAbout.containerNode;

	var cpdiv = dojo.create("div", {
		id: "cp-div"
	}, container);
	var aboutContainer = new dijit.layout.ContentPane({
		title: "About",
		style: style
	}, "cp-div");

	dojo.create("div", {
		innerHTML: "<a href='http://wahsp.nl' target='_blank'><img src='/static/image/logos/WAHSPlogo.png' height='48' align='left' /></a>",
		style: "clear: both"
	}, aboutContainer.domNode);

	// var innerHTML = "<a href='/static/BiLand_manual.pdf' target='_blank'>BiLand Manual</a>";
	var innerHTML = "<a href='/static/WAHSP_manual.pdf' target='_blank'>WAHSP/BiLand Manual</a>";

	dojo.create("div", {
		innerHTML: innerHTML,
		style: "clear: both"
	}, aboutContainer.domNode);

	dojo.create("div", {
		innerHTML: "<hr>",
		style: "clear: both"
	}, aboutContainer.domNode);

	dojo.create("div", {
		innerHTML: "<a href='http://www.uva.nl' target='_blank'><img src='/static/image/logos/UvA.gif' height='50' align='left' /></a>",
		style: "clear: both"
	}, aboutContainer.domNode);
	dojo.create("div", {
		innerHTML: "<hr>",
		style: "clear: both"
	}, aboutContainer.domNode);

	dojo.create("div", {
		innerHTML: "<a href='http://www.uu.nl' target='_blank'><img src='/static/image/logos/UniversiteitUtrecht.gif' height='50' align='left' /></a>",
		style: "clear: both"
	}, aboutContainer.domNode);
	dojo.create("div", {
		innerHTML: "<hr>",
		style: "clear: both"
	}, aboutContainer.domNode);

	dojo.create("div", {
		innerHTML: "<a href='http://www.kb.nl' target='_blank'><img src='/static/image/logos/KB.gif' height='40' align='left' /></a>",
		style: "clear: both"
	}, aboutContainer.domNode);
	dojo.create("div", {
		innerHTML: "<hr>",
		style: "clear: both"
	}, aboutContainer.domNode);

	dojo.create("div", {
		innerHTML: "<a href='http://huygensinstituut.knaw.nl' target='_blank'><img src='/static/image/logos/HuygensInstituut.gif' height='30' align='left' /></a>",
		style: "clear: both"
	}, aboutContainer.domNode);

	dojo.create("div", {
		innerHTML: "<hr>",
		style: "clear: both"
	}, aboutContainer.domNode);
	dojo.create("div", {
		innerHTML: "<a href='http://staatsbibliothek-berlin.de/' target='_blank'><img src='/static/image/logos/StaatsbibliothekBerlin.png' height='40' align='left' /></a>",
		style: "clear: both"
	}, aboutContainer.domNode);

	var actionBar = dojo.create("div", {
		className: "dijitDialogPaneActionBar",
		style: "height: 30px"
	}, container);

	var bClose = new dijit.form.Button({
		label: "<img src='/static/image/icon/Tango/16/actions/dialog-close.png'/> Close",
		showLabel: true,
		role: "presentation",
		onClick: function() {
			dijit.byId("about").destroyRecursive();
		}
	});
	actionBar.appendChild(bClose.domNode);
}; // createAbout


// Basic validation of dates.
function validateDates() {
	if (dijit.byId("begindate").value == undefined || dijit.byId("enddate").value == undefined ||
		dijit.byId("begindate-2").value == undefined || dijit.byId("enddate-2").value == undefined) 
	{
		var message = 'You entered an invalid date range. Please check your date filters.'
        genDialog('Invalid date range', message, {OK: true});
		return false;
	}
	return true;
}