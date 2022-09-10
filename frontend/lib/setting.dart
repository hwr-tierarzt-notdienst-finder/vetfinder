import 'package:flutter/material.dart';

import 'package:frontend/utils/preferences.dart';

class Setting extends StatefulWidget {
  const Setting({Key? key}) : super(key: key);

  @override
  State<Setting> createState() => _SettingState();
}

class _SettingState extends State<Setting> {
  bool darkmodeOn = false;
  bool isUpdated = false;

  @override
  Widget build(BuildContext context) {
    // Update app setting once on the first build
    if (!isUpdated) {
      darkmodeOn = SharedPrefs().isDarkMode;
      isUpdated = true;
    }

    return Scaffold(
      appBar: AppBar(
        title: Text('Einstellungen'),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(20.0),
            child: Container(
              margin: EdgeInsets.symmetric(horizontal: 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Darkmode',
                    style: TextStyle(
                      fontSize: 20,
                    ),
                  ),
                  Switch(
                    value: darkmodeOn,
                    onChanged: (bool value) {
                      setState(() {
                        darkmodeOn = value;
                        SharedPrefs().isDarkMode = darkmodeOn;
                      });
                    },
                  ),
                ],
              ),
            ),
          ),
          const Divider(
            height: 10,
            thickness: 1,
            color: Colors.grey,
            indent: 20,
            endIndent: 20,
          ),
          TextButton(
            onPressed: () {},
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Row(
                children: [
                  Text(
                    'Impressum',
                    style: TextStyle(
                      fontSize: 20,
                      color: Colors.black,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const Divider(
            height: 10,
            thickness: 1,
            color: Colors.grey,
            indent: 20,
            endIndent: 20,
          ),
        ],
      ),
    );
  }
}