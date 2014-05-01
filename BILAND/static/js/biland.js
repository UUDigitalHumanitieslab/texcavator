// FL-09-May-2012
// FL-26-Aug-2013 Changed

try {
	dojo.registerModulePath( "uva", "../../uva" );
} catch( error ) {
	console.log( "Dojo is required for BiLand." );
}

dojo.require( "uva.logger" );
dojo.require( "uva.xtas" );

var xtasUrl = "/services/xtas/";
//var xtasUrl = "/biland/services/xtas/";
var xtas = Xtas( { "xtasUrl" : xtasUrl } );

if( xtas.validateKey() )
{
	console.log( "Loaded xTas for username: " + xtas.username );
	glob_key_validated = true;
}
else
{
	console.error( "xTas key could not be validated" );
	glob_key_validated = false;
}

// [eof]
