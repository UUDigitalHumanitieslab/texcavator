//(function(){  
    var createWordCloud = function (scope, element, window) {    
        //Render graph based on 'data'
        scope.render = function(data) {	
            var top = element[0].getBoundingClientRect().top;  

            var h = window.innerHeight - top;
            var w = window.innerWidth - 310;
            w = 1000;

            var minHeight = 400;
            var minWidth = 500;

            if (h < minHeight){
                h = minHeight;
            };
            if (w < minWidth){
                w = minWidth;
            };

            d3.select(element[0]).html("");

            //      var wordScale = d3.scale.linear();
            //      if(data.length > 0) {
            //        wordScale.domain([data[data.length-1].doc_count, data[0].doc_count]).range([20, 100]);
            //      }

            var wordScale = d3.scale.log().range([14, 100]);
            if(data.length > 0) {
                // min font: 14px
                // max font: 100px
                wordScale.domain([data[data.length-1].doc_count, data[0].doc_count]).range([14, 100]);
            };

            var fill = d3.scale.category20();
            d3.layout.cloud().size([w, h])
            .words(data.map(function(d) {
                return {text: d.key, size: wordScale(d.doc_count)};
            }))
            .padding(5)
            //      .rotate(function() { return ~~(Math.random() * 2) * 90; })
            .rotate(0)
            //.font("Impact")
            .fontSize(function(d) { return d.size; })
            .on("end", draw)
            .start();

            function draw(words) {
                d3.select(element[0]).append("svg")
                .attr("width", w)
                .attr("height", h)
                .attr("class", "remove-height")
                .append("g")
                // for position of the wordcloud
                .attr("transform", "translate(" + w/2 + "," +  h/2 + ")")
                .selectAll("text")
                .data(words)
                .enter().append("text")
                .style("font-size", function(d) { return d.size + "px"; })
                //.style("font-family", "Impact")
                //.style("fill", function(d, i) { return fill(i); })
                .attr("text-anchor", "middle")
                .attr("transform", function(d) {
                    return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
                })
                .text(function(d) { return d.text; });
            }
        };

        //Watch 'data' and run scope.render(newVal) whenever it changes
        //Use true for 'objectEquality' property so comparisons are done on equality and not reference
        scope.$watch('data', function(){
            scope.render(scope.data);
        }, true);

        //    var t;
        //    // Render graphic again on resize
        //    angular.element(window).bind('resize', function () {
        //        if (scope.$parent.tab === 3 ){
        //      	  // Timeout to prevent to much resizing
        //      	  clearTimeout(t);
        //  		  t = setTimeout(function(){
        //  			  scope.render(scope.data);
        //  		  }, 100);  
        //         };
        //    });
    };
//})();
