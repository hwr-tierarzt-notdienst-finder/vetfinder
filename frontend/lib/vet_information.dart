import 'package:flutter/material.dart';
import 'package:frontend/api.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:easy_localization/easy_localization.dart';

class VetInformationScreenArguments {
  final String id;
  VetInformationScreenArguments(this.id);
}

class VetInformation extends StatelessWidget {
  const VetInformation({Key? key}) : super(key: key);
  double deviceHeight(BuildContext context) =>
      MediaQuery.of(context).size.height;
  double deviceWidth(BuildContext context) => MediaQuery.of(context).size.width;

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
      // 2 rows with 8 columns
      body: Container(
        padding: EdgeInsets.only(
          // top: deviceHeight(context) * 0.05,
          left: deviceWidth(context) * 0.05,
          right: deviceWidth(context) * 0.05,
          bottom: deviceHeight(context) * 0.05,
        ),
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
            Row(
              children: [
                // add a container with a border
                Container(
                  width: deviceWidth(context) * 0.9,
                  height: deviceHeight(context) * 0.12,
                  decoration: BoxDecoration(
                      color: Colors.white,
                      border: Border.all(
                        color: Colors.white,
                        width: 4,
                      ),
                      borderRadius:
                          const BorderRadius.all(Radius.circular(20))),
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
                        // padding on the left side
                        padding: const EdgeInsets.only(left: 10),
                        child: Text(
                          vet.getAddress(),
                          style: const TextStyle(
                            fontSize: 18,
                            // padding left
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
                // add a container with a border
                Container(
                  width: deviceWidth(context) * 0.9,
                  height: deviceHeight(context) * 0.12,
                  decoration: BoxDecoration(
                      color: Colors.white,
                      border: Border.all(
                        color: Colors.white,
                        width: 4,
                      ),
                      borderRadius:
                          const BorderRadius.all(Radius.circular(20))),
                  child: Row(
                    // mainAxisAlignment: MainAxisAlignment.center,
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
                        // padding on the left side
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
                // add a container with a border
                Container(
                  width: deviceWidth(context) * 0.9,
                  height: deviceHeight(context) * 0.12,
                  decoration: BoxDecoration(
                      color: Colors.white,
                      border: Border.all(
                        color: Colors.white,
                        width: 4,
                      ),
                      borderRadius:
                          const BorderRadius.all(Radius.circular(20))),
                  child: Row(
                    // mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Container(
                        padding: const EdgeInsets.only(left: 10),
                        child: const Icon(
                          Icons.email,
                          size: 30,
                        ),
                      ),
                      const SizedBox(height: 10),
                      Container(
                        // padding on the left side
                        padding: const EdgeInsets.only(left: 10),
                        child: Text(
                          vet.email,
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
            const SizedBox(height: 50),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                // 1st column
                Column(
                  children: [
                    ElevatedButton(
                      onPressed: () {
                        launch('tel:${vet.telephoneNumber}');
                      },
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.all(20),
                      ),
                      child: const Icon(Icons.phone_outlined),
                    ),
                  ],
                ),
                // 2nd column
                Column(
                  children: [
                    ElevatedButton(
                      onPressed: () {
                        launch(vet.websiteUrl);
                      },
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.all(20),
                      ),
                      child: const Icon(Icons.public),
                    ),
                  ],
                ),
                Column(
                  children: [
                    // add button
                    ElevatedButton(
                      onPressed: () {
                        launch(
                            'https://www.google.com/maps/search/?api=1&query=${vet.location.position.latitude},${vet.location.position.longitude}');
                      },
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.all(20),
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
    );
  }
}
