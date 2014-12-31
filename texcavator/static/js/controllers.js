var app = angular.module('texcavatorApp', ['ui.bootstrap', 
                                           'checklist-model', 
                                           'truncate', 
                                           'nvd3ChartDirectives'])

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

        $scope.selectedResult = {
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
        };

        $scope.searchResults = [{
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

        $scope.articleTypesData = [
            { key: "Article", y: 5 },
            { key: "Advertisement", y: 2 },
            { key: "Illustration", y: 9 },
            { key: "Family message", y: 7 },
        ];

        $scope.distributionsData = [
            { key: "National", y: 5 },
            { key: "Regional", y: 2 },
            { key: "Antilles", y: 9 },
            { key: "Surinam", y: 7 },
            { key: "Indonesia", y: 5 },
        ];

        $scope.newspapersData = [
            {
                "key": "Series 1",
                "values": [ [ "de Volkskrant" , 23] , [ "Het Parool" , 12] , [ "NRC" , 10] , [ "De Telegraaf" , 10] , [ "Echo" , 9] ]
            },
        ];

        $scope.xFunction = function(){
            return function(d) {
                return d.key;
            };
        };

        $scope.yFunction = function(){
            return function(d){
                return d.y;
            };
        };

        $scope.wordCloudData = [
        {
            "key": "fiets",
            "doc_count": 2114
        },
        {
            "key": "den",
            "doc_count": 1747
        },
        {
            "key": "ter",
            "doc_count": 1003
        },
        {
            "key": "per",
            "doc_count": 995
        },
        {
            "key": "goed",
            "doc_count": 937
        },
        {
            "key": "zoo",
            "doc_count": 924
        },
        {
            "key": "no",
            "doc_count": 909
        },
        {
            "key": "jaar",
            "doc_count": 873
        },
        {
            "key": "alle",
            "doc_count": 859
        },
        {
            "key": "gt",
            "doc_count": 856
        },
        {
            "key": "uur",
            "doc_count": 825
        },
        {
            "key": "zeer",
            "doc_count": 808
        },
        {
            "key": "twee",
            "doc_count": 787
        },
        {
            "key": "groote",
            "doc_count": 751
        },
        {
            "key": "10",
            "doc_count": 747
        },
        {
            "key": "lt",
            "doc_count": 739
        },
        {
            "key": "adres",
            "doc_count": 736
        },
        {
            "key": "waar",
            "doc_count": 730
        },
        {
            "key": "nieuwe",
            "doc_count": 729
        },
        {
            "key": "heer",
            "doc_count": 725
        },
        {
            "key": "ten",
            "doc_count": 706
        },
        {
            "key": "eerste",
            "doc_count": 697
        },
        {
            "key": "zien",
            "doc_count": 675
        },
        {
            "key": "eenige",
            "doc_count": 666
        },
        {
            "key": "11",
            "doc_count": 652
        },
        {
            "key": "wegens",
            "doc_count": 648
        },
        {
            "key": "amp",
            "doc_count": 641
        },
        {
            "key": "weg",
            "doc_count": 622
        },
        {
            "key": "koop",
            "doc_count": 618
        },
        {
            "key": "kwam",
            "doc_count": 618
        },
        {
            "key": "prijs",
            "doc_count": 608
        },
        {
            "key": "15",
            "doc_count": 597
        },
        {
            "key": "rijwiel",
            "doc_count": 595
        },
        {
            "key": "wel",
            "doc_count": 594
        },
        {
            "key": "man",
            "doc_count": 593
        },
        {
            "key": "plaats",
            "doc_count": 586
        },
        {
            "key": "enz",
            "doc_count": 582
        },
        {
            "key": "le",
            "doc_count": 577
        },
        {
            "key": "geheel",
            "doc_count": 573
        },
        {
            "key": "12",
            "doc_count": 568
        },
        {
            "key": "werden",
            "doc_count": 564
        },
        {
            "key": "welke",
            "doc_count": 562
        },
        {
            "key": "25",
            "doc_count": 560
        },
        {
            "key": "heeren",
            "doc_count": 560
        },
        {
            "key": "huis",
            "doc_count": 555
        },
        {
            "key": "nieuw",
            "doc_count": 551
        },
        {
            "key": "20",
            "doc_count": 545
        },
        {
            "key": "br",
            "doc_count": 544
        },
        {
            "key": "blad",
            "doc_count": 543
        },
        {
            "key": "groot",
            "doc_count": 542
        },
        {
            "key": "staat",
            "doc_count": 540
        },
        {
            "key": "weer",
            "doc_count": 540
        },
        {
            "key": "af",
            "doc_count": 539
        },
        {
            "key": "do",
            "doc_count": 536
        },
        {
            "key": "aangeboden",
            "doc_count": 529
        },
        {
            "key": "komen",
            "doc_count": 527
        },
        {
            "key": "tijd",
            "doc_count": 527
        },
        {
            "key": "on",
            "doc_count": 524
        },
        {
            "key": "gevraagd",
            "doc_count": 520
        },
        {
            "key": "politie",
            "doc_count": 517
        },
        {
            "key": "30",
            "doc_count": 516
        },
        {
            "key": "fr",
            "doc_count": 515
        },
        {
            "key": "dag",
            "doc_count": 514
        },
        {
            "key": "rotterdam",
            "doc_count": 514
        },
        {
            "key": "to",
            "doc_count": 514
        },
        {
            "key": "terwijl",
            "doc_count": 504
        },
        {
            "key": "jarige",
            "doc_count": 499
        },
        {
            "key": "straat",
            "doc_count": 485
        },
        {
            "key": "ie",
            "doc_count": 484
        },
        {
            "key": "tusschen",
            "doc_count": 478
        },
        {
            "key": "dagen",
            "doc_count": 475
        },
        {
            "key": "bureau",
            "doc_count": 472
        },
        {
            "key": "50",
            "doc_count": 468
        },
        {
            "key": "goede",
            "doc_count": 468
        },
        {
            "key": "week",
            "doc_count": 464
        },
        {
            "key": "oud",
            "doc_count": 457
        },
        {
            "key": "alleen",
            "doc_count": 453
        },
        {
            "key": "wij",
            "doc_count": 452
        },
        {
            "key": "werk",
            "doc_count": 447
        },
        {
            "key": "gaan",
            "doc_count": 445
        },
        {
            "key": "16",
            "doc_count": 444
        },
        {
            "key": "maken",
            "doc_count": 443
        },
        {
            "key": "verder",
            "doc_count": 442
        },
        {
            "key": "slechts",
            "doc_count": 441
        },
        {
            "key": "thans",
            "doc_count": 441
        },
        {
            "key": "echter",
            "doc_count": 438
        },
        {
            "key": "net",
            "doc_count": 434
        },
        {
            "key": "zaak",
            "doc_count": 434
        },
        {
            "key": "ver",
            "doc_count": 427
        },
        {
            "key": "14",
            "doc_count": 426
        },
        {
            "key": "st",
            "doc_count": 426
        },
        {
            "key": "drie",
            "doc_count": 423
        },
        {
            "key": "beide",
            "doc_count": 417
        },
        {
            "key": "gulden",
            "doc_count": 417
        },
        {
            "key": "waarvan",
            "doc_count": 416
        },
        {
            "key": "woning",
            "doc_count": 414
        },
        {
            "key": "ging",
            "doc_count": 412
        },
        {
            "key": "toe",
            "doc_count": 412
        },
        {
            "key": "boven",
            "doc_count": 408
        },
        {
            "key": "dien",
            "doc_count": 405
        }];

        $scope.articleCloudData = $scope.wordCloudData.slice(0, 10);

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

