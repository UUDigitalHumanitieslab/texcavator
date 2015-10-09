// FL-04-Mar-2013 Created
// FL-24-Oct-2013 Changed

/*
function clearTextview()
function writeTextview(article_title, ocr_text)
*/

function clearTextview() {
	if (dojo.byId("record") === undefined) {
		return;
	} else {
		dojo.byId("record").innerHTML = "";
	}
}

function writeTextview(article_title, ocr_text) {
	// Replace HTML entities
	var article_text = ocr_text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
	// Replace line feeds
	article_text = article_text.replace(/\n\n/g, "</br></br>");

	dojo.byId("record").innerHTML = "<h1>" + article_title + "</h1><p>" + article_text + "</p>";
}