import 'package:flutter/foundation.dart';
import 'package:url_launcher/url_launcher.dart';

// https://www.youtube.com/watch?v=BMbGE7LRwvc

class MapUtils {
  MapUtils._();

  static Future<void> openMap(double latitude, double longitude) async {
    String googleMapsUrl =
        'https://www.google.com/maps/search/?api=1&query=$latitude,$longitude';

    if (await canLaunch(googleMapsUrl)) {
      await launch(googleMapsUrl);
    } else {
      throw 'Could not open the map.';
    }
  }
}
