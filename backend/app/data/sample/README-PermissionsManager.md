# Permissions Manager

This module simplifies the process for requesting permissions in an Android application. 
The default required permissions are those required for the BeNomad SDK, but you can specify which one you want to use.

## Dependencies

```kotlin
implementation "androidx.core:core-ktx:1.5.0"
implementation "org.jetbrains.kotlin:kotlin-stdlib:1.5.10"
implementation "androidx.appcompat:appcompat:1.3.0"
implementation "com.google.android.material:material:1.3.0"
```



The permissions are defined by a Pair of String for the permission name and a Boolean that indicates whereas the permission is required or not : 

``` Kotlin
    //not required
    val fineLocationPermission = Pair(Manifest.permission.ACCESS_FINE_LOCATION, false) 
    val coarseLocationPermission = Pair(Manifest.permission.ACCESS_COARSE_LOCATION, false)

    //required
    val externalStoragePermission = Pair(Manifest.permission.WRITE_EXTERNAL_STORAGE, true)
    val readPhoneStatePermission = Pair(Manifest.permission.READ_PHONE_STATE, true)
```

To define the permissions that you want to request, use the defineRequiredPermissions method :

``` Kotlin

        PermissionsManager.definePermissions(linkedMapOf(
            fineLocationPermission,
            coarseLocationPermission,
            externalStoragePermission,
            readPhoneStatePermission
        ))

```

The Activity used for requesting the permissions must implement this interface : 

``` kotlin
ActivityCompat.OnRequestPermissionsResultCallback
```

Then request the permissions in your application : 

``` Kotlin

val permissionsAlreadyGranted = PermissionsManager.requestPermissions(this)

        if(permissionsAlreadyGranted)
            Toast.makeText(this, "All permissions are granted", Toast.LENGTH_LONG).show() //the permissions are already granted

```

You can also call directly the requestPermissions method and give the permissions that you want to request : 

``` Kotlin

        val permissionsAlreadyGranted = PermissionsManager.requestPermissions(this, linkedMapOf(
            readPhoneStatePermission
        ))

        if(permissionsAlreadyGranted)
            Toast.makeText(this, "All permissions are granted", Toast.LENGTH_LONG).show() //the permissions are already granted


```

To handle the results of the permissions request (when all permissions are not granted yet), your Activity must implement the ActivityCompat.OnRequestPermissionsResultCallback interface. Here is a sample code that shows how the results can be handled : 

``` Kotlin

       /** Handle permissions request results */
       override fun onRequestPermissionsResult(
           requestCode: Int,
           permissions: Array<out String>,
           grantResults: IntArray
       ) {
           super.onRequestPermissionsResult(requestCode, permissions, grantResults)
   
           //Check if the request code matches the request code used for requesting the permissions
           if (requestCode == PermissionsManager.PERMISSIONS_REQUEST_CODE) {
               val permissionsResults: HashMap<String, Int> = hashMapOf()
               var count = 0
   
               //Count the number of permissions denied during the request
               for (i in 0..grantResults.size - 1) {
                   if (grantResults[i] == PackageManager.PERMISSION_DENIED && PermissionsManager.isPermissionRequired(permissions[i])) {
                       permissionsResults.put(permissions[i], grantResults[i])
                       count++
                   }
               }
   
               //All permissions have been granted
               if (count == 0) {
                   Toast.makeText(this, "All permissions are granted", Toast.LENGTH_LONG).show()
               } else {
                   //Some permissions have been denied by the user
                   for (entry in permissionsResults.entries) {
                       val permissionName = entry.key
   
                       if(isPermissionRequired(permissionName)){
                           if (shouldShowRequestPermissionRationaleCompat(this, permissionName)) {
                               //Permission is denied for the first time : shows a dialog
                               PermissionsManager.showRequiredPermissionExplainedDialog(this, permissionName, "OPTIONAL : Custom explanation for the declined permission here. It should be a string resource with translations")
                           } else {
                               //Permission is denied (and never ask again is checked or permission is not defined in the manifest)
                               PermissionsManager.showRequiredPermissionIsFullyDeniedDialog(this)
                           }
                       }
                   }
               }
           }
       }


```