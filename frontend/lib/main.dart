import 'package:flutter/material.dart';
import 'package:frontend/home.dart';
import 'package:frontend/vet_information.dart';
import 'package:frontend/search_page.dart';

//
// leicht abgerundete Ecken
// relativ viel Platz zwischen Elementen
// Farben:
// - primary: #b71c1c
// - secondary: #fdfdfd
//

/*

  Aufgaben:
    - Home Screen (+ Card), VetInformation Screen --> Orhun
    - Filterfunktion + Suche --> Nico
    - Karte implementieren (https://navoki.com/open-street-map-using-flutter/) --> Denis

    - nebenbei:
      - Typ Vetenarian erweitern (GPS Daten (lat, lon), Tiere (die behandelt werden), ...)

*/

void main() {
  runApp(MaterialApp(
    title: 'Flutter Demo',
    theme: ThemeData(
      primarySwatch: Colors.red,
    ),
    initialRoute: '/home',
    routes: {
      '/home': (context) => const Home(
            title: 'VetFinder',
          ),
      '/vet_information': (context) => const VetInformation(),
      '/search_page': (context) => const SearchPage(),
    },
  ));
}
