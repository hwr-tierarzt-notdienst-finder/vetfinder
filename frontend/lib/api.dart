// import 'dart:ffi';
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
        id: '0',
        name: 'Tierklinik Berlin-Biesdorf',
        clinicName: 'Tierärztliche Klinik für Klein- und Heimtiere',
        email: 'kontakt@tierklinik-in-biesdorf.de',
        telephoneNumber: '+49305143760',
        websiteUrl: 'https://www.tierklinik-in-biesdorf.de/',
        location: Location(
            position: LatLng(52.50878687199156, 13.555776987579236),
            address: const Address(
                street: "Alt-Biesdorf",
                number: "22",
                zipCode: 12683,
                city: "Berlin")),
        categories: ["Heimtiere"]),
  );
  vets.add(
    Veterinarian(
        id: '1',
        name: 'Dr. Robert Höpfner / Dr. Kay Schmerbach',
        clinicName: 'Kleintierspezialisten Berlin-Brandenburg',
        email: 'kontakt@kleintierspezialisten.de',
        telephoneNumber: '+493043662200',
        websiteUrl: 'https://www.kleintierspezialisten.de/de',
        location: Location(
            position: LatLng(52.580648779854506, 13.294731784658856),
            address: const Address(
                street: "Wittestraße",
                number: "30P",
                zipCode: 13509,
                city: "Berlin")),
        categories: ["Heimtiere"]),
  );
  vets.add(
    Veterinarian(
        id: '2',
        name: 'Olof Löwe',
        clinicName: 'Klinik für Kleintiere',
        email: 'kontakt@tierklinik-in-berlin.de',
        telephoneNumber: '+49309322093',
        websiteUrl: 'https://www.tierklinik-in-berlin.de/',
        location: Location(
            position: LatLng(52.55563564107943, 13.553283642580288),
            address: const Address(
                street: "Märkische Allee",
                number: "258",
                zipCode: 12679,
                city: "Berlin")),
        categories: ["Heimtiere"]),
  );
  vets.add(
    Veterinarian(
        id: '3',
        name: 'Freie Universität Berlin',
        clinicName: 'Klinik für Pferde, allgemeine Chirurgie und Radiologie (WE17)',
        email: 'pferdeklinik@vetmed.fu-berlin.de',
        telephoneNumber: '+493083862299',
        websiteUrl: 'https://www.vetmed.fu-berlin.de/einrichtungen/kliniken/we17',
        location: Location(
            position: LatLng(52.43006758423042, 13.237440001529311),
            address: const Address(
                street: "Oertzenweg",
                number: "19B",
                zipCode: 14163,
                city: "Berlin")),
        categories: ["Pferde"]),
  );
  vets.add(
    Veterinarian(
        id: '4',
        name: 'Freie Universität Berlin',
        clinicName: 'Klinik für Klauentiere (WE18)',
        email: 'klauentierklinik@vetmed.fu-berlin.de',
        telephoneNumber: '+493083862261',
        websiteUrl: 'https://www.vetmed.fu-berlin.de/einrichtungen/kliniken/we18/index.html',
        location: Location(
            position: LatLng(52.427122150532384, 13.234963828118532),
            address: const Address(
                street: "Königsweg",
                number: "65",
                zipCode: 14163,
                city: "Berlin")),
        categories: ["Klauentiere"]),
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
