// Based on https://simondev.medium.com/use-sharedpreferences-in-flutter-effortlessly-835bba8f7418

import 'package:latlong2/latlong.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:easy_localization/easy_localization.dart';

import 'package:frontend/utils/constants.dart';

class SharedPrefs {
  static late SharedPreferences _sharedPrefs;
  factory SharedPrefs() => SharedPrefs._internal();
  SharedPrefs._internal();

  Future<void> init() async {
    _sharedPrefs = await SharedPreferences.getInstance();
  }

  // App Settings
  bool get isDarkMode => _sharedPrefs.getBool(keyIsDarkMode) ?? false;
  set isDarkMode(bool value) {
    _sharedPrefs.setBool(keyIsDarkMode, value);
  }

  String get language => _sharedPrefs.getString(keyLanguage) ?? 'en';
  set language(String value) {
    _sharedPrefs.setString(keyLanguage, value);
  }

  // Filter Settings
  int get searchRadius => _sharedPrefs.getInt(keySearchRadius) ?? minSearchRadius;
  set searchRadius(int value) {
    _sharedPrefs.setInt(keySearchRadius, value);
  }

  List<String> get categories => _sharedPrefs.getStringList(keyCategories) ?? [];
  set categories(List<String> value) {
    _sharedPrefs.setStringList(keyCategories, value);
  }

  // Location Settings
  String get currentAddress => _sharedPrefs.getString(keyCurrentAddress) ?? "";
  set currentAddress(String value) {
    _sharedPrefs.setString(keyCurrentAddress, value);
  }

  LatLng get currentPosition {
    String value = _sharedPrefs.getString(keyCurrentPosition) ?? "0.0;0.0";
    List<String> splitted = value.split(";");
    double latitude = double.tryParse(splitted[0]) ?? 0.0;
    double longitude = double.tryParse(splitted[1]) ?? 0.0;
    return LatLng(latitude, longitude);
  }
  set currentPosition(LatLng position) {
    _sharedPrefs.setString(keyCurrentPosition, "${position.latitude};${position.longitude}");
  }
}

