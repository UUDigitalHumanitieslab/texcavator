$(document).ready(function () {
    var grammar = $('#peg-query-grammar').text();
    window.queryParser = PEG.buildParser(grammar);
});

var defaultExplanation = 'A problem was found in your query. '
                       + 'Please read the description below, '
                       + 'then review your query and try again.'

function validateQuery(query) {
    try {
        queryParser.parse(query);
        return true;
    } catch (error) {
        var messageBits = [
                defaultExplanation,
                '<br><br>',
                $('<div>').text(error.message).html(),  // entities
                '<br><br><kbd>'
            ],
            start = error.location.start.offset,
            end = error.location.end.offset,
            contextStart = Math.max(start - 10, 0),
            contextEnd = Math.min(end + 10, query.length);
        if (contextStart !== 0) messageBits.push('...');
        messageBits.push(query.slice(contextStart, start));
        messageBits.push('<mark>');
        messageBits.push(query.slice(start, end));
        messageBits.push('</mark>');
        messageBits.push(query.slice(end, contextEnd));
        if (contextEnd !== query.length) messageBits.push('...');
        messageBits.push('</kbd>');
        var message = messageBits.join('');
        genDialog('Invalid query string', message, {OK: true});
    }
}
