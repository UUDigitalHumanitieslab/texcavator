// FL-27-Mar-2013 Created
// FL-10-Sep-2013 Changed

/*
	function collection_fromradio()
	function accordionSelectChild( id )
	function createQueryLine( item )
	function createQueryList()
	function refreshQueriesDocCounts()
	function updateQueryDocCounts( item )
	function updateQueryDocCountsElasticSearch( item )
	function updateQueryDocCountsMongoDB( item )
*/

dojo.require( "dojo.store.JsonRest" );
dojo.require( "dojox.form.RangeSlider" );


function collection_fromradio()
{
	if( getDualMode() == false )
	{ var collection = XTAS_COLLECTION; }		// default collection name
	else
	{
		var radio1 = dijit.byId( "radioCollOne" );
		if( radio1 == undefined )
		{ var collection = XTAS_COLLECTION; }		// default collection name
		else
		{
			if( radio1.checked == true )
			{ var collection = ES_INDEX_KONBIB; }
			else
			{ var collection = ES_INDEX_STABI; }
		}
	}
	return collection
}


function accordionSelectChild( id )
{
	// how to select accordion child?
	var accordion = dijit.byId( "leftAccordion" );
	var selected_child = accordion.get( "selectedChildWidget" );
	if( selected_child.id !== id ) { accordion.back(); }	// show Search pane
} // accordionSelectChild()


function createYearSlider( SRU_DATE_LIMITS )
{
//	console.log( "createYearSlider()" );

	storeDateLimits( SRU_DATE_LIMITS );

	var min_date = getBeginDate();
	var max_date = getEndDate();
//	console.log( "from: " + min_date  + " to: " + max_date );

	var min_year = min_date.getFullYear();
	var max_year = max_date.getFullYear();
//	console.log( "from: " + min_year  + " to: " + max_year );

	var discrete_values = max_year - min_year + 1;
//	console.log( "discrete_values: " + discrete_values );

	var rangeSlider = new dojox.form.HorizontalRangeSlider({
		id                  : "year-range-slider",
		value               : [ min_year, max_year ],
		minimum             : min_year,
		maximum             : max_year,
		intermediateChanges : false,
		discreteValues      : discrete_values,
		onChange            : function( value )
		{
		//	console.log( "value:" + value );

			var new_min_year = Math.ceil(  value[ 0 ] );
			var new_max_year = Math.floor( value[ 1 ] );
		//	console.log( "from: " + new_min_year  + " to: " + new_max_year );

			var old_min_date = getBeginDate();
			var old_max_date = getEndDate();
		//	console.log( "old from: " + old_min_date + ", to: " + old_max_date );
			var old_min_year = old_min_date.getFullYear();
			var old_max_year = old_max_date.getFullYear();

			var min_month = old_min_date.getMonth();
			var max_month = old_max_date.getMonth();

			var min_day   = old_min_date.getDate();
			var max_day   = old_max_date.getDate();

		//	console.log( "from: year: " + old_min_year + ", month: " + min_month + ", day: " + min_day );
		//	console.log( "to: year:   " + old_max_year + ", month: " + max_month + ", day: " + max_day );

			var new_min_date = new Date( new_min_year, min_month, min_day );
			var new_max_date = new Date( new_max_year, max_month, max_day );

			// update date widgets in toolbar
			dijit.byId( "begindate" ).set( "value", new_min_date );
			dijit.byId( "enddate"   ).set( "value", new_max_date );
		}
	}, "div-year-range-slider" );

	// create legend for year slider range
	var min_date = SRU_DATE_LIMITS[ 0 ].toString();
	var max_date = SRU_DATE_LIMITS[ 1 ].toString();

	// parseInt with radix 10 to prevent trouble with leading 0's (octal, hex)
	// substring: from index is included, to index is not included
	var min_year = parseInt( min_date.substring( 0, 4 ), 10 );
	var max_year = parseInt( max_date.substring( 0, 4 ), 10 );

	var legend = '<span style="float:left">'   + min_year + '</span>'
	legend    += '<span style="float:center">' + "search period" + '</span>'
	legend    += '<span style="float:right">'  + max_year + '</span><hr>'

	dojo.create( "label", { innerHTML: legend }, "div-year-range-legend" );
} // createYearSlider()


function updateYearSlider( min_date, max_date )
{
//	console.log( "updateYearSlider()" );
	// we get here from the toolbar date widgets
	var min_year = min_date.getFullYear();
	var max_year = max_date.getFullYear();
//	console.log( "from: " + min_year  + " to: " + max_year );
	dijit.byId( "year-range-slider" ).set( "value", [ min_year, max_year] );
}

// the "btn-sq-fetch-" button becomes dead with Dojo-1.9.0
// strangely, the other queryline buttons do work with Dojo-1.9.0
function createQueryLine( item )
{
//	console.log( "createQueryLine() " + lexiconTitle );
	var lexiconTitle = item[ "fields" ][ "title" ];
	var query_string = item[ "fields" ][ "query" ];
//	console.log( query_string );

	if( ! lexiconTitle.endsWith( "_daterange" ) )	// do not show lexicons with *_daterange names
	{
		var pk = item[ "pk" ];
		var itemNode = dojo.byId( "query-" + item.pk );
		var string = "<span id=query-string-" + item.pk + " />" + lexiconTitle + " <em> " + item[ "fields" ][ "created" ] + " </em> </span>";
		var params = { style: 'clear: both;' };
		dojo.html.set( itemNode, string, params );
		var buttonsNode = dojo.create( 'span', { style: 'float:right;' }, itemNode );

		var btn = null;
		var debug_destroy = false;

	//	console.log( "Button retrieve lexicon metadata+ocrdata" );
		btn = dijit.byId( "btn-sq-fetch-" + item.pk );
		if( btn != null )
		{
			if( debug_destroy ) { console.error( "btn-sq-fetch button already exists" ); }
			btn.destroy();
		}

		config = getConfig();
		var datastore = config[ "datastore" ];
		if( datastore === "DSTORE_ELASTICSEARCH" )		// re-search; no download of KB articles
		{
			console.log( "Re-search" );

			dojo.place(( new dijit.form.Button({
				id: "btn-sq-fetch-" + item.pk,
				disabled: fetch_disabled,
				label: "Basis lexicon",
				showLabel: false,
				title: "Re-search: " + lexiconTitle,
				pk: item.pk,
				iconClass: "dijitIconNewTask",
				onClick: function() {
					console.log( "Re-search" );
					researchSubmit( item );
				}
			})).domNode, buttonsNode );
		}
		else				// download of KB articles
		{
			console.log( "Download" );

			if( glob_key_validated == false )
			{ var fetch_disabled = true; }
			else
			{ var fetch_disabled = false; }

			dojo.place(( new dijit.form.Button({
				id: "btn-sq-fetch-" + item.pk,
				disabled: fetch_disabled,
				label: "Basis lexicon",
				showLabel: false,
				title: "Create basis lexicon: " + lexiconTitle,
				pk: item.pk,
				iconClass: "dijitIconNewTask",
				onClick: function() { fetchDataDialog( item ); }	// lexicon.js: calls onClickLoadData()
			})).domNode, buttonsNode );
		}

	//	console.log( "Button cloud for lexicon item" );
		btn = dijit.byId( "btn-sq-cloud-" + item.pk );
		if( btn != null )
		{
			if( debug_destroy ) { console.error( "btn-sq-cloud button already exists" ); }
			btn.destroy();
		}

		if( glob_key_validated == false )
		{ var cloud_disabled = true; }
		else
		{ var cloud_disabled = false; }

		dojo.place(( new dijit.form.Button({
			id: "btn-sq-cloud-" + item.pk,
			disabled: cloud_disabled,
			label: "Apply",
			showLabel: false,
			title: "Apply query: " + item[ "fields" ][ "query" ],
			query: item[ "fields" ][ "query" ],
			pk: item.pk,
			iconClass: "dijitIconSearch",
			onClick: function() { onClickExecute( item.pk, this.query ); }
		})).domNode, buttonsNode );


	//	console.log( "Button timeline for lexicon item" );
		btn = dijit.byId( "btn-sq-timeline-" + item.pk );
		if( btn != null )
		{
			if( debug_destroy ) { console.error( "btn-sq-timeline button already exists" ); }
			btn.destroy();
		}

		if( glob_key_validated == false )
		{ var timeline_disabled = true; }
		else
		{ var timeline_disabled = false; }

		// timeline for lexicon item

		dojo.place(( new dijit.form.Button({
			id: "btn-sq-timeline-" + item.pk,
			disabled: timeline_disabled,
			label: "Timeline",
			showLabel: false,
			title: "Timeline",
			iconClass: "dijitIconChart",
			pk: item.pk,
			onClick: function() {
				var collection = collection_fromradio();
				showTimeline( this.pk, lexiconTitle, query_string, collection );	// timeline.js
			}
		})).domNode, buttonsNode );


	//	console.log( "Button update for lexicon item" );
		btn = dijit.byId( "btn-sq-modify-" + item.pk );
		if( btn != null )
		{
			if( debug_destroy ) { console.error( "btn-sq-modify button already exists" ); }
			btn.destroy();
		}

		dojo.place(( new dijit.form.Button({
			id: "btn-sq-modify-" + item.pk,
			label: "Modify",
			showLabel: false,
			title: "Modify",
			iconClass: "dijitIconSave",
			pk: item.pk,
			onClick: function() { updateItemInLexicon( this.pk ).then( createQueryList ); }
		})).domNode, buttonsNode );


	//	console.log( "Button delete for lexicon item" );
		btn = dijit.byId( "btn-sq-delete-" + item.pk );
		if( btn != null )
		{
			if( debug_destroy ) { console.error( "btn-sq-delete button already exists" ); }
			btn.destroy();
		}

		// lexiconStore.remove() -> // HTTP DELETE
		dojo.place(( new dijit.form.Button({
			id: "btn-sq-delete-" + item.pk,
			label: "Delete",
			showLabel: false,
			title: "Delete",
			iconClass: "dijitIconDelete",
			pk: item.pk,
			onClick: function() { lexiconStore.remove( this.pk ).then( createQueryList ); }
		})).domNode, buttonsNode );
	}
} // createQueryLine()



function createQueryList()
{
	console.log( "createQueryList()" );
//	console.log( "username: " + glob_username );

	// show busy indicator over Accordion, because reading the article counts takes a while
//	var standby = new dojox.widget.Standby({
//		target: dijit.byId( "leftAccordion" ).domNode,
//		centerIndicator: "image",		// "text" or "image"
//		text: "Reading Lexicons..."
//	});
//	document.body.appendChild( standby.domNode );
//	standby.startup();
//	standby.show();


	dojo.place( new dijit.ProgressBar( { indeterminate: true }).domNode, dojo.byId( "lexiconItems" ), "only" );
	var query_params = "?username=" + glob_username;

	lexiconStore.query( query_params ).then( function( response )			// HTTP GET
	{
		var status = response[ "status" ];
		if( status !== "SUCCESS" )
		{
			var msg = "We could not read the lexicons:<br/>" + response[ "msg" ];
			var dialog = new dijit.Dialog({
				title: "Lexicons",
				style: "width: 300px",
				content: msg
			});
			dialog.show();
		}

		dojo.empty( dojo.byId( "lexiconItems" ) );	// this does not delete the buttons!, memory leak: 
		// see: http://higginsforpresident.net/2010/01/widgets-within-widgets/

		var items = JSON.parse( response[ "lexicon_items" ] );
		glob_lexiconData = items;

		dojo.forEach( items, function( item )
		{
			// create the divs for the saved queries
			var itemNode = dojo.create( 'div',
			{
				id: "query-" + item.pk,
				innerHTML: "",				// title, counts & date are added later
				style: 'clear: both;'
			}, dojo.byId( "lexiconItems" ) );
		});

		dojo.forEach( items, function( item )
		{ createQueryLine( item ); });		// title, date, buttons

		refreshQueriesDocCounts();			// refresh doc counts, enable/disable buttons

	//	standby.hide();						// hide the busy indicator
		return response;
	});
} // createQueryList()



function refreshQueriesDocCounts()
{
	// get collection setting from radio buttons
	var collection = collection_fromradio();

	console.log( "refreshQueriesDocCounts() " + collection );
	items = glob_lexiconData;

	if( glob_key_validated == true )
	{
		console.log( "key validated" ); 
		dojo.forEach( items, function( item )
		{ updateQueryDocCounts( item, collection ); });
	}
	else
	{ console.log( "key not validated" ); }
} // refreshQueriesDocCounts()



function updateQueryDocCounts( item, collection )
{
	config = getConfig();
	if( config[ "datastore" ] === "DSTORE_ELASTICSEARCH" )
	{ updateQueryDocCountsElasticSearch( item, collection ); }
	else
	{ updateQueryDocCountsMongoDB( item ); }
} // updateQueryDocCounts()


function updateQueryDocCountsElasticSearch( item, collection )
{
	// documents counts (identical for ocr & metadata) from ElasticSearch

	// http://zookst18.science.uva.nl:8001/services/doc_count/?lexiconID=1&dateRange=18500101,19451231&datastore=DSTORE_ELASTICSEARCH
	var lexiconTitle = item[ "fields" ][ "title" ];
	if( ! lexiconTitle.endsWith( "_daterange" ) )	// do not show lexicons with *_daterange names
	{
		var pk =  item[ "pk" ];
	//	console.log( "updateQueryDocCountsElasticSearch() " + pk );

		var url = SUB_SITE + "services/doc_count/";

		var params = getSearchParameters();			// from config

		params [ "lexiconID" ]  = pk;
		params [ "collection" ] = collection;
		params [ "datastore" ]  = "DSTORE_ELASTICSEARCH";

		dojo.xhrGet({
			url: url,
			content : params,
			handleAs: "json",
			load: function( resp )
			{
				if( resp == null )
				{ console.error( "updateQueryDocCountsElasticSearch(): " + url + " null response" ); }
				else if( resp.status === "ok" )
				{
					doc_count = resp.doc_count;
					config = getConfig();
					if( config[ "datastore" ] === "DSTORE_ELASTICSEARCH" )	// no metadata in Django DB
					{ var counts_str = " [" + doc_count + "] "; }
					else
					{ var counts_str = ""; }
				//	console.log( counts_str );

					var cspan = dojo.byId( "query-string-" + pk );
					if( cspan != null )
					{
						var html = "<span id=query-string-" + item.pk + " />" + lexiconTitle + counts_str + "<em> " + item[ "fields" ][ "created" ] + " </em> </span>";
						cspan.innerHTML = html;

						var btn_sq_cloud = dijit.byId( "btn-sq-cloud-" + pk );
						var btn_sq_timeline = dijit.byId( "btn-sq-timeline-" + pk );
						if( doc_count == 0 )
						{
							btn_sq_cloud.set( "disabled", true );		// disable cloud button
							btn_sq_timeline.set( "disabled", true );	// disable timeline button
						}
						else
						{
							btn_sq_cloud.set( "disabled", false );		// enable cloud button
							btn_sq_timeline.set( "disabled", false );	// enable timeline button
						}
					}
				}
				else
				{
					console.log( resp );
					console.error( "updateQueryDocCountsElasticSearch(): " + url + " response status: " + resp.status );
					var title = "updateQueryDocCountsElasticSearch failed";
					var msg = "Query with title:<br/><b>" + lexiconTitle + "</b><br/>" + resp.msg;
					var buttons = { "OK": true };
					genDialog( title, msg, buttons );
				}
			},
			error: function( err )
			{
				console.error( err );
				var title = "updateQueryDocCountsElasticSearch failed";
				var buttons = { "OK": true };
				genDialog( title, err, buttons );
				return err;
			}
		});
	}
} // updateQueryDocCountsElasticSearch()


function updateQueryDocCountsMongoDB( item )
{
	// ocr counts from MongoDB, metadata counts from DjangoDB
	var lexiconTitle = item[ "fields" ][ "title" ];
//	console.log( "updateQueryDocCountsMongoDB() " + lexiconTitle );

	if( ! lexiconTitle.endsWith( "_daterange" ) )	// do not show lexicons with *_daterange names
	{
		var pk =  item[ "pk" ];
		var url = SUB_SITE + "list/" + pk + "/docs/";

		dojo.xhrGet({
			url: url,
			handleAs: "json",
			sync: false,				// sync no longer needed; get correct div by id
			load: function( resp )
			{
				if( resp == null )
				{ console.error( "updateQueryDocCountsMongoDB(): " + url + " null response" ); }
				else if( resp.status === "SUCCESS" )
				{
					var metadata_count = resp.metadata;
					var ocrdata_count  = resp.ocrdata;
					item[ "fields" ][ "metadata_count" ] = metadata_count;
					item[ "fields" ][ "ocrdata_count" ]  = ocrdata_count;

					config = getConfig();
					if( config[ "datastore" ] === "DSTORE_ELASTICSEARCH" )	// no metadata in Django DB
					{ var counts_str = " [" + ocrdata_count + "] "; }
					else
					{
						if( metadata_count === ocrdata_count )
						{
							if( metadata_count === 0 )
							{ var counts_str = " [" + metadata_count + "] "; }
							else
							{ var counts_str = " [<font color=green>" + metadata_count + "</font>] "; }
						}
						else
						{ var counts_str = " [<font color=red>" + metadata_count + "</font>,<font color=red>" + ocrdata_count + "</font>] "; }
					}

				//	console.log( "id: " + item.pk );
				//	var itemNode = dojo.byId( "query-" + item.pk );
					var cspan = dojo.byId( "query-string-" + pk );
					if( cspan != null )
					{
					//	var string = lexiconTitle + counts_str + "<em>" + item[ "fields" ][ "created" ] + '</em>';
						var string = "<span id=query-string-" + item.pk + " />" + lexiconTitle + counts_str + "<em> " + item[ "fields" ][ "created" ] + " </em> </span>";
					//	var params = { style: 'clear: both;' };
					//	dojo.html.set( cspan, string, params );
						cspan.innerHTML = string;

						var btn_sq_cloud = dijit.byId( "btn-sq-cloud-" + pk );
						if( config[ "datastore" ] === "DSTORE_ELASTICSEARCH" )	// no metadata in Django DB
						{
							if( ocrdata_count == 0 )
							{ btn_sq_cloud.set( "disabled", true ); }		// disable cloud button
							else
							{ btn_sq_cloud.set( "disabled", false ); }		// enable cloud button
						}
						else
						{
							if( metadata_count == 0 || ocrdata_count == 0 )
							{ btn_sq_cloud.set( "disabled", true ); }		// disable cloud button
							else
							{ btn_sq_cloud.set( "disabled", false ); }		// enable cloud button
						}

						var btn_sq_timeline = dijit.byId( "btn-sq-timeline-" + pk );
						if( config[ "datastore" ] === "DSTORE_ELASTICSEARCH" )	// no metadata in Django DB
						{
							if( ocrdata_count == 0 )
							{ btn_sq_timeline.set( "disabled", true ); }	// disable timeline button
							else
							{ btn_sq_timeline.set( "disabled", false ); }	// enable timeline button
						}
						else
						{
							if( metadata_count == 0 )
							{ btn_sq_timeline.set( "disabled", true ); }	// disable timeline button
							else
							{ btn_sq_timeline.set( "disabled", false ); }	// enable timeline button
						}
					}
					else { console.log( "null id: " + pk + pk ); }
				}
				else
				{ console.error( "updateQueryDocCountsMongoDB(): " + url + " response status: " + resp.status ); }
			},
			error: function( err ) { console.error( err ); return err; }
		});
	}
} // updateQueryDocCountsMongoDB()

// [eof]
