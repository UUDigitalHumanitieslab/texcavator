// FL-07-Sep-2012 Created
// FL-11-Sep-2012 Changed

dojo.require( "dojox.charting.Chart" );			// Require the basic 2d chart resource: Chart2D
dojo.require( "dojox.charting.widget.Sparkline" );
dojo.require( "dojox.charting.plot2d.Lines" );
dojo.require( "dojox.charting.plot2d.Pie" );

dojo.require( "dojox.charting.themes.Claro" );	// "Claro", new in Dojo 1.6, will be used
dojo.require( "dojox.charting.themes.Julie" );
dojo.require( "dojox.charting.themes.Tufte" );

dojo.require( "dojox.charting.action2d.Highlight" );
dojo.require( "dojox.charting.action2d.MoveSlice" );
dojo.require( "dojox.charting.action2d.Tooltip" );


// create metadata graphics
function metadataGraphics( lexiconID )
{
	console.log( "metadataGraphics()" );

	// select the tab containing the graphs
	var tc = dijit.byId( "articleContainer" );
	tc.selectChild( dijit.byId( "statistics" ) );

	dojo.place( new dijit.ProgressBar( { indeterminate: true }).domNode, dojo.byId( "statistics" ), "only" );

	//articleurl, date, edition, id, identifier, issue, lexiconarticle, lexiconitem, page, pageurl, papertitle, paperurl, ppn, publisher, source, spatialCreation, title, type, url, year
	//http://localhost:8000/lexicon/4/aggregation?field=page

	dojo.byId( "statistics" ).innerHTML = "";

	var aggregateField = function( id, field )
	{
		dojo.xhrGet({
			url: "lexicon/" + id + "/aggregation?field=" + field,
			handleAs: "text",
			load: function( data )
			{
				console.log( field );
			//	console.log( data );
				// Cleanup data
				var newData = data.replace(/u(\'|\")/g, "$1").replace(/}{/g, '},{');
				try {
					var rawData = dojo.fromJson( '[' + newData + ']' );
				} catch ( error ) {
					console.error( error );
					console.log( newData );
					return error;
				}

			//	console.log( rawData );
				var countField = field + "__count";
				var chartValues = dojo.map( rawData, function( row ) { return parseInt( row[ countField ] ); } );
				var chartData = dojo.map( rawData, function( row ) {
					return { tooltip: row[ field ], y: parseInt( row[ countField ] ) };
				});

				var text = "<b>" + field + "</b><br />";
				dojo.forEach( rawData, function( row ) {
					text += row[ field ] + ": " + row[ countField ] + "<br />";
				});

			//	var textTarget   = dojo.create( 'div', { innerHTML: text, style: "min-height: 110px" }, "statistics" );
				var textTarget   = dojo.create( 'div', { innerHTML: text, style: "min-height: 300px" }, "statistics" );
				var targetPie    = dojo.create( 'div', { style: "width: 200px; height: 150px; float: right;"}, textTarget, "first" );
				var targetSparks = dojo.create( 'div', { style: "width: 300px; height: 150px; float: right;"}, textTarget, "first" );


				// Create the chart within it's "holding" node
				pieChart = new dojox.charting.Chart( targetPie );
				//pieChart.style = "width: 100px; height: 15px;";

				// Set the theme
				pieChart.setTheme( dojox.charting.themes.Julie );

				// Add the only/default plot 
				pieChart.addPlot( "Pie", {
					type: dojox.charting.plot2d.Pie, 
					radius: 60, 
					labelOffset: -5, 
					labelStyle: "none",
					hAxis: "text", 
					vAxis: "y",
					margins: { l: 0, r: 0, t: 0, b: 0 }
				});
				//style="width: 100px; height: 15px;">
				//<div class="series" name="Series A" store="tableStore" valueFn="Number(x)"></div> 

				// Add the series of data
				pieChart.addSeries( "Data", chartData, { plot: "Pie" } );

				new dojox.charting.action2d.Tooltip(   pieChart, "Pie" );
				new dojox.charting.action2d.Highlight( pieChart, "Pie" );
				new dojox.charting.action2d.MoveSlice( pieChart, "Pie" );

				pieChart.render();	// Render the chart!

				var sparksChart = new dojox.charting.Chart( targetSparks );
				sparksChart.addSeries( "Data", chartValues );
				sparksChart.setTheme( dojox.charting.themes.Tufte );
				sparksChart.addPlot( "Record", { type: dojox.charting.plot2d.Lines } );
				sparksChart.render();

				return chartData;
			},
			error: function( err ) { console.error( err ); return err; }
		});
	};

	// some of the fields in lexicon/models.py class DigitaleDagbladenArticle
//	console.log( "edition" );
	aggregateField( lexiconID, "edition" );

//	console.log( "page" );
//	aggregateField( lexiconID, "page" );			// SyntaxError: missing } after property list

//	console.log( "papertitle" );
	aggregateField( lexiconID, "papertitle" );

//	console.log( "publisher" );
	aggregateField( lexiconID, "publisher" );

//	console.log( "spatialCreation" );
	aggregateField( lexiconID, "spatialCreation" );

//	console.log( "type" );
	aggregateField( lexiconID, "type" );

//	console.log( "year" );
//	aggregateField( lexiconID, "year" );			// SyntaxError: missing } after property list

//	console.log( "issue" );
//	aggregateField( lexiconID, "issue" );			// SyntaxError: missing } after property list

	// articleurl, date, edition, id, identifier, issue, lexiconarticle, lexiconitem, page, pageurl, papertitle, paperurl, ppn, publisher, source, spatialCreation, title, type, url, year
	// http://localhost:8000/lexicon/4/aggregation?field=page&order=year&extra=year
}

// [eof]
