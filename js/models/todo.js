define([
	'underscore',
	'backbone',
	], function(_, Backbone){
		var TodoModel = Backbone.Model.extend({
			defaults: {
				content: "Nothing to do...",
				done: false,
				priority: 3,
				due: new Date()
			},
			initialize: function() {
				if(!this.get("content")){
					this.set({"content": this.defaults.content});
				}
				if(!this.get("due")){
					this.set({"due": this.defaults.due});
				}
			}
		});
		return TodoModel;
	});