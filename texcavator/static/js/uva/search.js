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
				displaySearchResults(data.hits, newStartRecord, params.maximumRecords);
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


// Turns ElasticSearch hits into HTML
function displaySearchResults(hits, start_record, chunk_size) {
	var hits_total = hits.total;
	var hits_max_score = hits.max_score;
	var hits_list = hits.hits;

	var html_str = '';
	
	if (hits_list.length !== hits_total) {  // did not get everything
		html_str += paging_links(start_record, chunk_size, hits_total);
	}

	if (hits_total === 0 || !hits_max_score) {  // no results found OR not sorting on score
		html_str += '<p>Found ' + hits_total + ' records.</p>';
	}
	else {
		html_str += '<p>Found ' + hits_total + ' records, ';
		html_str += 'max score = ' + hits_max_score.toFixed(2) + '.</p>';
	}

	html_str += '<ol start="' + start_record + '">';

	for (var i = 0; i < hits_list.length; i++) {
		var hit = hits_list[i];

		var article_dc_title = hit.fields.article_dc_title[0];
		var paper_dcterms_temporal = hit.fields.paper_dcterms_temporal[0];
		var paper_dcterms_spatial = hit.fields.paper_dcterms_spatial[0];
		var paper_dc_title = hit.fields.paper_dc_title[0];
		var paper_dc_date = hit.fields.paper_dc_date[0];

		var item_str = '<li id="' + hit._id + '">';
		item_str += '<a href="javascript:retrieveRecord(\'' + hit._id + '\');" title="' + article_dc_title + '">';

		// limit displayed title length
		if (article_dc_title.length > 45) {
			item_str += '<b>' + article_dc_title.substring(0, 45) + '</b>...</a>';
		}
		else {
			item_str += '<b>' + article_dc_title + '</b></a>';
		}

		item_str += '<br>' + paper_dc_title;
		item_str += '<br>' + paper_dc_date;

		if (paper_dcterms_temporal !== "") {
			item_str += ', ' + paper_dcterms_temporal;
		}
		if (paper_dcterms_spatial !== "") {
			item_str += ', ' + paper_dcterms_spatial;
		}

		if (hit._score) {
			item_str += ' [score: ' + hit._score.toFixed(2) + ']';
		}
			
		item_str += '</li>';
		html_str += item_str;
	}

	html_str += '</ol>';
	html_str += paging_links(start_record, chunk_size, hits_total);
	html_str += '<a href="#search">Back to top</a>';

	dojo.byId( "search-result" ).innerHTML = html_str;
}

function paging_links(start_record, chunk_size, hits_total) {
	have_prev = start_record > 1;
	have_next = start_record + chunk_size < hits_total;

	href_prev = '<a href="javascript:nextResults(-' + chunk_size + ');">previous</a>';
	href_next = '<a href="javascript:nextResults(+' + chunk_size + ');">next</a>';

	result = '<span style="float:right">';
	if (have_prev && have_next) {
		result += href_prev + ' | ' + href_next;
	}
	else if (have_prev) {
		result += href_prev;
	}
	else if (have_next) {
		result += href_next;
	}
	result += '</span>';

	return result;
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