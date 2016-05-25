(function() {
  'use strict';

  angular
    .module('shico')
    .run(runBlock);

  function runBlock(GraphConfigService) {
    GraphConfigService.addForceGraphHook(function(node) {
      // Remove existing text elements
      node.select('text').remove();

      // Create link to function in parent frame
      node.append('a')
        .attr('xlink:href', function(d) {
            return 'javascript:parent.startSearch("' + d.name + '");';
        })
        // Append the text element
        .append('text')
        .attr('dx', '12')
        .attr('dy', '.35em')
        .text(function(d) {
            return d.name;
        });
    });
  }
})();
