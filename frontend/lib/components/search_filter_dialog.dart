import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:easy_localization/easy_localization.dart';

import 'package:frontend/utils/preferences.dart';
import 'package:frontend/utils/constants.dart';

class FilterNotifier extends ChangeNotifier {
  late int _searchRadius;
  late List<String> _categories;
  late bool _filterUpdated;

  int get searchRadius => _searchRadius;
  List<String> get categories => _categories;

  bool get filterUpdated => _filterUpdated;
  set filterUpdated(bool value) {
    _filterUpdated = value;
  }
  
  FilterNotifier() {
    updateFilter();
  }

  updateFilter() async {
    _searchRadius = SharedPrefs().searchRadius;
    _categories = SharedPrefs().categories;
    _filterUpdated = true;
    notifyListeners();
  }
}

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

  int currentRadius = SharedPrefs().searchRadius; // Current Radius (km)
  List<String> currentCategories = SharedPrefs().categories; // Chosen animal categories
  bool isUpdated = false;

  void _setFilterSetting() {
    SharedPrefs().searchRadius = currentRadius;
    SharedPrefs().categories = currentCategories;
  }

  void _getFilterSetting() {
    currentRadius = SharedPrefs().searchRadius;
    currentCategories = SharedPrefs().categories;
  }

  @override
  Widget build(BuildContext context) {
    // Update filter setting once on the first build
    if (!isUpdated) {
      _getFilterSetting();
      isUpdated = true;
    }

    return Consumer<FilterNotifier>(
      builder: (context,notifier,child) => AlertDialog(
        title: Text('search_filter_dialog.title'.tr()),
        contentPadding: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
        ),
        actions: <Widget>[
          TextButton(
            style: TextButton.styleFrom(
              textStyle: Theme.of(context).textTheme.labelLarge,
            ),
            child: Text('search_filter_dialog.reset'.tr()),
            onPressed: () {
              setState(() {
                currentRadius = minSearchRadius;
                currentCategories = [];
              });
            },
          ),
          TextButton(
            style: TextButton.styleFrom(
              textStyle: Theme.of(context).textTheme.labelLarge,
            ),
            child: Text('search_filter_dialog.cancel'.tr()),
            onPressed: () {
              Navigator.of(context).pop();
            },
          ),
          TextButton(
            style: TextButton.styleFrom(
              textStyle: Theme.of(context).textTheme.labelLarge,
            ),
            child: Text('search_filter_dialog.apply'.tr()),
            onPressed: () {
              _setFilterSetting();
              notifier.updateFilter();
              Navigator.of(context).pop();
            },
          ),
        ],
        content: Container(
          padding: const EdgeInsets.symmetric(horizontal: 25),
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
                      Text(
                        '${'search_filter_dialog.search_radius'.tr()}:',
                        style: const TextStyle(
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
                          decoration: const InputDecoration(
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
                              if (input > maxSearchRadius) {
                                input = maxSearchRadius;
                              } else if (input < minSearchRadius) {
                                input = minSearchRadius;
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
                    min: minSearchRadius.toDouble(),
                    max: maxSearchRadius.toDouble(),
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
                      Text(
                        '${'search_filter_dialog.category'.tr()}:',
                        style: const TextStyle(
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
      ),
    );
  }
}