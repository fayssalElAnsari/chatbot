# Core Module

This module handles the BeNomad license validation, the download/deployment of the maps and other required resources.
Following modules require core module initialization: 

- Map module
- Planner module
- Navigation module
- GPS module
- Geocoder module

To initialize this module, you need a valid purchase UUID code provided by BeNomad. This code will determine which maps (HERE/TomTom/OpenStreetMap/etc., map coverage, full maps vs hybrid maps), have to be downloaded and how many installations are allowed.
Note: for the first Core initialization, the device must have an internet connection.

## Dependencies

This module depends on other BeNomad's modules :

- **Error Manager**

Other module's dependencies :

```
implementation "androidx.appcompat:appcompat:1.3.0"
implementation "com.google.android.material:material:1.3.0"
implementation "androidx.core:core-ktx:1.5.0"
implementation "org.jetbrains.kotlin:kotlin-stdlib:1.5.10"
implementation "org.jetbrains.kotlinx:kotlinx-coroutines-android:1.4.1"
implementation "org.jetbrains.kotlinx:kotlinx-coroutines-core:1.4.1"
```



## Permissions

On Android platforms < 10 and before starting the module initialization, your Android application must request the READ_PHONE_STATE mandatory permission (It is required for the licensing validation process).

Optionally, the WRITE_EXTERNAL_STORAGE permission may be required if maps have to be deployed outside of the application's scoped storage.

The application must also declare the INTERNET permission in its Manifest.


We simplified this process in the Permissions Manager module. You can see how to use it in its own documentation. It is not mandatory to use this module.



## Core initialization 

Here is a sample code that shows how the Core can be initialized :

``` Kotlin

import kotlinx.coroutines.launch
import androidx.lifecycle.lifecycleScope
import com.benomad.msdk.core.callbacks.OnCoreInit.OnCoreInitCallback
import com.benomad.msdk.core.Core


// Callback used to get the result of the Core initialization
val coreInitCallback = object : OnCoreInitCallback{
    override fun onCoreReady() {
        //Core initialization is successful
    }

    override fun onCoreInitError(error: Error) {
        //An error occurred during the Core initialization
    }

    override fun onCoreInitException(exception: Exception) {
        //An exception was raised during the Core initialization
    }
}

// The READ_PHONE_STATE permission must have been accepted by the user (if the Android version < 10)

//internally launched in a coroutine
    Core.getInstance().init(
        applicationContext,
        purchaseUUID,
        mapsDeploymentPath,
        resourcesPathInAssets,
        mapsPathInAssets,
        coreInitCallback
    )
```

Here is a description of the init method's arguments : 

- ```applicationContext```: the application context
- ```purchaseUUID```: A BeNomad purchase UUID
- ```mapsDeploymentPath```: the absolute path to deploy the maps to. If the maps are already deployed in the given path, it will be considered as already deployed (the maps won't be downloaded). If no value is passed for this argument, the maps are deployed in a "Maps" folder in the external scoped storage (the "files" folder of the application)
- ```resourcesPathInAssets```: the relative path from the assets folder to the resources folder. Pass null if you don't need to deploy the resources (required to use the Map module)
- ```mapsPathInAssets```: the relative path from the assets to the maps folder to deploy. If you pass null, the maps will be automatically downloaded from the BeNomad servers if no maps resources are found in the given ```mapsDeploymentPath``` 
- ```callback```: the ``` OnCoreInitCallback ``` observer that will notify about the Core init result

Note : if you specify a mapsDeploymentPath that is outside of the application's scoped storage, you will need to request the WRITE_EXTERNAL_STORAGE permission before initializing the Core.

## Observables 

There are other observables that you can subscribe to before starting the Core initialization : 

- The `OnInitProgressCallback` to get the Core initialization progress

Usage : 

``` kotlin
Core.getInstance().addOnInitProgressObserver(this) 
    // the observer parameter in this example is the class that implements the OnInitProgressCallback, but it can be also be an object variable

override fun onInitProgress(progress: Float) {
    // progress is the current global progress of the Core initialization from 0 to 100
}

```



- The `OnMapDownloadProgressCallback` to get the progress of the maps download

Usage :

``` kotlin
Core.getInstance().addOnMapDownloadProgressObserver(this)

override fun onMapDownloadProgress(progress: Float, downloaded: Float, total: Float) {
    //progress is the current progress of the maps download from 0 to 100
    //downloaded is the size in KB of the data already downloaded
    //total is the total size in KB to download
}

```

- The `OnHybridMapDownloadProgressCallback` to get the progress of the hybrid maps download (only if you're using the hybrid mode)

Usage :

``` kotlin
Core.getInstance().addOnHybridDownloadProgressObserver(this)

override fun onHybridMapDownloadProgress(status: Int, progress: Double) {
    //status is the current status of the hybrid download
    /**
        -3: Not enough storage space,
        -2: Internal error,
        -1: Download failed (network error), 
         0: Download started, 
         1: Download in progress and the percentage is available, 
         2: Download finished
     */
    
    //progress is the current progress of the maps download from 0 to 100
}
```



- The `OnMapExtractionProgressCallback` to get the progress of the maps extraction

Usage : 

``` kotlin
Core.getInstance().addOnMapExtractionProgressObserver(this)

override fun onMapExtractionProgress(progress: Float) {
   //progress is the current progress of the map extraction from 0 to 100
}

```



- The `OnLicenseErrorCallback` to be notified about errors with the license 

Usage : 

``` kotlin
Core.getInstance().addOnLicenseErrorObserver(this)

override fun onLicenseError(error: Error) {
    val messageId = error.messageId // the message id of the error
    val errorExplanation = error.detailedMessage // a more detailed message about the error (not always available, in this case an empty String is returned)
}

```



- The `OnLicenseExpiredCallback` to be notified when the license has expired 

Usage :

``` kotlin
Core.getInstance().addOnLicenseExpiredObserver(this)

override fun onLicenseExpired() {
    //this is triggered when your license has expired
}

```



- The `OnMapUpdateAvailableCallback` to be notified when a map update is available

Usage : 

``` kotlin
Core.getInstance().addOnMapUpdateAvailableObserver(this)

override fun onMapUpdateAvailable() {
    //a map update is available.
    Core.getInstance().downloadAvailableUpdate(userChoice) //user choice is a Boolean that indicates if the user accepted the update download or refused it.
}

```

*Note : To be notified about the update download progress, use `OnMapDownloadProgressCallback` which is the same callback used for the maps download progress.*



- The `OnMapDownloadedCallback` to be notified when the map update is downloaded, or when the initial map data is downloaded

Usage : 

``` kotlin
Core.getInstance().addOnMapDownloadedObserver(this)

override fun onMapDownloaded() {
    //the initial map download or the map update download has finished. In case of an update, it will be installed on next application start
}

```
- The `OnMapDownloadErrorCallback` to be notified when an error occurred during the map download, whether it's the original download or an update

Usage : 

``` kotlin
Core.getInstance().addOnMapDownloadErrorObserver(this)

override fun onMapDownloadError(error: Error) {
    //called if something happened during the map download (connection error, no space available, unzipping, etc)
    val messageId = error.messageId // the message id of the error
    val errorExplanation = error.detailedMessage // a more detailed message about the error (not always available, in this case an empty String is returned)
}

```

- The `OnOfflinePeriodExpiredCallback` to be notified when the offline period has expired

Usage : 

``` kotlin
Core.getInstance().addOnOfflinePeriodExpiredObserver(this)

override fun onOfflinePeriodExpired() {
    //this is triggered when the offline period has expired
}
```

