import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_map/plugin_api.dart';
import 'package:frontend/utils/notifiers.dart';
import 'package:frontend/utils/preferences.dart';
import 'package:string_similarity/string_similarity.dart';
import 'package:provider/provider.dart';
import 'package:easy_localization/easy_localization.dart';

import 'package:frontend/components/veterinarian.dart';
import 'package:frontend/components/search_widget.dart';
import 'package:frontend/components/search_filter_dialog.dart';
import 'package:frontend/components/edit_address_modal.dart';
import 'package:frontend/api.dart';

import 'dart:collection';

class Home extends StatefulWidget {
  const Home({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  State<Home> createState() => _HomeState();
}

class _HomeState extends State<Home> {
  MapController mapController = MapController();
  List<Marker> markers = [];
  List<Veterinarian> vets = getFilteredVeterinarians();
  String query = '';
  Marker? currentLocationMarker;

  TextButton createMarkerWidget(Veterinarian vet) {
    return TextButton.icon(
      onPressed: () {
        showDialog(
            context: context,
            builder: (BuildContext context) {
              return AlertDialog(
                title: Text(vet.name),
                content: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: <Widget>[
                    Text("Adresse: ${vet.getAddress()}"),
                    const SizedBox(height: 10),
                    Text("Telefonnummer: ${vet.telephoneNumber}"),
                    const SizedBox(height: 10),
                    Text("Webseite: ${vet.websiteUrl}"),
                  ],
                ),
                actions: <Widget>[
                  TextButton(
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: const <Widget>[
                        Text("Okay"),
                        SizedBox(width: 5),
                        Icon(Icons.arrow_forward)
                      ],
                    ),
                    onPressed: () {
                      // Close the dialog
                      Navigator.of(context).pop();
                    },
                  ),
                ],
              );
            });
      },
      icon: const Icon(Icons.location_on, color: Colors.red, size: 35.0),
      label: Text(
        vet.name,
        overflow: TextOverflow.ellipsis,
        softWrap: false,
        maxLines: 2,
      ),
    );
  }

  void createMarkers(LocationNotifier notifier) {
    markers.clear();
    for (Veterinarian vet in vets) {
      markers.add(Marker(
          width: 100,
          height: 50,
          point: vet.getPosition(),
          builder: (context) => createMarkerWidget(vet)));
    }
  }

  void addCurrentLocationMarker(LocationNotifier notifier) {
    if (currentLocationMarker != null) {
      markers.remove(currentLocationMarker);
    }

    currentLocationMarker = Marker(
        width: 100,
        height: 50,
        point: notifier.position,
        builder: (context) =>
            const Icon(Icons.location_pin, color: Colors.blue, size: 35.0));
    markers.add(currentLocationMarker!);
  }

  void searchVet(String query) {
    setState(() {
      this.query = query.toLowerCase();

      // Create a list of veterinarians based on query
      Map similarityMap = {};

      for (Veterinarian vet in vets) {
        String vetInfo = '${vet.name} ${vet.getAddress()}';
        final comparison = this.query.similarityTo(vetInfo);
        similarityMap[vet.id] = comparison;
      }

      var sortedMap = SplayTreeMap<String, double>.from(similarityMap,
          (key1, key2) => (similarityMap[key1] > similarityMap[key2]) ? -1 : 1);
      vets = sortedMap.keys.map((id) => getVeterinarianById(id)).toList();
    });
  }

  Future<void> _showFilterDialog(BuildContext context) {
    return showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return SearchFilterDialog(
          availableCategories: getAvailableCategories(),
        );
      },
    );
  }

  void _showEditAddressModalBottomSheet(BuildContext context) {
    showModalBottomSheet(
        context: context,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        builder: (BuildContext context) {
          return EditAddressModal(
            currentAddress: SharedPrefs().currentAddress,
            onPositionChanged: (position, address) => {
              setState(() {
                SharedPrefs().currentAddress = address;
                SharedPrefs().currentPosition = position;
                mapController.move(position, 18);
              })
            },
          );
        });
  }

  @override
  Widget build(BuildContext context) {
    // This method is rerun every time setState is called, for instance as done
    // by the _incrementCounter method above.
    //
    // The Flutter framework has been optimized to make rerunning build methods
    // fast, so that you can just rebuild anything that needs updating rather
    // than having to individually change instances of widgets.
    return Consumer2<FilterNotifier, LocationNotifier>(
        builder: (context, filterNotifier, locationNotifier, child) {
      // Update the list of vets if filter is applied
      if (filterNotifier.filterUpdated) {
        vets = getFilteredVeterinarians();
        createMarkers(locationNotifier);
        filterNotifier.filterUpdated = false;
      }

      addCurrentLocationMarker(locationNotifier);

      return Scaffold(
        appBar: AppBar(
          title: Text(widget.title),
          actions: [
            IconButton(
                onPressed: () => Navigator.pushNamed(context, '/setting'),
                icon: const Icon(Icons.settings)),
          ],
        ),
        body: Column(
          children: [
            TextButton(
              onPressed: () {
                _showEditAddressModalBottomSheet(context);
              },
              child: Padding(
                padding: const EdgeInsets.all(10),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(locationNotifier.address.isNotEmpty
                        ? locationNotifier.address
                        : 'home.current_address'.tr()),
                    const Icon(Icons.arrow_drop_down_rounded),
                  ],
                ),
              ),
            ),
            Row(
              children: [
                Flexible(
                  child: SearchWidget(
                      text: query,
                      onSubmitted: searchVet,
                      hintText: 'home.query_hint'.tr()),
                ),
                Container(
                  margin: const EdgeInsets.fromLTRB(0, 0, 8, 0),
                  child: ElevatedButton(
                      onPressed: () => _showFilterDialog(context),
                      child: const Icon(
                        Icons.filter_list_rounded,
                      )),
                ),
              ],
            ),
            Expanded(
              child: Container(
                width: MediaQuery.of(context).size.width,
                height: MediaQuery.of(context).size.height * 0.5,
                child: Stack(
                  children: [
                    Padding(
                      padding: const EdgeInsets.all(8),
                      child: FlutterMap(
                        mapController: mapController,
                        options: MapOptions(zoom: 11, rotation: 0),
                        layers: [
                          TileLayerOptions(
                            minZoom: 1,
                            maxZoom: 18,
                            backgroundColor: Colors.black,
                            urlTemplate:
                                'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                            subdomains: ['a', 'b', 'c'],
                          ),
                          MarkerLayerOptions(markers: markers)
                        ],
                      ),
                    ),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Padding(
                          padding: const EdgeInsets.all(12.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            mainAxisAlignment: MainAxisAlignment.end,
                            children: [
                              FloatingActionButton(
                                mini: true,
                                onPressed: () => {
                                  mapController.move(
                                      locationNotifier.position, 18)
                                },
                                child: const Icon(Icons.search),
                              ),
                            ],
                          ),
                        ),
                      ],
                    )
                  ],
                ),
              ),
            ),
            Expanded(
              child: ListView.builder(
                  itemCount: vets.length,
                  itemBuilder: (context, index) {
                    return VetCard(
                        id: vets[index].id,
                        name: vets[index].name,
                        telephoneNumber: vets[index].telephoneNumber,
                        location: vets[index].location,
                        onViewInMap: (position) {
                          mapController.move(position, 16);
                        },
                        websiteUrl: vets[index].websiteUrl);
                  }),
            )
          ],
        ),
      );
    });
  }
}
