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

	// Use the false flag to prevent onChange from firing (hence setting the global variables above)
	// Also, we should temporarily set intermediateChanges to false, otherwise the onChange still fires.
	// See https://bugs.dojotoolkit.org/ticket/17361 for details.
	bDate = dijit.byId("begindate");
	bDate.set("intermediateChanges", false);
	bDate.set("value", dateStart, false);
	bDate.set("intermediateChanges", true);

	eDate = dijit.byId("enddate");
	eDate.set("intermediateChanges", false);
	eDate.set("value", dateEnd, false);
	eDate.set("intermediateChanges", true);

	if (beginDate2 !== undefined) {
		toggleSecondDateFilter();
	}
}
