import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:easy_localization/easy_localization.dart';

import 'package:frontend/utils/preferences.dart';
import 'package:frontend/utils/constants.dart';

class FilterNotifier extends ChangeNotifier {
  late int _searchRadius;
  late List<String> _treatments;
  late bool _filterUpdated;

  int get searchRadius => _searchRadius;
  List<String> get treatments => _treatments;

  bool get filterUpdated => _filterUpdated;
  set filterUpdated(bool value) {
    _filterUpdated = value;
  }
  
  FilterNotifier() {
    updateFilter();
  }

  updateFilter() async {
    _searchRadius = SharedPrefs().searchRadius;
    _treatments = SharedPrefs().treatments;
    _filterUpdated = true;
    notifyListeners();
  }
}

class SearchFilterDialog extends StatefulWidget {
  final List<String> availableTreatments;

  const SearchFilterDialog({
    Key? key,
    required this.availableTreatments
  }) : super(key: key);

  @override
  State<SearchFilterDialog> createState() => _SearchFilterDialogState();
}

class _SearchFilterDialogState extends State<SearchFilterDialog> {
  // TextEditingController
  final radiusFieldController = TextEditingController();

  int currentRadius = SharedPrefs().searchRadius; // Current Radius (km)
  List<String> currentTreatments = SharedPrefs().treatments; // Chosen animal treatments
  bool isUpdated = false;

  void _setFilterSetting() {
    SharedPrefs().searchRadius = currentRadius;
    SharedPrefs().treatments = currentTreatments;
  }

  void _getFilterSetting() {
    currentRadius = SharedPrefs().searchRadius;
    currentTreatments = SharedPrefs().treatments;
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
                currentTreatments = [];
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
                        '${'search_filter_dialog.treatment'.tr()}:',
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
                      List<Widget>.generate(widget.availableTreatments.length, (index) {
                      final treatment = widget.availableTreatments[index];
                      final isSelected = currentTreatments.contains(treatment);

                      return FilterChip(
                        label: Text('treatments.$treatment'.tr()),
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
                              currentTreatments.add(treatment);
                            } else {
                              currentTreatments.remove(treatment);
                            }
                          });
                        },
                      );
                    }),
                  ),
                  const SizedBox(height: 10),
                  CheckboxListTile(
                    title: Text(
                      'search_filter_dialog.emergency_service'.tr(),
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                      ),  
                    ),
                    controlAffinity: ListTileControlAffinity.leading, 
                    value: SharedPrefs().emergencyServiceAvailable,
                    onChanged: (bool? value) {
                      setState(() {
                        SharedPrefs().emergencyServiceAvailable = value!;
                        print(SharedPrefs().emergencyServiceAvailable);
                      });
                    },
                  )
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}