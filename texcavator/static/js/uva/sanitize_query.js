$(document).ready(function () {
    var grammar = $('#peg-query-grammar').text();
    window.queryParser = PEG.buildParser(grammar);
});

var defaultExplanation = 'A problem was found in your query. '
                       + 'Please read the description below, '
                       + 'then review your query and try again.';

function validateQuery(query) {
    try {
        queryParser.parse(query);
        return true;
    } catch (error) {
        var messageBits = [defaultExplanation, '<br><br><kbd>'],
            start = error.location.start.offset,
            end = error.location.end.offset,
            contextStart = Math.max(start - 10, 0),
            contextEnd = Math.min(end + 10, query.length);
        if (contextStart !== 0) messageBits.push('...');
        messageBits.push(escapeHTML(query.slice(contextStart, start)));
        messageBits.push('<mark>');
        messageBits.push(escapeHTML(query.slice(start, end)));
        messageBits.push('</mark>');
        messageBits.push(escapeHTML(query.slice(end, contextEnd)));
        if (contextEnd !== query.length) messageBits.push('...');
        messageBits.push('</kbd><br><br>');
        messageBits.push(escapeHTML(error.message));
        var message = messageBits.join('');
        genDialog('Invalid query string', message, {OK: true});
        return false;
    }
}

function escapeHTML(text) {
    return escapeHTML.arena.text(text).html();
}

escapeHTML.arena = $('<div>');
