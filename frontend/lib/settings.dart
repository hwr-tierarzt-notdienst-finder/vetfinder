import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:easy_localization/easy_localization.dart';

import 'package:frontend/utils/preferences.dart';
import 'package:frontend/utils/constants.dart';

ThemeData lightTheme = ThemeData(
    brightness: Brightness.light,
    primarySwatch: Colors.red,
    buttonTheme: const ButtonThemeData(buttonColor: Colors.red),
    scaffoldBackgroundColor: const Color(0xfff1f1f1));

ThemeData darkTheme = ThemeData(
  brightness: Brightness.dark,
  primarySwatch: Colors.grey,
);

ThemeData darkThemeVetSettings = ThemeData(
  brightness: Brightness.dark,
  primarySwatch: Colors.grey,
);
ThemeData lightThemeVetSettings = ThemeData(
  brightness: Brightness.light,
  primarySwatch: Colors.red,
  buttonTheme: const ButtonThemeData(buttonColor: Colors.red),
  scaffoldBackgroundColor: const Color(0xfff1f1f1),
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

  _saveToPrefs() async {
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
  double deviceWidth(BuildContext context) => MediaQuery.of(context).size.width;
  double deviceHeight(BuildContext context) =>
      MediaQuery.of(context).size.height;

  @override
  Widget build(BuildContext context) {
    _selectedLanguage = SharedPrefs().language;
    return Scaffold(
      appBar: AppBar(
        title: Text('settings.title'.tr()),
      ),
      body: Column(
        mainAxisAlignment: MainAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(20.0),
            child: Container(
              width: deviceWidth(context) * 0.9,
              height: deviceHeight(context) * 0.12,
              decoration: BoxDecoration(
                color: Theme.of(context).brightness == Brightness.dark
                    ? Color.fromRGBO(48, 48, 48, 1)
                    : Colors.grey[200],
                border: Border.all(
                  color: Color.fromRGBO(244, 67, 54, 1),
                  width: 4,
                ),
                borderRadius: const BorderRadius.all(
                  Radius.circular(20),
                ),
              ),
              child: Padding(
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
                        builder: (context, notifier, child) => Switch(
                          onChanged: (bool value) {
                            notifier.toggleTheme();
                          },
                          value: SharedPrefs().isDarkMode,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
          // const SizedBox(height: 20),
          Container(
            width: deviceWidth(context) * 0.9,
            height: deviceHeight(context) * 0.12,
            padding: const EdgeInsets.only(left: 20),
            decoration: BoxDecoration(
              color: Theme.of(context).brightness == Brightness.dark
                  ? Color.fromRGBO(48, 48, 48, 1)
                  : Colors.grey[200],
              border: Border.all(
                color: Color.fromRGBO(244, 67, 54, 1),
                width: 4,
              ),
              borderRadius: const BorderRadius.all(
                Radius.circular(20),
              ),
            ),
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
                    color: Theme.of(context).brightness == Brightness.dark
                        ? Color.fromRGBO(48, 48, 48, 1)
                        : Colors.grey[200],
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
                        // if darkmode is checked make text color light
                        action: SnackBarAction(
                          label: 'settings.snackbar_close'.tr(),
                          onPressed: () {},
                        ),
                      );
                      ScaffoldMessenger.of(context).showSnackBar(snackBar);
                    },
                    items: languagesList
                        .map<DropdownMenuItem<String>>((String option) {
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
          const SizedBox(height: 20),
          Container(
            width: deviceWidth(context) * 0.9,
            height: deviceHeight(context) * 0.12,
            decoration: BoxDecoration(
              color: Theme.of(context).brightness == Brightness.dark
                  ? Color.fromRGBO(48, 48, 48, 1)
                  : Colors.grey[200],
              border: Border.all(
                color: Color.fromRGBO(244, 67, 54, 1),
                width: 4,
              ),
              borderRadius: const BorderRadius.all(
                Radius.circular(20),
              ),
            ),
            child: TextButton(
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
          ),
        ],
      ),
    );
  }
}
