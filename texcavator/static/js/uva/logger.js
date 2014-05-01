// Declare out the name of the test module to make dojo's module loader happy.
dojo.provide("uva.logger");

uva.logger.log = function(message) {
	console.log("[LOG] " + message);
	dojo.xhrGet({
		url: "/services/logger/",			// django development server
	//	url: "/biland/services/logger/",	// django production server
		content: {message: message},
		handleAs: "text",
		load: function(data) {
			if(data != "OK")
				console.log("Invalid answer from logger: " + data);
		},
		error: function(err){
		    console.error("Error in logger: " + err); // display the error
		}
	});	
};
