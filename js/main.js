require.config({
	paths: {
		jquery: 'libraries/jquery/jquery-min',
		underscore: 'libraries/underscore/underscore',
		backbone: 'libraries/backbone/backbone',
		text: 'libraries/require/text'
	},
	shim: {
        'backbone': {
            deps: ['underscore', 'jquery'],
            exports: 'Backbone'
        },
        'underscore': {
            exports: '_'
        },
    }
});
require(['views/app'], function(AppView){
	var app_view = new AppView();
})