import 'package:flutter/material.dart';
import 'package:flutter_geocoder/geocoder.dart';
import 'package:latlong2/latlong.dart';
import 'package:location/location.dart';
import 'package:easy_localization/easy_localization.dart';

class EditAddressModal extends StatefulWidget {
  final String currentAddress;
  final Function(LatLng, String) onPositionChanged;

  const EditAddressModal({
    Key? key,
    required this.currentAddress,
    required this.onPositionChanged,
  }) : super(key: key);

  @override
  State<EditAddressModal> createState() => _EditAddressModalState();
}

class _EditAddressModalState extends State<EditAddressModal> {
  Location location = Location();
  late LocationData currentPosition;
  String address = "";
  LatLng position = LatLng(0, 0);

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(borderRadius: BorderRadius.circular(20)),
      height: MediaQuery.of(context).size.height * 0.4,
      child: Padding(
        padding: const EdgeInsets.all(5),
        child: Column(
          children: [
            const SizedBox(height: 10),
            Text(
              'edit_address_modal.title'.tr(),
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 20),
            TextButton(
              onPressed: () {
                fetchCurrentLocation();
              },
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.my_location_rounded),
                    const SizedBox(width: 10),
                    Text(
                      'edit_address_modal.use_current_location'.tr(),
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const Divider(
              height: 10,
              thickness: 1,
              color: Colors.grey,
              indent: 20,
              endIndent: 20,
            ),
          ],
        ),
      ),
    );
  }

  fetchCurrentLocation() async {
    bool serviceEnabled;
    PermissionStatus permissionGranted;

    serviceEnabled = await location.serviceEnabled();
    if (!serviceEnabled) {
      serviceEnabled = await location.requestService();
      if (!serviceEnabled) {
        return;
      }
    }

    permissionGranted = await location.hasPermission();
    if (permissionGranted == PermissionStatus.denied) {
      permissionGranted = await location.requestPermission();
      if (permissionGranted != PermissionStatus.granted) {
        return;
      }
    }

    currentPosition = await location.getLocation();
    if (currentPosition.latitude != null && currentPosition.longitude != null) {
      position = LatLng(currentPosition.latitude!, currentPosition.longitude!);

      LocationData currentLocation = await location.onLocationChanged.first;
      setState(() {
        currentPosition = currentLocation;
        position =
            LatLng(currentPosition.latitude!, currentPosition.longitude!);

        getAddress(currentPosition.latitude!, currentPosition.longitude!)
            .then((value) {
          setState(() {
            address = "${value.first.addressLine}";
            Navigator.pop(context); // close the modal
          });
          widget.onPositionChanged(position, address);
        });
      });
    }
  }

  Future<List<Address>> getAddress(double lat, double lang) async {
    final coordinates = Coordinates(lat, lang);
    List<Address> add =
        await Geocoder.local.findAddressesFromCoordinates(coordinates);
    return add;
  }
}
