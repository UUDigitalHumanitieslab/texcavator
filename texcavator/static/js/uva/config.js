// FL-12-Sep-2012 Created
// FL-06-Dec-2013 Changed

dojo.require("dijit.Tooltip");

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
	celery_owner: "", // used for checking Celery processes

	search: {
		// putting some types false is used by Search, but not by fetching the KB articles
		type: {
			article: true, // type: "artikel"						regular articles
			advert: true, // type: "advertentie"					advertisements
			illust: true, // type: "illustratie met onderschrift"	illustration+text
			family: true // type: "familiebericht"				family messages
		},
		distrib: {
			national: true, // type: "Landelijk"					Landelijke pers NL
			regional: true, // type: "Regionaal/lokaal"				Regionaal/lokale pers NL
			antilles: true, // type: "Nederlandse Antillen"			Nederlandse Antillen
			surinam: true, // type: "Suriname"						Suriname
			indonesia: true // type: "Nederlands-Indië/Indonesië"	Indonesië
		},
		chunk_size: 50,
		sort_order: "_score"
	},

	cloud: { // word cloud
		// fixed cloud params
		//	words:    true,			// 
		//	order:   "count",		// ordering of response wordlist: "count", or "alpha" (default)
		//	output:  "json",		// "json", "xml"

		//	system_stopwords: "apos,quot,0,1,2,3,4,5,6,7,8,9,10,11,000,_,__,den,de,in,ter,ten",

		// settable cloud params
		//	stopwords_cat:	"singleq",	// stopword category: "singleq", "allqs", "system"
		stopwords_clean: false, // remove superfluous stopwords
		stopwords: true, // remove stopwords from list
		stopwords_default: true, // use default stopword set
		stoplimit: 4, // require word length > stoplimit

		fontscale: 75, // font scale factor
		fontreduce: true, // reduce fontsize differences
		stems: false, // apply stemming
		idf: false, // normalize using inverse document frequencies

		NER: false, // Named Entity Recognition
		maxwords: 100, // default max words displayed
		render: "svg" // "svg" or "canvas"
	},

	timeline: { // timeline chart
		normalize: false, // normalize document counts
		burst_detect: true // burst detection (red)
	},

	cloudexport: { // cloud data export
		separator: "tab", // "comma", or "tab"
		normalize_ws: true, // for NER terms
		comma2semicolon: false, // for NER terms
		//	cloud2export:   "normal"	// "normal" or "burst"
	},

	querydataexport: { // query data
		format: "csv", // "json", "xml", or "csv"
		simplified: false
	}
};


var getConfig = function() {
	return config;
};


function storeCeleryOwner(celery_owner) {
	config.celery_owner = celery_owner;
	console.log("celery_owner: " + celery_owner);
}


function storeDatastore(datastore) {
	config.datastore = datastore;
	console.log("xTAS datastore: " + datastore);
}


function getSearchParameters() {
	params = {
		datastore: config.datastore,
		maximumRecords: config.search.chunk_size,
		sort_order: config.search.sort_order,

		st_article: config.search.type.article,
		st_advert: config.search.type.advert,
		st_illust: config.search.type.illust,
		st_family: config.search.type.family,

		sd_national: config.search.distrib.national,
		sd_regional: config.search.distrib.regional,
		sd_antilles: config.search.distrib.antilles,
		sd_surinam: config.search.distrib.surinam,
		sd_indonesia: config.search.distrib.indonesia,

		pillars: getSelectedPillars(),

		dateRange: getDateRangeString()
	};

	// If second search filter is set, add this to the parameters
	if (beginDate2) {
		params.dateRange += "," + toDateString(beginDate2) + "," + toDateString(endDate2);
	}

	return params;
}


var getSelectedPillars = function() {
	var selected_pillars = [];
	$(".pillar input:checked").each(function(i) {
		selected_pillars.push($(this).val());
	});
	return selected_pillars;
};


var resetArticleTypes = function() {
    for (key in config.search.type) {
        config.search.type[key] = true;
    }
};


var resetDistributions = function() {
    for (key in config.search.distrib) {
        config.search.distrib[key] = true;
    }
};


var resetPillars = function() {
    $('.pillar input').each(function(i) {
        $(this).prop('checked', false);
    });
};


var getToolbarConfig = function() {
    return (dijit.byId("config") || createConfig());
};


var showConfig = function() {
	getToolbarConfig().show();
};


var createConfig = function() {
	var dlgConfig = new dijit.Dialog({
		id: "config",
		title: "Configuration"
	});

	dojo.style(dlgConfig.closeButtonNode, "visibility", "hidden"); // hide the ordinary close button

	var container = dlgConfig.containerNode;

	var tcdiv = dojo.create("div", {
		id: "tc-div-config"
	}, container);
	var tabCont = new dijit.layout.TabContainer({
		style: "background-color: white; width: 450px; height: 345px; line-height: 18pt"
	}, "tc-div-config");


	// search tab
	var cpSearch = new dijit.layout.ContentPane({
		title: "Search",
		content: "<b>Search options</b><br/>"
	});
	tabCont.addChild(cpSearch);

	var disabled = false;

	// Parent div for articles/distributions
	var divArticleDistribution = dojo.create("div", {
		id: "div-article-distribution"
	}, cpSearch.domNode);

	// Article types 
	var divArticleType = dojo.create("div", {
		id: "div-articletype"
	}, divArticleDistribution);

	var textArticleType = dojo.create("label", {
		id: "text-articletype",
		for: "div-articletype",
		innerHTML: "Article type<br/>"
	}, divArticleType);


	var divTypeArticle = dojo.create("div", {
		id: "div-type-article"
	}, divArticleType);

	var cbTypeArticle = new dijit.form.CheckBox({
		id: "cb-type-article",
		disabled: disabled,
		checked: config.search.type.article,
		onChange: function(btn) {
			config.search.type.article = btn;
			check_dctypes();
		}
	}, divTypeArticle);

	var labelypeArticle = dojo.create("label", {
		id: "label-type-article",
		for: "cb-type-article",
		innerHTML: "&nbsp;Search KB regular articles<br/>"
	}, divArticleType);


	var divTypeAdvert = dojo.create("div", {
		id: "div-type-advert"
	}, divArticleType);

	var cbTypeAdvert = new dijit.form.CheckBox({
		id: "cb-type-advert",
		disabled: disabled,
		checked: config.search.type.advert,
		onChange: function(btn) {
			config.search.type.advert = btn;
			check_dctypes();
		}
	}, divTypeAdvert);

	var labelypeAdvert = dojo.create("label", {
		id: "label-type-advert",
		for: "cb-type-advert",
		innerHTML: "&nbsp;Search KB advertisements<br/>"
	}, divArticleType);


	var divTypeIllust = dojo.create("div", {
		id: "div-type-illust"
	}, divArticleType);

	var cbTypeIllust = new dijit.form.CheckBox({
		id: "cb-type-illust",
		disabled: disabled,
		checked: config.search.type.illust,
		onChange: function(btn) {
			config.search.type.illust = btn;
			check_dctypes();
		}
	}, divTypeIllust);

	var labelypeIllust = dojo.create("label", {
		id: "label-type-illust",
		for: "cb-type-illust",
		innerHTML: "&nbsp;Search KB illustration text<br/>"
	}, divArticleType);


	var divTypeFamily = dojo.create("div", {
		id: "div-type-family"
	}, divArticleType);

	var cbTypeFamily = new dijit.form.CheckBox({
		id: "cb-type-family",
		disabled: disabled,
		checked: config.search.type.family,
		onChange: function(btn) {
			config.search.type.family = btn;
			check_dctypes();
		}
	}, divTypeFamily);

	var labelypeFamily = dojo.create("label", {
		id: "label-type-family",
		for: "cb-type-family",
		innerHTML: "&nbsp;Search KB family messages<br/>"
	}, divArticleType);

	// Distributions 
	var divDistribution = dojo.create("div", {
		id: "div-distribution"
	}, divArticleDistribution);

	var textDistribution = dojo.create("label", {
		id: "text-distribution",
		for: "div-distribution",
		innerHTML: "<hr>Distribution<br/>"
	}, divDistribution);


	var divDistribNationalNL = dojo.create("div", {
		id: "div-distrib-national-nl"
	}, divDistribution);

	var cbDistribNationalNL = new dijit.form.CheckBox({
		id: "cb-distrib-national-nl",
		disabled: disabled,
		checked: config.search.distrib.national,
		onChange: function(btn) {
			config.search.distrib.national = btn;
			check_dctypes();
		}
	}, divDistribNationalNL);

	var labelDistribNationalNL = dojo.create("label", {
		id: "label-distrib-national",
		for: "cb-distrib-national",
		innerHTML: "&nbsp;National NL<br/>"
	}, divDistribution);


	var divDistribRegionalNL = dojo.create("div", {
		id: "div-distrib-regional"
	}, divDistribution);

	var cbDistribRegionalNL = new dijit.form.CheckBox({
		id: "cb-distrib-regional",
		disabled: disabled,
		checked: config.search.distrib.regional,
		onChange: function(btn) {
			config.search.distrib.regional = btn;
			check_dctypes();
		}
	}, divDistribRegionalNL);

	var labelDistribRegionalNL = dojo.create("label", {
		id: "label-distrib-regional",
		for: "cb-distrib-regional",
		innerHTML: "&nbsp;Regional NL<br/>"
	}, divDistribution);


	var divDistribAntillen = dojo.create("div", {
		id: "div-distrib-antilles"
	}, divDistribution);

	var cbDistribAntillen = new dijit.form.CheckBox({
		id: "cb-distrib-antilles",
		disabled: disabled,
		checked: config.search.distrib.antilles,
		onChange: function(btn) {
			config.search.distrib.antilles = btn;
			check_dctypes();
		}
	}, divDistribAntillen);

	var labelDistribAntillen = dojo.create("label", {
		id: "label-distrib-antilles",
		for: "cb-distrib-antilles",
		innerHTML: "&nbsp;Antillen<br/>"
	}, divDistribution);


	var divDistribSurinam = dojo.create("div", {
		id: "div-distrib-surinam"
	}, divDistribution);

	var cbDistribSurinam = new dijit.form.CheckBox({
		id: "cb-distrib-surinam",
		disabled: disabled,
		checked: config.search.distrib.surinam,
		onChange: function(btn) {
			config.search.distrib.surinam = btn;
			check_dctypes();
		}
	}, divDistribSurinam);

	var labelDistribSurinam = dojo.create("label", {
		id: "label-distrib-surinam",
		for: "cb-distrib-surinam",
		innerHTML: "&nbsp;Surinam<br/>"
	}, divDistribution);


	var divDistribIndonesia = dojo.create("div", {
		id: "div-distrib-indonesia"
	}, divDistribution);

	var cbDistribIndonesia = new dijit.form.CheckBox({
		id: "cb-distrib-indonesia",
		disabled: disabled,
		checked: config.search.distrib.indonesia,
		onChange: function(btn) {
			config.search.distrib.indonesia = btn;
			check_dctypes();
		}
	}, divDistribIndonesia);

	var labelDistribIndonesia = dojo.create("label", {
		id: "label-distrib-indonesia",
		for: "cb-distrib-indonesia",
		innerHTML: "&nbsp;Indonesia<br/>"
	}, divDistribution);

	/* Pillars starts here */
	var divPillar = dojo.create("div", {
		id: "div-pillar"
	}, cpSearch.domNode);

	var textPillar = dojo.create("label", {
		id: "text-pillar",
		for: "div-pillar",
		innerHTML: "Pillar (<a href='query/newspaper/export'>download distribution as .csv</a>)<br/>"
	}, divPillar);

	// Retrieves pillars (synchronously)
	dojo.xhrGet({
		url: "query/pillars",
		handleAs: "json",
		sync: true
	}).then(function(response) {
		dojo.forEach(response.result, function(entry, i) {
			var div = dojo.create("div", {
				id: "div-pillar-" + entry.name
			}, divPillar);

			var cb = new dijit.form.CheckBox({
				id: "cb-pillar-" + entry.name,
				class: "pillar",
				checked: false,
				value: entry.id.toString()
			}, div);

			var label = dojo.create("label", {
				id: "label-pillar-" + entry.name,
				for: "cb-pillar-" + entry.name,
				innerHTML: "&nbsp;" + entry.name + "<br/>"
			}, divPillar);
		});
	});
	/* Pillars ends here */

	dojo.create("hr", {}, cpSearch.domNode);

	var divSearchChunk = dojo.create("div", {
		id: "div-search-chunk"
	}, cpSearch.domNode);

	var searchCunkSpinner = new dijit.form.NumberSpinner({
		id: "ns-search-chunk",
		smallDelta: 5,
		constraints: {
			min: 10,
			max: 500,
			places: 0
		},
		style: "width:50px",
		intermediateChanges: "true",
		value: config.search.chunk_size,
		onChange: function(value) {
			config.search.chunk_size = value;
		}
	}, divSearchChunk);

	var labelSearchChunk = dojo.create("label", {
		id: "label-search_chunk",
		for: "ns-search-chunk",
		innerHTML: "&nbsp;Number of results to show<br/>"
	}, cpSearch.domNode);

	var divSortOrder = dojo.create("div", {
		id: "div-sortorder"
	}, cpSearch.domNode);

	var textSortOrder = dojo.create("label", {
		id: "text-sortorder",
		for: "div-sortorder",
		innerHTML: "<hr/>Sort order<br/>"
	}, cpSearch.domNode);

	var divOrderScore = dojo.create("div", {
		id: "div-orderscore"
	}, cpSearch.domNode);

	var rbOrderScore = new dijit.form.RadioButton({
		id: "rb-orderscore",
		checked: config.search.sort_order === "_score",
		onChange: function(btn) {
			if (btn) {
				config.search.sort_order = "_score";
			}
		},
	}, "div-orderscore");

	var labelOrderScore = dojo.create("label", {
		id: "label-orderscore",
		for: "rb-orderscore",
		innerHTML: "&nbsp;By score<br/>"
	}, cpSearch.domNode);

	var divOrderDateAsc = dojo.create("div", {
		id: "div-orderdateasc"
	}, cpSearch.domNode);

	var rbOrderDateAsc = new dijit.form.RadioButton({
		id: "rb-orderdateasc",
		checked: config.search.sort_order === "paper_dc_date:asc,_score",
		onChange: function(btn) {
			if (btn) {
				config.search.sort_order = "paper_dc_date:asc,_score";
			}
		},
	}, "div-orderdateasc");

	var labelOrderDateAsc = dojo.create("label", {
		id: "label-orderdateasc",
		for: "rb-orderdateasc",
		innerHTML: "&nbsp;By date (oldest first)<br/>"
	}, cpSearch.domNode);

	var divOrderDateDesc = dojo.create("div", {
		id: "div-orderdatedesc"
	}, cpSearch.domNode);

	var rbOrderDateDesc = new dijit.form.RadioButton({
		id: "rb-orderdatedesc",
		checked: config.search.sort_order === "paper_dc_date:desc,_score",
		onChange: function(btn) {
			if (btn) {
				config.search.sort_order = "paper_dc_date:desc,_score";
			}
		},
	}, "div-orderdatedesc");

	var labelOrderDateDesc = dojo.create("label", {
		id: "label-orderdatedesc",
		for: "rb-orderdatedesc",
		innerHTML: "&nbsp;By date (newest first)<br/>"
	}, cpSearch.domNode);

	var check_dctypes = function() {
		//	console.log( "check_dctypes()" );
		// prevent unselection of all options
		if (config.search.type.article === false &&
			config.search.type.advert === false &&
			config.search.type.illust === false &&
			config.search.type.family === false) {
			// all false: -> make all true
			dijit.byId("cb-type-article").set("value", true);
			dijit.byId("cb-type-advert").set("value", true);
			dijit.byId("cb-type-illust").set("value", true);
			dijit.byId("cb-type-family").set("value", true);
		}
	};


	// cloud tab
	var cpCloud = new dijit.layout.ContentPane({
		title: "Cloud",
		content: "<b>Word cloud options</b><br/>"
	});
	tabCont.addChild(cpCloud);

	var divFReduce = dojo.create("div", {
		id: "div-freduce"
	}, cpCloud.domNode);

	var cbFReduce = new dijit.form.CheckBox({
		id: "cb-freduce",
		checked: config.cloud.fontreduce,
		onChange: function(btn) {
			config.cloud.fontreduce = btn;
		}
	}, divFReduce);

	var labelFReduce = dojo.create("label", {
		id: "label-freduce",
		for: "cb-freduce",
		innerHTML: "&nbsp;Reduce font size differences<br/>"
	}, cpCloud.domNode);


	var divFScale = dojo.create("div", {
		id: "div-fscale"
	}, cpCloud.domNode);

	var fscaleSpinner = new dijit.form.NumberSpinner({
		id: "ns-fscale",
		smallDelta: 5,
		constraints: {
			min: 10,
			max: 100,
			places: 0
		},
		style: "width:50px",
		intermediateChanges: "true",
		value: config.cloud.fontscale,
		onChange: function(value) {
			config.cloud.fontscale = value;
		}
	}, divFScale);

	var labelFScale = dojo.create("label", {
		id: "label-fscale",
		for: "ns-fscale",
		innerHTML: "&nbsp;Font scale factor<br/>"
	}, cpCloud.domNode);


	var divStopwords = dojo.create("div", {
		id: "div-stopwords"
	}, cpCloud.domNode);

	var textStopwords = dojo.create("label", {
		id: "text-stopwords",
		for: "div-stopwords",
		innerHTML: "<hr/><strong>Stop words</strong> (<a href='query/stopword/export'>download as .csv</a>)<br/>"
	}, cpCloud.domNode);


	var divStop = dojo.create("div", {
		id: "div-stop"
	}, cpCloud.domNode);

	var cbStop = new dijit.form.CheckBox({
		id: "cb-stop",
		checked: config.cloud.stopwords,
		onChange: function(btn) {
			config.cloud.stopwords = btn;
			if (!btn) {
				dijit.byId("cb-stopdefault").set("value", false);
			}
		}
	}, divStop);

	var labelStop = dojo.create("label", {
		id: "label-stop",
		for: "cb-stop",
		innerHTML: "&nbsp;Remove stop words<br/>"
	}, cpCloud.domNode);


	var divStopDefault = dojo.create("div", {
		id: "div-stopdefault"
	}, cpCloud.domNode);

	var cbStopDefault = new dijit.form.CheckBox({
		id: "cb-stopdefault",
		checked: config.cloud.stopwords_default,
		onChange: function(btn) {
			config.cloud.stopwords_default = btn;
			if (btn) {
				dijit.byId("cb-stop").set("value", true);
			}
		}
	}, divStopDefault);

	var stopword_link = 'https://github.com/UUDigitalHumanitieslab/texcavator/blob/develop/query/management/commands/stopwords/nl.txt';
	var labelStopDefault = dojo.create("label", {
		id: "label-stopdefault",
		for: "cb-stopdefault",
		innerHTML: "&nbsp;Use the <a href='" + stopword_link + "' target='_blank'>default stop word set</a> on top of your own set of stopwords<br/>"
	}, cpCloud.domNode);


	var divWMinLen = dojo.create("div", {
		id: "div-wminlen"
	}, cpCloud.domNode);

	var wminlenSpinner = new dijit.form.NumberSpinner({
		id: "ns-wminlen",
		smallDelta: 1,
		constraints: {
			min: 1,
			max: 10,
			places: 0
		},
		style: "width:50px",
		intermediateChanges: "true",
		value: config.cloud.stoplimit,
		onChange: function(value) {
			config.cloud.stoplimit = value;
			var lenrequired = 1 + value;
			var charstr = "characters";
			if (lenrequired == 1) {
				charstr = "character";
			}
			labelWMinLen.innerHTML = "&nbsp;Minimum word length<br/><em>This will remove words shorter than " + lenrequired + " " + charstr + "</em><br/>";
		}
	}, divWMinLen);

	var labelWMinLen = dojo.create("label", {
		id: "label-wminlen",
		for: "ns-wminlen",
		innerHTML: "&nbsp;Minimum word length"
	}, cpCloud.domNode);


	var divOther = dojo.create("div", {
		id: "div-other"
	}, cpCloud.domNode);

	var textOther = dojo.create("label", {
		id: "text-other",
		for: "div-other",
		innerHTML: "<hr/><strong>Other options</strong><br/>"
	}, cpCloud.domNode);

	var divStem = dojo.create("div", {
		id: "div-stem"
	}, cpCloud.domNode);

	var cbStem = new dijit.form.CheckBox({
		id: "cb-stem",
		checked: config.cloud.stems,
		onChange: function(btn) {
			config.cloud.stems = btn;
		}
	}, divStem);

	var labelStem = dojo.create("label", {
		id: "label-stem",
		for: "cb-stem",
		innerHTML: "&nbsp;Stemming<br/>"
	}, cpCloud.domNode);

	var divIdf = dojo.create("div", {
		id: "div-idf"
	}, cpCloud.domNode);

	var cbIdf = new dijit.form.CheckBox({
		id: "cb-idf",
		checked: config.cloud.idf,
		onChange: function(btn) {
			config.cloud.idf = btn;
			$("#div-idf-timeframes").toggle(btn);
		}
	}, divIdf);

	var labelIdf = dojo.create("label", {
		id: "label-idf",
		for: "cb-idf",
		innerHTML: "&nbsp;Normalize using inverse document frequency<br/>"
	}, cpCloud.domNode);

	/* IDF timeframes starts here */
	var divIdfTimeframes = dojo.create("div", {
		id: "div-idf-timeframes",
		style: "display: none"
	}, cpCloud.domNode);

	var textIdfTimeframes = dojo.create("label", {
		id: "text-idf-timeframes",
		for: "div-idf-timeframes",
		innerHTML: "&nbsp;Select a time frame:<br/>"
	}, divIdfTimeframes);

	// Retrieves IDF timeframes (synchronously)
	dojo.xhrGet({
		url: "query/timeframes",
		handleAs: "json",
		sync: true
	}).then(function(response) {
		dojo.forEach(response.result, function(entry, i) {
			var div = dojo.create("div", {
				id: "div-idf-timeframes-" + entry.name
			}, divIdfTimeframes);

			var rb = new dijit.form.RadioButton({
				id: "rb-idf-timeframes-" + entry.name,
				class: "idf-timeframe",
				checked: i + 1 == response.result.length, // Select last item by default
				value: entry.id.toString()
			}, div);

			var label = dojo.create("label", {
				id: "label-idf-timeframes-" + entry.name,
				for: "rb-idf-timeframes-" + entry.name,
				innerHTML: "&nbsp;" + entry.name + "<br/>"
			}, divIdfTimeframes);
		});
	});
	/* IDF timeframes ends here */

	var divWCount = dojo.create("div", {
		id: "div-wcount"
	}, cpCloud.domNode);

	var wcountSpinner = new dijit.form.NumberSpinner({
		id: "ns-wcount",
		smallDelta: 10,
		constraints: {
			min: WORDCLOUD_MIN_WORDS,
			max: WORDCLOUD_MAX_WORDS,
			places: 0
		},
		style: "width:50px",
		intermediateChanges: "true",
		value: config.cloud.maxwords,
		onChange: function(value) {
			config.cloud.maxwords = value;
		}
	}, divWCount);

	var labelWCount = dojo.create("label", {
		id: "label-wcount",
		for: "ns-wcount",
		innerHTML: "&nbsp;Max # of words in cloud<br/>"
	}, cpCloud.domNode);


	var divCloudRender = dojo.create("div", {
		id: "div-cloudrender"
	}, cpCloud.domNode);

	var textCloudRender = dojo.create("label", {
		id: "text-cloudrender",
		for: "div-cloudrender",
		innerHTML: "<hr/><strong>Cloud rendering</strong><br/>"
	}, cpCloud.domNode);


	var divSvgRender = dojo.create("div", {
		id: "div-svgrender"
	}, cpCloud.domNode);

	var svgrender_val = config.cloud.render === "svg";

	var rbSvgRender = new dijit.form.RadioButton({
		id: "rb-svgrender",
		checked: svgrender_val,
		onChange: function(btn) {
			if (btn) {
				config.cloud.render = "svg";
			}
		},
	}, "div-svgrender");

	var labelSvgRender = dojo.create("label", {
		id: "label-svgrender",
		for: "rb-svgrender",
		innerHTML: "&nbsp;SVG - Scalable Vector Graphics<br/>"
	}, cpCloud.domNode);


	var divCanvasRender = dojo.create("div", {
		id: "div-canvasrender"
	}, cpCloud.domNode);

	var canvasrender_val = config.cloud.render === "canvas";

	var rbCanvasRender = new dijit.form.RadioButton({
		id: "rb-canvasrender",
		checked: canvasrender_val,
		onChange: function(btn) {
			if (btn) {
				config.cloud.render = "canvas";
			}
		},
	}, "div-canvasrender");

	var labelCanvasRender = dojo.create("label", {
		id: "label-canvasrender",
		for: "rb-canvasrender",
		innerHTML: "&nbsp;HTML Canvas<br/>"
	}, cpCloud.domNode);


	// timeline tab
	var cpTimeline = new dijit.layout.ContentPane({
		title: "Timeline",
		content: "<b>Timeline options</b><br/>"
	});
	tabCont.addChild(cpTimeline);


	var divNormalize = dojo.create("div", {
		id: "div-normalize"
	}, cpTimeline.domNode);

	var cbNormalize = new dijit.form.CheckBox({
		id: "cb-normalize",
		checked: config.timeline.normalize,
		onChange: function(btn) {
			config.timeline.normalize = btn;
		}
	}, divNormalize);

	var labelNormalize = dojo.create("label", {
		id: "label-normalize",
		for: "cb-normalize",
		innerHTML: "&nbsp;Normalize document counts<br/>"
	}, cpTimeline.domNode);


	var divBurst = dojo.create("div", {
		id: "div-burst"
	}, cpTimeline.domNode);

	var cbBurst = new dijit.form.CheckBox({
		id: "cb-burst",
		checked: config.timeline.burst_detect,
		onChange: function(btn) {
			config.timeline.burst_detect = btn;
		}
	}, divBurst);

	var labelBurst = dojo.create("label", {
		id: "label-burst",
		for: "cb-burst",
		innerHTML: "&nbsp;Highlight bursts in red<br/>"
	}, cpTimeline.domNode);


	// export tab
	var cloudexportcfg = config.cloudexport;
	var cpExport = new dijit.layout.ContentPane({
		title: "Export",
		content: "<b>Cloud export options</b><br/>"
	});
	tabCont.addChild(cpExport);


	var divSepComma = dojo.create("div", {
		id: "div-sepcomma"
	}, cpExport.domNode);

	var sepcomma_val = cloudexportcfg.separator === "comma";

	var rbSepComma = new dijit.form.RadioButton({
		id: "rb-sepcomma",
		checked: sepcomma_val,
		onChange: function(btn) {
			if (btn) {
				config.cloudexport.separator = "comma";
			}
		},
	}, "div-sepcomma");

	var labelSepComma = dojo.create("label", {
		id: "label-sepcomma",
		for: "rb-sepcomma",
		innerHTML: "&nbsp;Comma separator<br/>"
	}, cpExport.domNode);


	var divSepTab = dojo.create("div", {
		id: "div-septab"
	}, cpExport.domNode);

	var septab_val = cloudexportcfg.separator === "tab";

	var rbSepTab = new dijit.form.RadioButton({
		id: "rb-septab",
		checked: septab_val,
		onChange: function(btn) {
			if (btn) {
				config.cloudexport.separator = "tab";
			}
		},
	}, "div-septab");

	var labelSepTab = dojo.create("label", {
		id: "label-septab",
		for: "rb-septab",
		innerHTML: "&nbsp;Tab separator<br/>"
	}, cpExport.domNode);


	var divExportNER = dojo.create("div", {
		id: "div-exportner"
	}, cpExport.domNode);

	var textExportNER = dojo.create("label", {
		id: "text-exportner",
		for: "div-exportner",
		innerHTML: "<br/>NER cloud phrase options<br/>"
	}, cpExport.domNode);


	var divNormalizeWS = dojo.create("div", {
		id: "div-normalize-ws"
	}, cpExport.domNode);

	var cbNormalizeWS = new dijit.form.CheckBox({
		id: "cb-normalize-ws",
		checked: config.cloudexport.normalize_ws,
		onChange: function(btn) {
			config.cloudexport.normalize_ws = btn;
		}
	}, divNormalizeWS);

	var labelNormalizeWS = dojo.create("label", {
		id: "label-normalize-ws",
		for: "cb-normalize-ws",
		innerHTML: "&nbsp;Normalize whitespace<br/>"
	}, cpExport.domNode);


	var divComma2Semicolon = dojo.create("div", {
		id: "div-comma2semicolon"
	}, cpExport.domNode);

	var cbComma2Semicolon = new dijit.form.CheckBox({
		id: "cb-comma2semicolon",
		checked: config.cloudexport.comma2semicolon,
		onChange: function(btn) {
			config.cloudexport.comma2semicolon = btn;
		}
	}, divComma2Semicolon);

	var labelComma2Semicolon = dojo.create("label", {
		id: "label-comma2semicolon",
		for: "cb-comma2semicolon",
		innerHTML: "&nbsp;Replace comma by semicolon<br/>"
	}, cpExport.domNode);

	// Action bar
	var actionBar = dojo.create("div", {
		className: "dijitDialogPaneActionBar",
		style: "height: 30px"
	}, container);

	var bOK = new dijit.form.Button({
		label: "<img src='/static/image/icon/Tango/16/actions/dialog-ok.png'/> OK",
		showLabel: true,
		role: "presentation",
		onClick: function() {
			dijit.byId("config").hide();
		}
	});
	actionBar.appendChild(bOK.domNode);
    return dijit.byId("config");
}; // createConfig