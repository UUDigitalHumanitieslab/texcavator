dojo.require("dojox.xml.parser");

/*
Functions:
	function scanImages( record_id )
	function scanImagesKB( record, metadata_xml )
	function generateImageForPage( record )
*/


function scanImages( record_id )
{
	// this KB specific
	console.log( "scanImages: record_id: " + record_id );

	var urn = record_id.split( ':' ).slice( 0, 3 ).join( ':' );
	// e.g record_id -> urn: ddd:010434315:mpeg21:a0003:ocr -> ddd:010434315:mpeg21

	// retrieve the metadata XML from KB
	dojo.xhrGet({
		url: "services/kb/resolver/" + urn,
		handleAs: "json",
		load: function( response )
		{	
			if( response.status != "success" )
			{
				console.warn( "scanImagesKB: " + response.msg );
				var title = "Retrieving KB metadata failed";
				var buttons = { "OK": true };
				genDialog( title, response.msg, buttons );
			}
			else
			{
				var record_noocr = record_id.split( ':' ).slice( 0, 4 ).join( ':' );
				// e.g record_id -> urn: ddd:010434315:mpeg21:a0003:ocr -> ddd:010434315:mpeg21:a0003
				var metadata_xml = response.text;
				scanImagesKB( record_noocr, metadata_xml );
			}
		},
		error: function( err ) { console.error( err ); return err; }
	});
} // scanImages()



function scanImagesKB( record, metadata_xml )
{
	console.log( "scanImagesKB: " + record );
//	console.log( metadata_xml );

	var doc = dojox.xml.parser.parse( metadata_xml );

	var items = doc.firstChild.getElementsByTagNameNS( "urn:mpeg:mpeg21:2002:02-DIDL-NS", "Item" );
	var recordItems = [];
	dojo.forEach(items, function( item ) {
		var article_id = item.getAttributeNS( "http://www.kb.nl/namespaces/ddd", "article_id" );
		if( article_id == record ) { recordItems.push(item); }
	});

	for( var item = 0; item < recordItems.length; item++ )
	{
		var url = 'http://resolver.kb.nl/resolve?urn=' + record;
		var hyperlink = $('<a>');
		hyperlink.attr({href: url, target: '_blank'});
		hyperlink.html(generateImageForPage(recordItems[item]));
		hyperlink.appendTo('#record');
	}
} // scanImagesKB()



function generateImageForPage( record )
{
	console.log( "generateImageForPage()" );
	// Find common bounding box
	var top, right, bottom, left;
	var min = function( a, b ) { return ( a == undefined ) ? b : Math.min( a, b ); };
	var max = function( a, b ) { return ( a == undefined ) ? b : Math.max( a, b ); };
	var i = function( s ) { return parseInt( s ); };

	console.log( typeof( record ) );
	var areaTagName = "area";
	if( dojo.isMozilla ) {
		console.log( "isMozilla" );
		areaTagName = "dcx:area";
	}
	var areas = record.getElementsByTagName( areaTagName );

	dojo.forEach(areas, function(area) {
		top    = min(top,      area.getAttribute("vpos"));
		right  = max(right,  i(area.getAttribute("hpos")) + i(area.getAttribute("width")));
		bottom = max(bottom, i(area.getAttribute("vpos")) + i(area.getAttribute("height")));
		left   = min(left,     area.getAttribute("hpos"));
	});

	var scale = 0.3;
	var identifier = record.parentNode.getAttributeNS("http://purl.org/dc/elements/1.1/", "identifier");

	var query = dojo.byId("query").value.replace(/[()]/g, ''); // removes parentheses from query

	var url = "http://imageviewer.kb.nl/ImagingService/imagingService?colour=89c5e7";
	url += "&coords=" + identifier + ":alto";
	url += "&id=" + identifier + ":image";
	url += "&words=" + encodeURIComponent(query);
	url += "&r=0&s=" + scale;

	if( areas.length === 0 )	// use some dummy coordinates
	{
		var x = 0;
		var y = 0;
		var w = 500;
		var h = 200;
	}
	else
	{
		var x = Math.floor(scale*left);
		var y = Math.floor(scale*top);
		var w = Math.ceil( scale*(right-left)+1);
		var h = Math.ceil( scale*(bottom-top)+1);
	}
	url += "&x=" + x + "&y=" + y;
	url += "&w=" + w + "&h=" + h;
//	console.log( "img url: + " + url );

	return '<img src="' + url + '" />';
} // generateImageForPage()