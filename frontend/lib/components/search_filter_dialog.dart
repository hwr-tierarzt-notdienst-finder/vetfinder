import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';

const int maxRadius = 50;
const int minRadius = 5;

class SearchFilterDialog extends StatefulWidget {
  final List<String> availableCategories;

  const SearchFilterDialog({
    Key? key,
    required this.availableCategories
  }) : super(key: key);

  @override
  State<SearchFilterDialog> createState() => _SearchFilterDialogState();
}

class _SearchFilterDialogState extends State<SearchFilterDialog> {
  // TextEditingController
  final radiusFieldController = TextEditingController();
  int currentRadius = minRadius; // Current Radius (km)
  List<String> currentCategories = []; // Chosen animal categories
  bool filterSettingUpdated = false;

  void setFilterSetting() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt('searchRadius', currentRadius);
    await prefs.setStringList('categories', currentCategories);
  }

  void getFilterSetting() async {
    final prefs = await SharedPreferences.getInstance();
    final int? searchRadius = prefs.getInt('searchRadius');
    final List<String>? categories = prefs.getStringList('categories');

    setState(() {
      currentRadius = searchRadius!;
      currentCategories = categories!;
    });
  }

  @override
  Widget build(BuildContext context) {
    // Update filter setting once on the first build
    if (!filterSettingUpdated) {
      getFilterSetting();
      filterSettingUpdated = true;
    }

    return AlertDialog(
      title: const Text('Suchfilter'),
      contentPadding: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(10),
      ),
      actions: <Widget>[
        TextButton(
          style: TextButton.styleFrom(
            textStyle: Theme.of(context).textTheme.labelLarge,
          ),
          child: const Text('Abbrechen'),
          onPressed: () {
            Navigator.of(context).pop();
          },
        ),
        TextButton(
          style: TextButton.styleFrom(
            textStyle: Theme.of(context).textTheme.labelLarge,
          ),
          child: const Text('Anwenden'),
          onPressed: () {
            setFilterSetting();
            Navigator.of(context).pop();
          },
        ),
      ],
      content: Container(
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
            Column(
              children: [
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
                        controller: radiusFieldController
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
                            if (input > maxRadius) {
                              input = maxRadius;
                            } else if (input < minRadius) {
                              input = minRadius;
                            }
                            currentRadius = input;
                            radiusFieldController.text = currentRadius.toString();
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
                  min: minRadius.toDouble(),
                  max: maxRadius.toDouble(),
                  onChanged: (double value) {
                    setState(() {
                      currentRadius = value.toInt();
                      radiusFieldController.text = currentRadius.toString();
                    });
                  },
                ),
              ],
            ),
            const SizedBox(height: 30),
            Column(
              children: [
                Row(
                  children: [
                    const Text(
                      'Tierart:',
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(width: 10),
                    Text(
                      '${currentCategories.length} von ${widget.availableCategories.length} ausgewählt',
                      style: TextStyle(
                        fontSize: 15,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Wrap(
                  spacing: 10,
                  children:
                    List<Widget>.generate(widget.availableCategories.length, (index) {
                    final category = widget.availableCategories[index];
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
          ],
        ),
      ),
    );
  }
}