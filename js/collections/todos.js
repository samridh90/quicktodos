define([
	'underscore',
	'backbone',
	'models/todo'
	],
	function(_, Backbone, Todo){
		var TodosCollection = Backbone.Collection.extend({
			model: Todo,
			url: '/todos',
			sortParam: "byDate",
			done: function() {
				return this.filter(function(todo) {return todo.get('done'); });
			},
			remaining: function() {
				return this.without.apply(this, this.done());
			},
			comparator: function(todo) {
				if(this.sortParam == "byDate") {
					return Date.parse(todo.get('due'));
				}
				else if(this.sortParam == "byPriority"){
					return todo.get('priority');
				}
			}
		});
		return TodosCollection;
	});