angular.module('texcavatorApp', ['ui.bootstrap'])

    .config(function($httpProvider){
        // set csrftoken for Django
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    })

    .controller('texcavatorCtrl', ['$scope', '$http', function($scope, $http) {
        $scope.search = function () {
           console.log('search()');


           var params = {
               'query': $scope.queryStr
           };

           $http.get('services/search/', {params: params}).
               success(function (data) {
               console.log(data);
               $scope.searchResults = data.data.hits.hits;
           }).
           error(function (error) {
           });
        }
    }]);

