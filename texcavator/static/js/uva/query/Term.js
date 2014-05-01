dojo.provide("uva.query.Term");
dojo.require("dijit.TooltipDialog");
dojo.require("dijit.form.DropDownButton");
dojo.require("dijit.form.TextBox");
dojo.require("dijit.form.Select");
dojo.require("dojo.cache");
dojo.require("uva.query.InlineEditBoxList");
dojo.declare("uva.query.Term", [dijit._Widget, dijit._Templated], {
    widgetsInTemplate: true,
	templateString: dojo.cache("uva.query", "Term.html"),
    buildRendering: function() {
		this.inherited(arguments);
		// Inform DropDownButton about its popup
	   	this.button.dropDown = this.dialog;
    	dijit.popup.moveOffScreen(this.dialog.domNode);
    },
	value: "term",
	modifier: "",
	forbidden: false,
	attributeMap: {
		value: [{node: "button", attribute: "label"}, "termInput"]
	},
	setProperty: function() {
		this.set(arguments[0], arguments[arguments.length-1]);
	},
	postCreate: function() {
		this.termInput.set('value', this.value);
		this.termInput.set('intermediateChanges', true);
		this.termInput.watch('value', dojo.hitch(this, 'setProperty'));
		this.termInput.watch('value', dojo.hitch(this, 'termChanged'));
		this.modifierSelect.watch('value', dojo.hitch(this, dojo.partial(this.setProperty, 'modifier')));
		this.modifierSelect.watch('value', dojo.hitch(this, 'termChanged'));
		this.set('modifier', this.modifierSelect.get('value'));
		this.forbiddenToggle.watch('checked', dojo.hitch(this, dojo.partial(this.setProperty, 'forbidden')));
		this.forbiddenToggle.watch('checked', dojo.hitch(this, 'termChanged'));
		this.set('forbidden', this.forbiddenToggle.get('checked'));
		dojo.connect(this.wordList, 'itemsChanged', this, 'termChanged');
		dojo.connect(this.wordListButton, 'onClick', this, 'convertToWordList');
		dojo.connect(this.deleteButton, 'onClick', this, 'destroy');
		this.termChanged();
	},
	// Function that converts the current term to a wordlist
	convertToWordList: function() {
		var words = this.get('words');
		this.isWordList = true;
		this.set('words', words);
		var animateIn = function(node) {
			return dojo.fadeIn({ node: node, beforeBegin: function() {
					this.node.style.opacity = 0;
					this.node.style.display = "block";
			} });
		};
		var animateOut = function(node) {
			return dojo.fadeOut({ node: node, onEnd: function() { 
				this.node.style.display = "none"; 
			} });
		};
		dojo.fx.combine([
			dojo.fx.chain([animateOut(this.termLabel), 
						   animateIn(this.titleLabel)]),
			animateOut(this.wordListButton.domNode),
			dojo.fx.chain([animateOut(this.alternativesLabel), 
						   animateIn(this.wordListLabel)]),
		]).play();
	},
	isWordList: false,
	_getWordsAttr: function() {
		if(!this.isWordList)
			return [this.value].concat(this.wordList.get('items'));
		return this.wordList.get('items'); 
	},
	_setWordsAttr: function(newWords) {
		if(!this.isWordList)
			this.value = newWords.splice(0, 1);
		this.wordList.set('items', newWords);
	},
	termChanged: function() { console.log("Term changed to: " + this.get('words')); }
});
