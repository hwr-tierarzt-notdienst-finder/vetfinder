import 'dart:ffi';

import 'package:latlong2/latlong.dart';

import 'package:frontend/utils/preferences.dart';

class AddressSuggestion {
  const AddressSuggestion(
      {required this.latitude,
      required this.longitude,
      required this.displayName,
      required this.type,
      required this.importance})
      : super();

  final double latitude;
  final double longitude;
  final String displayName;
  final String type;
  final double importance;
}

class Address {
  const Address({
    required this.street,
    required this.number,
    required this.zipCode,
  }) : super();

  final String street;
  final String number;
  final int zipCode;
}

class Location {
  const Location({required this.position, required this.address}) : super();

  final LatLng position;
  final Address address;
}

class Veterinarian {
  Veterinarian(
      {required this.id,
      required this.name,
      required this.telephoneNumber,
      required this.websiteUrl,
      required this.location,
      required this.categories})
      : super();

  final String id;
  final String name;
  final String telephoneNumber;
  final String websiteUrl;
  final Location location;
  final List<String> categories;

  String getAddress() {
    return "${location.address.street} ${location.address.number}";
  }

  LatLng getPosition() {
    return location.position;
  }
}

List<Veterinarian> getVeterinarians() {
  List<Veterinarian> vets = [];
  vets.add(
    Veterinarian(
        id: '0',
        name: 'Mr. Happy',
        telephoneNumber: '+49 123 456 789',
        websiteUrl: 'https://www.google.com',
        location: Location(
            position: LatLng(52.5278578, 13.6243765),
            address: const Address(
                street: "Hönower Straße", number: "263", zipCode: 16000)),
        categories: ["Hunde"]),
  );
  vets.add(
    Veterinarian(
        id: '1',
        name: 'Mr. Unappy',
        telephoneNumber: '+49 123 456 789',
        websiteUrl: 'https://www.google.com',
        location: Location(
            position: LatLng(52.5373378, 13.2664472),
            address: const Address(
                street: "Wattstraße", number: "10", zipCode: 13629)),
        categories: ["Hunde", "Katzen"]),
  );
  vets.add(
    Veterinarian(
        id: '2',
        name: 'Mr. Happy1',
        telephoneNumber: '+49 123 456 789',
        websiteUrl: 'https://www.google.com',
        location: Location(
            position: LatLng(10.4, 20.5),
            address: const Address(
                street: "Teststraße", number: "10", zipCode: 16000)),
        categories: ["Hunde", "Katzen", "Pferde"]),
  );
  vets.add(
    Veterinarian(
        id: '3',
        name: 'Mr. Unappy2',
        telephoneNumber: '+49 123 456 789',
        websiteUrl: 'https://www.google.com',
        location: Location(
            position: LatLng(10.4, 20.5),
            address: const Address(
                street: "Teststraße", number: "10", zipCode: 16000)),
        categories: ["Katzen", "Pferde"]),
  );

  return vets;
}

List<String> getAvailableCategories() {
  List<Veterinarian> allVets = getVeterinarians();
  List<String> availableCategories = [];
  for (Veterinarian vet in allVets) {
    List<String> categories = vet.categories;
    for (String category in categories) {
      if (!(availableCategories.contains(category))) {
        availableCategories.add(category);
      }
    }
  }
  return availableCategories;
}

List<Veterinarian> getFilteredVeterinarians() {
  List<Veterinarian> vets = getVeterinarians();
  List<Veterinarian> filteredVets = [];

  // Filter animal categories
  if (SharedPrefs().categories.isNotEmpty) {
    for (Veterinarian vet in vets) {
      for (String category in SharedPrefs().categories) {
        if (vet.categories.contains(category)) {
          filteredVets.add(vet);
          break;
        }
      }
    }
  }

  if (filteredVets.isNotEmpty) {
    return filteredVets;
  } else {
    return vets;
  }
}

Veterinarian getVeterinarianById(String id) {
  List<Veterinarian> vets = getVeterinarians();
  for (var vet in vets) {
    if (vet.id == id) {
      return vet;
    }
  }
  throw 'Could not find veterinarian with id $id';
}
