
dojo.provide("uva.query.InlineEditBoxList");
dojo.require("dijit.form.TextBox");
dojo.require("dijit.InlineEditBox");
dojo.require("dojo.cache");

dojo.require("dijit._Widget");
dojo.require("dijit._Templated");

dojo.declare("uva.query.InlineEditBoxList", [dijit._Widget, dijit._Templated], {
    widgetsInTemplate: true,
	templateString: dojo.cache("uva.query", "InlineEditBoxList.html"),
	items: [],
	_inlineEditBoxes: [],
	constructor: function() {
		this.items = [];
		this._inlineEditBoxes = [];
	},
	// Function that is called if the InlineEditBox for a new item changes
	newItemChanged: function(attr, oldValue, newValue) {
		if(newValue == "") return;
		this.newItem.set('value', '');
		this._newItemEditBox(newValue);
		this.items.push(newValue);
		this.itemsChanged();
	},
	_newItemEditBox: function(newValue) {
		// Construct a new InlineEditBox
		var edit = new dijit.InlineEditBox({value: newValue}, dojo.create("span"));
		// Update the alternatives list if alternative changes
		edit.watch('value', dojo.hitch(this, 'itemChanged'));
		// Destroy the InlineEditBox if it is left empty
		edit.watch('value', function(a, o, newValue) { if(newValue == "") {
			this.destroyRendering();
			setTimeout(dojo.hitch(this, 'destroy'), 100);
		}});
		edit.placeAt(this.newItem.domNode, "before");
		this._inlineEditBoxes.push(edit);
		return edit;
	},
	// Function that is called if an InlineEditBox for an item changes
	itemChanged: function(attr, oldValue, newValue) {
	 	// Find the oldValue
		var index = dojo.indexOf(this.items, oldValue);
		if(index == -1) return;
		if(newValue != "") {
			// Update the value
			this.items[index] = newValue;		
		} else {
			// Remove the value
			this.items.splice(index, 1);			
			this._inlineEditBoxes.splice(index, 1);			
		}
		this.itemsChanged();
	},
	itemsChanged: function() {},
	postCreate: function() {
		this.newItem.watch('value', dojo.hitch(this, 'newItemChanged'));
		this.itemsChanged();
	},
	_setItemsAttr: function(newItems) {
		// Remove all inlineEditBoxes
		dojo.forEach(this._inlineEditBoxes, function(edit) {
			edit.destroyRendering();
			setTimeout(dojo.hitch(edit, 'destroy'), 100);
		});
		this._inlineEditBoxes = [];
		// Create new edit boxes
		dojo.forEach(newItems, function(newValue) {
			this._inlineEditBoxes.push(this._newItemEditBox(newValue));
		}, this);
		this.items = newItems;
		this.itemsChanged();
	}
});
