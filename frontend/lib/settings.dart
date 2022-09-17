import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:easy_localization/easy_localization.dart';

import 'package:frontend/utils/preferences.dart';
import 'package:frontend/utils/constants.dart';

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

class Setting extends StatefulWidget {
  const Setting({Key? key}) : super(key: key);

  @override
  State<Setting> createState() => _SettingState();
}

class _SettingState extends State<Setting> {
  List<String> languagesList = List<String>.from(availableLanguages.keys);
  late String _selectedLanguage;

  @override
  Widget build(BuildContext context) {
    _selectedLanguage = SharedPrefs().language;
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
                    style: const TextStyle(
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
                    style: const TextStyle(
                      fontSize: 20,
                    ),
                  ),
                  Container(
                    padding: EdgeInsets.symmetric(horizontal: 30, vertical: 5),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: DropdownButton<String>(
                      value: _selectedLanguage,
                      icon: Icon(Icons.arrow_drop_down),
                      iconSize: 42,
                      elevation: 16,
                      onChanged: (String? value) {
                        setState(() {
                          SharedPrefs().language = value!;
                        });
                        final snackBar = SnackBar(
                          content: Text('settings.snackbar_language_change'.tr()),
                          backgroundColor: Colors.black,
                          action: SnackBarAction(
                            label: 'settings.snackbar_close'.tr(),
                            onPressed: () {
                            },
                          ),
                        );
                        ScaffoldMessenger.of(context).showSnackBar(snackBar);
                      },
                      items: languagesList.map<DropdownMenuItem<String>>((String option) {
                        return DropdownMenuItem<String>(
                          value: availableLanguages[option],
                          child: Text(option),
                        );
                      }).toList(),
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
          TextButton(
            onPressed: () {},
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Row(
                children: [
                  Text(
                    'settings.publisher'.tr(),
                    style: const TextStyle(
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