import 'package:flutter/material.dart';
import 'package:frontend/vet_information.dart';

class VetCard extends Card {
  const VetCard(
      {Key? key,
      required this.id,
      required this.name,
      required this.telephoneNumber,
      required this.address,
      required this.websiteUrl})
      : super(key: key);

  final String id;
  final String name;
  final String telephoneNumber;
  final String address;
  final String websiteUrl;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Column(
        children: [
          const SizedBox(height: 10),
          Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 5),
          Text(address),
          Text(telephoneNumber),
          const SizedBox(height: 5),
          Text(websiteUrl),
          TextButton.icon(
              onPressed: () {
                Navigator.pushNamed(context, '/vet_information',
                    arguments: VetInformationScreenArguments(id));
              },
              icon: const Icon(Icons.arrow_forward_ios_rounded),
              label: const Text('Zum Tierarzt'))
        ],
      ),
    );
  }
}
