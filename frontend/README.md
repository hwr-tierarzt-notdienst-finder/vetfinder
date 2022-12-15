# VetFinder Mobile App

## Folder Structure

- `lib/` : the main directory in the project where the .dart codes are written. It contains .dart components for the API functionality (`api.dart`) and different screens/pages in the app (e.g. `home.dart` and `settings.dart`).
- `lib/components/` : subdirectory containing reusable components (Widgets) that can be imported and used in one or multiple screens.
- `lib/utils/` :  subdirectory containing general purpose components such as constant variables and other classes.

## Saving data locally using *shared_preferences*

Source: https://pub.dev/packages/shared_preferences

A `SharedPrefs` class is defined in the `preferences.dart` file with getter and setter for the various user settings in the app. The following data types can be used for this functionality: int, bool, String, List<String>. Simply add a new getter and setter entry in `preferences.dart` to add a new variable to be saved locally.
When the app is first ran, an instance of the `SharedPrefs` class will be created, allowing the getter and setter to be accessed at any part of the code using `SharedPrefs().nameOfTheVariable`.

## Localization using *easy_localization*

Source: https://pub.dev/packages/easy_localization

Localization is accomplished using the easy_localization library. Please refer to the documentation page of the library, as the implementation in the app adheres to it exactly.

## General workflow of the app

1.	Initialization of the app happens in the `main.dart` file. Data will be fetched from the server by calling the `fetchVeterinarians` function from `api.dart`.
2.	Data fetched from `fetchVeterinarians` will be saved in the `SharedPrefs` instance as JSON-String and passed on to the `getFilteredVeterinarians` function to be filtered based on the filter settings saved in the `SharedPrefs` instance and sorted based on distance and search query.
3.	Home page (`home.dart`) is shown first to user. Refreshing the list by swiping down on it will recall `fetchVeterinarians`, resulting in the saved JSON-String to be overwritten (if the GET Request is successfull) and rebuild the page.
4.	The home page shall always use the filtered data returned from `getFilteredVeterinarians`.
5.	Each `Veterinarian` object owns a unique ID, that can be passed to the next page as an argument, allowing the next page (`vet_information.dart`) to access the attribute of this object and thus to show information about a veterinarian.
6.	Updating the filter settings in the filter dialog window (`search_filter_dialog.dart`) and pressing the apply button will update the filter settings variables in the `SharedPrefs` instance, recall `getFilteredVeterinarians` and rebuild the home page.
7.	Updating the user’s current location in the address dialog window (`edit_address_modal.dart`), be it automatically via GPS or manually by inputting  the address,  will update the user’s location variable in the `SharedPrefs` instance, recall `getFilteredVeterinarians` and rebuild the home page.

## Setup

In order for the API to work, a JWT token generated from the backend should be provided locally as `secret_token.txt` in the `assets/` directory.
Please refer to the documentation for backend for more information about the token generation.

## Building

To create a production version of your app:

Update package dependencies with:
```bash
flutter pub get
```

Compile and run the app with:
```bash
flutter run
```
