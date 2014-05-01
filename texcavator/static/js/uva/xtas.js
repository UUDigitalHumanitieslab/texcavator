// DO-%%-%%%-2011 Created
// FL-24-May-2013 repeated request with taskid
// FL-09-Sep-2013 

// Declare the name of the test module to make dojo's module loader happy.
dojo.provide( "uva.xtas" );


dojo.declare( "Xtas", null,
{
	url: "/services/xtas/",				// Django dev server
//	url: "/biland/services/xtas/",		// Apache uses prefix

	username: null,

	constructor: function( args )
	{
		dojo.mixin( this, args );		// args should contain xtasUrl
	},

	globalOptions:
	{
	//	handleAs: "xml",		// (legacy)
		handleAs: "json",		// xTAS
	},

	validateKey: function()
	{
		var validKey = false, username;
		var options = {
			sync: true,
			failOk: true,
			load: function( data ) {
				if( data !== null )
				{
				//	console.log( data );
				//	username = data.firstChild.getElementsByTagName( "name" )[ 0 ].firstChild.nodeValue;	// xml
					if( data.status === "ok" )
					{
						validKey = true;
						username = data.result.key;
					//	console.log( username );
					}
					else
					{
						alert( "Error:\nxTas key could not be validated" );
						validKey = false;
					}
				}
				else
				{ console.log( "validateKey(): " + "data is null" ); }
				return data;
			},
			error: function( data )
			{
				validKey = false;
				console.log( data );
				alert( "Error:\nxTas key could not be validated" );
				return data;
			}
		};
		this.get( "key", options );
		this.username = username;
		return validKey;
	},

	mixOptions: function( defaultOptions, options )
	{
		dojo.mixin( defaultOptions, this.globalOptions );
		dojo.mixin( defaultOptions, options );
		dojo.mixin( defaultOptions.content, this.globalOptions.content );
		if( defaultOptions != undefined && defaultOptions.content != undefined )
		{ dojo.mixin( defaultOptions.content, defaultOptions.content ); }
		if( options != undefined && options.content != undefined )
		{ dojo.mixin( defaultOptions.content, options.content ); }
	},

	get: function( service, options )
	{
		var defaultOptions = { url: this.url + service };
		this.mixOptions( defaultOptions, options );
		return dojo.xhrGet( defaultOptions );
	},

	post: function( service, options )
	{
	//	console.log( "xtas.js/post(), options: " );
	//	console.log( options );
		var defaultOptions = { url: this.url + service };
		this.mixOptions( defaultOptions, options );
		return dojo.xhrPost( defaultOptions );
	},

	postWaiting: function( service, options, callback, timeout )
	{
	//	console.log( "xtas.js/postWaiting(), options:" );
	//	console.log( "service: " + service );
	//	console.log( options );

		if( timeout == undefined ) timeout = 60;
		if( timeout <= 0 )
		{
			alert( "xtasPostWaiting timed out on service " + service );
			throw Error( "xtasPostWaiting timed out on service " + service );
		}

		var defaultOptions = { url: this.url + service };
		this.mixOptions( defaultOptions, options );
	//	options[ "failOk" ] = true;
	    defaultOptions[ "handleAs" ] = "text";
		var deferred = this.post( service, defaultOptions );
		var xtasObject = this;

		deferred.addErrback( function( error ) {
			throw error;
		});

		deferred.addCallback( function( data )
		{
		//	console.log( "data: " + data );
			if( data == null )
			{ console.log( "xTas result is null." ); }

			else
			{
				if( data.length == 0 )
				{ console.log( "xTas return empty result." ); }

				// xml
				else if( data.match( "<status>waiting</status>" ) != null )
				{ console.log( "xTas is processing..." ); }
				else if( data.match( /\|\s*waiting\s*\|/i ) != null ) 
				{ console.log( "xTas is still processing..." ); }

				// json
				var parsedData = dojo.fromJson( data );
				var status = parsedData.status;
				if( status === "processing" )
				{
					var taskid = parsedData.taskid;
					console.log( "xTas is still processing, taskid: + " + taskid );
				}
				else
				{
					console.log( "xTas return." );
					return callback( data );
				} 
			}

			// No result yet, so waiting...
			var wait = 1;
			console.log( "Waiting for " + wait + " seconds, timeout in " + timeout + " seconds." );

			if( service == "cloud/" )
			{   // http://zookst17.science.uva.nl:8000/api/cloud_bytaskid?key=test&taskid=862f0c75c0701b1cab8ab63cddadb23d
				var taskid = parsedData.taskid;
				console.log( "followup fetch using cloud_bytaskid call: " + taskid );
				options = { content: { "taskid" : taskid }, "handleAs": "json" };	// overwrite previous options
				setTimeout( xtasPostWaitingTimeoutHandler( xtasObject, "cloud_bytaskid/", options, callback, timeout-wait ), wait*1000 );
			}
			else
			{ setTimeout( xtasPostWaitingTimeoutHandler( xtasObject, service, options, callback, timeout-wait ), wait*1000 ); }
		});
		return deferred;
	},
});


function xtasPostWaitingTimeoutHandler( xtasObject, service, options, callback, timeout )
{
	return function() { xtasObject.postWaiting( service, options, callback, timeout ); };
}

// [eof]
