import 'dart:convert';
import 'package:flutter/services.dart';
import 'package:latlong2/latlong.dart';
import 'package:string_similarity/string_similarity.dart';
import 'package:http/http.dart' as http;
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

  Address.fromJson(Map<String, dynamic> json)
      : street = json["street"],
        number = json["number"],
        zipCode = json["zipCode"],
        city = json["city"];
}

class Location {
  const Location({required this.position, required this.address}) : super();

  final LatLng position;
  final Address address;

  Location.fromJson(Map<String, dynamic> json)
      : position = LatLng(json["lat"], json["lon"]),
        address = Address.fromJson(json["address"]);
}

class Person {
  const Person({
    required this.formOfAddress,
    required this.title,
    required this.firstName,
    required this.lastName
  }) : super();

  final String? formOfAddress;
  final String? title;
  final String firstName;
  final String lastName;

  Person.fromJson(Map<String, dynamic> json)
      : formOfAddress = json["formOfAddress"]?? "",
        title = json["title"]?? "",
        firstName = json["firstName"],
        lastName = json["lastName"];
}

class Veterinarian {
  Veterinarian({
    required this.id,
    required this.person,
    required this.clinicName,
    required this.contacts,
    required this.location,
    required this.categories,
    required this.availability,
    required this.emergencyAvailability
  }) : super();

  final String id;
  final Person person;
  final String clinicName;
  final List<Map<String, dynamic>> contacts;
  final Location location;
  final List<String> categories;
  final Map<String, dynamic> availability;
  final Map<String, dynamic>? emergencyAvailability;

  Veterinarian.fromJson(Map<String, dynamic> json)
      : id = json["id"],
        person = Person.fromJson(json["nameInformation"]),
        clinicName = json["clinicName"],
        contacts = List<Map<String, dynamic>>.from(json['contacts'] as List),
        location = Location.fromJson(json["location"]),
        categories = List<String>.from(json["categories"] as List),
        availability = json["availabilityDuringWeek"],
        emergencyAvailability = json["emergencyAvailabilityDuringWeek"];

  // Get contact data of a specific type
  // @param type The type of data (email, tel:landline, tel:mobile, website)
  String getContact(String type) {
    for (Map<String, dynamic> item in contacts) {
      if (item["type"] == type) {
        return item["value"];
      }
    }

    // Contact type not found
    return "";
  }

  String getName() {
    String name = "${person.formOfAddress} ${person.title} ${person.firstName} ${person.lastName}";

    if (person.formOfAddress!.isEmpty && person.title!.isEmpty) {
      name = "${person.firstName} ${person.lastName}";
    } else if (person.formOfAddress!.isEmpty) {
      name = "${person.title} ${person.firstName} ${person.lastName}";
    } else if (person.title!.isEmpty) {
      name = "${person.formOfAddress} ${person.firstName} ${person.lastName}";
    }

    return name;
  }

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

  bool getEmergencyAvailabilityStatus() {
    if (emergencyAvailability != null) {
      // Logik, um die jetzige Zeit mit der Notdienst-Öffnungszeit zu vergleichen
      // wenn die jetzige Zeit innerhalb der Öffnungszeit ist, return true, else false.
    }

    return false;
  }
}

// Fetch veterinarians data from the server and save it in the app
Future<void> fetchVeterinarians() async {
  String availabilityFrom = DateTime.utc(2022, 09, 20, 20, 18, 04).toIso8601String();
  String availabilityTo = DateTime.utc(2022, 12, 20, 20, 18, 04).toIso8601String();
  var uri = Uri(
        scheme: "https",
        host: "vetfinder.dowahdid.de",
        pathSegments: ["vets"],
        query: "availability_from=$availabilityFrom&availability_to=$availabilityTo");

  String secretToken = await rootBundle.loadString('assets/secret_token.txt');
  Map<String, String> headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": "Bearer $secretToken",
  };

  try {
    http.Response response = await http.get(uri, headers: headers);

    // Successful GET request. Save JSON String.
    if (response.statusCode == 200) {
      DateTime timeNow = DateTime.now();
      String formattedTime = "${timeNow.day}-${timeNow.month}-${timeNow.year} ${timeNow.hour}:${timeNow.minute}";

      SharedPrefs().vets = response.body;
      SharedPrefs().lastUpdated = formattedTime;
    } else {
      throw Exception("Failed to load data. Status code: ${response.statusCode}");
    }
  } catch (e) {
    // Failed GET Request. Handle the error.
    print("Couldn't open $uri");
    print(e);
  }
}

// Parse the saved veterinarian data from JSON String to list
List<Veterinarian> getVeterinarians() {
  List<Veterinarian> vets = [];

  // Process the JSON.
  if(SharedPrefs().vets.isNotEmpty) {
    List<dynamic> result = json.decode(SharedPrefs().vets);
        
    // Parse data to a list of vets
    for (Map<String, dynamic> vet in result) {
      vets.add(Veterinarian.fromJson(vet));
    }
  }

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
        String vetInfo1 = '${a.getName} ${a.getAddress()}';
        String vetInfo2 = '${b.getName} ${b.getAddress()}';

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
