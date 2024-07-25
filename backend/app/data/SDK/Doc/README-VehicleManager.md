# Vehicle Manager

This module gets Energetic Vehicle Profiles from 'BeNomad' servers and uses a Room Database for handling data persistence.

## Dependencies

This module depends on other BeNomad's modules :

- **Core**
- **Settings**
- **Error Manager**

Note : in order to use this module, you have to initialize the Core module with a valid purchase UUID. See the documentation of the Core module for more details.*

Other module's dependencies :

```kotlin
kapt "androidx.room:room-compiler:2.3.0"
implementation "com.google.code.gson:gson:2.8.7"
implementation "androidx.room:room-runtime:2.3.0"
implementation "androidx.lifecycle:lifecycle-runtime-ktx:2.4.0"
implementation "org.jetbrains.kotlinx:kotlinx-coroutines-core:1.4.1"
implementation "org.jetbrains.kotlinx:kotlinx-coroutines-android:1.4.1"
implementation "org.jetbrains.kotlin:kotlin-stdlib:1.5.10"
implementation "androidx.core:core-ktx:1.5.0"
implementation "androidx.appcompat:appcompat:1.3.0"
implementation "com.google.android.material:material:1.3.0"
```



In order to interact with the module first you need to aquire a 'VehicleRepository' instance:

``` kotlin
private val vehicleRepository: VehicleRepository by lazy {
        BeMapVehicleRepository(appContext, "your_login", "your_password", "api_url")
    }
}
```

In order to refresh the database with the server data: 

``` kotlin
/**
 * Refreshes local EV vehicle repository 
 */
private fun refreshVehiclesRepository() {
    lifecycleScope.launch(Dispatchers.IO) {
        vehicleRepository.refreshManufacturers()
        vehicleRepository.refreshVehicleModels()
    }
}
```
Note: This method is a suspend function (it must be used in a coroutine).

To get all Manufacturers and Vehicle Models: 

``` kotlin
vehicleRepository.manufacturers
vehicleRepository.vehicleModels

```

Note: Manufacturers and Vehicle models are wrapped with LiveData, you can use it directly in your ViewModel and the data will be automatically updated after refreshing the repository.


To select your Vehicle Model:

``` kotlin
const val DEFAULT_CAR_ID = "44587c46-88a4-453e-9763-2cfb7a3661f4" // Renault ZOE
if (chosenVehicleModel == null) {
    vehicleRepository.vehicleModelWithId(DEFAULT_CAR_ID)
        .observe(viewLifecycleOwner) {
        this.chosenVehicleModel = it
}
    
```

Note: After saving your current vehicle, its data will automatically be updated each time the repository data is updated.

