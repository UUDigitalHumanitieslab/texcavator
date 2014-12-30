// Wordcloud
app.directive( 'wordcloud', ['$window',
   function ($window) {
     return {
       restrict: 'E',
       scope: {
       data: '='
     },
     link: function(scope, element){
       createWordCloud(scope, element, $window);
     }
   };
  }
 ]);  
