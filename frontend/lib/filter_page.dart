import 'package:flutter/material.dart';

class FilterPage extends StatefulWidget {
  const FilterPage({Key? key}) : super(key: key);

  @override
  State<FilterPage> createState() => _FilterPageState();
}

class _FilterPageState extends State<FilterPage> {
    // Initial Selected Location
    String currentLocation = 'Berlin';
    // List of location
    var locations = [
      'Berlin', 'München', 'Frankfurt', 'Düsseldorf'
    ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
          title: const Text('Suchfilter')
      ),
      body: Container(
        margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 40),
        child: ListView(
          children: [
            const Text(
              'Standort:',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            DropdownButton<String>(
                isExpanded: true,
                value: currentLocation,
                items: locations.map((String locations) {
                  return DropdownMenuItem(
                    value: locations,
                    child: Text(locations),
                  );
                }).toList(),
                onChanged: (String? newLocation) {
                  setState(() {
                    currentLocation = newLocation!;
                  });
                },
            ),
            const SizedBox(height: 30),
            const Text(
              'Tierart:',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const TextField(

            ),
            const SizedBox(height: 30),
            ElevatedButton(
              onPressed: () {
                Navigator.pushNamedAndRemoveUntil(
                  context,
                  '/home',
                  (Route<dynamic> route) => false,
                  arguments: {
                    'location': currentLocation
                  },
                );
              },
              child: const Text(
                'Filter anwenden',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        )
      )
    );
  }
}