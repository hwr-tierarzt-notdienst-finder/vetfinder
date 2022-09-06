import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:convert';

const int MAX_RADIUS = 50;
const int MIN_RADIUS = 5;

class FilterPage extends StatefulWidget {
  const FilterPage({Key? key}) : super(key: key);

  @override
  State<FilterPage> createState() => _FilterPageState();
}

class _FilterPageState extends State<FilterPage> {
    // TextEditingController
    final radius_field_controller = TextEditingController();

    // Filter options
    String currentLocation = 'Berlin'; // Current Selected Location
    int currentRadius = MIN_RADIUS; // Current Radius (km)
    List<String> currentCategories = [];

    // List of locations
    var locations = [
      'Berlin', 'München', 'Frankfurt', 'Düsseldorf'
    ];

    // List of animal types
    var categories = [
      'Hunde', 'Katzen'
    ];

  String getSettingInJson() {
    Map currentSetting = {
      'location' : currentLocation,
      'search_radius' : currentRadius,
      'categories' : currentCategories
    };
    return json.encode(currentSetting);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
          title: const Text('Sucheinstellungen')
      ),
      body: Container(
        margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 40),
        child: ListView(
          children: [
            const Text(
              'Standort',
              style: TextStyle(
                fontSize: 15,
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
            Row(
              children: [
                const Text(
                  'Suchradius:',
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(width: 10),
                Container(
                  width: 50,
                  height: 40,
                  child: TextField(
                    controller: radius_field_controller
                                ..text = currentRadius.toString(),
                    decoration: InputDecoration(
                      border: OutlineInputBorder(),
                    ),
                    inputFormatters: <TextInputFormatter>[
                      FilteringTextInputFormatter.digitsOnly,
                      LengthLimitingTextInputFormatter(2),
                    ],
                    keyboardType: TextInputType.number,
                    textAlign: TextAlign.center,
                    onSubmitted: (String text) {
                      setState(() {
                        int input = int.parse(text);

                        // Allow input range: 5 - 50
                        if (input > MAX_RADIUS) {
                          input = MAX_RADIUS;
                        } else if (input < MIN_RADIUS) {
                          input = MIN_RADIUS;
                        }
                        currentRadius = input;
                        radius_field_controller.text = currentRadius.toString();
                      });
                    },
                  ),
                ),
                const SizedBox(width: 10),
                const Text(
                  'km',
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            Slider(
              value: currentRadius.toDouble(),
              min: MIN_RADIUS.toDouble(),
              max: MAX_RADIUS.toDouble(),
              onChanged: (double value) {
                setState(() {
                  currentRadius = value.toInt();
                  radius_field_controller.text = currentRadius.toString();
                });
              },
            ),
            const SizedBox(height: 30),
            const Text(
              'Tierart',
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 10,
              children:
                List<Widget>.generate(categories.length, (index) {
                final category = categories[index];
                final isSelected = currentCategories.contains(category);

                return FilterChip(
                  label: Text(category),
                  labelStyle: TextStyle(
                    color: isSelected
                        ? Colors.white
                        : Colors.grey,
                    fontSize: 15,
                    fontWeight: FontWeight.bold,
                  ),
                  selected: isSelected,
                  selectedColor: Colors.redAccent,
                  checkmarkColor: Colors.white,
                  onSelected: (bool selected) {
                    setState(() {
                      if (selected) {
                        currentCategories.add(category);
                      } else {
                        currentCategories.remove(category);
                      }
                    });
                  },
                );
              }),
            ),
            const SizedBox(height: 60),
            ElevatedButton(
              onPressed: () {
                Navigator.pushNamedAndRemoveUntil(
                  context,
                  '/home',
                  (Route<dynamic> route) => false,
                );
              },
              child: const Text(
                'Anwenden',
                style: TextStyle(
                  fontSize: 15,
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