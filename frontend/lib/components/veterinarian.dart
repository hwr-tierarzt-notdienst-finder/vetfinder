import 'package:flutter/material.dart';
import 'package:frontend/api.dart';
import 'package:frontend/utils/notifiers.dart';
import 'package:frontend/vet_information.dart';
import 'package:latlong2/latlong.dart';
import 'package:easy_localization/easy_localization.dart';
import 'package:provider/provider.dart';

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
    required this.emergencyAvailability,
  }) : super(key: key);

  final String id;
  final String name;
  final String telephoneNumber;
  final Location location;
  final String clinicName;
  final Function(LatLng) onViewInMap;
  final double distance;
  final bool emergencyAvailability;

  @override
  Widget build(BuildContext context) {
    Text emergencyIcon = const Text("");
    // Determine if a clinic has emergency service available
    if (emergencyAvailability) {
      emergencyIcon = 
        Text(
          'veterinarian.emergency'.tr(),
          style: const TextStyle(
            color: Colors.red
          )
        );
    }

    return Consumer<LocationNotifier>(
      builder: (context, notifier, child) {
        return Card(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(5),
          ),
          child: Column(
            children: [
              const SizedBox(height: 10),
              Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 5),
              Text(clinicName),
              const SizedBox(height: 5),
              Text(
                  "${location.address.street} ${location.address.number}, ${location.address.zipCode} ${location.address.city}"),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  TextButton.icon(
                    onPressed: () {
                      onViewInMap(location.position);
                    },
                    icon: const Icon(Icons.map_rounded),
                    label: Text('veterinarian.show_in_map'.tr())
                  ),
                  TextButton.icon(
                    onPressed: () {
                      Navigator.pushNamed(context, '/vet_information',
                          arguments: VetInformationScreenArguments(id));
                    },
                    icon: const Icon(Icons.arrow_forward_ios_rounded),
                    label: Text('veterinarian.view_vet'.tr())
                  ),
                ],
              ),
              Stack(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      emergencyIcon
                    ],
                  ),
                  Container(
                    alignment: Alignment.centerRight,
                    margin: const EdgeInsets.only(right: 5, bottom: 5),
                    child: Text(
                      '${((distance / 1000).toStringAsFixed(2))} km',
                      style: const TextStyle(
                        fontStyle: FontStyle.italic,
                        color: Colors.grey,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }
}
