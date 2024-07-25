# Map module

*The Core module is required to use this module. See the documentation of the Core module to see how you can use it.*

## Dependencies

This module depends on other BeNomad's modules :

- **Error Manager**
- **Core**
- **Settings**

Other module's dependencies :

```
implementation "androidx.lifecycle:lifecycle-runtime-ktx:2.4.0"
implementation "org.jetbrains.kotlin:kotlin-stdlib:1.5.10"
implementation "androidx.core:core-ktx:1.5.0"
implementation "androidx.appcompat:appcompat:1.3.0"
implementation "com.google.android.material:material:1.3.0"
```



## Using a MapView

To use a map in your application, you can add a `MapView` member in your Activity/Fragment. 

You can also use directly the `MapViewFragment`, which encapsulates a `MapView` and handles the restoration of its `MapState` across configuration changes.

``` kotlin
private lateinit var mapView: MapView
```

Then, initialize it after your Activity/Fragment view is created

``` kotlin
mapView = MapView(requireContext(), callback = this) //the callback argument is the Activity/Fragment that implements the OnMapReadyCallback
```

Here is a full description of the `MapView` constructor : 

- context : the context of the Activity/Fragment that uses the view
- gestureOptions : optional argument of `GestureOptions` type that defines which gestures are enabled. By default, all gestures are enabled if no argument is passed to the constructor of the `MapView`
- onGestureListener : optional argument of `onGestureListener `type that allows you to be notified about the gesture events of the `MapView` (for example, when the user performs a double tap gesture on the `MapView`)
- callback: an observer of `OnMapReadyCallback` type that allows to be notified when the map is ready to be manipulated, or if an error occurred during the map initialization

*Note : if the `MapView` is directly set in the XML file of the layout, there is no need to use the constructor as above. You can find an example in the "Mapping and POI" sample*

Here is a more detailed example that initializes the `MapView` using the 4 arguments of its constructor : 

``` kotlin
val onMapReadyCallback = object : OnMapReadyCallback{
    override fun onMapReady() {
		// map is ready to be manipulated
    }

    override fun onMapError(error: Error) {
        // an error occurred during the map initialization
        val messageId = error.messageId // the message id of the error
        val errorExplanation = error.detailedMessage // a more detailed message about the error (not always available, in this case an empty String is returned)
    }
}

val gestureOptions = GestureOptions() // by default all gestures are enabled
gestureOptions.setGestureStatus(Gesture.DOUBLE_TAP, false) // disable the double tap gesture


val gestureListener = object : OnGestureListener {
    override fun onTapEvent(point: PointF) {
    }

    override fun onDoubleTapEvent(point: PointF) {
    }

    override fun onLongPressEvent(point: PointF) {
    }

    override fun onPanStart() {
    }

    override fun onPanEnd() {
    }

    override fun onPinchZoomEvent(scaleFactor: Double) {
    }

    override fun onRotateEvent(angle: Double) {
    }

    override fun onTiltEvent(angle: Double) {
    }
}

mapView = MapView(requireContext(), gestureOptions, gestureListener, onMapReadyCallback)
viewLifecycleOwner.lifecycle.addObserver(mapView) // make the MapView observe the activity lifecycle to automatically call the onDestroy method of the MapView when the OnDestroy cycle of the activity is triggered (the OnDestroyView cycle in case of a Fragment)

```

Several observers can be notified of the `MapView` initialization result.

```kotlin
mapView.addOnMapReadyObserver(observer) // the observer of onMapReadyCallback type
```

Be sure to remove the observers on the appropriate lifecycle event : 

``` 
mapView.removeOnMapReadyObserver(observer)
```



## Map states

You may want to get the state of your `MapView` at a specific moment, or just have different states that you want to apply to the `MapView`. In order to do this, you can use the `MapState` class constructor : 

``` kotlin
val mapCenter = GeoPoint(3.24, 43.6) //defines a GeoPoint to center the map on
val tiltAngle = 60.0 // defines the tilt angle of the map in degrees
val zoomLevel = 15.2 //defines the zoom level of the map between 
val orientation = 20.0 // defines the map orientation in degrees

val mapState = MapState(mapCenter, tiltAngle, zoomLevel, orientation) 
mapView.updateMapState(mapState) //updates the MapView with the created MapState


MapView.Companion.setDefaultMapState(applicationContext, mapState) //save a default MapState using the SharedPreferences
val defaultMapState = MapView.Companion.getDefaultMapState(applicationContext) //get the saved default MapState

```



To get the current `MapState` of the `MapView` :

``` kotlin
val currentMapState = mapView.getCurrentMapState()
```



### Note on zoom levels

- Zoom level 0 is the zoom level where at least half the Earth is visible independently of the screen’s dimension and its dpi.

- Zoom level *n* = twice the scale of zoom level *n-1*.
  In other words the number of meters per pixel at zoom level *n* is half the number of meters at zoom level *n-1*.

  

You can zoom on the map without using the `MapState` : 

``` kotlin
mapView.zoom(zoomLevel, true) //zoom to the given zoomLevel and redraw the map
```

To access the current zoom level of the `MapView`

``` kotlin
val currentZoomLevel = mapView.zoomLevel
```



You can find all other methods available in the API Reference.



## Map parameters

**Double tap behavior**

By default, a double tap action is zooming on the map using the tapped screen's coordinates to move the map in its direction. That behavior can be changed to zoom on the map's center :

```kotlin
mapView.useMapCenterForDoubleTap = true
```

### Double tap zoom scale

The zoom scale of the double tap action on the MapView can be changed :

``` kotlin
mapView.doubleTapZoomScale = 2.0
```

### Double tap animation speed

The speed of the zoom animation when the map is double tapped can be changed : 

``` kotlin
mapView.doubleTapZoomScaleStep = 0.2 //zoom animation is now 2x quicker (initial value is 0.1)
```

*Note : the default value of this parameter is 0.1. If you want to reduce the speed of the animation, specify a lower value. If you want to increase the speed of the animation, specify a higher value.*

### Maximum tilt angle

The maximum tilt angle of the MapView can be changed : 

``` kotlin
mapView.maxTiltAngle = 50.0 //set the maximum tilt angle to 50 degrees
```



## Map Style

The different styles of the map (graphic charts) are defined by .cht files provided by BeNomad. Those files have to be deployed in the application storage in order to be used. We recommend to include all .cht files in the folder that contains the required resources to deploy in the application (see the Core documentation for more details about the resources deployment).

Here is how you can use the .cht files to change the style of the `MapView` in your application

````kotlin
val chartFile = File(getExternalFilesDir(null), "day.cht") //the path to the day.cht file already deployed in the external scoped storage of the application (files directory)
val baseDir = File(getExternalFilesDir(null), "") //the path to the base directory

val styleLoader = MapStyleLoader //used for loading the styles
styleLoader.loadStyle("DAY_STYLE", chartFile, baseDir) // loads the style from the day.cht file
mapView.setMapStyle(styleLoader.getStyle("DAY_STYLE")) // Apply the loaded 'DAY_STYLE' to the MapView

````



## Layers style

*Note : you have to load at least one map style like described above before creating new layers style*

In addition to the defined style in the .cht file, you can programmatically add new styles for some types of layers : 

- POI style : use the `createPOIStyle` method : 

  ``` kotlin
  //using the sample example as above
  val loadedStyle = MapStyleLoader.getStyle("DAY_STYLE")
  val styleCreationResult = loadedStyle?.createPOIStyle(12001, POIStyle()) //a new POI style has been created in the loaded style for the classID 12001 using the default parameters of the POIStyle constructor. See the API reference for more details about the POIStyle class.
  ```

- Polyline style : use the `createPolylineStyle` method :

  ``` kotlin
  val styleCreationResult = loadedStyle?.createPolylineStyle(12002, PolylineStyle())
  ```

- Polygon style : use the  `createPolygonStyle` method : 

  ``` kotlin
  val styleCreationResult = loadedStyle?.createPolygonStyle(12003, ClosedStyle())
  ```

`Note : Its currently not possible to change or delete a created style for a class ID`



## Add a POI to the map (add a layer)

You can programmatically add POIs to a MapView. When creating a POI, you will need to provide a class ID.

*Note about the class identifier (classID) :*

Cartographic identifiers are already defined and can be used when creating new layers to the map. (See CartoConst enum in the Core module for the full list of existing Cartographic class IDs).
You can use those existing class IDs when creating new layers. The layers will be rendered according to the style defined for this class ID.
You can also use your own class ID. Its value must be different that those defined in CartoConst enum.

The z-index of the layers is defined by their class ID : a higher class ID mean a higher z-index.
For example, a layer with a classID of 10003L will be rendered of top of all layers with a classID < 10003L



Here is an example to understand how you can handle custom layers :

``` kotlin
const val POI_POINT_ID = 10002L //ID for the POIs
private val dynamicLayerGroup = DynamicLayersGroup() //group of layers that will be attached to the MapView

val geoPoint = GeoPoint(3.24, 43.6)
val secondGeoPoint = GeoPoint(2.10, 42.5)

dynamicLayerGroup.newPoint(POI_POINT_ID, geoPoint, emptyArray()) //add a point to the group of layers with no attributes (emptyArray)

val atts = arrayOf<Attribute>(StringAttribute(KB_ATT_NAME, "Second POI"))
dynamicLayerGroup.newPoint(POI_POINT_ID, secondGeoPoint, atts) //add a second point with the same classID (same style and same z-order) but with a label

mapView?.attachDynamicLayers(dynamicLayerGroup) //attach the group of layers to the MapView. The layers of the group will be rendered on the MapView
mapView?.detachDynamicLayers() //detach the group of layers from the MapView. Layers are not visible anymore on the MapView
mapView?.attachDynamicLayers(dynamicLayerGroup) //reattach layers

dynamicLayerGroup.remove(POI_POINT_ID) //remove the two created points from the group of layers (as its the same class id). The points won't be visible on the MapView anymore (as the dynamicLayerGroup is attached to the mapview)

dynamicLayerGroup.newPoint(POI_POINT_ID, geoPoint, emptyArray()) //add a point to the group of layers that is already attached to the MapView. The point is now visible on the map 

dynamicLayerGroup.newPoint(POI_POINT_ID, secondGeoPoint, emptyArray()) //add a second point
```

Types of layers that you can create on the MapView : 

- Point
- Line
- Polyline
- Rectangle
- Ellipse
- Polygon
- Corridor

See the DynamicLayersGroup class of the Core module for more details.

You can also provide your own SVS form to add a custom layer on the map. The SVS form has to be created using the Form abstract class of the Core module.



## Layers clustering 

You can enable clustering for layers using their class ID. For example, if you enable clustering for the POI_POINT_ID defined in the example above, it means that all layers of the MapView with this class ID will automatically be regrouped in clusters depending on their position on the map. 

The layers will be regrouped in a single layer (the cluster) depending on the zoom level. (a cluster will be created with at least 3 layers). By default the icon of this cluster will show the number of layers that are regrouped.

Here is an example that shows how you can activate the clustering for points of the same class ID on the MapView (it uses the example from above) :

``` kotlin
val ids = ArrayList<Int>()
ids.add(POI_POINT_ID)

mapView?.createPOICluster("cluster_name_identifier",
                          ids, //the list of class IDs that defines which layers will be clustered
                          null, //an optional Bitmap image to change the cluster appearance
                          0xFFA500FF.toInt(), //color for the text, and for the icon if no custom icon is provided
                          1.2) //the scale of the icon shown for the cluster

mapView?.removePOICluster("cluster_name_identifier") //disable the clustering
```

You can choose to enable clustering for multiple class IDs, in order to "mix" the layers of those class IDs in the clusters.
