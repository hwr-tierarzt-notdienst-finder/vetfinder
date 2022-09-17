import 'package:flutter/material.dart';
import 'package:frontend/api.dart';
import 'package:frontend/vet_information.dart';
import 'package:latlong2/latlong.dart';
import 'package:easy_localization/easy_localization.dart';

import 'package:provider/provider.dart';
import 'package:frontend/components/search_filter_dialog.dart';
import 'package:frontend/utils/preferences.dart';

class VetCard extends Card {
  const VetCard(
      {Key? key,
      required this.id,
      required this.name,
      required this.telephoneNumber,
      required this.location,
      required this.websiteUrl,
      required this.onViewInMap})
      : super(key: key);

  final String id;
  final String name;
  final String telephoneNumber;
  final Location location;
  final String websiteUrl;
  final Function(LatLng) onViewInMap;

  double _countDistance(double userLatitude, double userLongitude) {
    return Distance().as(
      LengthUnit.Kilometer,
      LatLng(SharedPrefs().currentPosition.latitude,
          SharedPrefs().currentPosition.longitude),
      LatLng(userLatitude, userLongitude),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<FilterNotifier>(
      builder: (context, FilterNotifier notifier, child) {
        // Update the list of vets if filter is applied
        if (notifier.filterUpdated) {
          print('test');
          notifier.filterUpdated = false;
        }
        return Card(
          child: Column(
            children: [
              const SizedBox(height: 10),
              Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 5),
              Text("${location.address.street} ${location.address.number}"),
              Text(telephoneNumber),
              const SizedBox(height: 5),
              Text(websiteUrl),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  TextButton.icon(
                      onPressed: () {
                        onViewInMap(location.position);
                      },
                      icon: const Icon(Icons.map_rounded),
                      label: Text('veterinarian.show_in_map'.tr())),
                  TextButton.icon(
                      onPressed: () {
                        Navigator.pushNamed(context, '/vet_information',
                            arguments: VetInformationScreenArguments(id));
                      },
                      icon: const Icon(Icons.arrow_forward_ios_rounded),
                      label: Text('veterinarian.view_vet'.tr())),
                ],
              ),
              Container(
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.black),
                  borderRadius: BorderRadius.circular(10),
                ),
                width: MediaQuery.of(context).size.width * 0.17,
                height: MediaQuery.of(context).size.height * 0.04,
                margin: const EdgeInsets.only(bottom: 10.0),
                child: Center(
                  child: FittedBox(
                    fit: BoxFit.scaleDown,
                    child: Text(
                      '${_countDistance(location.position.latitude, location.position.longitude).toStringAsFixed(2)} km',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                  //
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
