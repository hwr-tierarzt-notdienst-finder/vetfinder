import 'package:flutter/material.dart';
import 'package:string_similarity/string_similarity.dart';
import 'package:frontend/components/veterinarian.dart';
import 'package:frontend/components/search_widget.dart';
import 'package:frontend/api.dart';

import 'dart:collection';

class Home extends StatefulWidget {
  const Home({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  State<Home> createState() => _HomeState();
}

class _HomeState extends State<Home> {
  List<Veterinarian> vets = getVeterinarians();
  String query = '';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
        actions: [
          IconButton(
              onPressed: () => Navigator.pushNamed(context, '/filter_page'),
              icon: const Icon(Icons.filter_list_rounded)),
        ],
      ),
      body: Container(
        margin: const EdgeInsets.all(10),
        child: Center(
          child: Column(
            children: <Widget>[
              Text(
                'Tierärzte in deiner Nähe',
                style: Theme.of(context).textTheme.headline4,
              ),
              SearchWidget(
                text: query,
                onSubmitted: searchVet,
                hintText: 'Name, Adresse, Posleitzahl'),
              Container(
                width: MediaQuery.of(context).size.width * 0.9,
                height: MediaQuery.of(context).size.height * 0.3,
                color: Colors.black,
              ),
              Expanded(
                child: ListView.builder(
                    itemCount: vets.length,
                    itemBuilder: (context, index) {
                      return VetCard(
                          id: vets[index].id,
                          name: vets[index].name,
                          telephoneNumber: vets[index].telephoneNumber,
                          address: vets[index].address,
                          websiteUrl: vets[index].websiteUrl);
                    }),
              )
            ],
          ),
        ),
      ),
    );
  }

  void searchVet(String query) {
    setState(() {
      this.query = query.toLowerCase();
      List<String> keywords = this.query.split(' ');

      // Create a list of veterinarians based on query
      vets = getVeterinarians();
      Map similarityMap = {};
  
      for (var vet in vets) {
        String vetInfo = '${vet.name} ${vet.address}';
        final comparison = this.query.similarityTo(vetInfo);
        similarityMap[vet.id] = comparison;
      }

      var sortedMap = new SplayTreeMap<String, double>.from(
        similarityMap, (key1, key2) => (similarityMap[key1] > similarityMap[key2])? -1 : 1);
      vets = sortedMap.keys.map((id) => getVeterinarianById(id)).toList();
    });
  }
}
