import 'package:flutter/material.dart';
import 'package:frontend/api.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:easy_localization/easy_localization.dart';

import 'package:frontend/utils/preferences.dart';
import 'package:frontend/utils/constants.dart';
import 'package:frontend/components/schedule_dialog_emergency.dart';
import 'package:frontend/components/schedule_dialog_regular.dart';

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

  Future<void> _showScheduleDialogEmergency(
      BuildContext context, String currentId) {
    return showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return ScheduleDialogEmergency(id: currentId);
      },
    );
  }

  Future<void> _showScheduleDialogRegular(
      BuildContext context, String currentId) {
    return showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return ScheduleDialogRegular(id: currentId);
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    // Get the vet object by ID
    final arguments = ModalRoute.of(context)!.settings.arguments
        as VetInformationScreenArguments;
    String id = arguments.id;
    Veterinarian vet = getVeterinarianById(id);

    // Translate treatments to be shown in the correct language
    List<String> translatedTreatments = [];
    for (String treatment in vet.treatments) {
      translatedTreatments.add('treatments.$treatment'.tr());
    }

    return Scaffold(
      resizeToAvoidBottomInset: false,
      appBar: AppBar(
        title: Text('vet_information.title'.tr()),
      ),
      body: Container(
        padding: EdgeInsets.only(
            left: deviceWidth(context) * 0.05,
            right: deviceWidth(context) * 0.05),
        child: SingleChildScrollView(
          child: Column(
            children: [
              const SizedBox(height: 10),
              Text(
                vet.getName(),
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 25,
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
                            translatedTreatments.toString().substring(
                                1, translatedTreatments.toString().length - 1),
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
                            Icons.schedule_outlined,
                            size: 30,
                          ),
                        ),
                        const SizedBox(height: 10),
                        Container(
                          padding: const EdgeInsets.only(left: 10),
                          child: Text(
                            'vet_information.open_schedule'.tr() +
                                ": " +
                                vet.getAvailabilityToday(),
                            style: const TextStyle(
                              fontSize: 16,
                            ),
                          ),
                        ),
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
                            Icons.emergency_outlined,
                            size: 30,
                          ),
                        ),
                        const SizedBox(height: 10),
                        Container(
                          padding: const EdgeInsets.only(left: 10),
                          child: Text(
                            'vet_information.open_schedule_emergency'.tr() +
                                ": " +
                                vet.getEmergencyAvailabilityToday(),
                            style: const TextStyle(
                              fontSize: 16,
                            ),
                          ),
                        ),
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
                        launch('tel:${vet.getContact(contactsTelLandline)}');
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
                          onPressed: () =>
                              _showScheduleDialogEmergency(context, id),
                          icon: const Icon(Icons.emergency_outlined),
                          label: Text(
                            'vet_information.open_schedule_emergency_week'.tr(),
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
                          onPressed: () =>
                              _showScheduleDialogRegular(context, id),
                          icon: const Icon(Icons.schedule_outlined),
                          label: Text(
                            'vet_information.open_schedule_week'.tr(),
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
                          launch('mailto:${vet.getContact(contactsEmail)}');
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
                          launch(vet.getContact(contactsWebsite));
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
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }
}
