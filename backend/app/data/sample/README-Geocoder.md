# Geocoder Module

This module provides online geocoding functionalities (searching for addresses by text with optional filters) using the BeMap API. 

It also provides offline reversed geocoding functionalities (converting location to an address) using local map data.

## Dependencies

This module depends on other BeNomad's modules :

- **Error Manager**
- **Core**
- **BeMapAPI**
- **Vehicle Manager**

Other module's dependencies :

```
implementation "com.google.code.gson:gson:2.8.7"
implementation "androidx.lifecycle:lifecycle-runtime-ktx:2.4.0"
implementation "org.jetbrains.kotlin:kotlin-stdlib:1.5.10"
implementation "androidx.core:core-ktx:1.5.0"
implementation "androidx.appcompat:appcompat:1.3.0"
implementation "com.google.android.material:material:1.3.0"
```



## Geocoder

In order to interact with the geocoding online service, you need to create an OnlineGeocoder Instance.
The authorization data needed to interact with this API will be automatically fetched from the license file. (See the Core documentation for more info about the licensing process)

``` kotlin
val geocoder = OnlineGeoCoder(applicationContext)
```

Querying for suggestions with given text can be made with the call to `autoComplete` method 

``` kotlin
geocoder.autoComplete(
            "Louvre",
            OnlineSearchFilter("fr", position = GeoPoint(2.38305, 48.902475)),
            object : SearchCallback {
                override fun onSuggestions(suggestions: List<AutocompleteResult>, error: Error?) {
                    //error is null when no error occurred
                    Log.d(
                        TAG,
                        "onSuggestions called with $suggestions ${error?.code} ${error?.detailedMessage}"
                    )
                }
            })
```

*Note: Its currently mandatory to specify the position in the OnlineSearchFilter.*



## GeoDecoder

GeoDecoder uses local map data for searching addresses around a specific location. The search can be requested with the `searchAround` method :

``` kotlin
GeoDecoder.searchAround(
    GeoPoint(2.38305, 48.902475), 
    NearbySearchFilter("fr", 50, 5, -1, false),
    object : NearbySearchCallback {
        override fun onResults(results: List<NearbySearchResult>?) {
            if(results != null){
                for(result in results){
                    val distanceFromPosition = result.distance //the distance in meters between the provided GeoPoint and the result
                    val addressLocation = result.address.location //the location of the postal address
                    val poiLocation = if(result.address.isPOI) result.address.POILocation else null //the location of the POI (if the result is a POI)
                    val poiClassID = result.address.POIClassID //the class ID of the POI (0 if its not a POI). 
                    //The complete list of the different cartographic class IDs are available in the CartoConst class of the Map module.
                }
            }else{
                //no result
            }
        }
    })
```

You can find more details about the NearbySearchResult in the API reference.



If you want to search for EV stations, use an EvSearchFilter :

``` kotlin
GeoDecoder.searchAround(GeoPoint(2.38305, 48.902475), EvSearchFilter(
                evProfile = null, //you can pass an EvProfile to filter the results on the electric vehicle characteristics (to get only EV stations that are available for the vehicle). See the documentation of the Vehicle Manager module for more details.
                language = "fr",
                maxRadius = 10000L
            ), callback = object : NearbySearchCallback {

    override fun onResults(results: List<NearbySearchResult>?) {
        
		if (stations == null) {
            //no stations available that matches with the given EvSearchFilter
        } else {
            for (station in stations) {
                if(station is NearbyEVSearchResult){ //smart cast
                    val chargingPoints = station.compatibleChargingPoints //Get all charging points of the station that are compatible with the passed EV profile in the EvSearchFilter.
                    val nbEffectiveChargingPoints = station.nbEffectiveChargingPoints //the total number of charging points of the station, compatible or not
                    for(chargingPoint in chargingPoints){
                        val accessibility = chargingPoint.accessibility //see the full list in AccessibilityType enum
                        val authentication = chargingPoint.authentication //list of the authentication type of the charging point. See the full list in AuthenticationType enum
                        val bookingType = chargingPoint.booking //can define if the charging point can be booked (if the info is available)
                        val payment = chargingPoint.payment //all payment type available for this charging point. See the full list in PaymentType enum
                        val maxPower = chargingPoint.maxKWPower //the maximum power available for this charging point in kW
                        
                        val connectors = chargingPoint.connectors //all connectors of the charging point
                        for(connector in connectors){
                            connector.type //the connector type
                            connector.currentType //the current type of the connector
                            connector.power //the power of the connector in hW
                            connector.kWPower //the power of the connector in kW
                        }
                    }
                }
            }
        }
    
    })
```
