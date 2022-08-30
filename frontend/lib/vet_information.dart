import 'package:flutter/material.dart';
import 'package:frontend/api.dart';

class VetInformationScreenArguments {
  final String id;
  VetInformationScreenArguments(this.id);
}

class VetInformation extends StatelessWidget {
  const VetInformation({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final arguments = ModalRoute.of(context)!.settings.arguments
        as VetInformationScreenArguments;

    String id = arguments.id;
    Veterinarian vet = getVeterinarianById(id);

    return Scaffold(
        appBar: AppBar(
          title: Text(vet.name),
        ),
        body: Container(
          child: Column(children: [
            Text(id),
            Text(vet.name),
            Text(vet.telephoneNumber),
            Text(vet.address),
            Text(vet.websiteUrl),
          ]),
        ));
  }
}
