import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:convert';

const int MAX_RADIUS = 50;
const int MIN_RADIUS = 5;

class SearchFilterDialog extends StatefulWidget {
  const SearchFilterDialog({Key? key}) : super(key: key);

  @override
  State<SearchFilterDialog> createState() => _SearchFilterDialogState();
}

class _SearchFilterDialogState extends State<SearchFilterDialog> {
    // TextEditingController
    final radius_field_controller = TextEditingController();

    // Filter options
    int currentRadius = MIN_RADIUS; // Current Radius (km)
    List<String> currentCategories = [];

    // List of animal types
    var categories = [
      'Hunde', 'Katzen'
    ];

  String getSettingInJson() {
    Map currentSetting = {
      'search_radius' : currentRadius,
      'categories' : currentCategories
    };
    return json.encode(currentSetting);
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 25),
      width: MediaQuery.of(context).size.width * 0.75,
      height: MediaQuery.of(context).size.height * 0.5,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Divider(
            thickness: 1,
            color: Colors.grey,
          ),
          const SizedBox(height: 20),
          Container(
            child: Column(
              children: [
                Row(
                  children: [
                    Container(
                      child: const Text(
                        'Suchradius:',
                        style: TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.bold,
                        ),
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
              ],
            ),
          ),
          const SizedBox(height: 30),
          Container(
            child: Column(
              children: [
                Row(
                  children: [
                    const Text(
                      'Tierart',
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
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
              ],
            ),
          ),
        ],
      ),
    );
  }
}