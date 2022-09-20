import 'dart:collection';
import 'dart:convert';
import 'package:frontend/api.dart' as api;
import 'package:frontend/utils/notifiers.dart';
import 'package:http/http.dart' as Http;

import 'package:flutter/material.dart';
import 'package:flutter_geocoder/geocoder.dart';
import 'package:frontend/components/search_widget.dart';
import 'package:latlong2/latlong.dart';
import 'package:location/location.dart';
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
  Location location = Location();
  List<api.AddressSuggestion> suggestions = [];

  @override
  Widget build(BuildContext context) {
    return Consumer<LocationNotifier>(builder: (context, notifier, child) {
      return Container(
        decoration: BoxDecoration(borderRadius: BorderRadius.circular(20)),
        height: MediaQuery.of(context).size.height * 0.9,
        child: Padding(
          padding: const EdgeInsets.all(5),
          child: Column(
            children: [
              const SizedBox(height: 10),
              Text(
                'edit_address_modal.title'.tr(),
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
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
              const Divider(
                height: 10,
                thickness: 1,
                color: Colors.grey,
                indent: 20,
                endIndent: 20,
              ),
              SearchWidget(
                text: notifier.address,
                onSubmitted: (text) {
                  fetchAddressCompletion(text);
                },
                hintText: 'edit_address_modal.address_hint'.tr(),
              ),
              Expanded(
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
                                    fontWeight: FontWeight.bold,
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
                              height: 20,
                            )
                          ],
                        ),
                      );
                    }),
              )
            ],
          ),
        ),
      );
    });
  }

  fetchCurrentLocation(LocationNotifier notifier) async {
    bool serviceEnabled;
    PermissionStatus permissionGranted;

    serviceEnabled = await location.serviceEnabled();
    if (!serviceEnabled) {
      serviceEnabled = await location.requestService();
      if (!serviceEnabled) {
        return;
      }
    }

    permissionGranted = await location.hasPermission();
    if (permissionGranted == PermissionStatus.denied) {
      permissionGranted = await location.requestPermission();
      if (permissionGranted != PermissionStatus.granted) {
        return;
      }
    }

    LocationData currentPosition = await location.getLocation();
    if (currentPosition.latitude != null && currentPosition.longitude != null) {
      notifier.setPosition(
          LatLng(currentPosition.latitude!, currentPosition.longitude!));

      getAddress(currentPosition.latitude!, currentPosition.longitude!)
          .then((values) {
        notifier.setAddress(values.first.addressLine ?? "");
        Navigator.pop(context); // close the modal
        widget.onPositionChanged(notifier.position, notifier.address);
      });
    }
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

      Http.Response response = await Http.get(uri, headers: headers);
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
