import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_map/plugin_api.dart';
import 'package:string_similarity/string_similarity.dart';
import 'package:latlong2/latlong.dart';

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
  List<Marker> markers = [];
  List<Veterinarian> vets = getVeterinarians();
  String query = '';
  Map? filterSetting = {
    'searchRadius' : minRadius,
    'categories' : <String>[],
  };

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

  void createMarkers() {
    markers.clear();
    for (Veterinarian vet in vets) {
      markers.add(Marker(
          width: 100,
          height: 50,
          point: vet.getPosition(),
          builder: (context) => createMarkerWidget(vet)));
    }
  } 

  void searchVet(String query) {
    setState(() {
      this.query = query.toLowerCase();

      // Create a list of veterinarians based on query
      vets = getVeterinarians();
      Map similarityMap = {};
  
      for (Veterinarian vet in vets) {
        String vetInfo = '${vet.name} ${vet.getAddress()}';
        final comparison = this.query.similarityTo(vetInfo);
        similarityMap[vet.id] = comparison;
      }

      var sortedMap = new SplayTreeMap<String, double>.from(
        similarityMap, (key1, key2) => (similarityMap[key1] > similarityMap[key2])? -1 : 1);
      vets = sortedMap.keys.map((id) => getVeterinarianById(id)).toList();
    });
  }

  List<String> fetchAvailableCategories() {
    List<String> availableCategories = [];
    for (Veterinarian vet in vets) {
      List<String> categories = vet.categories;
      for (String category in categories) {
        if (!(availableCategories.contains(category))) {
          availableCategories.add(category);
        }
      }
    }
    return availableCategories;
  }

  void showFilterDialog(BuildContext context) async {
    Map? newFilterSetting = await showDialog<Map>(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return SearchFilterDialog(
          availableCategories: fetchAvailableCategories(),
          currentFilterSetting: filterSetting,
        );
      },
    );

    setState(() {
      filterSetting = newFilterSetting;
    });
  }

  void showEditAddressModalBottomSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
      ),
      builder: (BuildContext context) {
        return EditAddressModal(
          currentAddress: 'Platzhalter Straße 123',
        );
      }
    );
  }

  @override
  Widget build(BuildContext context) {
    // This method is rerun every time setState is called, for instance as done
    // by the _incrementCounter method above.
    //
    // The Flutter framework has been optimized to make rerunning build methods
    // fast, so that you can just rebuild anything that needs updating rather
    // than having to individually change instances of widgets.
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
              showEditAddressModalBottomSheet(context);
            },
            child: Padding(
              padding: const EdgeInsets.all(10),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    'Current Address'
                  ),
                  Icon(
                    Icons.arrow_drop_down_rounded
                  ),
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
                  hintText: 'Name, Adresse, Posleitzahl'),
              ),
              Container(
                margin: EdgeInsets.fromLTRB(0, 0, 8, 0),
                child: ElevatedButton(
                  onPressed: () {
                    showFilterDialog(context);
                  },
                  child: Icon(Icons.filter_list_rounded,)
                ),
              ),
            ],
          ),
          Container(
            width: MediaQuery.of(context).size.width,
            height: MediaQuery.of(context).size.height * 0.5,
            child: Stack(
              children: [
                Padding(
                  padding: const EdgeInsets.all(8),
                  child: FlutterMap(
                    options: MapOptions(
                      center: LatLng(vets[0].location.latitude,
                          vets[0].location.longitude),
                      zoom: 11,
                      rotation: 0,
                    ),
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
              ],
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
                    address: vets[index].getAddress(),
                    websiteUrl: vets[index].websiteUrl
                  );
                }),
          )
        ],
      ),
    );
  }
}
