dojo.require("dijit.ProgressBar");

// HTML search result in Search panel of accordion (TODO: move this and everything below somewhere else?)
function searchSubmit(newStartRecord)
{
	// Hide the search help
	$("#search_help").hide();

	// Select the searchPane
	accordionSelectChild( "searchPane" );

	// Set the new start record, if set
	newStartRecord = typeof newStartRecord !== 'undefined' ? newStartRecord : 1;
	dojo.byId('startRecord').value = newStartRecord;

	var query = dojo.byId( "query" ).value.trim();
	if (query === "")
	{
		console.log( "searchSubmit(): empty query: nothing to do." );
		return;
	}

	// toolbar.js
	if (!validateDates()) {
		console.log('searchSubmit(): invalid date range.');
		return;
	}
	
	// sanitize_query.js
	if (!validateQuery(query)) {
		console.log('searchSubmit(): invalid query.');
		return;
	}

	console.log( "Starting search at record " + newStartRecord );
	dojo.place( new dijit.ProgressBar( { indeterminate: true } ).domNode, dojo.byId( "search-result" ), "only" );

	var params = getSearchParameters();        // get user-changeable parameters from config
	params.query = query;
	params.startRecord = newStartRecord;

	dojo.xhrGet({
		url: "services/search",
		content: params,
		handleAs: "json",
		load: function( data ) {
			if( data.status === "error" ){
				dojo.byId( "search-result" ).innerHTML = "";
				console.error( data.msg );
				var title = "Query invalid";
				var buttons = { "OK": true };
				genDialog( title, data.msg, buttons );
				return;
			} else {
				dojo.byId( "search-result" ).innerHTML = data.html; // put html text in panel
				metadataGraphics( itemFromCurrentQuery() );         // Visualise metadata
			}
		},
		error: function( err ) {
			console.error( err );  // display the error
			var title = "An error occurred";
			var buttons = { "OK": true };
			genDialog( title, err.message, buttons );
			dojo.byId( "search-result" ).innerHTML = '<div>' + title + '.</div>';
		}
	});
}


/**
 * Starts a search (called from the ShiCo iframe)
 * - Sets the date filters to the first and last day of the given year
 * - Sets the given keyword on the query input element
 * - Starts the search
 */
function startSearch(keyword, year)
{
	setDateFilters(new Date(year, 0, 1), new Date(year, 11, 31));
	$('#query').val(keyword);
	searchSubmit();
}


function searchReset() {
	dijit.byId("query").set("value", "");
	storeDateLimits( "{{ PROJECT_MIN_DATE }}", "{{ PROJECT_MAX_DATE }}" );
}


function researchSubmit( item )
{
	console.log( "researchSubmit()" );
	dojo.place( new dijit.ProgressBar( { indeterminate: true } ).domNode, dojo.byId( "search-result" ), "only" );

	setQueryMetadata(item);

	searchSubmit();
} // researchSubmit()


function nextResults( amount )
{
	if ( dojo.byId( "query" ).value === "" ) { 
		return;		// nothing to do
	}

	var oldStartRecord = parseInt( dojo.byId( 'startRecord' ).value );
	var newStartRecord = oldStartRecord + amount;
	if ( newStartRecord < 1 ) {
		newStartRecord = 1;
	}

	searchSubmit(newStartRecord);		// HTML search result in Search panel of accordion
}