define([
	'jquery',
	'underscore',
	'backbone',
	'models/todo',
	'text!templates/todo.html'
	], function($, _, Backbone, Todo, todosTemplate){
		var TodoView = Backbone.View.extend({
			model: Todo,
			tagName: "li",
			template: _.template(todosTemplate),
			events: {
				'click .check': 'toggleDone',
				'dblclick div.todo-content': 'edit',
				'click span.todo-destroy': 'clear',
				'keypress .todo-input': 'updateOnEnter'
			},
			initialize: function() {
				_.bindAll(this, 'render');
				this.model.bind('change', this.render, this);
				this.model.bind('destroy', this.remove, this);	
			},
			render: function() {
				//can use $el also
				$(this.el).html(this.template(this.model.toJSON()));
				this.input = this.$('.todo-input');
				return this;
			},
			toggleDone: function() {
				this.model.save({done: !this.model.get('done')});
			},
			edit: function() {
				$(this.el).addClass('editing');
				this.input.focus();
			},
			close: function() {
				this.model.save({content: this.input.val()});
				$(this.el).removeClass('editing');
			},
			updateOnEnter: function(e) {
				if(e.keyCode == 13)
					this.close();
			},
			remove: function() {
				$(this.el).remove();
			},
			clear: function() {
				this.model.unbind('change', this.render, this);
				this.model.unbind('destroy', this.remove, this);
				this.model.destroy();
				this.remove();
			}
		});
		return TodoView;
	});