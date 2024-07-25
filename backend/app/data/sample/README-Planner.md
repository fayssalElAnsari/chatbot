# Planner Module

This module is used to plan and compute routes. You can then use the result to preview a route on a `MapView` using the Map module, and use it in the Navigation module.
It supports simple route to one point to the other(s), alternative routes, consideration for route options, consumption calculation, optimization for electric vehicles...

## Dependencies

This module depends on other BeNomad's modules :

- **Core**
- **Settings**
- **Error Manager**
- **Vehicle Manager**

Note : in order to use this module, you have to initialize the Core module with a valid purchase UUID. See the documentation of the Core module for more details.*

Other module's dependencies :

```kotlin
implementation "androidx.core:core-ktx:1.5.0"
implementation "org.jetbrains.kotlin:kotlin-stdlib:1.5.10"
implementation "androidx.appcompat:appcompat:1.3.0"
implementation "com.google.android.material:material:1.3.0"
```



## Using the Planner

After the Core has been successfully initialized, you can start to use an instance of the Planner : 

``` kotlin
//this method will be used in examples
private fun initPlanner() : Planner?{
    planner?.cancel()
    planner = Planner()
    val planner = this.planner ?: return null
    if (!planner.isInitialized()) {
        Log.e(
            TAG,
            "Planner not initialised ! Make sure that the Core Module was initialized successfully"
        )
        return null
    }
    return planner
}
```

*Note : you can have multiple instances of the Planner, and having each of them computing a route simultaneously (one route calculation by instance)*



## Compute routes 

To start computing routes : 

``` kotlin
//assuming addresses is a variable of type List<Address> that contains at least 2 entries
planner.computeRoute(
    //define all the required information needed to calculate a route.
    RoutePlan(
        departures = listOf(addresses.first().location ?: return), //all the starting points for a route calculation
        destinations = listOf(addresses.last().location ?: return), //all the final points for a route calculation
        viaPoints = addresses.subList(1, addresses.size - 1).mapNotNull { it.location }, //all the viaPoints for the route
        routeOptions = RouteOptions(maxAlternativeRoutes = 10) //used to define parameters for the route calculation, see the RouteOptions documentation for more info. In this example, the maximum number of alternative routes is set to 10.
    ), object : ComputeRouteListener {

        override fun onComputeError(
            planner: Planner,
            error: Error
        ) {
            //an error occurred, onComputeFinished won't be called
        }

        override fun onComputeStarted(planner: Planner) {
            Log.d(TAG, "onComputeStarted called")
        }

        override fun onProgress(planner: Planner, progress: Int) {
            Log.d(TAG, "onProgress called with progress $progress")
        }

        override fun onComputeFinished(planner: Planner, routes: List<RouteResult>) {
            Log.d(TAG, "onComputeFinished called with ${routes.size} routes")
            val validComputedRoutes = mutableListOf<Route>()
                for(routeResult in routes){
                    if(routeResult.error != null){
                        //handle error for this specific route result
                        //note that you can receive an error and still have a Route object that can be used
                    }
                    if(routeResult.route != null){
                        //add the route to the list
                        validComputedRoutes.add(routeResult.route!!)
                    }
                }
        }
    })
```

A `Route` object contains information like the estimated travel/driving duration, route length, route instructions, route bounding box (see the API reference of the Planner module for more details)

*Note : matrix computation is not available for the moment. Therefore you can't use a `RoutePlan` that has multiple starting points and multiple arrival points. In other words, you can do **1 to n** or **n to 1** computations, but you can't do **n to n** computations.*



## Trace Route functionnality

You can compute a route using a list of GPS measures.

A `GPSMeasure` contains at least the GPS coordinates of the point, and can also contain : 

- The speed in km/h
- The GPS heading measure in degrees
- The time of GPS satellites in millisecond offset from the Epoch

These optional parameters are used by the SDK in order to reduce risks of map-matching errors while computing the route. In other words, it allows the SDK to compute the route with more accuracy.

*Note : The GPS heading measure is taken into account only if speed parameter >= 5 kph.*

Here is an example of trace route usage : 

```kotlin
        planner.traceRoute(
            gpsMeasures = gpsPoints,
            vehicle = vehicle,
            returnMapMatchedPoints = true,
            getAdminPath = true,
            language = Locale.getDefault(),
            listener = object : TraceRouteListener {
                override fun onComputeError(planner: Planner, error: Error) {
                	//an error occurred, route can't be computed
                }

                override fun onComputeStarted(planner: Planner) {
                    //route computation has started without error
                }

                override fun onComputeFinished(
                    planner: Planner,
                    result: RouteResult,
                    points: List<GeoMapMatchedPoint?>? 
                ) {
                    //route computation has finished
                    val route = result.route 
                    val error = result.error //an error can occur even if a route has been successfully computed
                    if(points != null){
                        for (mapMatchedPoint in points) {
                            if(mapMatchedPoint != null) { //point can be null if map-matching failed
                                val streetName = mapMatchedPoint.name
                                val adminPath = mapMatchedPoint.leftGeoPath
                                var address = ""
                                var separator = "/"
                                for (value in adminPath.withIndex()) {
                                    if(value.index == adminPath.lastIndex){
                                        separator = ""
                                    }
                                    address += "$value$separator" //build postal address
                                }
                            }
                        }
                    }
                }
            }
        )
```

In this example, all options are enabled : 

`returnMapMatchedPoints` is set to true in order to get the list of the map-matched positions (computed from passed GPS measures)

`getAdminPath` is set to true to get the full postal adress of map-matched points, meaning the administrative levels (city/department/region/country) in addition to the street name.

`language` is specified to set the preferential language for object's names (for example, objects return by `GeoMapMatchedPoint.getLeftGeoPath` will use the passed language if its available in the cartography.



## Showing `Waypoints` of a `Route` on a `MapView`

The Route object provides a list of Waypoints that can be drawn on the `MapView` using dynamic layers. Check the *Layers style* section documentation of the Map module for more info about styles and dynamic layers.

``` kotlin
val WAYPOINT_CLASS_ID = 12400 //class ID associated with a custom POI style (see the Map module documentation)
for(waypoint in route.waypoints){
    dynamicLayer.newPoint(WAYPOINT_CLASS_ID, waypoint.geoPoint, emptyArray())
}
```



## Showing a `Route` on a `MapView`

When `onComputeFinished` is called with a list of routes, you can draw them on a `MapView`. In this example, all computed routed will be drawn with the same style

``` kotlin
override fun onComputeFinished(planner: Planner, routes: List<Route>) {
    val CUSTOM_ROUTE_CLASS_ID = 12300 //class ID associated with a custom polyline style (see the Map module documentation)
	for(route in routes){
        dynamicLayer.addForm(CUSTOM_ROUTE_CLASS_ID, route.polyline2D, emptyArray()) //you can check the documentation of the Map module for more info about dynamic layers of the MapView, and how to define a style for polylines.
    }
}
```

Too see a full example where routes are drawn with different styles that are dynamically changed depending on the user choice, check the Basic Planner sample.



### Set the `MapView` centered on a specific route (where the full route is visible on the `MapView`) 

``` kotlin
route.boundingBox?.let { mapView?.zoomToRect(it, true) }
```

### Remove drawn routes from the `MapView`

Removing a drawn route mean removing the class ID associated to this route(s) from the attached dynamic layer of the `MapView` :

``` kotlin
dynamicLayer.remove(CUSTOM_ROUTE_CLASS_ID) //all layers associated with this class ID will be removed from the MapView
```



## EV features

*To use EV features of the Planner module, you need to use the Vehicle Manager module*

*If you're using hybrid maps, an internet connection is required to use EV features*

### Autonomy zone

Depending on the vehicle and its current battery level, you can show a polygon on the `MapView` that corresponds to the reachable area of the vehicle around a given map-matched location.

First, you need to get a map-matched location. In this example, we're using the GPS Manager module to get the last known location of the device and use its coordinates to get a map-matched location : 

``` kotlin
GPSManager.getLastKnownLocation().let {
    if(it != null) {
        //get a map-matched location from the "basic" last known location found
        Address.create(GeoPoint(it.longitude, it.latitude), object : AddressCreationCallback{
            override fun onResult(address: Address?) {
                if(address != null){
                    isochroneCenter = address.location
                    if(isochroneCenter != null){
                        //use the map-matched location to compute isochrone of the autonomy zone
                        computeIsochrone(isochroneCenter) //code of this function in next block
                    }else{
                        Toast.makeText(context, "Map-matched location not found", Toast.LENGTH_LONG).show()
                    }
                }else{
                    Toast.makeText(context, "Map-matching failed", Toast.LENGTH_LONG).show()
                }
            }
        })
    }else{
        Toast.makeText(context, "Location not found", Toast.LENGTH_LONG).show()
    }
}
```

`computeIsochrone` function with vehicle selection :

```kotlin
//class ID for the isochrone polygon that defines how it will be rendered on the MapView (see the section Layers style of the Map Module documentation for more details)
const val ISOCHRONE_ID = 12000L

val vehicleRepository: VehicleRepository by lazy {
    BeMapVehicleRepository(
        this,
        "login",
        "password",
        "api_url",
    )
}

val chosenVehicleModel = null
const val DEFAULT_CAR_ID = "44587c46-88a4-453e-9763-2cfb7a3661f4"

if (chosenVehicleModel == null) {
    vehicleRepository.vehicleModelWithId(DEFAULT_CAR_ID)
        .observe(viewLifecycleOwner) {
        this.chosenVehicleModel = it //select default car
}
//set current battery level to 100% using full battery capacity of vehicle
chosenVehicle?.status?.currentEnergyLoad = ((chosenVehicle?.vehicleModel?.profile as EVProfile).battery)

private fun launchReachableAreaIsochrone(mapMatchedLocation: GeoPoint){
        val batterycapacity = if(chosenVehicle?.vehicleModel?.profile is EVProfile) (chosenVehicle?.vehicleModel?.profile as EVProfile).battery else 0
        val socLimit = chosenVehicle?.status?.currentEnergyLoad?.toInt() ?: batterycapacity.toInt()
    	//cancel current computation of this planner instance (if any) and checks that the planner is initialized and not null
        val planner = initPlanner() ?: return  

        planner.computeIsochrone(
            mapMatchedLocation,
            socLimit*1000, //convert current battery level from kWh to Wh
            RouteOptions(vehicle = chosenVehicle, routeCriteria = listOf(RouteCriteria.DEFAULT, RouteCriteria.NO_FERRY), routeOptim = RouteOptim.ECO),
            object : ComputeIsochroneListener {
                override fun onComputeError(planner: Planner, error: Error) {
                    //an error occured
                }

                override fun onComputeStarted(planner: Planner) {
                    //isochrone computation start
                }

                override fun onProgress(planner: Planner, progress: Int) {
                    //isochrone computation progress
                }

                override fun onComputeFinished(planner: Planner, polygon: Polygon2D) {
                    //show the isochrone polygon on the MapView
                    dynamicLayer.addForm(ISOCHRONE_ID, polygon, emptyArray())
                    //zoom MapView to the bounding rectangle of the computed isochrone. MapView is now centered on the center of that bounding rectangle
                    mapView?.zoomToRect(polygon.boundingRect, true)
                }
            })
    }
```

*Note : the `RouteOptions` passed to the `runIsochrone` method must have a `routeOptim` set to `RouteOptim.ECO` and `routeCriteria` must have at least `RouteCriteria.DEFAULT` in order to compute an isochrone that corresponds to the reachable area for an electric vehicle*

You can also compute a reversed isochrone polygon. You can use the same example and use the `computeReversedIsochrone` function instead of the `computeIsochrone`



### Check if a route's arrival is reachable with the current SoC

After computing routes, you can check if a route's arrival is reachable with the current battery level of the vehicle : 

``` kotlin
//assuming we have a route variable that corresponds to a computed Route

//you can use the example above for the initialization of the chosenVehicle variable
val currentSoc: Double? = route.value.routeOptions.vehicle?.status?.currentEnergyLoad
val maxAcc = route.value.routeOptions.vehicle?.vehicleModel?.profile?.maxAcc ?: -1.0
val maxDec = route.value.routeOptions.vehicle?.vehicleModel?.profile?.maxDec ?: -1.0

if(currentSoc != null && maxAcc != -1.0 && maxDec != -1.0){
    //checks if the route is reachable
    val isArrivalReachable = route.isArrivalReachable(currentSoc, maxAcc, maxDec) 
}
```



### Check if a route's arrival is reachable with a SoC at arrival above a defined percentage

You can also check if the arrival is reachable with a battery level above a specified percentage : 

``` kotlin
//assuming we have a route variable that corresponds to a computed Route

//you can use the example above for the initialization of the chosenVehicle variable
val currentSoc: Double? = route.value.routeOptions.vehicle?.status?.currentEnergyLoad
val batteryCapacity: Double = (route.value.routeOptions.vehicle?.vehicleModel?.profile as EVProfile).battery
val maxAcc = route.value.routeOptions.vehicle?.vehicleModel?.profile?.maxAcc ?: -1.0
val maxDec = route.value.routeOptions.vehicle?.vehicleModel?.profile?.maxDec ?: -1.0
val minSocAtArrival = 10.0 //in percentage

if(currentSoc != null && maxAcc != -1.0 && maxDec != -1.0 && batteryCapacity > 0){
    //checks if the route is reachable with a SoC's percentage at arrival > minSocAtArrival
    val isArrivalReachable = route.isArrivalReachable(currentSoc, batteryCapacity, maxAcc, maxDec, minSocAtArrival) 
}
```



### Optimize routes

Once you have computed routes, you can optimize them using `RechargeParameters` in order to add charging stations along the route :

`socMin` : to never go under a defined battery level during the whole route

`socMinAtArrival` : to reach the arrival above a defined battery level

`socMax` : the maximum battery level to reach while charging the vehicle on the charging stations added on the route

`stopFixedTime` : an additional fixed time that will be added at each charging station added on the route

`chargingPointFilter` : filters for the charging stations that will be added on the route (see `ChargingPointFilter` methods for more info)



*Note : the `socMinAtArrival` should not be inferior to the `socMin`. If that's the case, the `socMinAtArrival` value will be set to the value of the `socMin`* when computing EV routes.

Here is an example that uses `RechargeParameters` to optimize computed routes :

```kotlin
val planner = initPlanner() ?: return
val rechargeParams = RechargeParameters(10, 15, 95, 2*60, ChargingPointFilter())
val evProfile = chosenVehicle.vehicleModel?.profile as? EVProfile
val status = chosenVehicle.status
val computedRoutes = ... //list of computed routes obtained using the Planner.computeRoute function

if(evProfile != null && status != null){
    planner.computeRouteWithChargeStops(computedRoutes, evProfile, status, rechargeParams, object : ComputeRouteListener {
        override fun onComputeError(
            planner: Planner,
            error: Error
        ) {
            //an error occurred, onComputeFinished won't be called (no optimization)
        }

        override fun onComputeStarted(planner: Planner) {
            Log.d(TAG, "onComputeStarted called")
        }

        override fun onProgress(planner: Planner, progress: Int) {
            Log.d(TAG, "onProgress called with progress $progress")
        }

        override fun onComputeFinished(planner: Planner, routes: List<RouteResult>) {
            Log.d(TAG, "onComputeFinished called with ${routes.size}")
            val computedRoutesOptimized = mutableListOf<Route>()

            for((i, routeResult) in routes.withIndex()){
                if(routeResult is EVRouteResult){ //smart cast
                    val optimizationResult = routeResult.optimChargeResult
                    val optimResultDescription = optimizationResult.text //the description of the optimization result for this route
                    if(routeResult.route != null){
                        computedRoutesOptimized.add(routeResult.route!!) //add the optimized route
                    }else{
                        val routeNotOptimized = computedRoutes?.get(i) //get the initial computed route (as no optimization is available)
                        if(routeNotOptimized != null){
                            computedRoutesOptimized.add(routeNotOptimized)
                        }
                    }
                }
            }
            //computedRoutesOptimized now contains optimized routes (or initial computed routes if no optimization for a route is available)
        }
    })
}
```



### Compute optimized routes

You can also compute routes and optimize them at the same time

``` kotlin
val planner = initPlanner() ?: return
val rechargeParams = RechargeParameters(10, 15, 95, 2*60, ChargingPointFilter())
//assuming chosenVehicle is a Vehicle not null that has an EVProfile and a VehicleStatus with a currentEnergyLoad defined in kWh
val evRouteOptions = EVRouteOptions(vehicle = chosenVehicle!!, maxAlternativeRoutes = 2, rechargeParameters = rechargeParams)
//assuming addresses is a variable of type List<Address> that contains at least 2 entries
val evRoutePlan = EVRoutePlan(
    departures = listOf(addresses.first().location ?: return),
    destinations = listOf(addresses.last().location ?: return),
    viaPoints = addresses.subList(1, addresses.size - 1).mapNotNull { it.location },
    evRouteOptions
)

planner.computeRouteWithChargeStops(evRoutePlan, object : ComputeRouteListener {
        override fun onComputeError(
            planner: Planner,
            error: Error
        ) {
		//an error occurred, onComputeFinished won't be called
        }

        override fun onComputeStarted(planner: Planner) {
            Log.d(TAG, "onComputeStarted called")
        }

        override fun onProgress(planner: Planner, progress: Int) {
            Log.d(TAG, "onProgress called with progress $progress")
        }

        override fun onComputeFinished(planner: Planner, routes: List<RouteResult>) {
            Log.d(TAG, "onComputeFinished called with ${routes.size}")
		   val computedRoutesOptimized = mutableListOf<Route>()

            for(routeResult in routes){
                if(routeResult is EVRouteResult){ //smart cast
                    val optimizationResult = routeResult.optimChargeResult
                    val optimResultDescription = optimizationResult.text //the description of the optimization result for this route
                    if(routeResult.route != null){
                        computedRoutesOptimized.add(routeResult.route!!) //add the optimized route
                    }
                }
            }
            //computedRoutesOptimized now contains optimized routes
    })
```
