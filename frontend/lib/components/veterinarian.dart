import 'package:flutter/material.dart';
import 'package:frontend/api.dart';
import 'package:frontend/utils/notifiers.dart';
import 'package:frontend/vet_information.dart';
import 'package:latlong2/latlong.dart';
import 'package:easy_localization/easy_localization.dart';

import 'package:provider/provider.dart';
import 'package:frontend/components/search_filter_dialog.dart';
import 'package:frontend/utils/preferences.dart';

class VetCard extends Card {
  const VetCard({
    Key? key,
    required this.id,
    required this.name,
    required this.telephoneNumber,
    required this.location,
    required this.clinicName,
    required this.onViewInMap,
    required this.distance,
  }) : super(key: key);

  final String id;
  final String name;
  final String telephoneNumber;
  final Location location;
  final String clinicName;
  final Function(LatLng) onViewInMap;
  final double distance;

  @override
  Widget build(BuildContext context) {
    return Consumer<LocationNotifier>(
      builder: (context, notifier, child) {
        return Card(
          child: Column(
            children: [
              const SizedBox(height: 10),
              Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 5),
              Text(clinicName),
              const SizedBox(height: 5),
              Text(
                  "${location.address.street} ${location.address.number}, ${location.address.zipCode} ${location.address.city}"),
              Text(telephoneNumber),
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
                      '${((distance / 1000).toStringAsFixed(2))} km',
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
