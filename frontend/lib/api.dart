// import 'dart:ffi';

import 'dart:collection';

import 'package:frontend/utils/notifiers.dart';
import 'package:latlong2/latlong.dart';
import 'package:string_similarity/string_similarity.dart';

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
    required this.city,
  }) : super();

  final String street;
  final String number;
  final int zipCode;
  final String city;
}

class Location {
  const Location({required this.position, required this.address}) : super();

  final LatLng position;
  final Address address;
}

class Veterinarian {
  Veterinarian({
    required this.id,
    required this.name,
    required this.email,
    required this.clinicName,
    required this.telephoneNumber,
    required this.websiteUrl,
    required this.location,
    required this.categories,
  }) : super();

  final String id;
  final String name;
  final String clinicName;
  final String email;
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

  double getDistanceInMeters(LatLng position) {
    return const Distance().as(
      LengthUnit.Meter,
      position,
      getPosition(),
    );
  }
}

List<Veterinarian> getVeterinarians() {
  List<Veterinarian> vets = [];
  vets.add(
    Veterinarian(
        id: '3',
        name: 'Mr. Unappy2',
        clinicName: 'Unappy Clinic 2',
        email: 'vet_mail_4@gmail.com',
        telephoneNumber: '+49 123 456 789',
        websiteUrl: 'https://www.google.com',
        location: Location(
            position: LatLng(10.4, 20.5),
            address: const Address(
                street: "Teststraße",
                number: "10",
                zipCode: 16000,
                city: "Berlin")),
        categories: ["Katzen", "Pferde"]),
  );

  vets.add(
    Veterinarian(
        id: '0',
        name: 'Mr. Happy',
        clinicName: 'Happy Clinic 1',
        email: 'vet_mail_1@gmail.com',
        telephoneNumber: '+49 123 456 789',
        websiteUrl: 'https://www.google.com',
        location: Location(
            position: LatLng(52.5278578, 13.6243765),
            address: const Address(
                street: "Hönower Straße",
                number: "263",
                zipCode: 16000,
                city: "Berlin")),
        categories: ["Hunde"]),
  );
  vets.add(
    Veterinarian(
        id: '1',
        name: 'Mr. Unappy',
        clinicName: 'Unappy Clinic 1',
        email: 'vet_mail_2@gmail.com',
        telephoneNumber: '+49 123 456 789',
        websiteUrl: 'https://www.google.com',
        location: Location(
            position: LatLng(52.5373378, 13.2664472),
            address: const Address(
                street: "Wattstraße",
                number: "10",
                zipCode: 13629,
                city: "Berlin")),
        categories: ["Hunde", "Katzen"]),
  );
  vets.add(
    Veterinarian(
        id: '2',
        name: 'Mr. Happy1',
        clinicName: 'Happy Clinic 3',
        email: 'vet_mail_3@gmail.com',
        telephoneNumber: '+49 123 456 789',
        websiteUrl: 'https://www.google.com',
        location: Location(
            position: LatLng(10.4, 20.5),
            address: const Address(
                street: "Teststraße",
                number: "10",
                zipCode: 16000,
                city: "Berlin")),
        categories: ["Hunde", "Katzen", "Pferde"]),
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

List<Veterinarian> getFilteredVeterinarians(
    LatLng currentPosition, String query) {
  List<Veterinarian> vets = getVeterinarians();
  List<Veterinarian> filteredVets = [];

  // Filter vets list based on categories and search radius
  for (Veterinarian vet in vets) {
    if ((vet.getDistanceInMeters(currentPosition) / 1000) <
        SharedPrefs().searchRadius) {
      if (SharedPrefs().categories.isNotEmpty) {
        for (String category in SharedPrefs().categories) {
          if (vet.categories.contains(category)) {
            filteredVets.add(vet);
            break;
          }
        }
      } else {
        filteredVets.add(vet);
      }
    }
  }

  List<Veterinarian> returnedVets = [];

  if (filteredVets.isNotEmpty) {
    returnedVets = List.of(filteredVets);

    // Sort based on search query or distance
    if (query.isEmpty) {
      returnedVets.sort((a, b) {
        double distance1 = a.getDistanceInMeters(currentPosition);
        double distance2 = b.getDistanceInMeters(currentPosition);

        if (distance1 == distance2) {
          return 0;
        } else if (distance1 > distance2) {
          return 1;
        } else {
          return -1;
        }
      }
    );
    } else {
      returnedVets.sort((a, b) {
        String vetInfo1 = '${a.name} ${a.getAddress()}';
        String vetInfo2 = '${b.name} ${b.getAddress()}';

        double similarityScore1 = query.similarityTo(vetInfo1);
        double similarityScore2 = query.similarityTo(vetInfo2);

        if (similarityScore1 == similarityScore2) {
          return 0;
        } else if (similarityScore1 > similarityScore2) {
          return -1;
        } else {
          return 1;
        }
      });
    }
  
  }

  return returnedVets;
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
