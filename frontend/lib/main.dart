import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:easy_localization/easy_localization.dart';

import 'package:frontend/home.dart';
import 'package:frontend/settings.dart';
import 'package:frontend/vet_information.dart';
import 'package:frontend/components/search_filter_dialog.dart';
import 'package:frontend/utils/preferences.dart';

//
// leicht abgerundete Ecken
// relativ viel Platz zwischen Elementen
// Farben:
// - primary: #b71c1c
// - secondary: #fdfdfd
//

Future<void> main() async {
  // Make sure an instance of WidgetsBinding has been initialized
  WidgetsFlutterBinding.ensureInitialized();
  // Initialize shared preferences instance
  await SharedPrefs().init();
  await EasyLocalization.ensureInitialized();

  runApp(
    EasyLocalization(
      supportedLocales: [Locale('en'), Locale('de')],
      path: 'assets/translations',
      fallbackLocale: Locale('en'),
      child: MultiProvider(
        providers: [
          ChangeNotifierProvider(create: (_) => ThemeNotifier()),
          ChangeNotifierProvider(create: (_) => LanguageNotifier()),
          ChangeNotifierProvider(create: (_) => FilterNotifier()),
        ],
        child: App(),
      )
    )
  );
}

class App extends StatelessWidget {
  const App({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Consumer2<ThemeNotifier, LanguageNotifier>(
      builder: (context, ThemeNotifier, LanguageNotifier, child) {
        context.setLocale(LanguageNotifier.locale);
        return MaterialApp(
          title: 'VetFinder',
          localizationsDelegates: context.localizationDelegates,
          supportedLocales: context.supportedLocales,
          locale: context.locale,
          theme: ThemeNotifier.isDarkMode ? darkTheme : lightTheme,
          initialRoute: '/home',
          routes: {
            '/home': (context) => const Home(
                  title: 'VetFinder',
                ),
            '/vet_information': (context) => const VetInformation(),
            '/setting': (context) => const Setting(),
          },
        );
      },
    );
  }
}
