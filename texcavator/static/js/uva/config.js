// FL-12-Sep-2012 Created
// FL-06-Dec-2013 Changed

dojo.require( "dijit.Tooltip" );

//dijit.Tooltip.defaultPosition = [ "below" ];

/*
var config
var getConfig = function()
function storeCeleryOwner( celery_owner )
function storeDatastore( datastore )
function getSearchParameters()
var toolbarConfig = function()
var showConfig = function()
var createConfig = function()
*/



// default configuration parameters;
// changeable by toolbar Config
var config = {
	celery_owner : "",				// used for checking Celery processes
//	datastore: XTAS_DATASTORE,		// "DSTORE_MONGODB" or "DSTORE_ELASTICSEARCH"

	search: {
		// putting some types false is used by Search, but not by fetching the KB articles
		type: {
			article:	true,		// type: "artikel"						regular articles
			advert:		true,		// type: "advertentie"					advertisements
			illust:		true,		// type: "illustratie met onderschrift"	illustration+text
			family:		true		// type: "familiebericht"				family messages
		},
		distrib: {
			national:	true,		// type: "Landelijk"					Landelijke pers NL
			regional:	true,		// type: "Regionaal/lokaal"				Regionaal/lokale pers NL
			antilles:	true,		// type: "Nederlandse Antillen"			Nederlandse Antillen
			surinam:	true,		// type: "Suriname"						Suriname
			indonesia:	true		// type: "Nederlands-Indië/Indonesië"	Indonesië
		},
		chunk_size : 20
	},

	cloud: {				// word cloud
		// fixed cloud params
	//	words:    true,			// 
	//	order:   "count",		// ordering of response wordlist: "count", or "alpha" (default)
	//	output:  "json",		// "json", "xml"

	//	system_stopwords: "apos,quot,0,1,2,3,4,5,6,7,8,9,10,11,000,_,__,den,de,in,ter,ten",

		// settable cloud params
		stopwords_str:	"",			// loaded from db
	//	stopwords_cat:	"singleq",	// stopword category: "singleq", "allqs", "system"
		stopwords_clean:false,		// remove superfluous stopwords
		stopwords:		true,		// remove stopwords from list
		stopshort:		true,		// remove very short words
		stoplimit:		2,			// require word length > stoplimit

		refresh:		false,		// false: get cloud from cache; true: force recompute
		fontscale:		50,			// font scale factor
		fontreduce:		false,		// reduce fontsize differences
		stems:			false, 		// apply stemming

		NER:			false,		// Named Entity Recognition
		maxwords:		100,		// default max words displayed
		render:			"svg"		// "svg" or "canvas"
	},

	timeline: {				// timeline chart
		normalize:    false,	// normalize document counts
		burst_detect: true		// burst detection (red)
	},

	cloudexport: {			// cloud data export
		separator:      "tab",		// "comma", or "tab"
		normalize_ws:    true,		// for NER terms
		comma2semicolon: false,		// for NER terms
	//	cloud2export:   "normal"	// "normal" or "burst"
	},

	sentiment: {			// sentiment
		highlight: false
	},

	querydataexport: {		// query data
		format: "csv"		// "json", "xml", or "csv"
	}

}

var getConfig = function()
{ return config; }


function storeCeleryOwner( celery_owner )
{
	config[ "celery_owner" ] = celery_owner;
	console.log( "celery_owner: " + celery_owner );
}

function storeDatastore( datastore )
{
	config[ "datastore" ] = datastore;
	console.log( "xTAS datastore: " + datastore );
}


function getSearchParameters()
{
	params = {
		datastore      : config[ "datastore" ],
		maximumRecords : config[ "search" ][ "chunk_size" ],

		st_article     : config[ "search" ][ "type" ][ "article" ],
		st_advert      : config[ "search" ][ "type" ][ "advert" ],
		st_illust      : config[ "search" ][ "type" ][ "illust" ],
		st_family      : config[ "search" ][ "type" ][ "family" ],

		sd_national    : config[ "search" ][ "distrib" ][ "national" ],
		sd_regional    : config[ "search" ][ "distrib" ][ "regional" ],
		sd_antilles    : config[ "search" ][ "distrib" ][ "antilles" ],
		sd_surinam     : config[ "search" ][ "distrib" ][ "surinam" ],
		sd_indonesia   : config[ "search" ][ "distrib" ][ "indonesia" ],

		dateRange      : getDateRangeString()
	};

	return params;
}


var toolbarConfig = function()
{
	if( ! dijit.byId( "config" ) )
	{
	//	console.log( "creating config" );
		createConfig();
	}
	showConfig();
}

var showConfig = function()
{
	dijit.byId( "config" ).show();
}

var createConfig = function()
{
	var dlgConfig = new dijit.Dialog({
		id: "config",
		title: "Configuration"
	});

	dojo.style( dlgConfig.closeButtonNode, "visibility", "hidden" );	// hide the ordinary close button

	var container = dlgConfig.containerNode;

	var tcdiv = dojo.create( "div", { id: "tc-div-config" }, container );
	var tabCont = new dijit.layout.TabContainer({
		style: "background-color: white; width: 450px; height: 345px; line-height: 18pt"
	}, "tc-div-config" );


	// search tab
	var cpSearch = new dijit.layout.ContentPane({
		title: "Search",
		content: "<b>Search options</b><br/>"
	});
	tabCont.addChild( cpSearch );

	// for the time being; must be treated as daterange cloud!
	if( config[ "datastore" ] == "DSTORE_ELASTICSEARCH" )
	{ var disabled = false; }		// make false when properly debugged
	else
	{ var disabled = true; }


	var divArticleType = dojo.create( "div", {
		id: "div-articletype"
	}, cpSearch.domNode );

	var textArticleType = dojo.create( "label", {
		id: "text-articletype",
		for: "div-articletype",
		innerHTML: "Article type<br/>"
	}, cpSearch.domNode );


	var divTypeArticle = dojo.create( "div", {
		id: "div-type-article"
	}, cpSearch.domNode );

	var cbTypeArticle = new dijit.form.CheckBox({
		id: "cb-type-article",
		disabled: disabled,
		checked: config[ "search" ][ "type" ][ "article" ],
		onChange: function( btn ) {
			config[ "search" ][ "type" ][ "article" ] = btn;
			check_dctypes();
		}
	}, divTypeArticle );

	var labelypeArticle = dojo.create( "label", {
		id: "label-type-article",
		for: "cb-type-article",
		innerHTML: "&nbsp;Search KB regular articles<br/>"
	}, cpSearch.domNode );


	var divTypeAdvert = dojo.create( "div", {
		id: "div-type-advert"
	}, cpSearch.domNode );

	var cbTypeAdvert = new dijit.form.CheckBox({
		id: "cb-type-advert",
		disabled: disabled,
		checked: config[ "search" ][ "type" ][ "advert" ],
		onChange: function( btn ) {
			config[ "search" ][ "type" ][ "advert" ] = btn;
			check_dctypes();
		}
	}, divTypeAdvert );

	var labelypeAdvert = dojo.create( "label", {
		id: "label-type-advert",
		for: "cb-type-advert",
		innerHTML: "&nbsp;Search KB advertisements<br/>"
	}, cpSearch.domNode );


	var divTypeIllust = dojo.create( "div", {
		id: "div-type-illust"
	}, cpSearch.domNode );

	var cbTypeIllust = new dijit.form.CheckBox({
		id: "cb-type-illust",
		disabled: disabled,
		checked: config[ "search" ][ "type" ][ "illust" ],
		onChange: function( btn ) {
			config[ "search" ][ "type" ][ "illust" ] = btn;
			check_dctypes();
		}
	}, divTypeIllust );

	var labelypeIllust = dojo.create( "label", {
		id: "label-type-illust",
		for: "cb-type-illust",
		innerHTML: "&nbsp;Search KB illustration text<br/>"
	}, cpSearch.domNode );


	var divTypeFamily = dojo.create( "div", {
		id: "div-type-family"
	}, cpSearch.domNode );

	var cbTypeFamily = new dijit.form.CheckBox({
		id: "cb-type-family",
		disabled: disabled,
		checked: config[ "search" ][ "type" ][ "family" ],
		onChange: function( btn ) {
			config[ "search" ][ "type" ][ "family" ] = btn;
			check_dctypes();
		}
	}, divTypeFamily );

	var labelypeFamily = dojo.create( "label", {
		id: "label-type-family",
		for: "cb-type-family",
		innerHTML: "&nbsp;Search KB family messages<br/>"
	}, cpSearch.domNode );


	var divDistribution = dojo.create( "div", {
		id: "div-distribution"
	}, cpSearch.domNode );

	var textDistribution = dojo.create( "label", {
		id: "text-distribution",
		for: "div-distribution",
		innerHTML: "<hr>Distribution<br/>"
	}, cpSearch.domNode );



	var divDistribNationalNL = dojo.create( "div", {
		id: "div-distrib-national-nl"
	}, cpSearch.domNode );

	var cbDistribNationalNL = new dijit.form.CheckBox({
		id: "cb-distrib-national-nl",
		disabled: disabled,
		checked: config[ "search" ][ "distrib" ][ "national" ],
		onChange: function( btn ) {
			config[ "search" ][ "distrib" ][ "national" ] = btn;
			check_dctypes();
		}
	}, divDistribNationalNL );

	var labelDistribNationalNL = dojo.create( "label", {
		id: "label-distrib-national",
		for: "cb-distrib-national",
		innerHTML: "&nbsp;National NL<br/>"
	}, cpSearch.domNode );


	var divDistribRegionalNL = dojo.create( "div", {
		id: "div-distrib-regional"
	}, cpSearch.domNode );

	var cbDistribRegionalNL = new dijit.form.CheckBox({
		id: "cb-distrib-regional",
		disabled: disabled,
		checked: config[ "search" ][ "distrib" ][ "regional" ],
		onChange: function( btn ) {
			config[ "search" ][ "distrib" ][ "regional" ] = btn;
			check_dctypes();
		}
	}, divDistribRegionalNL );

	var labelDistribRegionalNL = dojo.create( "label", {
		id: "label-distrib-regional",
		for: "cb-distrib-regional",
		innerHTML: "&nbsp;Regional NL<br/>"
	}, cpSearch.domNode );


	var divDistribAntillen = dojo.create( "div", {
		id: "div-distrib-antilles"
	}, cpSearch.domNode );

	var cbDistribAntillen = new dijit.form.CheckBox({
		id: "cb-distrib-antilles",
		disabled: disabled,
		checked: config[ "search" ][ "distrib" ][ "antilles" ],
		onChange: function( btn ) {
			config[ "search" ][ "distrib" ][ "antilles" ] = btn;
			check_dctypes();
		}
	}, divDistribAntillen );

	var labelDistribAntillen = dojo.create( "label", {
		id: "label-distrib-antilles",
		for: "cb-distrib-antilles",
		innerHTML: "&nbsp;Antillen<br/>"
	}, cpSearch.domNode );


	var divDistribSurinam = dojo.create( "div", {
		id: "div-distrib-surinam"
	}, cpSearch.domNode );

	var cbDistribSurinam = new dijit.form.CheckBox({
		id: "cb-distrib-surinam",
		disabled: disabled,
		checked: config[ "search" ][ "distrib" ][ "surinam" ],
		onChange: function( btn ) {
			config[ "search" ][ "distrib" ][ "surinam" ] = btn;
			check_dctypes();
		}
	}, divDistribSurinam );

	var labelDistribSurinam = dojo.create( "label", {
		id: "label-distrib-surinam",
		for: "cb-distrib-surinam",
		innerHTML: "&nbsp;Surinam<br/>"
	}, cpSearch.domNode );


	var divDistribIndonesia = dojo.create( "div", {
		id: "div-distrib-indonesia"
	}, cpSearch.domNode );

	var cbDistribIndonesia = new dijit.form.CheckBox({
		id: "cb-distrib-indonesia",
		disabled: disabled,
		checked: config[ "search" ][ "distrib" ][ "indonesia" ],
		onChange: function( btn ) {
			config[ "search" ][ "distrib" ][ "indonesia" ] = btn;
			check_dctypes();
		}
	}, divDistribIndonesia );

	var labelDistribIndonesia = dojo.create( "label", {
		id: "label-distrib-indonesia",
		for: "cb-distrib-indonesia",
		innerHTML: "&nbsp;Indonesia<br/><hr>"
	}, cpSearch.domNode );


	/*
	var divFixedSearch = dojo.create( "div", {
		id: "div-fixed-search"
	}, cpSearch.domNode );

	var textFixedSearch = dojo.create( "label", {
		id: "text-fixed-search",
		for: "div-fixed-search",
		innerHTML: "(Fixed to only 'regular articles' for the time being.)<br/>"
	}, cpSearch.domNode );
	*/

	var divSearchChunk = dojo.create( "div", {
		id: "div-search-chunk"
	}, cpSearch.domNode );

	var searchCunkSpinner = new dijit.form.NumberSpinner({
		id: "ns-search-chunk",
		smallDelta: 5,
		constraints: { min: 10, max: 500, places: 0 },
		style: "width:50px",
		intermediateChanges: "true",
		value: config[ "search" ][ "chunk_size" ],
		onChange: function( value ) { config[ "search" ][ "chunk_size" ] = value; }
	}, divSearchChunk );

	var labelSearchChunk = dojo.create( "label", {
		id: "label-search_chunk",
		for: "ns-search-chunk",
		innerHTML: "&nbsp;Search chunk size<br/>"
	}, cpSearch.domNode );


	var check_dctypes = function()
	{
	//	console.log( "check_dctypes()" );
		// prevent unselection of all options
		if( config[ "search" ][ "type" ][ "article" ] == false && 
			config[ "search" ][ "type" ][ "advert" ]  == false && 
			config[ "search" ][ "type" ][ "illust" ]  == false && 
			config[ "search" ][ "type" ][ "family" ]  == false )
		{
			// all false: -> make all true
			dijit.byId( "cb-type-article" ).set( "value",  true );
			dijit.byId( "cb-type-advert" ). set( "value",  true );
			dijit.byId( "cb-type-illust" ). set( "value",  true );
			dijit.byId( "cb-type-family" ). set( "value",  true );
		}
	}


	// cloud tab
	var cpCloud = new dijit.layout.ContentPane({
		title: "Cloud",
		content: "<b>Word cloud options</b><br/>"
	});
	tabCont.addChild( cpCloud );


	var divRefresh = dojo.create( "div", {
		id: "div-refresh"
	}, cpCloud.domNode );

	var cbRefresh = new dijit.form.CheckBox({
		id: "cb-refresh",
		checked: config[ "cloud" ][ "refresh" ],
		onChange: function( btn ) { config[ "cloud" ][ "refresh" ] = btn; }
	}, divRefresh );

	var labelRefresh = dojo.create( "label", {
		id: "label-refresh",
		for: "cb-refresh",
		innerHTML: "&nbsp;Require fresh cloud (ignore browser cache)<br/>"
	}, cpCloud.domNode );


	var divFReduce = dojo.create( "div", {
		id: "div-freduce"
	}, cpCloud.domNode );

	var cbFReduce = new dijit.form.CheckBox({
		id: "cb-freduce",
		checked: config[ "cloud" ][ "fontreduce" ],
		onChange: function( btn ) { config[ "cloud" ][ "fontreduce" ] = btn; }
	}, divFReduce );

	var labelFReduce = dojo.create( "label", {
		id: "label-freduce",
		for: "cb-freduce",
		innerHTML: "&nbsp;Reduce font size differences<br/>"
	}, cpCloud.domNode );


	var divFScale = dojo.create( "div", {
		id: "div-fscale"
	}, cpCloud.domNode );

	var fscaleSpinner = new dijit.form.NumberSpinner({
		id: "ns-fscale",
		smallDelta: 5,
		constraints: { min: 10, max: 100, places: 0 },
		style: "width:50px",
		intermediateChanges: "true",
		value: config[ "cloud" ][ "fontscale" ],
		onChange: function( value ) { config[ "cloud" ][ "fontscale" ] = value; }
	}, divFScale );

	var labelFScale = dojo.create( "label", {
		id: "label-fscale",
		for: "ns-fscale",
		innerHTML: "&nbsp;Font scale factor<br/>"
	}, cpCloud.domNode );


	var divStop = dojo.create( "div", {
		id: "div-stop"
	}, cpCloud.domNode );

	var cbStop = new dijit.form.CheckBox({
		id: "cb-stop",
		checked: config[ "cloud" ][ "stopwords" ],
		onChange: function( btn ) { config[ "cloud" ][ "stopwords" ] = btn; }
	}, divStop );

	var labelStop = dojo.create( "label", {
		id: "label-stop",
		for: "cb-stop",
		innerHTML: "&nbsp;Remove stop words<br/>"
	}, cpCloud.domNode );


	var divWMinLen = dojo.create( "div", {
		id: "div-wminlen"
	}, cpCloud.domNode );

	var wminlenSpinner = new dijit.form.NumberSpinner({
		id: "ns-wminlen",
		smallDelta: 1,
		constraints: { min: 1, max: 10, places: 0 },
		style: "width:50px",
		intermediateChanges: "true",
		value: config[ "cloud" ][ "stoplimit" ],
		onChange: function( value ) {
			config[ "cloud" ][ "stoplimit" ] = value;
			var lenrequired = 1 + config[ 'cloud' ][ 'stoplimit' ];
			if( lenrequired == 1 ) 
			{ var charstr = "character"; }
			else
			{ var charstr = "characters"; }
			labelShort.innerHTML = "&nbsp;Remove words shorter than " + lenrequired + " " + charstr + "<br/>";
		}
	}, divWMinLen );

	var labelWMinLen = dojo.create( "label", {
		id: "label-wminlen",
		for: "ns-wminlen",
		innerHTML: "&nbsp;Minimum word length<br/>"
	}, cpCloud.domNode );


	var divShort = dojo.create( "div", {
		id: "div-short"
	}, cpCloud.domNode );

	var cbShort = new dijit.form.CheckBox({
		id: "cb-short",
		checked: config[ "cloud" ][ "stopshort" ],
		onChange: function( btn ) { config[ "cloud" ][ "stopshort" ] = btn; }
	}, divShort );

	var lenrequired = 1 + config[ 'cloud' ][ 'stoplimit' ];
	var labelShort = dojo.create( "label", {
		id: "label-short",
		for: "cb-short",
		innerHTML: "&nbsp;Remove words shorter than " + lenrequired + " characters<br/>"
	}, cpCloud.domNode );


	var divStem = dojo.create( "div", {
		id: "div-stem"
	}, cpCloud.domNode );

	var cbStem = new dijit.form.CheckBox({
		id: "cb-stem",
		checked: config[ "cloud" ][ "stems" ],
		onChange: function( btn ) {
			config[ "cloud" ][ "stems" ] = btn;
			if( btn == true ) { dijit.byId( "cb-ner" ).set( "checked", false ); }		// either stemming, or NER
		}
	}, divStem );

	var labelStem = dojo.create( "label", {
		id: "label-stem",
		for: "cb-stem",
		innerHTML: "&nbsp;Stemming<br/>"
	}, cpCloud.domNode );


	var divNer = dojo.create( "div", {
		id: "div-ner"
	}, cpCloud.domNode );

	var cbNer = new dijit.form.CheckBox({
		disabled: false,
		id: "cb-ner",
		checked: config[ "cloud" ][ "NER" ],
		onChange: function( btn ) {
			config[ "cloud" ][ "NER" ] = btn;
			if( btn == true ) { dijit.byId( "cb-stem" ).set( "checked", false ); }		// either stemming, or NER
		}
	}, divNer );

	var labelNer = dojo.create( "label", {
		id: "label-ner",
		for: "cb-ner",
		innerHTML: "&nbsp;Named Entity Recognition<br/>"
	}, cpCloud.domNode );


	var divWCount = dojo.create( "div", {
		id: "div-wcount"
	}, cpCloud.domNode );

	var wcountSpinner = new dijit.form.NumberSpinner({
		id: "ns-wcount",
		smallDelta: 10,
		constraints: { min: 10, max: 500, places: 0 },
		style: "width:50px",
		intermediateChanges: "true",
		value: config[ "cloud" ][ "maxwords" ],
		onChange: function( value ) { config[ "cloud" ][ "maxwords" ] = value; }
	}, divWCount );

	var labelWCount = dojo.create( "label", {
		id: "label-wcount",
		for: "ns-wcount",
		innerHTML: "&nbsp;Max # of words in cloud<br/>"
	}, cpCloud.domNode );


	var divCloudRender = dojo.create( "div", {
		id: "div-cloudrender"
	}, cpCloud.domNode );

	var textCloudRender = dojo.create( "label", {
		id: "text-cloudrender",
		for: "div-cloudrender",
		innerHTML: "Cloud rendering<br/>"
	}, cpCloud.domNode );


	var divSvgRender = dojo.create( "div", {
		id: "div-svgrender"
	}, cpCloud.domNode );

	if( config[ "cloud" ][ "render" ] === "svg" )
	{ var svgrender_val = true; }
	else
	{ var svgrender_val = false; }

	var rbSvgRender = new dijit.form.RadioButton({
		id: "rb-svgrender",
		checked: svgrender_val,
		onChange: function( btn )
		{
			if( btn == true )
			{ config[ "cloud" ][ "render" ] = "svg"; }
		},
	}, "div-svgrender");

	var labelSvgRender = dojo.create( "label", {
		id: "label-svgrender",
		for: "rb-svgrender",
		innerHTML: "&nbsp;SVG - Scalable Vector Graphics<br/>"
	}, cpCloud.domNode );


	var divCanvasRender = dojo.create( "div", {
		id: "div-canvasrender"
	}, cpCloud.domNode );

	if( config[ "cloud" ][ "render" ] === "canvas" )
	{ var canvasrender_val = true; }
	else
	{ var canvasrender_val = false; }

	var rbCanvasRender = new dijit.form.RadioButton({
		id: "rb-canvasrender",
		checked: canvasrender_val,
		onChange: function( btn )
		{
			if( btn == true )
			{ config[ "cloud" ][ "render" ] = "canvas"; }
		},
	}, "div-canvasrender");

	var labelCanvasRender = dojo.create( "label", {
		id: "label-canvasrender",
		for: "rb-canvasrender",
		innerHTML: "&nbsp;HTML Canvas<br/>"
	}, cpCloud.domNode );


	// timeline tab
	var cpTimeline = new dijit.layout.ContentPane({
		title: "Timeline",
		content: "<b>Timeline options</b><br/>"
	});
	tabCont.addChild( cpTimeline );


	var divNormalize = dojo.create( "div", {
		id: "div-normalize"
	}, cpTimeline.domNode );

	var cbNormalize = new dijit.form.CheckBox({
		id: "cb-normalize",
		checked: config[ "timeline" ][ "normalize" ],
		onChange: function( btn ) 
		{ config[ "timeline" ][ "normalize" ] = btn; }
	}, divNormalize );

	var labelNormalize = dojo.create( "label", {
		id: "label-normalize",
		for: "cb-normalize",
		innerHTML: "&nbsp;Normalize document counts<br/>"
	}, cpTimeline.domNode );


	var divBurst = dojo.create( "div", {
		id: "div-burst"
	}, cpTimeline.domNode );

	var cbBurst = new dijit.form.CheckBox({
		id: "cb-burst",
		checked: config[ "timeline" ][ "burst_detect" ],
		onChange: function( btn ) { config[ "timeline" ][ "burst_detect" ] = btn; }
	}, divBurst );

	var labelBurst = dojo.create( "label", {
		id: "label-burst",
		for: "cb-burst",
		innerHTML: "&nbsp;Highlight bursts in Red<br/>"
	}, cpTimeline.domNode );


	// export tab
	var cloudexportcfg = config[ "cloudexport" ];
	var cpExport = new dijit.layout.ContentPane({
		title: "Export",
		content: "<b>Cloud CSV export options</b><br/>"
	});
	tabCont.addChild( cpExport );


	var divSepComma = dojo.create( "div", {
		id: "div-sepcomma"
	}, cpExport.domNode );

	if( cloudexportcfg.separator === "comma" )
	{ var sepcomma_val = true; }
	else
	{ var sepcomma_val = false; }

	var rbSepComma = new dijit.form.RadioButton({
		id: "rb-sepcomma",
		checked: sepcomma_val,
		onChange: function( btn )
		{
			if( btn == true )
			{ config[ "cloudexport" ][ "separator" ] = "comma"; }
		},
	}, "div-sepcomma");

	var labelSepComma = dojo.create( "label", {
		id: "label-sepcomma",
		for: "rb-sepcomma",
		innerHTML: "&nbsp;Comma separator<br/>"
	}, cpExport.domNode );


	var divSepTab = dojo.create( "div", {
		id: "div-septab"
	}, cpExport.domNode );

	if( cloudexportcfg.separator === "tab" )
	{ var septab_val = true; }
	else
	{ var septab_val = false; }

	var rbSepTab = new dijit.form.RadioButton({
		id: "rb-septab",
		checked: septab_val,
		onChange: function( btn )
		{
			if( btn == true )
			{ config[ "cloudexport" ][ "separator" ] = "tab"; }
		},
	}, "div-septab");

	var labelSepTab = dojo.create( "label", {
		id: "label-septab",
		for: "rb-septab",
		innerHTML: "&nbsp;Tab separator<br/>"
	}, cpExport.domNode );


	var divExportNER = dojo.create( "div", {
		id: "div-exportner"
	}, cpExport.domNode );

	var textExportNER = dojo.create( "label", {
		id: "text-exportner",
		for: "div-exportner",
		innerHTML: "<br/>NER cloud phrase options<br/>"
	}, cpExport.domNode );


	var divNormalizeWS = dojo.create( "div", {
		id: "div-normalize-ws"
	}, cpExport.domNode );

	var cbNormalizeWS = new dijit.form.CheckBox({
		id: "cb-normalize-ws",
		checked: config[ "cloudexport" ][ "normalize_ws" ],
		onChange: function( btn ) 
		{ config[ "cloudexport" ][ "normalize_ws" ] = btn; }
	}, divNormalizeWS );

	var labelNormalizeWS = dojo.create( "label", {
		id: "label-normalize-ws",
		for: "cb-normalize-ws",
		innerHTML: "&nbsp;Normalize whitespace<br/>"
	}, cpExport.domNode );


	var divComma2Semicolon = dojo.create( "div", {
		id: "div-comma2semicolon"
	}, cpExport.domNode );

	var cbComma2Semicolon = new dijit.form.CheckBox({
		id: "cb-comma2semicolon",
		checked: config[ "cloudexport" ][ "comma2semicolon" ],
		onChange: function( btn ) 
		{ config[ "cloudexport" ][ "comma2semicolon" ] = btn; }
	}, divComma2Semicolon );

	var labelComma2Semicolon = dojo.create( "label", {
		id: "label-comma2semicolon",
		for: "cb-comma2semicolon",
		innerHTML: "&nbsp;Replace comma by semicolon<br/>"
	}, cpExport.domNode );

	/*
	var divExportCloud = dojo.create( "div", {
		id: "div-exportcloud"
	}, cpExport.domNode );

	var textExportCloud = dojo.create( "label", {
		id: "text-exportcloud",
		for: "div-exportcloud",
		innerHTML: "<br/>Which cloud to export<br/>"
	}, cpExport.domNode );


	var divCloudNormal = dojo.create( "div", {
		id: "div-cloudnormal"
	}, cpExport.domNode );

	if( cloudexportcfg.cloud2export === "normal" )
	{ var cloud_normal_val = true; }
	else
	{ var cloud_normal_val = false; }

	var rbCloudNormal = new dijit.form.RadioButton({
		id: "rb-cloudnormal",
		checked: cloud_normal_val,
		onChange: function( btn )
		{
			if( btn == true )
			{ config[ "cloudexport" ][ "cloud2export" ] = "normal"; }
		},
	}, "div-cloudnormal");

	var labelCloudNormal = dojo.create( "label", {
		id: "label-cloudnormal",
		for: "rb-cloudnormal",
		innerHTML: "&nbsp;Export normal cloud<br/>"
	}, cpExport.domNode );


	var divCloudBurst = dojo.create( "div", {
		id: "div-cloudburst"
	}, cpExport.domNode );

	if( cloudexportcfg.cloud2export === "burst" )
	{ var cloud_burst_val = true; }
	else
	{ var cloud_burst_val = false; }

	var rbCloudBurst = new dijit.form.RadioButton({
		id: "rb-cloudburst",
		checked: cloud_burst_val,
		onChange: function( btn )
		{
			if( btn == true )
			{ config[ "cloudexport" ][ "cloud2export" ] = "burst"; }
		},
	}, "div-cloudburst");

	var labelCloudBurst = dojo.create( "label", {
		id: "label-cloudburst",
		for: "rb-cloudburst",
		innerHTML: "&nbsp;Export burst cloud<br/>"
	}, cpExport.domNode );
	*/

	// sentiment tab
	var sentimentcfg = config[ "sentiment" ];
	var cp_sentiment = new dijit.layout.ContentPane({
		title: "Sentiment",
		content: "<b>Sentiment options</b><br/>"
	});
	tabCont.addChild( cp_sentiment );

	var divHighlight = dojo.create( "div", {
		id: "div-highlight"
	}, cp_sentiment.domNode );

	var cbHighlight = new dijit.form.CheckBox({
		id: "cb-highlight",
		checked: config[ "sentiment" ][ "highlight" ],
		onChange: function( btn ) { config[ "sentiment" ][ "highlight" ] = btn; }
	}, divHighlight );

	var labelHighlight = dojo.create( "label", {
		id: "label-highlight",
		for: "cb-highlight",
		innerHTML: "&nbsp;Highlight sentiment words in article text<br/>"
	}, cp_sentiment.domNode );


	// NER tab
	var cp_ner = new dijit.layout.ContentPane({
		title: "NER",
		content: "<b>Named-Entity Recognition engine</b><br/>"
	});
	tabCont.addChild( cp_ner );


	var divStanford = dojo.create( "div", {
		id: "div-stanford"
	}, cp_ner.domNode );

	var rbStanford = new dijit.form.RadioButton({
		id: "rb-stanford",
		checked: true
	}, "div-stanford");

	var labelStanford = dojo.create( "label", {
		id: "label-stanford",
		for: "rb-stanford",
		innerHTML: "&nbsp;Stanford<br/>"
	}, cp_ner.domNode );


	var divLingpipe = dojo.create( "div", {
		id: "div-lingpipe"
	}, cp_ner.domNode );

	var rbLingpipe = new dijit.form.RadioButton({
		id: "rb-lingpipe",
		checked: false,
		disabled: true
	}, "div-lingpipe");

	var labelLingpipe = dojo.create( "label", {
		id: "label-lingpipe",
		for: "rb-lingpipe",
		innerHTML: "&nbsp;<font color=grey>LingPipe</font><br/>"
	}, cp_ner.domNode );


	var divTNT = dojo.create( "div", {
		id: "div-tnt"
	}, cp_ner.domNode );

	var rbTNT = new dijit.form.RadioButton({
		id: "rb-tnt",
		checked: false,
		disabled: true
	}, "div-tnt");

	var labelTNT = dojo.create( "label", {
		id: "label-tnt",
		for: "rb-tnt",
		innerHTML: "&nbsp;<font color=grey>TNT</font><br/>"
	}, cp_ner.domNode );


	var divLBJlars = dojo.create( "div", {
		id: "div-lbjlars"
	}, cp_ner.domNode );

	var rbLBJlars = new dijit.form.RadioButton({
		id: "rb-lbjlars",
		checked: false,
		disabled: true
	}, "div-lbjlars");

	var labelLBJlars = dojo.create( "label", {
		id: "label-lbjlars",
		for: "rb-lbjlars",
		innerHTML: "&nbsp;<font color=grey>LBJ Lars</font><br/>"
	}, cp_ner.domNode );


	// System tab
	var cp_celery = new dijit.layout.ContentPane({
		title: "System",
		content: "<b>Celery task queue</b><br/>"
	});
	tabCont.addChild( cp_celery );


	var divCheck0 = dojo.create( "div", {
		id: "div-check0",
	}, cp_celery.domNode );

	var labelCheck0 = dojo.create( "label", {
		innerHTML: "&nbsp;The task queue is responsible for loading the Meta- and OCR data from the KB<br/>",
		id: "label-check0",
		for: "div-check0",
	}, cp_celery.domNode );

	var divCheck = dojo.create( "div", {
		id: "div-check"
	}, cp_celery.domNode );

	var bCheck = new dijit.form.Button({
		id: "btn-check",
		label: "<img src='/static/image/icon/Tango/16/actions/system-run.png'/> Check",
		showLabel: true,
		onClick: function()
		{
			celeryCheck( config[ "celery_owner" ] );				// celery.js
			dijit.byId( "config" ).hide();
		}
	},"div-check" );

	var labelCheck = dojo.create( "label", {
		id: "label-check",
		for: "btn-check",
		innerHTML: "&nbsp;the Celery task queue<br/>"
	}, cp_celery.domNode );



	var divXtasDatastore = dojo.create( "div", {
		id: "div-xtas-datastore"
	}, cp_celery.domNode );

	var textXtasDatastore = dojo.create( "label", {
		id: "text-retrieve-ocr",
		for: "div-xtas-datastore",
		innerHTML: "<br/><b>xTAS datastore</b><br/>"
	}, cp_celery.domNode );


	var divMongoDB = dojo.create( "div", {
		id: "div-mongodb"
	}, cp_celery.domNode );

	if( config[ "datastore" ] === "DSTORE_MONGODB" )
	{ var mongodb_val = true; }
	else
	{ var mongodb_val = false; }

	var rbMongoDB = new dijit.form.RadioButton({
		id: "rb-mongodb",
		checked: mongodb_val,
		disabled: true,				// from settings.py
		onChange: function( btn )
		{
			if( btn == true )
			{ config[ "datastore" ] = "DSTORE_MONGODB"; }
		},
	}, "div-mongodb");

	var labelMongoDB = dojo.create( "label", {
		id: "label-mongodb",
		for: "rb-mongodb",
		innerHTML: "&nbsp;MongoDB (OCR from KB)<br/>"
	}, cp_celery.domNode );


	var divElasticSearch = dojo.create( "div", {
		id: "div-elasticsearch"
	}, cp_celery.domNode );

	if( config[ "datastore" ] === "DSTORE_ELASTICSEARCH" )
	{ var elasticsearch_val = true; }
	else
	{ var elasticsearch_val = false; }

	var rbElasticSearch = new dijit.form.RadioButton({
		id: "rb-elasticsearch",
		checked: elasticsearch_val,
		disabled: true,				// from settings.py
		onChange: function( btn )
		{
			if( btn == true )
			{ config[ "datastore" ] = "DSTORE_ELASTICSEARCH"; }
		},
	}, "div-elasticsearch");

	var labelElasticSearch = dojo.create( "label", {
		id: "label-elasticsearch",
		for: "rb-elasticsearch",
		innerHTML: "&nbsp;ElasticSearch (OCR preloaded)<br/>"
	}, cp_celery.domNode );


	// Action bar
	var actionBar = dojo.create( "div", {
		className: "dijitDialogPaneActionBar",
		style: "height: 30px"
	}, container );

	var bOK = new dijit.form.Button({
		label: "<img src='/static/image/icon/Tango/16/actions/dialog-ok.png'/> OK",
		showLabel: true,
		role: "presentation",
		onClick: function() { dijit.byId( "config" ).hide(); }
	});
	actionBar.appendChild( bOK.domNode );
}; // createConfig

// [eof]
