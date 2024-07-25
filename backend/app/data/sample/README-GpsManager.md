# GPS Manager

This module simplifies the process of requesting GPS location updates in an Android application.
It allows users to have multiple GPS sources (for example the built-in GPS or a GPS simulation file) and switch between them programmatically.

## Dependencies

This module depends on other BeNomad's modules :

- **Error Manager**
- **Core**
- **Settings**

Other module's dependencies :

```
implementation "androidx.lifecycle:lifecycle-runtime-ktx:2.4.0"
implementation "androidx.core:core-ktx:1.5.0"
implementation "org.jetbrains.kotlin:kotlin-stdlib:1.5.10"
implementation "androidx.appcompat:appcompat:1.3.0"
implementation "com.google.android.material:material:1.3.0"
```



Before using any example below, you must request access to the required permissions for the source that you will use. You can do this using the Permissions Manager module (sse the documentation of the Permissions Manager module for more details about its implementation) : 

``` Kotlin

import com.benomad.permissionsmanager.*

val source = LocationFromBuiltInGPS(context) //Built-in GPS source of the Android device. 
PermissionsManager.requestPermissions(source.getRequiredPermissions())

*Note : Each source has it own implementation of the getRequiredPermissions method.*

```

## Getting location updates from the built-in GPS


``` Kotlin 
import com.benomad.msdk.gps.*

val source = LocationFromBuiltInGPS(context)

if(source.isFeatureEnabled()) {  
  // The phone GPS feature is enabled
  if (GPSManager.getInstance().start(source)) {    
    // Get the current user location
    val currentPosition = GPSManager.getInstance().getLastKnownLocation()
 } else {
   // Cannot get location data from built-in GPS
 }
} else {
  // The built-in GPS is disabled, we should ask the user to turn it on in an AlertDialog for example.
  // Use this to open GPS settings of the user's phone
  startActivity(source.getIntentForGPSActivation())
}

```
##  Getting location updates from a GPS simulation file.


``` Kotlin

import com.benomad.msdk.gps.*

val gpsFile = File (Environment.getExternalStorageDirectory()+"../fakegps.nmea"
//the path to the fake GPS file

val source = LocationFromNMEAFile(gpsFile)

if(source.isFeatureEnabled()) {  
  if (GPSManager.getInstance().start(source)) {    
    // Get the current user location
    val currentPosition = GPSManager.getInstance().getLastKnownLocation()
  } else {
    // Cannot start location updates using the provided GPS simulation file
  }
} else {
  // GPS simulation file couldn't be loaded as a source
}
...
