var ngApp = angular.module('BSPumpWebApp', []);

ngApp.controller('PipelineList', function($scope, $http) {
	$http.get('/pipelines').
		then(function(response) {
			$scope.pipelines = response.data;
		});
});
