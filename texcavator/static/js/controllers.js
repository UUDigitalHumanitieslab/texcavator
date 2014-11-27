angular.module('texcavatorApp', ['ui.bootstrap'])

    .config(function($httpProvider){
        // set csrftoken for Django
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    })

    .controller('texcavatorCtrl', ['$scope', '$http', function($scope, $http) {
        $scope.startRecord = 1;
        $scope.maxResultsPerPage= 20;

        $scope.search = function (newQuery) {
           console.log('search()');

           var params = {
               'query': $scope.queryStr,
               'startRecord': $scope.startRecord,
               'maximumRecords': $scope.maxResultsPerPage
           };

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

