# Navigation Module

This module offers real-time tracking and guidance features for both gas vehicles and electric vehicles.

## Dependencies

This module depends on other BeNomad's modules :

- **Core**
- **Settings**
- **Error Manager**
- **Mapping**
- **Planner**
- **Vehicle Manager**
- **Geocoder**
- **GPS**
- **Audio Manager**

*Note : in order to use this module, you have to initialize the Core module with a valid purchase UUID. See the documentation of the Core module for more details.*

Other module's dependencies :

```kotlin
implementation "androidx.appcompat:appcompat:1.3.0"
implementation "com.google.android.material:material:1.3.0"
implementation "androidx.navigation:navigation-fragment-ktx:2.3.5"
implementation "androidx.navigation:navigation-ui-ktx:2.3.5"
implementation "androidx.core:core-ktx:1.5.0"
implementation "org.jetbrains.kotlin:kotlin-stdlib-jdk7:1.5.10"
implementation "org.jetbrains.kotlinx:kotlinx-coroutines-android:1.4.1"
```



## Tracking mode

The Tracking mode allows the driver to have access to real-time data while driving :

- **Current speed** : the current speed in km/h of the driver
- **Current speed limit** : the current speed limit in km/h of the current road
- **Current address** : the current address that corresponds to the driver location
- **Current GPS position** : the current user "raw" location
- **Current "map-matched" position** : the map-matched location that corresponds to the position of the user on the current road.
- **Current "map-matched heading"** : the current orientation of the vehicle (angle) on the current map-matched location in degrees
- For an electric vehicle, the driver can also have access to the **current energy load** that is estimated by the SDK based on the vehicle profile, the SoC value given by the driver and its GPS location updates.



Here is how you can start a tracking session and have access to this data : 

1. Initialize the Navigation engine : 

``` kotlin
//audioFilesBasePath is the absolute path to the folder that contains all audio subfolders.
//navigationIconPath is the absolute path to the icon path used for vehicle icon during navigation.
val navigation = Navigation.getInstance(requireContext().applicationContext, audioFilesBasePath, navigationIconPath)
```

2. Attach the MapView to the Navigation instance and set the desired view mode : 

``` kotlin
//null if no error occurred while attaching the MapView
val mapViewError = navigation.attachMapView(mapView)
//see the NavigationMapViewMode enum class for more details about all available view modes
navigation.setNavigationMapViewMode(NavigationMapViewMode.GUIDANCE_VIEW_NORTH)
```

*Note : the MapView must be attached after the OnMapReady callback has been called. See the Map module documentation for more details*.

3. Set the GPS data source for the Navigation engine : 

``` kotlin
val source = LocationFromBuiltInGPS(applicationContext)
val wasGpsStarted = if (source.isFeatureEnabled()) {
    GPSManager.start(source)
}
navigation.initLocationDataSource(source)
```

4. Start the tracking session : 

``` kotlin
//null if no error occurred while starting the tracking session
val sessionError = navigation.startSession(null, null, null, null)
```

*Note : if you want to start a foreground service to have location updates while the application is in background, you have to specify the first argument which is the context, and the second which is required data for the foreground notification.* 
*For electric vehicles, you can specify the last argument which is the energy load of the vehicle in kWh to have access to the real-time estimated energy load.*

To get tracking data updates : 

``` kotlin
//the view model implements the NavigationProgressListener and gets data updates in the onNavigationProgressChanged callback
navigation.addNavigationProgressListener(viewModel) 
```

To stop the tracking session : 

``` kotlin
//you can pass null instead of the application context if you didn't pass it in the startSession method. Its only needed here to stop the foreground notification service
navigation.stopSession(applicationContext)
```



## Guidance mode

The Guidance mode allows the driver to have access to the tracking data and also the data about its current navigation on the passed route. Check the documentation of the Planner module to see how you can compute routes that will be used for the guidance mode.

In order to start a guidance session, follow the 3 first steps as to start a tracking session. Then :

**Start a guidance session :** 

```kotlin
//null if no error occurred while starting the guidance session
val sessionError = navigation.startSession(null, null, route, null)
```

*Note : for an EV guidance session, you have to specify the last argument which is the energy load of the vehicle in kWh*

**Define the guidance's view mode :**

```kotlin
//define it before starting the guidance session
navigation.defaultGuidanceViewMode = NavigationMapViewMode.GUIDANCE_VIEW_2D //guidance view mode will be 2D.
```

*Check the `NavigationMapViewMode` enumeration to see all available view modes*

**To get guidance data updates :** 

``` kotlin
//the view model implements the NavigationProgressListener and gets data updates in the onNavigationProgressChanged callback
navigation.addNavigationProgressListener(viewModel) 
```

**In the view model, use smart cast to get guidance data updates :** 

``` kotlin
if(navigationProgress is GuidanceProgress){
    //update your view model with data updates
}
```



**There are other listeners that you can use :** 

`ArrivalListener` : callbacks called when reaching via-points and destination

`ComputeRouteStateListener` : notifies when route is computed (for example, when a re-route occurs)

`ReroutingListener` : notifies when a re-route starts and indicates if its a fast re-route

`InstructionsListener` : to get real-time vocal and textual instructions

`NavigationErrorListener` : notifies when an error occurs during a navigation

`SpeedLimitListener` : notifies about speed limit changes during the navigation



See the API reference for more details. 

*Note : don't forget to add/remove your listeners. For example :* 

``` kotlin
navigation.addNavigationProgressListener(this)
navigation.removeAllNavigationProgressListeners()
```



## Notification with guidance data

When starting a guidance session using `Navigation.startSession`, you can decide to use a standard notification service that will show : 

- Remaining distance and duration
- Arrival's time
- Icon of the next instruction

If the guidance session uses a `Route` calculated using an `EV Profile`, is also shows : 

- Current SoC
- Estimated SoC at next charging station of the `Route` (see `Route.waypoints`)



To stop the notification service, call ``navigation.stopForegroundNotification(applicationContext)``

`Note : using this kind of Service allows the application to access background location updates without limitation. You can also build your own Foreground service in order to keep these location updates when your app is in background.`



## Custom instructions' icons

You can customize the icons of these instructions (from enum class `InstructionType`) : 

```
ENTER_MOTORWAY
EXIT_MOTORWAY
TAKE_FERRY
LEAVE_FERRY
STOP
```

As the icons for these maneuvers are not built by the SDK, we're using png images that can be replaced in the ressources folder deployed from the assets (icons are in **img/custom_maneuvers**).

Note that there is a **light** and a **dark** version for each icon : for example, there is "enter_motorway_dark_mode.png" and "enter_motorway_light_mode.png" that corresponds to the ENTER_MOTORWAY instruction.

These icons' size should be the same as defined in `LocationForegroundService.instructionIconWidth` (icon width, 1440 dp by default) and `LocationForegroundService.instructionIconHeight` (icon height, 720dp by default).

Here is an example of usage : 

```kotlin
var icon = GuidanceIconsBuilder.getInstructionIcon(instructionIndex, guidanceData.smBuilder)
if (icon == null) { //check if SDK has built an icon
    val instructionType =
        Navigation.getInstance().currentRoute?.sheet?.instructions?.get(instructionIndex)?.instructionType
    if (instructionType != null) {
        //get the custom icon corresponding to the instruction from deployed resources
        //the light or dark version of the icon will be chosen depending on the current phone's mode
        icon = CustomInstructionsIconBuilder.getCustomInstructionIcon( 
            appContext,
            instructionType
        )
    }
}
```

# Navigation UI

You can use the NavigationUI module which includes ready-to-use UI components.

## Dependencies

This module depends on other BeNomad's modules :

- **Core**
- **Error Manager**
- **Mapping**
- **Planner**
- **Vehicle Manager**
- **Geocoder**
- **GPS**
- **Navigation**

Other module's dependencies :

```kotlin
implementation "me.tankery.lib:circularSeekBar:1.3.2"
implementation "org.jetbrains.kotlin:kotlin-stdlib:1.5.10"
implementation "com.google.android.material:material:1.3.0"
implementation "androidx.core:core-ktx:1.5.0"
implementation "androidx.appcompat:appcompat:1.3.0"
implementation "androidx.lifecycle:lifecycle-livedata-ktx:2.4.0"
implementation "androidx.lifecycle:lifecycle-viewmodel-ktx:2.4.0"
implementation "androidx.lifecycle:lifecycle-viewmodel-savedstate:2.4.0"
implementation "androidx.core:core-ktx:1.5.0"
implementation "androidx.activity:activity-ktx:1.3.1"
implementation "androidx.fragment:fragment-ktx:1.3.6"
implementation "androidx.recyclerview:recyclerview:1.2.1"
```



## Attributions

<a href="https://www.flaticon.com/free-icons/highway" title="autoroute icônes">Link to the source of "enter_highway_black.png", "enter_highway_white.png", "exit_highway_black.png" and "exit_highway_white.png" resources</a>

<a href="https://www.flaticon.com/free-icons/ferry-boat" title="ferry boat icons">Link to the source of "enter_ferry_black.png", "enter_ferry_white.png", "exit_ferry_black.png", "exit_ferry_white.png" resources</a>

<a href="https://www.flaticon.com/free-icons/start" title="start icons">Link to the source of "arrival_flag_black.png" and "arrival_flag_white.png" resources</a>

