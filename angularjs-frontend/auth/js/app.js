(function() {

    'use strict';

    angular
        .module('authApp', ['ui.router', 'satellizer'])
        .config(function($stateProvider, $urlRouterProvider, $authProvider) {

            // Satellizer configuration that specifies which API
            // route the JWT should be retrieved from
            $authProvider.loginUrl = '/users/auth';

            // Redirect to the auth state if any other states
            // are requested other than users
            $urlRouterProvider.otherwise('/auth');
            
            $stateProvider
                .state('auth', {
                    url: '/auth',
                    templateUrl: 'login.html',
                    controller: 'AuthController as auth'
                })
                .state('tasks', {
                    url: '/tasks',
                    templateUrl: 'tasks.html',
                    controller: 'TaskController as task'
                });
        });
})();