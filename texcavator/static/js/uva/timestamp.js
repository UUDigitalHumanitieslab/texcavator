// FL-25-Mar-2013 Created
// FL-29-Jan-2014 Changed

var client_timestamp = "29-Jan-2014 15:17";		// in Toolbar About popup
var server_timestamp = "";

function getClientTimestamp()
{
	return client_timestamp;
}

function setServerTimestamp( timestamp )
{
	server_timestamp = timestamp;
}

function getServerTimestamp()
{
	return server_timestamp;
}

// [eof]
