var app = angular.module("kikk", ['ui.bootstrap']);

app.factory("OrderService", [
		"$http",
		function($http){
			var query = function(){
				console.log(this.filter);
				var qs = "";
				if ("condition" in this.filter && this.filter.condition.length > 0){
					qs += this.filter.conditionType + "=" + this.filter.condition + "&";
				}

				if ("dateFrom" in this.filter && this.filter.dateFrom.length > 0){
					qs += this.filter.dateType + "_from" + "=" + this.filter.dateFrom + "&";
					qs += this.filter.dateType + "_to" + "=" + this.filter.dateTo + "&";
				}

				if ("status" in this.filter && this.filter.status.length > 0){
					qs += "status=" + this.filter.status + "&";
				}

				// console.log(qs);
				var that = this;
				$http({
					method: 'GET',
					url: 'http://localhost:5000/order?' + qs
				}).then(function(response){
					that.data.length = 0;
					for (var i = 0; i < response.data.result.length; i ++){
						that.data.push(response.data.result[i]);
					}
					// console.log(that.data)
				},function(response){
					console.log(response);
				});

				// this.data.length = 0;
				// this.data.push(
				// 	{
				// 		id: 1,
				// 		itemNumber: "124",
				// 		description: "description 123",
				// 		image: "http://images17.newegg.com/is/image/newegg/20-226-792-Z01?$S640$",
				// 		qty : 3,
				// 		address : ["Evan liu", "16351 Brancusi LN"],
				// 		address2: "Evan Liu\n16351 Brancusi LN\nChino Hills,CA 91709",
				// 		trackingNumber : [
				// 			"1000000",
				// 			"1000001"
				// 		],
				// 		status: "O",
				// 	},
				// 	{
				// 		id: 2,
				// 		itemNumber: "123",
				// 		description: "description 123",
				// 		image: "http://images17.newegg.com/is/image/newegg/20-233-949-TS?$S125$",
				// 		qty : 1,
				// 		address : ["Evan liu2", "16351 Brancusi LN"],
				// 		address2: "Evan Liu2\n16351 Brancusi LN",
				// 		trackingNumber : [
				// 			"1000000",
				// 			"1000001"
				// 		],
				// 		status: "O",
				// 	}
				// );http://localhost:5000/order/
			};

			var update = function(order, successCallback, faildCallback){
				/////
				for (var i = order.tracking_numbers.length - 1; i >= 0; i --){
					if (order.tracking_numbers[i].tracking_number == undefined 
						|| order.tracking_numbers[i].tracking_number.length < 1){
						order.tracking_numbers.splice(i,1);
					}
				}
				var that = this;
				$http({
					method: 'PUT',
					url: 'http://localhost:5000/order',
					data: order

				}).then(successCallback, faildCallback);

			};



			return {
				data: [],
				query: query,
				update: update 
			};	
		}
	]);

app.factory("ItemService", ["$http", function($http){
	var getItemById = function(itemNumber){
		return {
			itemNumber: itemNumber,
			shippingCost: 3.99
		};
	}
	return {
		getItemById: getItemById
	}
}]);

app.run(function($rootScope){
	$rootScope.orderStatusDef = [{code:'O', desc:'Open'},{code:'S', desc:'Shipped'},{code:'C', desc:'Closed'}];
	$rootScope.formatOrderStatus = function(code){
		for(var i = 0; i < $rootScope.orderStatusDef.length; i ++){
			var status = $rootScope.orderStatusDef[i];
			if(status.code == code){
				return status.desc;
			}
		}
		return 'Unkown';
	};
});

app.controller("filterController", ["$scope","OrderService", function($scope, OrderService){
	$scope._name = "filter";
	$scope.filter = {
		conditionType: "item_id",
		dateType: "order_date",
		status: "O",
	};
	$scope.search = function(){
		OrderService.filter = $scope.filter;
		OrderService.query();
	};
	// $scope.search();
}
]);

app.controller("tableController",  function($scope, $uibModal, OrderService){
	$scope._name = "orderList";
	$scope.data = OrderService.data;

	// $scope.add = function(){
	// 	var order = {
	// 		itemNumber: "124",
	// 		description: "description 123",
	// 		image: "",
	// 		qty : 3,
	// 		address : "Evan liu 16351 Brancusi LN",
	// 		trackingNumber : "100000000",
	// 	}
	// 	$scope.data.push(order)
	// };
	// $scope.showDetail = function(order){
	// 	$scope.$emit("showDetail", order)
	// }


//--------------------------------------------


	$scope.detail = function(order){
		var detailInstance = $uibModal.open({
			templateUrl: '/detail.html',
			controller: 'detailController',
			resolve: {order: order}
		});

		detailInstance.opened.then(function(){
			// console.log('moda is opened');
		});

		detailInstance.result.then(function(result){
			// console.log(result);
		},function(reason){
			// console.log(reason);
		});
	};
}
);

app.controller("detailController",function($scope, $uibModalInstance, order, OrderService){
		$scope.error = null; 
		var copiedOrder = $.extend(true, {}, order);
		if (copiedOrder.tracking_numbers == undefined){
			copiedOrder.tracking_numbers = [];
		}
		var tmp = copiedOrder.qty - copiedOrder.tracking_numbers.length;
		for(var i = 0; i < tmp; i ++){
			copiedOrder.tracking_numbers.push({tracking_number:"", cost: copiedOrder.item.shipping_cost})
		}
		$scope.order = copiedOrder;

		$scope.update = function(){
		var order = $scope.order;
		OrderService.update(order, function(response){
			$uibModalInstance.close();
			OrderService.query();
		},function(response){
			if (response.data != null){
				$scope.error = response.data.error;
			}else{
				$scope.error = 'system exception';
			}
		});
	};

	$scope.cancel = function(){
			console.log('cancel');
			$uibModalInstance.close();
		}
});

// app.controller("detail", ["$scope", "OrderService", "ItemService", function($scope, OrderService, ItemService){
// 	$scope._name = "detail";
// 	$scope.$on("orderList_showDetail", function(e, order){
// 		if (order.tracking_numbers == undefined){
// 			order.tracking_numbers = [];
// 		}
// 		var tmp = order.qty - order.tracking_numbers.length;
// 		for(var i = 0; i < tmp; i ++){
// 			order.tracking_numbers.push({tracking_number:"", cost: order.item.shipping_cost})
// 		}

// 		$scope.order = order;

// 	});
// 	$scope.update = function(){
// 		// $scope.$emit("ship", $scope.orderShipped);
// 		var order = $scope.order;
// 		OrderService.update(order);
// 	};
// }
// ]);

app.directive('decimal', function(){
	return {
		require: 'ngModel',
		link: function(scope, elem, attrs, ngModel){
			ngModel.$parsers.push(function(input){
				return parseInt(input * 100);
			});

			ngModel.$formatters.push(function(input){
				return input / 100.0;
			});
		}
	};
});

app.directive('status_desc', function(){
	return {
		require: 'ngModel',
		link: function(scope, elem, attrs, ngModel){
			// ngModel.$parsers.push(function(input){

			// });
			// ngModel.$formatters.push(function(input){
			// 	swith(input){
			// 		case 'O':
			// 			return 'Open';
			// 		case 'S':
			// 			return 'Shipped';
			// 		case 'C':
			// 			return 'Closed';
			// 		default:
			// 			return 'Unkown';
			// 	}

		}
	};
});