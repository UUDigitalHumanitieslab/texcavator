dojo.require("dijit.ProgressBar");

function onClickExecuteCloud( queryID )
{
	console.log("onClickExecuteCloud() queryID: " + queryID);

	// Cancel any existing request for a word cloud
	if (current_task_id !== undefined) {
		cancel_celery_task(current_task_id);
	}

	// Select the cloud tab
	dijit.byId("articleContainer").selectChild(dijit.byId("cloudPane"));

	// Create a progress bar and cancel button
	dojo.byId("cloudPane").innerHTML = '';
	var pBar = new dijit.ProgressBar({indeterminate: true});
	dojo.place(pBar.domNode, dojo.byId("cloudPane"), "first");
	dojo.place('<div id="wordcloud_progress">Progress: 0 of ?</div><div id="cancel_wordcloud"></div>', pBar.domNode, "after");

	// Clear the canvas
	canvas = dojo.byId("cloudCanvas");
	if (canvas && canvas.getContext) {
		var context = canvas.getContext( '2d' );        // get the 2d context
		if( context ) { context.clearRect ( 0, 0, canvas.width, canvas.height ); }
	}

	// Set the cloud parameters
	var params = {
		queryID: queryID
	};
	params = getCloudParameters(params);

	// Create a request for a word cloud, and then start polling for the cloud
	dojo.xhrGet({
		url: "services/cloud",
		content: params, 
		failOk: false,            // true: No dojo console error message
		handleAs: "json",
	}).then(function( resp ){
		var json_data = resp;
		if ( typeof( json_data ) == "string" ) { 
			json_data = dojo.fromJson( json_data ); 
		}
		
		var status = json_data.status;

		if ( json_data.status != "ok" ) {
			console.warn( "onClickExecuteCloud: " + json_data.error );
			var title = "Cloud data request failed";
			var buttons = { "OK": true };
			dojo.byId('cloudPane').innerHTML = '<div>' + title + '.</div>';
			genDialog( title, json_data.error, buttons );
			return null;
		}
		else {
			console.log("got task_id: " + json_data.task);
			return json_data.task;
		}
		}, function( err ) { console.error( err ); }
	).then(function(task_id) {
		console.log("Start polling!");
		console.log("task_id: " + task_id);
		if(task_id) {
			// check every second
			check_status(task_id);
			// create cancel button
			dojo.byId('cancel_wordcloud').innerHTML = '<button onClick="cancel_celery_task(\''+task_id+'\');">Cancel wordcloud</button>';
		} else {
			console.log('Error: no task_id returned.');
		}
	});
} // onClickExecuteCloud

// Global variables to keep track of the current word cloud task
var current_task_id;
var current_interval_id;

/*
 * Functions for polling celery task
 */
 function handle_error(xhr, textStatus, errorThrown) {
	 clearTimeout(current_interval_id);
	 console.log("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
 }

 function show_status(obj) {
	 console.log(obj);
	 if (obj.error) {
		clearTimeout(current_interval_id);
		console.log(obj.error);
	 }
	 if (obj.status == "WAITING"){
		if ('total' in obj){
			// update progress
			console.log('Update wordcloud progress');
			update_wordcloud_progress(obj.current, obj.total);
		}
		clearTimeout(current_interval_id);
		check_status(current_task_id);
	 }
	 else if (obj.status == "ok"){
		console.log("finished generating cloud");
		clearTimeout(current_interval_id);
		// show the solution
		if (obj.burstcloud){
			createCloud( "burst", obj, "cloud" );
		} else {
			createCloud( "normal", obj, "cloudPane", "borderContainer" );
		}
	 } else {
		clearTimeout(current_interval_id);
		console.log("other status for celery task");
		console.log(obj);
		var title = "Wordcloud failed";
		var buttons = { "OK": true };
		dojo.byId('cloudPane').innerHTML = '<div>' + title + '.</div>';
		genDialog( title, obj.msg, buttons );
	 }
}

function check_status(task_id) {
	current_task_id = task_id;
	current_interval_id = setTimeout(function(){
		console.log('checking status of task_id ' + task_id);
		$.ajax({
			method: "GET",
			url: "/services/task_status/" + task_id,
			success: show_status,
			error: handle_error
		});
	}, 1000);
}
		
function update_wordcloud_progress(current, total){
	if(dojo.byId("wordcloud_progress")){
		dojo.byId( "wordcloud_progress" ).innerHTML = "Progress: "+current+" of "+total;
	}
}

// Cancels the given Celery task id, synchronously
function cancel_celery_task(task_id) {
	console.log('Canceling celery task ' + task_id);

	clearTimeout(current_interval_id);

	$.ajax({
		method: "GET",
		url: "/services/cancel_task/" + task_id,
		async: false,
		success: dojo.byId('cloudPane').innerHTML = '<div>Canceled generating wordcloud.</div>',
		error: handle_error
	});
}

// Creates a single article cloud
var retrieveRecordCloudData = function( record_id )
{
	console.log( "retrieveRecordCloudData: " + record_id );

	// Cancel any existing request for a word cloud
	if (current_task_id !== undefined) {
		cancel_celery_task(current_task_id);
	}

	// Collect the parameters
	var params = { "record_id": record_id };
	params = getCloudParameters( params );

	// Create a request for a word cloud
	dojo.xhrGet({
		url: "services/cloud",
		content: params,
		handleAs: "json",
		load: function(response)
		{
			if( response.status != "ok" )
			{
				console.warn( "retrieveRecordCloudData: " + response.error );
				genDialog( "Cloud data request failed", response.error, { "OK": true } );
			}
			else
			{
			    console.log( "Creating cloud" );
				createCloud( "article", response, "cloudPane", "borderContainer" );
			}
		},
		error: function(error) {
			console.error(error);
			return error;
		}
	});
};

var createCloud = function( cloud_src, cloud_data, target, container )
{
	console.log( "createCloud: " + cloud_src + " in " + target + " of " + container );

	if ( cloud_src != "burst" ) {
        var contentBox = dojo.contentBox( target );
        var rheight = contentBox.h -4;

        // Animate the cloud coming into view
        var animation = dojo.animateProperty({
            node: target,
            properties: { height: {end: rheight, units: "px"} }
        });

        // Update borderContainer on every step, as changing height doesn't automatically do so.
        dojo.connect( animation, "onAnimate", function() { dijit.byId( container ).layout(); });
        animation.play();
	}

	placeCloudInTarget( cloud_src, cloud_data, target );

    // Add download button
    var cloudDownload = new dijit.form.Button({
        label: "Show cloud data",
	    style: "float: right;",
        onClick: showCloudDlg,
    });
    $("#statusline").after(cloudDownload.domNode);

    // Add button to switch between stemmed and non-stemmed cloud
    var useStems = getConfig().cloud.stems;
    var switchStem = new dijit.form.Button({
        label: "Switch to " + (useStems ? "non-stemmed" : "stemmed") + " cloud",
	    style: "float: right;",
        onClick: function() {
            getConfig().cloud.stems = !useStems;
            refreshCloud(cloud_src);
        },
    });
    $("#statusline").after(switchStem.domNode);

    // Add button to switch between absolute and normalized (tf-idf) frequencies
    if (!useStems)
    {
        var useIdf = getConfig().cloud.idf;
        var switchIdf = new dijit.form.Button({
            label: "Switch to " + (useIdf ? "absolute" : "normalized") + " frequencies",
            style: "float: right;",
            onClick: function() {
                getConfig().cloud.idf = !useIdf;
                refreshCloud(cloud_src);
            },
        });
        $("#statusline").after(switchIdf.domNode);
    }
};

// Reloads the current cloud with other (possibly) different parameter settings.
function refreshCloud(cloud_src)
{
    switch (cloud_src) {
        case "article":
            retrieveRecordCloudData($(".active-article").prop('id'));
            break;
        case "normal":
            onClickExecuteCloud(retrieveQueryID());
            break;
        case "burst":
            burstCloud(retrieveQueryID());
            break;
        default:
            genDialog("Error while generating cloud", "Unknown method of cloud generation", { "OK": true });
    }
}