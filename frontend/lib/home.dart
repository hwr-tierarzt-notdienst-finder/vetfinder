import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_map/plugin_api.dart';
import 'package:frontend/utils/notifiers.dart';
import 'package:frontend/utils/preferences.dart';
import 'package:provider/provider.dart';
import 'package:easy_localization/easy_localization.dart';
import 'package:frontend/vet_information.dart';

import 'package:frontend/components/veterinarian.dart';
import 'package:frontend/components/search_widget.dart';
import 'package:frontend/components/search_filter_dialog.dart';
import 'package:frontend/components/edit_address_modal.dart';
import 'package:frontend/api.dart';

class Home extends StatefulWidget {
  const Home({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  State<Home> createState() => _HomeState();
}

class _HomeState extends State<Home> {
  MapController mapController = MapController();
  List<Marker> markers = [];
  List<Veterinarian> vets = [];
  String query = '';
  Marker? currentLocationMarker;

  TextButton createMarkerWidget(Veterinarian vet) {
    return TextButton.icon(
      // when pressed open the veterinarian detail page
      onPressed: () {
        Navigator.pushNamed(context, '/vet_information',
            arguments: VetInformationScreenArguments(vet.id));
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
          width: 200,
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
            const Icon(Icons.man_rounded, color: Colors.orange, size: 45.0));
    markers.add(currentLocationMarker!);
  }

  void searchVet(String query) {
    setState(() {
      this.query = query.toLowerCase();
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
        isScrollControlled: true,
        context: context,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadiusDirectional.vertical(top: Radius.circular(20)),
        ),
        builder: (_) {
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
    return Consumer2<FilterNotifier, LocationNotifier>(
        builder: (context, filterNotifier, locationNotifier, child) {
      // Update the list of vets if filter is applied
      vets = getFilteredVeterinarians(locationNotifier.position, query);

      // Create location markers
      createMarkers(locationNotifier);
      addCurrentLocationMarker(locationNotifier);

      // Check if the filtered vets list is empty
      Widget vetsListWidget;
      if (vets.isNotEmpty) {
        vetsListWidget = Expanded(
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
                    clinicName: vets[index].clinicName,
                    distance: vets[index]
                        .getDistanceInMeters(locationNotifier.position),
                  );
                }));
      } else {
        vetsListWidget = Expanded(
          child: Center(
            child: Text(
              "home.no_vet_found".tr(),
              style: const TextStyle(
                fontSize: 15,
                fontStyle: FontStyle.italic,
                color: Colors.grey,
              ),
            ),
          ),
        );
      }

      return Scaffold(
        appBar: AppBar(
          title: Text(widget.title),
          actions: [
            IconButton(
                onPressed: () {
                  String vetId = SharedPrefs().vetId;
                  if  (vetId.isEmpty) {
                    final snackBar = SnackBar(
                      content: Text('home.snackbar_no_fav'.tr()),
                      backgroundColor: Colors.black,
                      action: SnackBarAction(
                        label: 'settings.snackbar_close'.tr(),
                        onPressed: () {},
                      ),
                    );
                    ScaffoldMessenger.of(context).showSnackBar(snackBar);
                  } else {
                    Navigator.pushNamed(
                      context, '/vet_information',
                      arguments: VetInformationScreenArguments(vetId)
                    );
                  }
                },
                icon: const Icon(Icons.pets_rounded)
            ),
            IconButton(
                onPressed: () => Navigator.pushNamed(context, '/setting'),
                icon: const Icon(Icons.settings)
            ),
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
                    Expanded(
                      child: Center(
                        child: Text(locationNotifier.address.isNotEmpty
                            ? locationNotifier.address
                            : 'home.current_address'.tr(),
                            overflow: TextOverflow.ellipsis,
                            maxLines: 1,
                        ),
                      ),
                    ),
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
                                child: const Icon(Icons.my_location_rounded),
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
            vetsListWidget,
          ],
        ),
      );
    });
  }
}
