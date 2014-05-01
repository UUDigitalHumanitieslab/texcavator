dojo.provide("uva.query.CQL");
dojo.require("dijit.TooltipDialog");
dojo.require("dijit.form.DropDownButton");
dojo.require("dijit.form.TextBox");
dojo.require("dijit.form.Select");
dojo.require("dijit.InlineEditBox");
dojo.require("dojo.cache");
dojo.declare("uva.query.CQL", [], {
	_updateWord: function(modifier, word) {
		switch(modifier) {
			case "start":
				return word + "*";
				break;
			case "part":
				return "*" + word + "*";
				break;
			default:
				return word;
				break;				
		}
		
	},
	createQuery: function(words, modifier, forbidden) {
		var relation = 'exact';
		var modifiers = ["stem", "relevant", "fuzzy", "phonetic"];
		var modifiedWords = dojo.map(words, dojo.hitch(this, '_updateWord', modifier));
		if(dojo.indexOf(modifiers, modifier) >= 0)
			relation += "/" + modifier;
		var query = "";
		dojo.forEach(modifiedWords, function(word) {
			var part = dojo.replace('(cql.serverChoice {0} "{1}")', [relation, word]);
			if(query.length > 0)
    			query = this.combineWithOR(query, part, false);
    		else
    			query = part;
    	}, this);
    	if(modifiedWords.length > 1)
    		query = "(" + query + ")";
		if(forbidden)
			query = 'NOT ' + query;
		return query;
	},
	combineWithOR: function(query1, query2, includeParentheses) {
		if(includeParentheses == undefined) includeParentheses = true;
		return dojo.replace((includeParentheses) ? "({0} OR {1})" : "{0} OR {1}", [query1, query2]);
	},
	combineWithAND: function(query1, query2, includeParentheses) {
		if(includeParentheses == undefined) includeParentheses = true;
		if(query1.substr(0, 4) == "NOT ") {
			var q = query2;
			query2 = query1;
			query1 = q;
		}	
		if(query2.substr(0, 4) == "NOT ")
			return dojo.replace((includeParentheses) ? "({0} {1})" : "{0} {1}", [query1, query2]);
		return dojo.replace((includeParentheses) ? "({0} AND {1})" : "{0} AND {1}", [query1, query2]);
	}
});
