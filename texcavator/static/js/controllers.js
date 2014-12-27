angular.module('texcavatorApp', ['ui.bootstrap', 'checklist-model', 'truncate', 'nvd3ChartDirectives'])

    .config(function($httpProvider){
        // set csrftoken for Django
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    })

    .controller('texcavatorCtrl', ['$scope', '$http', function($scope, $http) {
        $scope.startRecord = 1;
        $scope.maxResultsPerPage= 20;
        $scope.query = {
            distributions: []
        }

        $scope.searchResults = [{
            "_score":2.3224924,
            "_type":"doc",
            "_id":"ddd:010230127:mpeg21:a0230",
            "fields": {
                "paper_dc_date":["1934-06-19"],
                "article_dc_title": ["Brigadier Lindemann op zijn „zwevende fiets\"."],
                "paper_dcterms_temporal":["Dag"],
                "paper_dc_title":["Het nieuws van den dag voor Nederlandsch-Indië"],
                "paper_dcterms_spatial":["Nederlands-Indië / Indonesië"]
            },
            "_index":"kb_tags_filtered_20141203"
        },
        {
            "_score":2.0837216,
            "_type":"doc",
            "_id":"ddd:010247615:mpeg21:a0049",
            "fields":{
                "paper_dc_date":["1939-02-21"],
                "article_dc_title":["Fiets gestolen."],
                "paper_dcterms_temporal":["Dag"],
                "paper_dc_title":["Nieuwe Tilburgsche Courant"],
                "paper_dcterms_spatial":["Regionaal/lokaal"]
            },
            "_index":"kb_tags_filtered_20141203"
        },
        {
            "_score":1.8228767,
            "_type":"doc",
            "_id":"ddd:010237980:mpeg21:a0002",
            "fields":{
                "paper_dc_date":["1937-06-19"],
                "article_dc_title":["Advertentie"],
                "paper_dcterms_temporal":["Dag"],
                "paper_dc_title":["Nieuwe Tilburgsche Courant"],
                "paper_dcterms_spatial":["Regionaal/lokaal"]
            },
            "_index":"kb_tags_filtered_20141203"
        },
        {
            "_score":1.7991908,
            "_type":"doc",
            "_id":"ddd:010237977:mpeg21:a0003",
            "fields":{
                "paper_dc_date":["1937-06-16"],
                "article_dc_title":["Advertentie"],
                "paper_dcterms_temporal":["Dag"],
                "paper_dc_title":["Nieuwe Tilburgsche Courant"],
                "paper_dcterms_spatial":["Regionaal/lokaal"]
            },
            "_index":"kb_tags_filtered_20141203"
        },
        {
            "_score":1.786047,
            "_type":"doc",
            "_id":"ddd:010238019:mpeg21:a0051",
            "fields":{
                "paper_dc_date":["1937-08-04"],
                "article_dc_title":["Aanrijding."],
                "paper_dcterms_temporal":["Dag"],
                "paper_dc_title":["Nieuwe Tilburgsche Courant"],
                "paper_dcterms_spatial":["Regionaal/lokaal"]
            },
            "_index":"kb_tags_filtered_20141203"
        },
        {
            "_score":1.7850507,
            "_type":"doc",
            "_id":"ddd:010237974:mpeg21:a0003",
            "fields":{
                "paper_dc_date":["1937-06-12"],
                "article_dc_title":["Advertentie"],
                "paper_dcterms_temporal":["Dag"],
                "paper_dc_title":["Nieuwe Tilburgsche Courant"],
                "paper_dcterms_spatial":["Regionaal/lokaal"]
            },
            "_index":"kb_tags_filtered_20141203"
        },
        {
            "_score":1.7418692,
            "_type":"doc",
            "_id":"ddd:010193891:mpeg21:a0099",
            "fields":{
                "paper_dc_date":["1930-05-30"],
                "article_dc_title":["ZIJN GESTOLEN FIETS „GESTOLEN\". Door het geluk nageloopen."],
                "paper_dcterms_temporal":["Dag"],
                "paper_dc_title":["Tilburgsche courant"],
                "paper_dcterms_spatial":["Regionaal/lokaal"]
            },
            "_index":"kb_tags_filtered_20141203"
        },
        {
            "_score":1.741524,
            "_type":"doc",
            "_id":"ddd:010238010:mpeg21:a0175",
            "fields":{
                "paper_dc_date":["1937-07-24"],
                "article_dc_title":["Fiets teruggevonden."],
                "paper_dcterms_temporal":["Dag"],
                "paper_dc_title":["Nieuwe Tilburgsche Courant"],
                "paper_dcterms_spatial":["Regionaal/lokaal"]
            },
            "_index":"kb_tags_filtered_20141203"
        },
        {
            "_score":1.6839013,
            "_type":"doc",
            "_id":"ddd:010193838:mpeg21:a0102",
            "fields":{
                "paper_dc_date":["1930-03-27"],
                "article_dc_title":["ALS DE KANS SCHOON IS.... Stelen ze zelfs de fiets van den agent."],
                "paper_dcterms_temporal":["Dag"],
                "paper_dc_title":["Tilburgsche courant"],
                "paper_dcterms_spatial":["Regionaal/lokaal"]
            },
            "_index":"kb_tags_filtered_20141203"
        },
        {
            "_score":1.6620213,
            "_type":"doc",
            "_id":"ddd:010193850:mpeg21:a0164",
            "fields":{
                "paper_dc_date":["1930-04-10"],
                "article_dc_title":["VERZEKER UW FIETS VOOR 2V2 Ct. Bij verschillende Haagsche winkeliers Is aan den gevel een automaat geplaatst, waar men zijn fiets voor IV% et kan verzekeren, door deze vast te leggen aan een ketting. In tiiden van fietsendiefstallen geen onwelkome maatregel."],
                "paper_dcterms_temporal":["Dag"],
                "paper_dc_title":["Tilburgsche courant"],
                "paper_dcterms_spatial":["Regionaal/lokaal"]
            },
            "_index":"kb_tags_filtered_20141203"
        },
        {
            "_score":1.6259217,
            "_type":"doc",
            "_id":"ddd:010238035:mpeg21:a0097",
            "fields":{
                "paper_dc_date":["1937-08-23"],
                "article_dc_title":["EEN FIETS VOOR PRINSES MARGARET ROSE."],
                "paper_dcterms_temporal":["Dag"],
                "paper_dc_title":["Nieuwe Tilburgsche Courant"],
                "paper_dcterms_spatial":["Regionaal/lokaal"]
            },
            "_index":"kb_tags_filtered_20141203"
        },
        {
            "_score":1.4883726,
            "_type":"doc",
            "_id":"ddd:010238007:mpeg21:a0072",
            "fields":{
                "paper_dc_date":["1937-07-21"],
                "article_dc_title":["MET DE FIETS GEVALLEN."],
                "paper_dcterms_temporal":["Dag"],
                "paper_dc_title":["Nieuwe Tilburgsche Courant"],
                "paper_dcterms_spatial":["Regionaal/lokaal"]
            },
            "_index":"kb_tags_filtered_20141203"
        },
        {
            "_score":1.4883726,
            "_type":"doc",
            "_id":"ddd:010238001:mpeg21:a0002",
            "fields":{
                "paper_dc_date":["1937-07-14"],
                "article_dc_title":["Advertentie"],
                "paper_dcterms_temporal":["Dag"],
                "paper_dc_title":["Nieuwe Tilburgsche Courant"],
                "paper_dcterms_spatial":["Regionaal/lokaal"]
            },
            "_index":"kb_tags_filtered_20141203"
        },
        {
            "_score":1.4883726,
            "_type":"doc",
            "_id":"ddd:010238022:mpeg21:a0006",
            "fields":{
                "paper_dc_date":["1937-08-07"],
                "article_dc_title":["Advertentie"],
                "paper_dcterms_temporal":["Dag"],
                "paper_dc_title":["Nieuwe Tilburgsche Courant"],
                "paper_dcterms_spatial":["Regionaal/lokaal"]
            },
            "_index":"kb_tags_filtered_20141203"
        },
        {
            "_score":1.4883726,
            "_type":"doc",
            "_id":"ddd:010193823:mpeg21:a0036",
            "fields":{
                "paper_dc_date":["1930-03-10"],
                "article_dc_title":["Van zijn fiets geslingerd en gedood."],
                "paper_dcterms_temporal":["Dag"],
                "paper_dc_title":["Tilburgsche courant"],
                "paper_dcterms_spatial":["Regionaal/lokaal"]
            },
            "_index":"kb_tags_filtered_20141203"
        },
        {
            "_score":1.469033,
            "_type":"doc",
            "_id":"ddd:010237995:mpeg21:a0007",
            "fields":{
                "paper_dc_date":["1937-07-07"],
                "article_dc_title":["Advertentie"],
                "paper_dcterms_temporal":["Dag"],
                "paper_dc_title":["Nieuwe Tilburgsche Courant"],
                "paper_dcterms_spatial":["Regionaal/lokaal"]
            },
            "_index":"kb_tags_filtered_20141203"
        },
        {
            "_score":1.469033,
            "_type":"doc",
            "_id":"ddd:010238028:mpeg21:a0002",
            "fields":{
                "paper_dc_date":["1937-08-14"],
                "article_dc_title":["Advertentie"],
                "paper_dcterms_temporal":["Dag"],
                "paper_dc_title":["Nieuwe Tilburgsche Courant"],
                "paper_dcterms_spatial":["Regionaal/lokaal"]
            },
            "_index":"kb_tags_filtered_20141203"
        },
        {
            "_score":1.4574878,
            "_type":"doc",
            "_id":"ddd:010237998:mpeg21:a0002",
            "fields":{
                "paper_dc_date":["1937-07-10"],
                "article_dc_title":["Advertentie"],
                "paper_dcterms_temporal":["Dag"],
                "paper_dc_title":["Nieuwe Tilburgsche Courant"],
                "paper_dcterms_spatial":["Regionaal/lokaal"]
            },
            "_index":"kb_tags_filtered_20141203"
        },
        {
            "_score":1.4515578,
            "_type":"doc",
            "_id":"ddd:010238025:mpeg21:a0002",
            "fields":{
                "paper_dc_date":["1937-08-11"],
                "article_dc_title":["Advertentie"],
                "paper_dcterms_temporal":["Dag"],
                "paper_dc_title":["Nieuwe Tilburgsche Courant"],
                "paper_dcterms_spatial":["Regionaal/lokaal"]
            },
            "_index":"kb_tags_filtered_20141203"
        },
        {
            "_score":1.4515578,
            "_type":"doc",
            "_id":"ddd:010238019:mpeg21:a0004",
            "fields":{
                "paper_dc_date":["1937-08-04"],
                "article_dc_title":["Advertentie"],
                "paper_dcterms_temporal":["Dag"],
                "paper_dc_title":["Nieuwe Tilburgsche Courant"],
                "paper_dcterms_spatial":["Regionaal/lokaal"]
            },
            "_index":"kb_tags_filtered_20141203"
        }];
        $scope.totalSearchResults = 4352;
        $scope.maxScore = 2.3224924;

        $http.get('query/metadata_options/').
            success(function (data) {
            console.log(data);
               $scope.distributions = data.distributions;
           }).
           error(function (error) {
               $scope.distributions = [];
           });

        $scope.search = function (newQuery) {
           console.log('search()');

           var params = {
               'query': $scope.queryStr,
               'startRecord': $scope.startRecord,
               'maximumRecords': $scope.maxResultsPerPage
           };

           // add distributions
           $scope.distributions.forEach(function (elem){
               if($scope.query.distributions.indexOf(elem.id) != -1){
                   params[elem.id] = 1;
               } else {
                   params[elem.id] = 0;
               }
           });

           console.log('search parameters');
           console.log(params);

           $http.get('services/search/', {params: params}).
               success(function (data) {
               console.log(data);
               $scope.searchResults = data.data.hits.hits;
               $scope.totalSearchResults = data.data.hits.total;


           }).
           error(function (error) {
           });
        };

        $scope.pageChanged = function () {
            $scope.startRecord = (($scope.searchResultsPage-1) * $scope.maxResultsPerPage)+1;

            console.log('new page: '+$scope.searchResultsPage);
            console.log('showing results from: '+$scope.startRecord);

            $scope.search();
        };
    }]);

