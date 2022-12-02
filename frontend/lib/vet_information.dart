import 'package:flutter/material.dart';
import 'package:frontend/api.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:easy_localization/easy_localization.dart';
import 'package:frontend/utils/preferences.dart';

import 'package:frontend/components/schedule_dialog.dart';

bool isDarkMode = SharedPrefs().isDarkMode;
ThemeData darkThemeVet = ThemeData(
  brightness: Brightness.dark,
  primarySwatch: Colors.grey,
);
ThemeData lightThemeVet = ThemeData(
  brightness: Brightness.light,
  primarySwatch: Colors.red,
  buttonTheme: const ButtonThemeData(buttonColor: Colors.red),
  scaffoldBackgroundColor: const Color(0xfff1f1f1),
);

class VetInformationScreenArguments {
  final String id;
  VetInformationScreenArguments(this.id);
}

class VetInformation extends StatefulWidget {
  const VetInformation({Key? key}) : super(key: key);

  @override
  State<VetInformation> createState() => _VetInformationState();
}

DateTime today = DateTime.now(); // Format: 2022-11-29 15:18:57.142575
String timeFrom = "${today.hour}:${today.minute}";
String timeTo = "${today.hour}:${today.minute}";

class _VetInformationState extends State<VetInformation> {
  double deviceHeight(BuildContext context) =>
      MediaQuery.of(context).size.height;

  double deviceWidth(BuildContext context) => MediaQuery.of(context).size.width;

  Future<void> _showScheduleDialog(BuildContext context) {
    return showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return ScheduleDialog();
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final arguments = ModalRoute.of(context)!.settings.arguments
        as VetInformationScreenArguments;

    String id = arguments.id;
    Veterinarian vet = getVeterinarianById(id);

    const descTextStyle = TextStyle(
      color: Colors.black,
      fontWeight: FontWeight.w800,
      fontSize: 18,
      height: 2,
    );
    return Scaffold(
      resizeToAvoidBottomInset: false,
      appBar: AppBar(
        title: Text('vet_information.title'.tr()),
      ),
      body: Container(
        padding: EdgeInsets.only(
          left: deviceWidth(context) * 0.05,
          right: deviceWidth(context) * 0.05
        ),
        child: SingleChildScrollView(
          child: Column(
            children: [
              const SizedBox(height: 10),
              Text(
                vet.name,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 30,
                ),
              ),
              const SizedBox(height: 10),
              Text(
                vet.clinicName,
                style: const TextStyle(
                  fontStyle: FontStyle.italic,
                  fontSize: 20,
                ),
              ),
              const SizedBox(height: 20),
              Container(
                alignment: Alignment.centerLeft,
                child: SharedPrefs().vetId != id
                    ? ElevatedButton.icon(
                        onPressed: () {
                          setState(() {
                            SharedPrefs().vetId = id;
                          });
                        },
                        icon: const Icon(Icons.star_border_rounded),
                        label: Text('vet_information.mark_as_fav'.tr()),
                        style: ElevatedButton.styleFrom(
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(20.0),
                          ),
                        ),
                      )
                    : ElevatedButton.icon(
                        onPressed: () {
                          setState(() {
                            SharedPrefs().vetId = "";
                          });
                        },
                        icon: const Icon(Icons.star_rounded),
                        label: Text('vet_information.unmark_as_fav'.tr()),
                        style: ElevatedButton.styleFrom(
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(20.0),
                          ),
                        ),
                      ),
              ),
              const SizedBox(height: 20),
              Row(
                children: [
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
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.only(left: 10),
                          child: const Icon(
                            Icons.location_on,
                            size: 30,
                          ),
                        ),
                        const SizedBox(height: 10),
                        Container(
                          padding: const EdgeInsets.only(left: 10),
                          child: Text(
                            vet.getAddress(),
                            style: const TextStyle(
                              fontSize: 18,
                            ),
                          ),
                        )
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              Row(
                children: [
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
                        borderRadius:
                            const BorderRadius.all(Radius.circular(20))),
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.only(left: 10),
                          child: const Icon(
                            Icons.pets,
                            size: 30,
                          ),
                        ),
                        const SizedBox(height: 10),
                        Container(
                          padding: const EdgeInsets.only(left: 10),
                          child: Text(
                            vet.categories.toString().substring(
                                1, vet.categories.toString().length - 1),
                            style: const TextStyle(
                              fontSize: 18,
                            ),
                          ),
                        )
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              Row(
                children: [
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
                        borderRadius:
                            const BorderRadius.all(Radius.circular(20))),
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.only(left: 10),
                          child: const Icon(
                            Icons.access_time_filled,
                            size: 30,
                          ),
                        ),
                        const SizedBox(height: 10),
                        Container(
                          padding: const EdgeInsets.only(left: 10),
                          child: Text(
                            'vet_information.open_schedule_today'.tr() +
                                ': ' +
                                timeFrom +
                                ' - ' +
                                timeTo,
                            style: const TextStyle(
                              fontSize: 16,
                            ),
                          ),
                        )
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {
                        launch('tel:${vet.getContact("tel:landline")}');
                      },
                      icon: const Icon(Icons.phone_outlined),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.all(10),
                      ),
                      label: Text(
                        'vet_information.call_vet'.tr(),
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 14,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              Column(
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () => _showScheduleDialog(context),
                          icon: const Icon(Icons.emergency_outlined),
                          label: Text(
                            'vet_information.open_schedule_emergency'.tr(),
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 14,
                            ),
                          ),
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.all(10),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () => _showScheduleDialog(context),
                          icon: const Icon(Icons.schedule_outlined),
                          label: Text(
                            'vet_information.open_schedule'.tr(),
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 14,
                            ),
                          ),
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.all(10),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 20),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  // 1st column
                  Column(
                    children: [
                      ElevatedButton(
                        onPressed: () {
                          launch('mailto:${vet.getContact("email")}');
                        },
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(
                            vertical: 20,
                            horizontal: 40,
                          ),
                        ),
                        child: const Icon(Icons.mail_outline),
                      ),
                    ],
                  ),
                  // 2nd column
                  Column(
                    children: [
                      ElevatedButton(
                        onPressed: () {
                          launch(vet.getContact("website"));
                        },
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(
                            vertical: 20,
                            horizontal: 40,
                          ),
                        ),
                        child: const Icon(Icons.public),
                      ),
                    ],
                  ),
                  Column(
                    children: [
                      ElevatedButton(
                        onPressed: () {
                          launch(
                              'https://www.google.com/maps/search/?api=1&query=${vet.location.position.latitude},${vet.location.position.longitude}');
                        },
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(
                            vertical: 20,
                            horizontal: 40,
                          ),
                        ),
                        child: const Icon(Icons.map),
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
