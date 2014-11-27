angular.module('texcavatorApp', ['ui.bootstrap', 'checklist-model'])

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
        }

        $scope.pageChanged = function () {
            $scope.startRecord = (($scope.searchResultsPage-1) * $scope.maxResultsPerPage)+1;

            console.log('new page: '+$scope.searchResultsPage);
            console.log('showing results from: '+$scope.startRecord);

            $scope.search();
        }
    }]);

