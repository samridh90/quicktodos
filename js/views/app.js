define([
	'jquery',
	'underscore',
	'backbone',
	'collections/todos',
	'views/todos',
	'text!templates/stats.html'
	], 
	function($, _, Backbone, TodosCollection, TodoView, statsTemplate){
		var AppView = Backbone.View.extend({
			el: $('#todoapp'),
			statsTemplate: _.template(statsTemplate),
			events: {
				"keypress #new-todo": "createOnEnter",
				"click .todo-clear a": "clearCompleted",
				"click #sortBy input[type=radio]": "toggleSortBy"
			},
			initialize: function(){
				_.bindAll(this, 'addOne', 'addAll', 'render');
				this.Todos = new TodosCollection();

				this.Todos.bind('add', this.addOne);
				this.Todos.bind('reset', this.addAll);
				this.Todos.bind('all', this.render);
				this.Todos.bind('sort', this.addAll);
				if(this.$("#todos #todo-list").length != 0)
				{
					this.input = this.$("#new-todo");
					this.pri = this.$("#todo-priority");
					this.due = this.$("#todo-due");
					this.Todos.fetch();
				}					
			},

			toggleSortBy: function(e) {
				this.Todos.sortParam = this.$('#sortBy input:radio[name=sort]:checked').val();
				this.Todos.sort();
				this.Todos.each(function(todo){console.log(todo.toJSON())});
			},

			render: function(){
				this.$('#todo-stats').html(this.statsTemplate({
					total: this.Todos.length,
					done: this.Todos.done().length,
					remaining: this.Todos.remaining().length
				}));
			},

			addOne: function(todo) {
				var view = new TodoView({model: todo});
				this.$('#todo-list').append(view.render().el);
			},

			addAll: function() {
				this.$('#todo-list').html('');
			    this.Todos.each(this.addOne);
		    },

			newAttributes: function() {
				return {
					content: this.input.val(),
					priority: parseInt(this.pri.val()),
					due: this.due.val(),
					done: false
				};
			},

			createOnEnter: function(e) {
				if (e.keyCode != 13) return;
			    this.Todos.create(this.newAttributes());
			    this.Todos.sort();
			    this.input.val('');
			    this.pri.val('');
			    this.due.val('');
			},

			clearCompleted: function() {
				_.each(this.Todos.done(), function(todo){ todo.destroy();});
				return false;
			}
		});
		return AppView;
	});