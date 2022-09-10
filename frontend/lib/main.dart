import 'package:flutter/material.dart';
import 'package:frontend/home.dart';
import 'package:frontend/setting.dart';
import 'package:frontend/vet_information.dart';
import 'package:frontend/utils/preferences.dart';

//
// leicht abgerundete Ecken
// relativ viel Platz zwischen Elementen
// Farben:
// - primary: #b71c1c
// - secondary: #fdfdfd
//

Future<void> main() async {
  // Load shared preferences
  await SharedPrefs().init();

  runApp(MaterialApp(
    title: 'Flutter Demo',
    theme: ThemeData(
      buttonTheme: const ButtonThemeData(
        buttonColor: Colors.red
      ),
      primarySwatch: Colors.red,
    ),
    initialRoute: '/home',
    routes: {
      '/home': (context) => const Home(
            title: 'VetFinder',
          ),
      '/vet_information': (context) => const VetInformation(),
      '/setting': (context) => const Setting(),
    },
  ));
}
