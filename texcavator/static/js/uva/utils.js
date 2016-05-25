// startsWith to check if a string starts with a particular character sequence
String.prototype.startsWith = function (str) {
	return this.match( "^" + str ) == str;
};

// endsWith to check if a string ends with a particular character sequence
String.prototype.endsWith = function (str) { 
	return this.match( str + "$" ) == str;
};

function isWhitespaceOrEmpty( text ) {
	return !/[^\s]/.test( text );
}

// Sets the begindate and enddate filters and sets the globale variables
function setDateFilters(dateStart, dateEnd) {
	beginDate = dateStart;
	endDate = dateEnd;

	// Use the false flag to prevent onChange from firing
	// (hence setting the global variables above)
	dijit.byId("begindate").set("value", dateStart, false);
	dijit.byId("enddate").set("value", dateEnd, false);

	if (beginDate2 !== undefined) {
		toggleSecondDateFilter();
	}
}
