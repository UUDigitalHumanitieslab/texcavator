try {
	dojo.registerModulePath( "uva", "../../uva" );
} catch( error ) {
	console.log( "Dojo is required for BiLand." );
}

dojo.require( "uva.logger" );
