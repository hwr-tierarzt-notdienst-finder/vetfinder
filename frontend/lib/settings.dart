import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:easy_localization/easy_localization.dart';

import 'package:frontend/theme.dart';
import 'package:frontend/utils/preferences.dart';
import 'package:frontend/utils/constants.dart';

class Setting extends StatefulWidget {
  const Setting({Key? key}) : super(key: key);

  @override
  State<Setting> createState() => _SettingState();
}

class _SettingState extends State<Setting> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('settings.title'.tr()),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(20.0),
            child: Container(
              margin: const EdgeInsets.symmetric(horizontal: 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'settings.darkmode'.tr(),
                    style: TextStyle(
                      fontSize: 20,
                    ),
                  ),
                  Consumer<ThemeNotifier>(
                    builder: (context,notifier,child) => Switch(
                      onChanged: (bool value){
                        notifier.toggleTheme();
                      },
                      value: SharedPrefs().isDarkMode,
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
          Padding(
            padding: const EdgeInsets.all(20.0),
            child: Container(
              margin: const EdgeInsets.symmetric(horizontal: 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'settings.language'.tr(),
                    style: TextStyle(
                      fontSize: 20,
                    ),
                  ),
                  DropdownButton<String>(
                    value: availableLanguages.first,
                    icon: const Icon(Icons.arrow_downward),
                    elevation: 16,
                    style: const TextStyle(color: Colors.deepPurple),
                    underline: Container(
                      height: 2,
                      color: Colors.deepPurpleAccent,
                    ),
                    onChanged: (String? value) {
                      // This is called when the user selects an item.
                      setState(() {
                        context.setLocale(Locale('de'));
                      });
                    },
                    items: availableLanguages.map<DropdownMenuItem<String>>((String value) {
                      return DropdownMenuItem<String>(
                        value: value,
                        child: Text(value),
                      );
                    }).toList(),
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
                    'settings.publisher'.tr(),
                    style: TextStyle(
                      fontSize: 20,
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