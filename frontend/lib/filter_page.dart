import 'package:flutter/material.dart';

class FilterPage extends StatelessWidget {
  const FilterPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
          title: const Text('Suchfilter')
      ),
      body: Container(
        margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 40),
        child: ListView(
          children: [
            const Text(
              'Standort:',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            DropdownButton<String>(
                isExpanded: true,
                items: [],
                onChanged: (value) {}
            ),
            const SizedBox(height: 30),
            const Text(
              'Tierart:',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const TextField(

            ),
            const SizedBox(height: 30),
            ElevatedButton(
              onPressed: () {},
              child: const Text(
                'Filter anwenden',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        )
      )
    );
  }
}