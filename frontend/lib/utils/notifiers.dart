import 'package:flutter/material.dart';
import 'package:frontend/utils/preferences.dart';
import 'package:latlong2/latlong.dart';
import 'package:provider/provider.dart';

class LocationNotifier extends ChangeNotifier {
  late LatLng _position;
  LatLng get position => _position;

  late String _address;
  String get address => _address;

  LocationNotifier() {
    _loadFromPrefs();
  }

  setPosition(LatLng position) {
    _position = position;
    _savePositionToPrefs();
    notifyListeners();
  }

  setAddress(String address) {
    _address = address;
    _saveAddressToPrefs();
    notifyListeners();
  }

  _loadFromPrefs() async {
    _position = SharedPrefs().currentPosition;
    _address = SharedPrefs().currentAddress;
    notifyListeners();
  }

  _savePositionToPrefs() async {
    SharedPrefs().currentPosition = _position;
  }

  _saveAddressToPrefs() async {
    SharedPrefs().currentAddress = _address;
  }
}
