// Clears the text view
function clearTextview() {
	if (dojo.byId("record") === undefined) {
		return;
	} else {
		dojo.byId("record").innerHTML = "";
	}
}

// Displays the article title and text
function writeTextview(article_title, ocr_text) {
	// Replace HTML entities
	var article_text = ocr_text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
	// Replace line feeds
	article_text = article_text.replace(/\n\n/g, "</br></br>");

	dojo.byId("record").innerHTML = "<h1>" + article_title + "</h1><p id='article-text'>" + wrapWords(article_text) + "</p>";
	addTooltips();
}

// Wraps all "words" in the article text in a span tag. A word is separated by a space and does contain numbers.
function wrapWords(article_text) {
	var text = [];
	var words = article_text.split(' ');
	$.each(words, function(i, w) {
		// Only wrap "words" in span tags, if there's a number in the word, don't wrap. 
		if (!/\d+/g.test(w)) {
			var w_id = 'w' + i.toString();

			// Don't include non alphanumeric characters from the span tag.
			var m = w.match(/[^A-Za-z\u00C0-\u017F]*$/); 
			text[i] = '<span id="' + w_id + '">' + w.substring(0, m.index) + '</span>' + w.substring(m.index, w.length);
		}
		else {
			text[i] = w;
		}
	});
	return text.join(' ');
}

// Adds mouseover functionality to each "word" to search the word in ShiCo
function addTooltips() {
	$('#article-text span').each(function() {
		var term = $(this).text().toLowerCase();

		$(this).mouseover(function() {
			if (dijit.byId('shicoDialog') !== undefined) {
				dijit.byId('shicoDialog').destroy();
			}

			var shicoDialog = new dijit.TooltipDialog({
				id: 'shicoDialog',
				content: '<a href="javascript:startShiCoSearch(\'' + term + '\');">Search <em>' + term + '</em> in ShiCo</a>',
				onMouseLeave: function() {
					dijit.popup.close(shicoDialog);
				}
			});

			dijit.popup.open({
				popup: shicoDialog,
				around: $(this).attr('id'),
			});
		});
	});
}

// Starts searching for the term in ShiCo
function startShiCoSearch(term) {
	// Select the ShiCo tab
	dijit.byId('articleContainer').selectChild(dijit.byId('shico'));

	var shicoFrame = $('#shicoframe').contents();
	var shicoAngular = document.getElementById("shicoframe").contentWindow.angular;

	// Set the 'terms' input field, trigger the Angular directive, and post the form
	shicoFrame.find('#terms').val(term);
	shicoAngular.element(shicoFrame.find('#terms')).trigger('input');
	shicoAngular.element(shicoFrame.find('form')).scope().vm.doPost();
}
