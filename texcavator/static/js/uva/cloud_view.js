/*
FL-07-Sep-2012 Created
FL-10-Sep-2013 Changed

Functions:
var getCloudParameters	= function( params )
var stopwordsRemove		= function()
var stopwordsGetString	= function()
var stopwordsGetTable	= function()
function stopwordsFillTable( stopwordsList, editglob, target )
var stopwordsSave		= function( word, stopwords_cat )
var clearCloud			= function()
var placeCloudInTarget	= function( cloud_src, data, target )
var wordCloudClicked	= function( event )
var d3CreateCloud		= function( cloud_src, svg_width, svg_height, weightFactor, 
		text_size_list, text_count_hash, text_type_hash, text_color_hash )
function destroyDlgCloudword()
*/

dojo.require( "dijit.Dialog" );
dojo.require( "dijit.Tooltip" );
dojo.require( "dojox.grid.DataGrid" );
dojo.require( "dojox.grid.EnhancedGrid" );


var getCloudParameters = function( params )
{
	var config = getConfig();

	// add user-changeable parameters
	var cloudcfg = config.cloud;

	// Ork expects { 0 | 1 }
	params.order = "count";

	if( cloudcfg.NER ) { params.entities = 1; }	// only entities in cloud
	else { params.words = 1; }							// all words cloud

	if( cloudcfg.stems ) { params.stems = 1; }
	if (cloudcfg.idf) {
		params.idf_timeframe = $(".idf-timeframe input:checked").val();
	}

	if( cloudcfg.stopwords )
	{
		params.stopwords = 1;
		params.stopwords_default = cloudcfg.stopwords_default ? 1 : 0;
	}

	if(cloudcfg.stoplimit){
		params.min_length = cloudcfg.stoplimit;
	} else {
		params.min_length = 2;
	}

//	console.log( params );
	return params;
};


var stopwordsRemove = function()
{
	var config = getConfig();
	return config.cloud.stopwords;
};


var stopwordsGetTable = function( target )
{
//	console.log( "stopwordsGetTable()" );
	// retrieve stopwords table data, place at target div

	dojo.xhrPost({
		url: "query/stopwords",	// POST url must end with `/'
		handleAs: "json",
		load: function(response)
		{
			var status = response.status;

			if (status === "SUCCESS")
			{
				stopwordsFillTable( response.stopwords, response.editglob, target );
			}
			else
			{
				console.error( status );
				var msg = response.msg;
				console.error( msg );
			}
		},
		error: function( err ) {
			console.error( err );
			return err;
		}
	});
};


function stopwordsFillTable( stopwordsList, editglob, target )
{
//	console.log( "stopwordsFillTable()" );
//	console.log( stopwordsList );

	var label = dojo.byId( "label-grid-stopwords" );
	if( label !== null )
	{ label.innerHTML = stopwordsList.length + " stopwords for user " + glob_username + ":<br/>"; }

	var table_data = 
	{
		identifier: 'id',
		label: 'id',
		items: []
	};

	destroyDlgCloudword();		// delete a pre-existing table, and the buttons

	dojo.forEach( stopwordsList, function( entry, i )
	{
		var pk    = entry.id;
		var word  = entry.word;
		var user  = entry.user;
		var query = entry.query;

		if( user == "" )
		{
			if( editglob == true ) { var disabled = false; }
			else { var disabled = true; }
			if( query == "" ) { query = "(all)"; }
		}
		else
		{
			var disabled = false;
			if( query == "" ) { query = "(all " + user + ")"; }
		}

	//	console.log( i, word, user, query, editglob );

		var btn = new dijit.form.Button({
			id: "btn-stopw-delete-" + i,
			label: "Delete",
			disabled: disabled,
			showLabel: false,
			title: "Delete stopword",
			iconClass: "dijitIconDelete",
			onClick: function()
			{
				dojo.xhrPost({
					url: "query/stopword/" + pk + "/delete",
					handleAs: "json",
					load: function(response)
					{
						genDialog("Delete stopword", response.msg, { "OK": true });
						dijit.byId("dlg-cloudword").destroyRecursive();
					},
					error: function(err) {
						console.error(err);
						return err;
					}
				});
			}
		});

		table_data.items.push({ 
			"i":		i + 1, 
			"id":		pk, 
			"word":		word, 
			"user":		user, 
			"query":	query, 
			"delete":	btn 
		});
	});

	var stopwords_layout = [
		{ name: "#",      field: "i",      width: "15%", hidden: false },
	//	{ name: "Id",     field: "id",     width: "15%", hidden: false },
		{ name: "Word",   field: "word",   width: "30%" },
		{ name: "User",   field: "user",   width: " 0%", hidden: true },
		{ name: "Query",  field: "query",  width: "40%" },
		{ name: "Delete", field: "delete", width: "15%" }
	];

	var stopwords_store = new dojo.data.ItemFileWriteStore({ data: table_data });

//	var grid = new dojox.grid.EnhancedGrid({
	var grid = new dojox.grid.DataGrid({
		id: 'grid-stopwords',
		store: stopwords_store,
		structure: stopwords_layout,
	//	rowSelector: '20px',
	//	style:  'font-size 8pt',	// no effect
	//	rowHeight: '12px',			// no effect
		width:  '45em',				// required
	//	height: '33ex'				// required
		height: '30ex'				// required
	});
	grid.placeAt( target );
	grid.startup();
}



var stopwordsSave = function( word, stopwords_cat )
{
	var stopwords_clean = config[ "cloud" ][ "stopwords_clean" ];
	if( stopwords_clean == true ) { stopwords_clean01 = 1; }
	else { stopwords_clean01 = 0; }

	var content = {
		stopword: word
	};

	if( stopwords_cat === "singleq" )
	{
		content[ "query_id" ] = lexiconID;
	}

	console.log(content)

	dojo.xhrPost({
		url: "query/stopword/add",
		handleAs: "json",
		content: content,
		load: function(response) {
			var status = response[ "status" ];
			var msg = response[ "msg" ];
			if( status !== "SUCCESS" )
			{
				console.log( status + ": " + msg );
				var buttons = { "OK": true, "Cancel": false };
				answer = genDialog( "Stopword save", msg, buttons );
			}
		},
		error: function( err ) {
			console.error( err );
			return err;
		}
	});
}



var clearCloud = function ()
{
	console.log( "clearCloud()" );

	var collection = collection_fromradio();		// accordion.js
	var cloud_pane = "cloudPane"

	if( dojo.byId( cloud_pane ) == undefined )
	{ return; }
	else
	{ dojo.byId( cloud_pane ).innerHTML = ""; }

	var config = getConfig();
	var cloud_render = config[ "cloud" ][ "render" ];

	if( cloud_render === "svg" )
	{ 
	//	console.log( "clearCloud() svg" ); 
	}
	else if( cloud_render === "canvas" )
	{
	//	console.log( "clearCloud() canvas" );

		var cloud_width  = 700;
		var cloud_height = 220;

		var cloudCanvas = dojo.create( "canvas", { 
			id:     "cloudCanvas", 
			width:   cloud_width,
			height:  cloud_height
		}, dojo.byId( cloud_pane ) );

		/*
		canvas = dojo.byId( "cloudCanvas" );
		if( canvas && canvas.getContext )
		{
			var context = canvas.getContext( '2d' );		// get the 2d context
			if( context ) { context.clearRect ( 0, 0, canvas.width, canvas.height ); }
		}
		else
		{ console.log( "clearCloudCanvas failed" ); }
		*/
	}
}



var placeCloudInTarget = function( cloud_src, json_data, target )
{
	console.log( "placeCloudInTarget() " );
	console.log( "Cloud source: " + cloud_src );
	console.log( "Cloud target: " + target );

	var config = getConfig();
	var cloud_render = config[ "cloud" ][ "render" ];
	console.log( "Cloud render: " + cloud_render);

	clearCloud();

	var contentBox = dojo.contentBox( target );
	// -8 to prevent scroll bars popping up
	var rwidth  = contentBox[ "w" ] -8;
	var rheight = contentBox[ "h" ] -8;

	var min_width = cloud_src == 'burst' ? 400 : 1000;
	if( isNaN( rwidth ) || rwidth < min_width )
	{
	//	console.log( "placeCloudInTarget() bad rwidth: " + rwidth );
		rwidth = min_width;		// just try something
	}

	var min_height = cloud_src == 'burst' ? 300 : 600;
	if( isNaN( rheight ) || rheight < min_height )
	{
	//	console.log( "placeCloudInTarget() bad rheight: " + rheight );
		rheight = min_height;		// just try something
	}

	if( cloud_render === "canvas" )
	{
		// this also removes the progress bar in wordCanvas
		$('#' + target).html('<center><canvas id="wordCanvas' + target + 
			'" width="' + rwidth + '" height="' + rheight + '"></canvas></center>');
	}
	else
	{
		console.log( "placeCloudInTarget: not clearing " + target );
	//	dojo.byId( target ).innerHTML = "";				// remove  progress bar
	}

	var cloud_data = json_data.result;

	storeCloudData( cloud_src, cloud_data );		// in table & global var

	var termCount = cloud_data.length;
	if( termCount === 0 )				// no cloud data
	{
		var title = "Word cloud";
		var message = "The word cloud is empty.";
		var buttons = { "OK": true, "Cancel": false };
		genDialog( title, message, buttons );
		return;
	}

	var status = json_data.status;
	if( status === "processing" )
	{
		var title = "Word cloud";
		var message = "The word cloud is being made.";
		console.log( message );
		var buttons = { "OK": true, "Cancel": false };
		genDialog( title, message, buttons );
		return;
	}
	else if( status !== "ok" )
	{
		var title = "Word cloud";
		var message = "The word cloud could not be made:<br/>" + json_data.error;
		var buttons = { "OK": true, "Cancel": false };
		genDialog( title, message, buttons );
		return;
	}

	var countMax = 0;
	var countAllWords = 0;
	var wordsDisplayed = 0;
	var wordsDisplayedMax = config[ "cloud" ][ "maxwords" ];
	var fontscale  = config[ "cloud" ][ "fontscale" ];
	var fontreduce = config[ "cloud" ][ "fontreduce" ];
	var stopwords  = config[ "cloud" ][ "stopwords" ];
	var stoplimit  = config[ "cloud" ][ "stoplimit" ];

	var nerType2Color = function( nertype )
	{
	//	console.log( "nerType2Color() " + nertype );
		if( nertype == undefined ) { return 'Black'; }
		else
		{
		//	console.log( cw );
			if ( nertype === "DATE" )
			{ return 'Yellow'; }
			else if ( nertype === "LOC" )
			{ return 'Green'; }
			else if ( nertype === "MISC" )		// recognized as entity, but cannot say which
			{ return 'Orange'; }
			else if ( nertype === "ORG" )
			{ return 'Purple'; }
			else if ( nertype === "PER" )
			{ return 'Blue'; }
			else if ( nertype === "UNKNOWN" )
			{ return 'Brown'; }
			else
			{ return 'Black'; }
		}
	}

	var text_size_list  = [];	// [ ["Duitsche", 13], ["Europa", 13], ... ]
	var text_count_hash = {};	// { {"Duitsche"=13}, {"Europa"=13}, ... }
	var text_tfidf_hash = {};	// { {"Duitsche"=13}, {"Europa"=13}, ... }
	var text_type_hash  = {};	// { {"Duitsche"="MISC"}, {"Europa"="LOC"}, ... }
	var text_color_hash = {};	// { {"Duitsche"="Orange"}, {"Europa"="Green"}, ...  }
	var minFontSize = 6;		// minimum size shown; used to be 8

	dojo.forEach( cloud_data, function( val, i )
	{
		freq = config.cloud.idf ? val.tfidf : val.count;
		countAllWords += 1;
		if( wordsDisplayed < wordsDisplayedMax )
		{
			if( fontreduce )
			{
				// using Math.sqrt() compresses the font size differences
				text_size_list.push( [ val.term, Math.sqrt( freq ) ] );
				if( countMax <  Math.sqrt( freq ) )
				{ countMax = Math.sqrt( freq ); }
			}
			else
			{
				text_size_list.push( [ val.term, freq ] );
				if( countMax < freq )
				{ countMax = freq; }
			}

			text_count_hash[ val.term ] = val.count;
			text_tfidf_hash[ val.term ] = val.tfidf;
			text_type_hash[  val.term ] = val.type;
		//	text_type_list.push( [ val.term, val.type ] );

			text_color_hash[ val.term ] = nerType2Color( val.type );
		//	text_color_list.push( [ val.term, nerType2Color( val.type ) ] );
			wordsDisplayed += 1;
		}
	});

	var weightFactor = fontscale / countMax;

	if( cloud_render === "svg" )
	{
		d3CreateCloud( target, cloud_src, rwidth, rheight, weightFactor, text_size_list, 
			text_count_hash, text_tfidf_hash, text_type_hash, text_color_hash );
	}

	else
	{
		$( '#wordCanvas' + target ).wordCloud( {
			wordList:         text_size_list,
			fontFamily:      'Myriad,Helvetica,Tahoma,Arial,clean,sans-serif',
			backgroundColor: 'White',
			weightFactor:     weightFactor,
			clearCanvas:      true,
			minSize:          minFontSize,		// minimum size shown

		//	wordColor: 'random-dark',	// could be a function too, function(word, weight, fontsize, radius, theta)
		//	wordColor: 'Black',			// but use colors with NER
			wordColor: function( w, we, fo, ra, the )
			{
				var cw = text_type_hash[ w ];
				if( cw == undefined ) { return 'Black'; }
				else
				{
					if ( cw === "DATE" )
					{ return 'Yellow'; }
					else if ( cw === "LOC" )
					{ return 'Green'; }
					else if ( cw === "MISC" )		// recognized as entity, but cannot say which
					{ return 'Orange'; }
					else if ( cw === "ORG" )
					{ return 'Purple'; }
					else if ( cw === "PER" )
					{ return 'Blue'; }
					else if ( cw === "UNKNOWN" )
					{ return 'Brown'; }
					else
					{ return 'Black'; }
				}
			}
		}).bind( "wordcloudclick", wordCloudClicked );
	}
}


var wordCloudClicked = function( event ) 
{
//	console.log( "wordCloudClicked()" )
	var query = dojo.byId( "query" ).value;
	var newQuery = query + " +" + event.word;
	if( !confirm( 'This adds ' + event.word + ' to the query. Do you want to continue?', 'Modify query' ) ) return;
	dojo.byId( "query" ).value = newQuery;
	searchSubmit();
}


// =============================================================================
var d3CreateCloud = function( target, cloud_src, svg_width, svg_height, weightFactor, 
	text_size_list, text_count_hash, text_tfidf_hash, text_type_hash, text_color_hash )
{
//	console.log( "d3CreateCloud() ");
	if( svg_width == undefined || svg_height == undefined )
	{
		console.error( "bad svg size, width: " + svg_width + " , height: " + svg_height ); 
		return
	}

	svg_height = svg_height - 18;		// leave some room for the mouseover statusline (without scrollbars)

	if( cloud_src === "burst" )
	{ var dest = "cloud"; }				// in Tooltip
	else
	{ var dest = target; }
	dojo.byId( dest ).innerHTML = "";	// removes ProgressBar

	// mouseover contents;
	var divStatusline = dojo.create( "div", { id: "statusline" }, dojo.byId( dest ) );
	divStatusline.innerHTML = "&nbsp;";		// prevent the cloud jumping up-and-down

	var text_size_list = text_size_list.map( function( d ) { 
		return { text: d[ 0 ], size: Math.round( weightFactor * d[ 1 ] ) }; 
	});

	var fontSize = d3.scale.log().range( [ 10, 100 ] );

	var layout = d3.layout.cloud()
		.size( [ svg_width, svg_height ] )
		.words( text_size_list )
	//	.rotate( function() { return ~~( Math.random() * 2 ) * 90; } )	// ~~ is a double NOT bitwise operator, comparable to Math.floor()
		.rotate( function() { return 0; } )
		.fontSize( function( d ) { return d.size; } )
	//	.on( "word", progress )
		.on( "end", draw )
		.start();

	function progress( word ) { console.log( word ); }

	function draw( words ) 
	{
		console.log( "Drawing word cloud..." );

		d3.select( "#" + dest )
			.append( "center" )
			.append( "svg:svg" )
				.attr( "width", svg_width )
				.attr( "height", svg_height)
			.append( "svg:g" )
				.attr( "transform", "translate("+ svg_width/2 + ", " + svg_height/2 + ")" )
			.selectAll( "text" )
			.data( words )
			.enter().append( "svg:text" )
				.style( "font-size", function( d ) { return d.size + "px"; } )
				.style( "fill", function( d ) { return text_color_hash[ d.text ]; } )
				.attr( "text-anchor", "middle" )
				.attr( "transform", function( d ) 
					{ return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")"; } )
				.attr( "count",   function( d ) { return text_count_hash[ d.text ]; } )
				.attr( "tfidf",   function( d ) { return text_tfidf_hash[ d.text ]; } )
				.attr( "nertype", function( d ) { return text_type_hash[  d.text ]; } )
			.text( function( d ) { return d.text; } )
			.on( "mouseover", function( d ) { 
				var count   = d3.select( this ).attr( "count" );
				var tfidf   = d3.select( this ).attr( "tfidf" );
				var nertype = d3.select( this ).attr( "nertype" );
				svgMouseover( d, count, tfidf, nertype ); } )
			.on( "mouseout", function( d ) { 
				svgMouseout( d ); } )
			.on( "mouseup", function( d ) { 
				var count = d3.select( this ).attr( "count" );
				svgMouseup( d, count ); } );
	}

	var svgMouseover = function( word, count, tfidf, nertype )
	{
		if (nertype == null)
		{
			result = "<center><u>word</u>: <b>" +  word.text + "</b>";
			result += ", <u>count</u>: <b>" + count + "</b>"; 

			if (config.cloud.idf) {
				result += ", <u>tdidf</u>: <b>" + tfidf + "</b>"; 
			}

			// Show stemmed form if we're not showing the stemmed cloud
			if (!config.cloud.stems)
			{
				dojo.xhrPost({
					url: "services/stem/",
					handleAs: "json",
					content: { "word": word.text },
					sync: true
				}).then(function(response) {
					result += ", <u>stemmed</u>: <b>" + response.stemmed + "</b>"; 
				});
			}

			result += "</center>";
			divStatusline.innerHTML = result;
		}
		else
		{
			divStatusline.innerHTML = "<center>phrase: <b>" +  word.text + "</b>" + ", count: <b>" + count + "</b>, NER type: <b>" + nertype + "</b></center>"; 
		}
	}

	var svgMouseout = function( word )
	{  divStatusline.innerHTML = "&nbsp;"; }


	var svgMouseup = function( word, count )
	{
	//	console.log( "svgMouseup: word: " + word.text + ", count: " + count );

		var old_dialog = dijit.byId( "dlg-cloudword" );
		if( old_dialog != null ) { old_dialog.destroyRecursive(); }		// ? not properly deleted last time

		var dialog = new dijit.Dialog({
			id: "dlg-cloudword",
			title: "Cloud word"
		});

		dojo.style( dialog.closeButtonNode, "visibility", "hidden" ); // hide the ordinary close button

		var container = dialog.containerNode;

		var cpdiv = dojo.create( "div", { id: "tc-div-cloudword" }, container );


		var tabCont = new dijit.layout.TabContainer({
			style: "background-color: white; width: 410px; height: 370px; line-height: 18pt"
		}, "tc-div-cloudword" );

		
		// stopwords tab
		var cp_grid_stopwords = new dijit.layout.ContentPane({
			id:     "cp-grid-stopwords",
			title:  "Stopwords",
			width:  "100%",
			height: "100%"
		});
		tabCont.addChild( cp_grid_stopwords );


		var stopwords_cat = "singleq"		// default

		//var change_system_stopwords = true; // enable for superusers?
		var change_system_stopwords = false;

		var divQuery = dojo.create( "div", {
			id: "div-stop-words"
		}, cp_grid_stopwords.domNode );


		dojo.create( "label", {
			innerHTML: "Add word to stopword table: <b>" + word.text + "</b><br/>"
		}, cp_grid_stopwords.domNode );


		if( stopwords_cat === "singleq" )
		{
			var stopwords_singleq = true;
			var stopwords_allqs   = false;
			var stopwords_system  = false;
		}
		else if( stopwords_cat === "allqs" )
		{
			var stopwords_singleq = false;
			var stopwords_allqs   = true;
			var stopwords_system  = false;
		}
		else if( stopwords_cat === "system" )
		{
			var stopwords_singleq = false;
			var stopwords_allqs   = false;
			var stopwords_system  = true;
		}


		var divSingleQStopword = dojo.create( "div", {
			id: "div-singleq-stopword"
		}, cp_grid_stopwords.domNode );

		var rbSingleQStopword = new dijit.form.RadioButton({
			id: "rb-singleq-stopword",
			checked: stopwords_singleq,
			onChange: function( btn )
			{
				if( btn == true )
				{ stopwords_cat = "singleq"; }
			},
		}, "div-singleq-stopword");

		var labelSingleQStopword = dojo.create( "label", {
			id: "label-singleq-stopword",
			for: "rb-singleq-stopword",
			innerHTML: "&nbsp;For only this query&nbsp;"
		}, cp_grid_stopwords.domNode );


		var divAllQStopword = dojo.create( "div", {
			id: "div-allqs-stopword"
		}, cp_grid_stopwords.domNode );

		var rbAllQStopword = new dijit.form.RadioButton({
			id: "rb-allqs-stopword",
			checked: stopwords_allqs,
			onChange: function( btn )
			{
				if( btn == true )
				{ stopwords_cat = "allqs"; }
			},
		}, "div-allqs-stopword");

		var htmlAllQStopword = "&nbsp;For all " + glob_username + " queries&nbsp;";
		if( change_system_stopwords == false ) { htmlAllQStopword += "<br/>"; }
		var labelAllQStopword = dojo.create( "label", {
			id: "label-allqs-stopword",
			for: "rb-allqs-stopword",
			innerHTML: htmlAllQStopword
		}, cp_grid_stopwords.domNode );


		if( change_system_stopwords == true )
		{
			var divSystemStopword = dojo.create( "div", {
				id: "div-system-stopword"
			}, cp_grid_stopwords.domNode );

			var rbSystemStopword = new dijit.form.RadioButton({
				id: "rb-system-stopword",
				checked: false,
				onChange: function( btn )
				{
					if( btn == true )
					{ stopwords_cat = "system"; }
				},
			}, "div-system-stopword");

			var labelSystemStopword = dojo.create( "label", {
				id: "label-system-stopword",
				for: "rb-system-stopword",
				innerHTML: "&nbsp;For all queries"
			}, cp_grid_stopwords.domNode );
		}


		var divGlobalStopw = dojo.create( "div", {
			id: "div-global-stopw"
		}, cp_grid_stopwords.domNode );

		var cbGlobalStopw = new dijit.form.CheckBox({
			id: "cb-global-stopw",
			checked: config[ "cloud" ][ "stopwords_clean" ],
			onChange: function( btn ) { config[ "cloud" ][ "stopwords_clean" ] = btn; }
		}, divGlobalStopw );

		var labelGlobalStopw = dojo.create( "label", {
			id: "label-global-stopw",
			for: "cb-global-stopw",
			innerHTML: "&nbsp;Remove superfluous stopwords on save<br/>"
		}, cp_grid_stopwords.domNode );


		dojo.create( "label", {
			id: "label-grid-stopwords",
			innerHTML: "stopwords:<br/>"
		}, cp_grid_stopwords.domNode );

		var divWData = dojo.create( "div", {
			id: "div-grid-stopwords"		// for the grid
		}, cp_grid_stopwords.domNode );

		stopwordsGetTable( divWData );		// and place grid at divWData


		var actionBar = dojo.create( "div", {
			className: "dijitDialogPaneActionBar",
			style: "height: 30px"
		}, container );

		var bCancel = new dijit.form.Button({
			id: "btn-cancel-cloudword",
			label: "<img src='/static/image/icon/Tango/16/actions/dialog-cancel.png'/> Cancel",
			showLabel: true,
			role: "presentation",
			onClick: function() {
				answer = "Cancel";
				dijit.byId( "tt-cancel-cloudword" ).destroyRecursive();
				dijit.byId( "tt-ok-cloudword" ).destroyRecursive();
				dijit.byId( "dlg-cloudword" ).destroyRecursive();
			}
		});
		actionBar.appendChild( bCancel.domNode );

		var tt = null;
		var debug_destroy = false;

		tt = dijit.byId( "tt-cancel-cloudword" );
		if( tt != null )
		{
			if( debug_destroy ) { console.error( "tt-cancel-cloudword tooltip already exists" ); }
			tt.destroy();
		}

		new dijit.Tooltip({
			id: "tt-cancel-cloudword",
			connectId: [ "btn-cancel-cloudword" ],
			label: "Close dialog"
		});

		var bOK = new dijit.form.Button(
		{
			id: "btn-ok-cloudword",
			label: "<img src='/static/image/icon/Tango/16/actions/dialog-ok.png'/> OK",
			showLabel: true,
			role: "presentation",
			onClick: function() {
				answer = "OK";
				var stopwords_clean = config[ "cloud" ][ "stopwords_clean" ];
				stopwordsSave( word.text, stopwords_cat, stopwords_clean );
				dijit.byId( "tt-cancel-cloudword" ).destroyRecursive();
				dijit.byId( "tt-ok-cloudword" ).destroyRecursive();
				dijit.byId( "dlg-cloudword" ).destroyRecursive();
			}
		});
		actionBar.appendChild( bOK.domNode );

		tt = dijit.byId( "tt-ok-cloudword" );
		if( tt != null )
		{
			if( debug_destroy ) { console.error( "tt-ok-cloudword tooltip already exists" ); }
			tt.destroy();
		}

		new dijit.Tooltip({
			id: "tt-ok-cloudword",
			connectId: [ "btn-ok-cloudword" ],
			label: "Save stopword <b>" + word.text + "</b>"
		});

		dialog.show();
	}
	var showDialog = function() { dijit.byId( "dlg-cloudword" ).show(); }
	var hideDialog = function() { dijit.byId( "dlg-cloudword" ).hide(); }


	// this works
	/*
	var svg = d3.select( "#cloudPane" )
		.append( "svg:svg" )
		.append( "svg:circle" )
		.attr( "cx", 100 )
		.attr( "cy", 50 )
		.attr( "r", 40 )
		.attr( "stroke", "black" )
		.attr( "stroke-width", 2 )
		.attr( "fill", "red" );
	*/
}



function destroyDlgCloudword()
{
	// delete a pre-existing table, and the buttons
	var old_grid = dojo.byId( "grid-stopwords" );
	if( old_grid != null )
	{
		console.log( "deleting old grid" );
		old_grid.destroyRecursive();
	}

	var i = 0;
	do {
		var old_btn = dijit.byId( "btn-stopw-delete-" + i );
		if( old_btn != null )
		{
		//	console.log( "deleting delete button " + i );
			old_btn.destroyRecursive();
			i++;
		}
	} while( old_btn != null );
//	console.log( dijit.registry._hash );	// show registered widgets
}

// [eof]
