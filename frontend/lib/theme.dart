import 'package:flutter/material.dart';

import 'package:frontend/utils/preferences.dart';

ThemeData lightTheme = ThemeData(
  brightness: Brightness.light,
  primarySwatch: Colors.red,
  buttonTheme: const ButtonThemeData(
    buttonColor: Colors.red
  ),
  scaffoldBackgroundColor: const Color(0xfff1f1f1)
);

ThemeData darkTheme = ThemeData(
  brightness: Brightness.dark,
  primarySwatch: Colors.grey,
);

class ThemeNotifier extends ChangeNotifier {
  late bool _isDarkMode;
  bool get isDarkMode => _isDarkMode;
  
  ThemeNotifier() {
    _isDarkMode = false;
    _loadFromPrefs();
  }

  toggleTheme() {
    _isDarkMode = !_isDarkMode;
    _saveToPrefs();
    notifyListeners();
  }

  _loadFromPrefs() async {
    _isDarkMode = SharedPrefs().isDarkMode;
    notifyListeners();
  }

  _saveToPrefs()async {
    SharedPrefs().isDarkMode = _isDarkMode;
  }
}