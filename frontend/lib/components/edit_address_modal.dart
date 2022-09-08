import 'package:flutter/material.dart';

class EditAddressModal extends StatefulWidget {
  final String currentAddress;

  const EditAddressModal({
    Key? key,
    required this.currentAddress,
  }) : super(key: key);

  @override
  State<EditAddressModal> createState() =>_EditAddressModalState();
}

class _EditAddressModalState extends State<EditAddressModal> {
  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20)
      ),
      height: MediaQuery.of(context).size.height * 0.4,
      child: Padding(
        padding: const EdgeInsets.all(5),
        child: Column(
          children: [
            const SizedBox(height: 10),
            const Text(
              'Standort',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 20),
            TextButton(
              onPressed: () {},
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(
                      Icons.my_location_rounded
                    ),
                    const SizedBox(width: 10),
                    const Text(
                      'Aktuellen Standort verwenden',
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
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
      ),
    );
  }
}
