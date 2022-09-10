import 'package:flutter/material.dart';
import 'package:frontend/api.dart';
import 'package:url_launcher/url_launcher.dart';

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
        title: const Text('Vet Information'),
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
            const Text(
              'vet.praxisName',
              style: TextStyle(
                fontStyle: FontStyle.italic,
                fontSize: 20,
              ),
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                const Icon(Icons.location_on),
                Text(
                  vet.getAddress(),
                  style: const TextStyle(
                    fontSize: 15,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                const Icon(Icons.phone),
                Text(
                  vet.telephoneNumber,
                  style: const TextStyle(
                    fontSize: 15,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              children: const [
                Text(
                  'vet.services',
                  style: descTextStyle,
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              children: const [
                Text(
                  'vet.pets',
                  style: descTextStyle,
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              children: const [
                Text(
                  'vet.mail',
                  style: descTextStyle,
                ),
              ],
            ),
            const SizedBox(height: 30),
            Row(
              children: [
                RaisedButton(
                    child: const Text(
                      'Open Website',
                      style: TextStyle(
                          color: Colors.white, fontWeight: FontWeight.bold),
                    ),
                    onPressed: () {
                      launch(vet.websiteUrl);
                    }),
              ],
            ),
            const SizedBox(height: 10),
            Container(
              decoration: BoxDecoration(
                border: Border.all(color: Colors.black),
                borderRadius: BorderRadius.circular(10),
              ),
              width: MediaQuery.of(context).size.width * 0.9,
              height: MediaQuery.of(context).size.height * 0.4,
              margin: const EdgeInsets.only(bottom: 20.0, top: 30.0),
              child: const Center(
                child: Text(
                  'Hier nur den Standort anzeigen',
                  style: TextStyle(fontSize: 20),
                  textAlign: TextAlign.center,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
