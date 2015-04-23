dojo.require( "dijit.Tooltip" );
dojo.require( "dijit.popup" );

/*
var showTimeline = function( lexiconId, lexiconTitle )
function loadGraphData( lexiconId )
function getDataForInterval( lexiconId, intervalIndex, callback )
function getData( lexiconId, field, interval, callback )
function getEndOfInterval( date, interval )
function createGraph() {
	function filterFunction( d )
	function redraw() {
		function nrOfBins( data )
		function burstUpdateFunction( burst )
		function pathUpdateFunction( path )
	}
}
function burstSearch( lexicon_query, date_range, max_records )
function burstClicked( data, index, element )
function burstCloud( params )
function closePopup() {}
*/

var intervals = [ "year", "month", "day" ];

var zoomLimit = 8*24*3600000;	// Eight days
var zoomLimit = 10*60000;		// Ten minutes //24*3600000; // One days

var detectBursts = true;


var showTimeline = function(item, collection)
{
    lexiconId = item.pk;
    lexiconTitle = item["fields"]["title"];
    query_string = item["fields"]["query"];
    console.log( "showTimeline() lexiconId: " + lexiconId + ", lexiconTitle: " + lexiconTitle + ", collection: " + collection );

    setQueryMetadata(item);

	storeLexiconID( lexiconId );			// query.js
	storeLexiconTitle( lexiconTitle );		// query.js
	storeLexiconQuery( query_string );		// query.js
	storeCollectionUsed( collection );		// query.js

	var sparksDD = dijit.byId( 'sparksDropDownButton' );
	if( sparksDD != undefined ) { sparksDD.closeDropDown(); }

	// select the tab containing the timeline
	var tc = dijit.byId( "articleContainer" );
	tc.selectChild( dijit.byId( "timeline" ) );

	loadGraphData( lexiconId );
}


function loadGraphData( lexiconId ) 
{
	burstData = {};
	burstIntervalIndex = 0;
	burstAnimation = false;

	getDataForInterval( lexiconId, 0, function () 
	{
		createGraph();

		var intervalIndex = 0;

		var continueFunction = function () 
		{
			if( ++intervalIndex < intervals.length ) 
			{ getDataForInterval( lexiconId, intervalIndex, continueFunction ); }
		};

		continueFunction();
	});
}


function getDataForInterval( lexiconId, intervalIndex, callback ) 
{
	var interval = intervals[ intervalIndex ];

	getData( lexiconId, "created_at", interval, function( data )
	{
		var mean = d3.mean( data, function( d ) { return d.value; } );
		var stddev = Math.sqrt( d3.mean( data, function( d ) { return Math.pow( d.value - mean, 2 ); } ) );

		var burstLimit = mean + 2 * stddev;
			
		if( detectBursts) $.each( data, function( index, entry ) {
			entry.burst = entry.value > burstLimit;
		});

		burstData[ intervalIndex ] = {
			data: data,
			range: [ 0, d3.max( data, function( d ) { return d.value; } ) ],

			// Compute the extent of the data set for dates
			dateRange: [d3.min(data, function(d) { return d.start; }), 
						d3.max(data, function(d) { return d.end; })],
			mean: mean,	stddev: stddev
		};
		console.log( "Loaded " + data.length + " data points for burst with interval " + interval + "." );
			
		// Add bogus data to fix last bar
		var bogusStart = new Date( getEndOfInterval( new Date( data[ data.length-1 ].start ), intervals[ burstIntervalIndex ] ) + 1 );
		burstData[ intervalIndex ].data.push( { 
			start: bogusStart,
    		end: getEndOfInterval( bogusStart, intervals[ burstIntervalIndex ] ),
    		value: 0, burst: false,
			index: -1 });

		// Set data for animation
		if( intervalIndex > 0 )
		{
			var originalData = burstData[ intervalIndex-1 ].data;

			function findValue( start, end, data, startIndex ) {
				if( data[ 0 ].start > end ) return [ 0, 0 ];
				if( data[ data.length-1 ].end < start ) return [ 0, data.length ];
				for( indx = startIndex; indx < data.length; indx++ ) {
					if( data[ indx ].end < start ) continue;
					return [ data[ indx ].value, indx ];
				}
				return [ 0, data.length ];
			}

			burstData[ intervalIndex ].animationData = [];
			var startIndex = 0;
			for( index = 0; index < burstData[ intervalIndex ].data.length; index++ ) {
				var result = findValue( burstData[ intervalIndex ].data[ index ].start,
					burstData[ intervalIndex ].data[ index ].end, originalData, startIndex );
				// Copy original data
				var newDatum = {};
				$.extend( newDatum, burstData[ intervalIndex ].data[ index ] );
				newDatum.value = result[ 0 ];
				burstData[ intervalIndex ].animationData.push( newDatum );
				startIndex = result[ 1 ];
			}
		}	

		callback( burstData[ interval ] );
	});	
}


function getData( lexiconId, field, interval, callback )
{
	var timeline_url = "query/timeline/" + lexiconId + "/" + interval;

	var config = getConfig();
	var collection = retrieveCollectionUsed();
	timeline_url = timeline_url + "?collection=" + collection;

	if( config[ "timeline" ][ "normalize" ] == true ) {
	    timeline_url += "&normalize=1";
	}
	else {
	    timeline_url += "&normalize=0";
	}

	var dateBeginStr = getDateBeginStr();
	var dateEndStr   = getDateEndStr();
	console.log( "daterange: from " + dateBeginStr + " till " + dateEndStr );
	timeline_url = timeline_url + "&begindate=" + dateBeginStr + "&enddate=" + dateEndStr;
	console.log( "timeline_url: " + timeline_url );

	$.ajax({
		url: timeline_url,
		type: 'GET', 
		dataType : 'json', 
		processData: false, 
		success: function( rawData ) 
		{
			// Prepare data
			var data = [];

			$.each( rawData, function( key, value ) 
			{
				data.push(
				{
					start: new Date( key ),
					end:   getEndOfInterval( new Date( key ), interval ),
					value: value[ 0 ],
					index: value[ 2 ],
					count: value[ 4 ],		// doc count shown in tooltip
					docs:  value[ 5 ]		// doc ids
				});
			});

			data = data.sort( function( a, b ) { return a.start - b.start } );
			callback( data );		// Add bogus data to fix last bar

		}, 
		error: function( xhr, message, error ) {
			console.error( "Error while loading timeline data:", message );
			throw( error );
		}
	});
}


function getEndOfInterval( date, interval ) 
{
	if( interval == "year" ) 
	{ return new Date( date.getTime() + 365*24*3600000 - 1 ); }

	if( interval == "month" ) 
	{ return new Date( date.getFullYear(), date.getMonth()+1, date.getDate(), 
		date.getHours(), date.getMinutes(), date.getSeconds(), date.getMilliseconds() ); }

	if( interval == "week" ) 
	{ return new Date( date.getTime() + 7*24*3600000 - 1 ); }

	if( interval == "day" ) 
	{ return new Date( date.getTime() + 24*3600000 - 1 ); }

	if( interval == "hour" ) 
	{ return new Date( date.getTime() + 3600000 - 1 ); }

	if( interval == "10m" ) 
	{ return new Date( date.getTime() + 10*60000 - 1 ); }

	if( interval == "5m" ) 
	{ return new Date( date.getTime() + 5*60000 - 1 ); }

	if( interval == "minute" ) 
	{ return new Date( date.getTime() + 60000 - 1 ); }
}


function createGraph() 
{
	var config = getConfig();

	// Create a place for the chart
	var collection = retrieveCollectionUsed();
	var dest = dojo.byId( "chartDiv" );
	if( dest == null ) 
	{ $( '#timeline' ).append( '<div id="chartDiv" style="width: 100%; height: 320px; float: center;"></div>' ); }
	else
	{ dest.innerHTML = ""; }			// Clear existing destination

    var w = $( "#chartDiv" ).width() - 30, 
	    h = $( "#chartDiv" ).height(),
	    x = d3.time.scale().range( [ 0, w ] ),
	    y = d3.scale.linear().range( [ h-20, h-20 ] );	// start with zero height at X-axis (20px reserved for ticks & years)
	console.log( "createGraph() w=" + w + ", h=" + h );	// debug: sometimes the graph is compressed to a small width

	// Update the scale domains.
	x.domain( burstData[ burstIntervalIndex ].dateRange );
	y.domain( burstData[ burstIntervalIndex ].range );

	// An SVG element
	var svg = d3.select( "#chartDiv" ).append( "svg:svg" )
		.attr( "width", w )
		.attr( "height", h )
		.attr( "pointer-events", "all" )
		.append( "svg:g" )
		.call( d3.behavior.zoom().on( "zoom", redraw ) );

	svg.append( "svg:rect" )
		.attr( "width", w )
		.attr( "height", h-19 )
		.style( "fill", "white" );

	var body = svg.append( "svg:g" );

	var area = d3.svg.area()
		.x( function( d ) { return x( d.start ); } )
		.y0( 0 )
		.y1( function( d ) { return y( d.value ); } )
		.interpolate( "step-after" );


	function filterFunction( d ) {
		if( d.end.getTime() < x.domain()[ 0 ] )
			return false;
		if( ( d.start.getTime() - (d.end.getTime()-d.start.getTime()) ) > x.domain()[ 1 ] )
			return false;
		return true;
	}


	function redraw() 
	{
		console.log( "redraw()" );

		if( burstAnimation )
		{ return; }		// Should only update X scale. Separate that from y scale? Can we do even that for area?

		// Use behavior instead of transform: 
		// https://github.com/mbostock/d3/blob/master/examples/zoom-pan/zoom-pan.html
		var previousXdomain = x.domain();
		if( d3.event ) { d3.event.transform( x ); }

		// Limit zooming in range
		var dateRange = burstData[ burstIntervalIndex ].dateRange;
		if( x.domain()[ 0 ] < dateRange[ 0 ] ) { x.domain( [ dateRange[ 0 ], x.domain()[ 1 ] ] ); }
		if( x.domain()[ 1 ] > dateRange[ 1 ] ) { x.domain( [ x.domain()[ 0 ], dateRange[ 1 ] ] ); }

		// Limit zooming to zoomLimit
		if( ( x.domain()[ 1 ].getTime() - x.domain()[ 0 ].getTime() ) < zoomLimit )
		{ x.domain( previousXdomain ); }

		// Prevent zooming out of Date range
		if( isNaN( x.domain()[ 0 ].getTime() ) || isNaN( x.domain()[ 1 ].getTime() ) )
		{ x.domain( previousXdomain ); }

		// Close popup on zooming or panning
		if( ( previousXdomain[ 0 ].getTime() != x.domain()[ 0 ].getTime() || 
			  previousXdomain[ 1 ].getTime() != x.domain()[ 1 ].getTime() ) )
		{ closePopup; }

		var ticksX = x.ticks( 10 );
		if( ticksX.length > 16 ) { ticksX = x.ticks( d3.time.years,  5 ); }
		if( ticksX.length > 16 ) { ticksX = x.ticks( d3.time.years, 10 ); }
		if( ticksX.length > 16 ) { ticksX = x.ticks( d3.time.years, 20 ); }
		var fx = x.tickFormat( 10 );
		var tx = function( d ) { return "translate(" + x( d ) + ",0)"; };

		// Regenerate x-ticks
		var gx = svg.selectAll( "g.x" )
			.data( ticksX, fx )
			.attr( "transform", tx );

		var gxe = gx.enter().insert( "svg:g", "a" )
			.attr( "class", "x" )
			.attr( "transform", tx );

		gxe.append( "svg:line" )
			.attr( "stroke", "#555" )
			.attr( "y1", h-20 )
			.attr( "y2", h-15 );

		gxe.append( "svg:text" )
			.attr( "y", h-12 )
			.attr( "dy", "1em" )
			.attr( "text-anchor", "middle" )
			.text( fx );

		gx.exit().remove();

		var newData;
		filteredData = burstData[ burstIntervalIndex ].data.filter( filterFunction );


		function nrOfBins( data ) 
		{
			var nrOfBins = data.length;
			if( nrOfBins > 1 ) 
			{
				var binSize = data[ 0 ].end - data[ 0 ].start;
				if( binSize > 0 )
				{ nrOfBins = ( data[ data.length-1 ].end - data[ 0 ].start ) / binSize; }
				// else return the data.length
			}
			return nrOfBins;
		}

		if( nrOfBins( filteredData ) < 10 && burstIntervalIndex < ( intervals.length-1 ) && 
			burstData[ burstIntervalIndex+1 ] != undefined ) 
		{
			// Zoom in
			burstIntervalIndex += 1;
			console.log( "Zooming in to interval " + intervals[ burstIntervalIndex ] );
			newData      = burstData[ burstIntervalIndex ].data.filter( filterFunction );
			filteredData = burstData[ burstIntervalIndex ].animationData.filter( filterFunction );
		} 
		else if( nrOfBins( filteredData ) > 20 && burstIntervalIndex > 0 && 
			burstData[ burstIntervalIndex-1 ] != undefined ) 
		{
			// Zoom out
			var zoomOutData = burstData[ burstIntervalIndex-1 ].data.filter( filterFunction );
			if( nrOfBins(zoomOutData) > 10 ) 
			{
				burstIntervalIndex -= 1;
				console.log( "Zooming out to interval " + intervals[ burstIntervalIndex ] );
				newData      = burstData[ burstIntervalIndex+1 ].animationData.filter( filterFunction );
				filteredData = burstData[ burstIntervalIndex+1 ].data.filter( filterFunction );
			}
		}

		// Select all bursts
		var bursts = body.selectAll( "rect.bursts" )
			.data( filteredData );

		// Create new burst when needed
		// 'd' is the data, 'i' is the bar index: 0, 1, ..., 'this' is a svg rect class
		bursts.enter().append( "svg:rect" )
			.attr( "class", "bursts" )
			.attr( "height", h-20 )
			.on( "mouseover", function( d, i ) 
			{
			//	console.log( "mouseover" );
				d3.select( this ).transition().duration( 300 ).style( "opacity", 0.5 ); 
			}) 
			.on( "mouseout", function( d, i ) 
			{ 
			//	console.log( "mouseout" );
				d3.select( this ).transition().duration( 300 ).style( "opacity", 1.0 ); 
			})
			.on( "mouseup", function( d, i ) 
			{ 
			//	console.log( "mouseup" );
				burstClicked( d, i, this ); 
			});

		// Set data for path
		var paths = svg.selectAll( "path" )
			.data( [ filteredData ] );

		// Add new items to path if needed
		paths.enter().append( "svg:path" )
			.style( "fill", "white" );

		// Function to transition exit, for consistent animation
		/*function exitTransition(updateFunction, time) {
			var exitTransitionFunction = function(selection) {
				selection.exit()
					.transition()
						.duration(time)
						.call(updateFunction)
						.remove();				
			};
			return exitTransitionFunction;
		}*/

		// Delete unneeded bursts and path
		bursts.exit().remove();		//call(exitTransition(burstUpdateFunction, 2500));
		paths.exit().remove();		//.call(exitTransition(pathUpdateFunction, 2500));


		function burstUpdateFunction( burst ) 
		{
			burst
				.attr( "x", function( d ) { return x( d.start ); } )
				.attr( "width", function( d ) { return Math.max( 4, x( d.end ) - x( d.start )+1 ); } )
				.style( "opacity", 1 )
				.style( "fill", function( d ) 
				{
					if( config[ "timeline" ][ "burst_detect" ] == true )
					{ return ( d.burst ) ? "red" : "steelblue"; }
					else
					{ return "steelblue"; }
				});
		}


		function pathUpdateFunction( path ) {
			path.attr( "d", area );
		}			


		// Place bursts at right spot
		bursts.call( burstUpdateFunction );
		paths.call( pathUpdateFunction );

		// Update tooltip document count
		body.selectAll( "title" ).remove();
		bursts.append( "svg:title" )
			.text( function( d, i ) { return d.value + " document" + ( ( d.value == 1 ) ? "" :"s" ); } );

		// Update period
		svg.selectAll( "text.period" )
			.data( [ 0 ] )
			.enter().append( "svg:text" )
				.attr( "class", "period" )
				.attr( "fill", "#555" )
				.attr( "x", 5 ).attr( "y", 22 )
				.attr( "dy", "1em" )
				.attr( "text-anchor", "left" );

		var xDomain = x.domain()[ 1 ].getTime() - x.domain()[ 0 ].getTime();
		var lexiconTitle = retrieveLexiconTitle();

		if( xDomain > 3*365*24*3600000 )		// Just show year if domain is larger than 3 years
		{
			svg.selectAll( "text.period" )
				.text( "Period: " + x.domain()[0].getFullYear() + " - " + x.domain()[1].getFullYear() + " , Query title: " + lexiconTitle );
		}
		else
		{
			svg.selectAll( "text.period" )
				.text( "Period: " + x.domain()[0].toDateString() + " - " + x.domain()[1].toDateString() + " , Query title: " + lexiconTitle );
		}

		// If we have newData, set up animation
		if( newData != undefined ) 
		{ 
			burstAnimation = true;

			y.domain( burstData[ burstIntervalIndex ].range );

			body.selectAll( "rect.bursts" )
				.data( newData )
				.transition()
					.duration( 2500 )
					.call( burstUpdateFunction );

			svg.selectAll( "path" )
				.data( [ newData ] )
				.transition()
					.duration( 2500 )
					.call( pathUpdateFunction )
					.each( "end", function() { burstAnimation = false; redraw(); } );
		}
	}
	redraw();


	// Raise the bars
	y.range( [ h-20, 0 ] );
	var collection = retrieveCollectionUsed();
	d3.select( "#chartDiv" ).selectAll( "path" )
		.transition()
			.duration( 2500 )
			.delay( 300 )
			.attr( "d", area );

	if( dijit.byId( 'sparksDialog' ) == undefined ) 
	{
		var chart_div = "chartDiv";

		var dialog = new dijit.TooltipDialog({
			id: 'sparksDialog',
			content: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer eget risus metus. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. In convallis, nunc non pretium vulputate, orci mi mollis eros, nec gravida mauris purus vel felis. Quisque semper aliquam quam, ac pellentesque tortor viverra eget. Vestibulum vel orci non tellus fermentum ornare at quis mauris. Praesent a placerat magna. Aliquam porttitor accumsan elementum. Phasellus ac leo non magna sollicitudin gravida. Fusce dapibus posuere eros sed sollicitudin. Curabitur ut ligula lacus, eu porta magna.',
			style: 'width: ' + dojo.position( chart_div ).w + 'px'
		});
	}

	var button = dijit.byId( 'sparksDropDownButton' );
	if( button == undefined ) 
	{
		button = new dijit.form.DropDownButton({
			id: 'sparksDropDownButton',
			label: "Tooltip",
			dropDown: dialog,
			style: 'position: absolute; left: 0; top: 320px; visibility: hidden'
		});
	}

    dojo.place( button.domNode, 'chartDiv' );

} // createGraph() 



function burstSearch( lexicon_query, date_range, max_records ) 
{
	console.log( "burstSearch()" );

	accordionSelectChild( "searchPane" );

	var params = getSearchParameters();		// get user-changeable parameters from config
	params.query = lexicon_query;			// insert the query string
	params.dateRange = date_range;			// replace dateRange from the date widgets with the timeline bar dateRange
	params.maximumRecords = max_records;

	var url = "services/search/";
	dojo.xhrGet({
		url : url,
		content : params,									// key:value pairs
		handleAs : "json",									// HTML data returned from the server
		load : function( data ) {
            console.log(data);
			dojo.byId( "search-result" ).innerHTML = data.html;	// put html text in panel
		},
		error: function( err ) {
			console.error( err );							// display the error
		}
	});
} // burstSearch()


function burstClicked( data, index, element ) 
{
	console.log( "burstClicked(): " + data.docs.length + " records" );

	var i = index;
	var e = element;
	var d = data;

	var lexicon_id    = retrieveLexiconID();
	var lexicon_title = retrieveLexiconTitle();
	var lexicon_query = retrieveLexiconQuery();
	console.log( "id: " + lexicon_id + ", title: " + lexicon_title + ", query: " + lexicon_query );

	dijit.byId( "query" ).set( "value", lexicon_query );	// show query in TextBox

	// show burst articles in accordion
	var start_date  = toDateString( d.start );			// toDateString() : toolbar.js
	var stop_date   = toDateString( d.end );			// toDateString() : toolbar.js
	var date_range  = start_date + "," + stop_date

	// retrieve all timeline bar records, not just the KB default 20
	// the timeline bar sometimes has a few less than found by search: the lexicon_daystatistic 
	// table may not exactly match the documents present in the db: just ask for the double count
	var max_records = 2 * data.docs.length;
	console.log( "max_records: " + max_records );

	burstSearch( lexicon_query, date_range, max_records );

	dijit.byId( 'sparksDropDownButton' ).openDropDown();

	var template = '<b>{burst}{start} - {end}: <a href="{link}">{count} documents</a>.</b><br /><br /><div id="cloud"></div>';
	var data = {
		burst: (d.burst) ? "Burst " : "",
		start: d.start.toString().substr(4, 11),
		end: d.end.toString().substr(4, 11),
		link: 'javascript:filterOnTime('+d.start.getTime()+', '+d.end.getTime()+')', count: d.count 
	};

	dijit.byId( "sparksDialog" ).set( "content", dojo.replace( template, data ) );

	// Load burst cloud here
	dojo.place( new dijit.ProgressBar( { indeterminate: true } ).domNode, dojo.byId( "cloud" ), "only" );

	var collection = retrieveCollectionUsed();
	console.log( "burst from: " + collection);
	var params = {
		collections : collection,	// 	can be more than 1
		ids: d.docs.join(',')		// cloud not by tag name, but by comma separated ids string
	};

	burstCloud( params );

	var oldPosition = dojo.position( dijit.byId( 'sparksDialog' )._popupWrapper );
	var newLeft  = dojo.position( "chartDiv" ).x;
	var newWidth = dojo.position( "chartDiv" ).w;

	dijit.byId( 'sparksDialog' )._popupWrapper.style.left  = newLeft  + "px";
	dijit.byId( 'sparksDialog' )._popupWrapper.style.width = newWidth + "px";
	var newLeft = e.x.animVal.value + e.width.animVal.value/2;
	newLeft -= dojo.position( dojo.query( '#sparksDialog .dijitTooltipConnector' )[ 0 ]).w/2;
	dojo.query( '#sparksDialog .dijitTooltipConnector' )[ 0 ].style.left = newLeft + "px";
} // burstClicked()


function burstCloud( params )
{
	console.log( "burstCloud()" );
	params = getCloudParameters( params );		// add user-changeable parameters from config

	dojo.xhrGet({
        url: "services/cloud",
		content: params, 
		failOk: false,			// true: No dojo console error message
		handleAs: "json",
    }).then(function( resp ){
        
            console.log("requesting task id for burstcloud");
            console.log(resp);

            if( resp.status != "ok" ){
	    		console.error( resp.msg );
		    	closePopup();
    			var title = "Cloud request failed";
			    var buttons = { "OK": true };
		    	genDialog( title, resp.msg, buttons );
	    		return null;
    		} else {
		    	console.log("got task_id: "+resp.task);
                return resp.task;
    		}
	    }, function( err ) { console.error( err ); }
    ).then(function(task_id){
        console.log("Start polling!")
        console.log("task_id: "+task_id)
        if(task_id){
            check_status(task_id);
        } else {
            console.log('Error: no task_id returned.');
        }
    });
} // burstCloud()


function closePopup()
{
	var sparksDD = dijit.byId( 'sparksDropDownButton' );
	if( sparksDD != undefined ) { sparksDD.closeDropDown(); }
} // closePopup()

// [eof]
