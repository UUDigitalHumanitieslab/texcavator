// FL-04-Mar-2013 Created
// FL-24-Oct-2013 Changed

/*
function clearTextview()
function updateTextview( record_id, data )
function writeTextview( record_id, data )
*/

function clearTextview()
{
	// close all tabs but the first 2
//	var tabs = dijit.byId( "articleContainer" ).getChildren();
//	for( var tab = 2; tab < tabs.length; tab++ )
//	{ dijit.byId( "articleContainer" ).closeChild( tabs[ tab ] ); }

	if( dojo.byId( "record" ) == undefined )
	{ return; }
	else
	{ dojo.byId( "record" ).innerHTML = ""; }		// clear text
}



function updateTextview( collection, record_id, data, documentObj )
{
	console.log( "updateTextview(): " + record_id );
	var record_id_ocr = record_id + ":ocr";

	var config = getConfig();
	var senthlight = config[ "sentiment" ][ "highlight" ];
	if( senthlight === true )		// highlight text content
	{
		xtas.postWaiting(
			"process/",
			{
				content: { 
					collections: collection,	// xTAS wants collections, not collection
					id: record_id, 
					methods: "sentiment" 
				},
				handleAs: "json"
			},
			function( sentdata ) 
			{
				if( typeof( sentdata ) === "string" && !( sentdata == null || sentdata.length == 0 ) )
				{ sentdata = dojo.fromJson( sentdata ); }

				if( sentdata.status === "ok" )
				{
					var word_sents = sentdata.result;
					dojo.forEach( word_sents, function( word_sent )
					{
						// the results may contain duplicate words
						var word = word_sent[ 0 ];
						// \b as word separator not supported by this RegExp() ?
						var re = new RegExp( "("+word+")", "gi" );	// g: global, i: case-insensitive
					//	console.log( re );
						var sentiment = word_sent[ 1 ];
						if( sentiment.split( "" )[ 0 ] === "+" )
						{ 
						//	console.log( word + ": " + sentiment + " green" );
							data = data.replace( re, "$1".bold().fontcolor("green") );
						}
						else if( sentiment.split( "" )[ 0 ] === "-" )
						{
						//	console.log( word + ": " + sentiment + " red" );
							data = data.replace( re, "$1".bold().fontcolor("red") );
						}
					//	else
					//	{ console.log( word + ": " + sentiment + " ?" ); }
					});
				//	dojo.byId( "record" ).innerHTML = data.replace( /<(\/?)title>/g, "<$1b>" );
					writeTextview( record_id, data, documentObj );
				}
			}
		);
	}
	else	// update article text view without highlighting
	{ writeTextview( record_id, data, documentObj ); }
} // updateTextview()


function writeTextview( record_id, data, documentObj )
{
	console.log( "writeTextview() " + record_id);
    
    article_text = documentObj.text_content.replace(/\n\n/g, "</br></br>");

	dojo.byId( "record" ).innerHTML = "<b>"+documentObj.article_dc_title+"</b></br>"+article_text;
}

// [eof]
