import 'dart:collection';
import 'dart:convert';
import 'package:frontend/api.dart' as api;
import 'package:frontend/utils/notifiers.dart';
import 'package:http/http.dart' as http;
import 'package:geolocator/geolocator.dart';

import 'package:flutter/material.dart';
import 'package:flutter_geocoder/geocoder.dart';
import 'package:frontend/components/search_widget.dart';
import 'package:latlong2/latlong.dart';
import 'package:easy_localization/easy_localization.dart';
import 'package:provider/provider.dart';

class EditAddressModal extends StatefulWidget {
  final String currentAddress;
  final Function(LatLng, String) onPositionChanged;

  const EditAddressModal({
    Key? key,
    required this.currentAddress,
    required this.onPositionChanged,
  }) : super(key: key);

  @override
  State<EditAddressModal> createState() => _EditAddressModalState();
}

class _EditAddressModalState extends State<EditAddressModal> {
  List<api.AddressSuggestion> suggestions = [];

  @override
  Widget build(BuildContext context) {
    return Consumer<LocationNotifier>(builder: (context, notifier, child) {
      return Padding(
        padding: MediaQuery.of(context).viewInsets,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(height: 10),
            Padding(
              padding: const EdgeInsets.only(top: 5),
              child: Text(
                'edit_address_modal.title'.tr(),
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(height: 15),
            const Divider(
              height: 10,
              thickness: 1,
              color: Colors.grey,
              indent: 10,
              endIndent: 10,
            ),
            TextButton(
              onPressed: () {
                fetchCurrentLocation(notifier);
              },
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.my_location_rounded),
                    const SizedBox(width: 10),
                    Text(
                      'edit_address_modal.use_current_location'.tr(),
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            SearchWidget(
              text: notifier.address,
              onSubmitted: (text) {
                fetchAddressCompletion(text);
              },
              hintText: 'edit_address_modal.address_hint'.tr(),
            ),
            Container(
              height: 160,
              child: ListView.builder(
                  itemCount: suggestions.length,
                  itemBuilder: (context, index) {
                    return Center(
                      child: Column(
                        children: [
                          TextButton(
                            child: Text(
                              suggestions[index].displayName,
                              style: const TextStyle(
                                  color: Colors.black),
                              textAlign: TextAlign.center,
                            ),
                            onPressed: () {
                              notifier.setPosition(LatLng(
                                  suggestions[index].latitude,
                                  suggestions[index].longitude));
                              getAddress(notifier.position.latitude,
                                      notifier.position.longitude)
                                  .then((value) {
                                notifier.setAddress(
                                    value.first.addressLine ?? "");
                                Navigator.pop(context); // close the modal
                              });
                            },
                          ),
                          const SizedBox(
                            height: 10,
                          ),
                          const Divider(
                            height: 10,
                            thickness: 1,
                            color: Colors.grey,
                            indent: 10,
                            endIndent: 10,
                          ),
                          const SizedBox(
                            height: 10,
                          ),
                        ],
                      ),
                    );
                  }),
            )
          ],
        ),
      );
    });
  }

  fetchCurrentLocation(LocationNotifier notifier) async {
    bool serviceEnabled;
    LocationPermission permission;

    // Test if location services are enabled.
    serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      // Location services are not enabled don't continue
      // accessing the position and request users of the
      // App to enable the location services.
      print('Location services are disabled.');
    }

    permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        // Permissions are denied, next time you could try
        // requesting permissions again (this is also where
        // Android's shouldShowRequestPermissionRationale
        // returned true. According to Android guidelines
        // your App should show an explanatory UI now.
        print('Location permissions are denied');
      }
    }

    if (permission == LocationPermission.deniedForever) {
      // Permissions are denied forever, handle appropriately.
      print(
          'Location permissions are permanently denied, we cannot request permissions.');
    }

    // When we reach here, permissions are granted and we can
    // continue accessing the position of the device.
    Position currentPosition =
        await Geolocator.getCurrentPosition(forceAndroidLocationManager: true);
    notifier.setPosition(
        LatLng(currentPosition.latitude, currentPosition.longitude));
    print(notifier.position);

    getAddress(currentPosition.latitude, currentPosition.longitude)
        .then((values) {
      notifier.setAddress(values.first.addressLine ?? "");
      print(notifier.address);
      Navigator.pop(context); // close the modal
      widget.onPositionChanged(notifier.position, notifier.address);
    });
  }

  Future<List<Address>> getAddress(double lat, double lang) async {
    final coordinates = Coordinates(lat, lang);
    List<Address> add =
        await Geocoder.local.findAddressesFromCoordinates(coordinates);
    return add;
  }

  Future<void> fetchAddressCompletion(String input) async {
    var uri = Uri(
        scheme: "https",
        host: "nominatim.openstreetmap.org",
        pathSegments: ["search"],
        query: "format=json&city=Berlin&street=$input");

    try {
      // Make the GET request
      Map<String, String> headers = HashMap();
      headers.putIfAbsent('Accept', () => 'application/json');

      http.Response response = await http.get(uri, headers: headers);
      // The request succeeded. Process the JSON.

      List<dynamic> result = json.decode(response.body);
      List<api.AddressSuggestion> localSuggestions = [];

      for (final entry in result) {
        api.AddressSuggestion suggestion = api.AddressSuggestion(
            displayName: entry["display_name"],
            latitude: double.tryParse(entry["lat"].toString()) ?? 0,
            longitude: double.tryParse(entry["lon"].toString()) ?? 0,
            type: entry["type"],
            importance: double.tryParse(entry["importance"].toString()) ?? 0);
        localSuggestions.add(suggestion);
      }
      setState(() {
        suggestions = localSuggestions;
      });
    } catch (e) {
      // The GET request failed. Handle the error.
      print("Couldn't open $uri");
      print(e);
    }
  }
}
