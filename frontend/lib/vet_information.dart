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
      body: SingleChildScrollView(
        // add margin all around with 0.9 size of screen
        // margin: const EdgeInsets.all(0.9),
        padding: EdgeInsets.only(
          // top: deviceHeight(context) * 0.05,
          left: deviceWidth(context) * 0.05,
          right: deviceWidth(context) * 0.05,
          bottom: deviceHeight(context) * 0.05,
        ),

        child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
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
                const Icon(Icons.location_on),
                Padding(
                  padding: const EdgeInsets.only(left: 10),
                  child: Text(
                    vet.getAddress(),
                    style: const TextStyle(
                      fontSize: 15,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                const Icon(Icons.phone),
                Padding(
                  padding: const EdgeInsets.only(left: 10),
                  child: Text(
                    vet.telephoneNumber,
                    style: const TextStyle(
                      fontSize: 15,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                const Icon(Icons.pets),
                Padding(
                  padding: const EdgeInsets.only(left: 10),
                  child: Text(vet.categories
                      .toString()
                      .substring(1, vet.categories.toString().length - 1)),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                const Icon(Icons.email),
                Padding(
                  padding: const EdgeInsets.only(left: 10),
                  child: Text(
                    vet.email,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 30),
            Row(
              children: [
                ElevatedButton(
                    child: Text(
                      'vet_information.open_website'.tr(),
                      style: const TextStyle(
                          color: Colors.white, fontWeight: FontWeight.bold),
                    ),
                    onPressed: () {
                      launch(vet.websiteUrl);
                    }),
              ],
            ),
            const SizedBox(height: 30),
            Row(
              children: [
                ElevatedButton(
                    child: Text(
                      'vet_information.open_map'.tr(),
                      style: TextStyle(
                          color: Colors.white, fontWeight: FontWeight.bold),
                    ),
                    onPressed: () {
                      launch(
                          'https://www.google.com/maps/search/?api=1&query=${vet.location.position.latitude},${vet.location.position.longitude}');
                    }),
              ],
            ),
            const SizedBox(height: 10),
          ],
        ),
      ),
    );
  }
}
