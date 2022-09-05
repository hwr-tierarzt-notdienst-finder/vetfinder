import 'package:flutter/material.dart';
import 'package:frontend/components/veterinarian.dart';
import 'package:frontend/api.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_map/plugin_api.dart';
import 'package:latlong2/latlong.dart';

class Home extends StatefulWidget {
  const Home({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  State<Home> createState() => _HomeState();
}

class _HomeState extends State<Home> {
  int _counter = 0;

  void _incrementCounter() {
    setState(() {
      // This call to setState tells the Flutter framework that something has
      // changed in this State, which causes it to rerun the build method below
      // so that the display can reflect the updated values. If we changed
      // _counter without calling setState(), then the build method would not be
      // called again, and so nothing would appear to happen.
      _counter++;
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

    List<Veterinarian> vets = getVeterinarians();
    List<Marker> markers = [];

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

    for (Veterinarian vet in vets) {
      markers.add(Marker(
          width: 100,
          height: 50,
          point: vet.getPosition(),
          builder: (context) => createMarkerWidget(vet)));
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Column(
        children: [
          Text(
            'Tierärzte in deiner Nähe',
            style: Theme.of(context).textTheme.headline4,
          ),
          const TextField(
              decoration: InputDecoration(
                  hintText: 'Suchen...', suffixIcon: Icon(Icons.search))),
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
                      websiteUrl: vets[index].websiteUrl);
                }),
          )
        ],
      ),

      /*floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: const Icon(Icons.add),
      ),*/ // This trailing comma makes auto-formatting nicer for build methods.
    );
  }
}
