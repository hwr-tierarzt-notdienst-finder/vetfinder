import 'package:flutter/material.dart';
import 'package:frontend/components/veterinarian.dart';
import 'package:frontend/api.dart';

class Home extends StatefulWidget {
  const Home({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  State<Home> createState() => _HomeState();
}

class _HomeState extends State<Home> {
  @override
  Widget build(BuildContext context) {
    // This method is rerun every time setState is called, for instance as done
    // by the _incrementCounter method above.
    //
    // The Flutter framework has been optimized to make rerunning build methods
    // fast, so that you can just rebuild anything that needs updating rather
    // than having to individually change instances of widgets.

    List<Veterinarian> vets = getVeterinarians();

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
        actions: [
          IconButton(
              onPressed: () => Navigator.pushNamed(context, '/search_page'),
              icon: const Icon(Icons.search)),
        ],
      ),
      body: Container(
        margin: const EdgeInsets.all(10),
        child: Center(
          child: Column(
            children: <Widget>[
              Text(
                'Tierärzte in deiner Nähe',
                style: Theme.of(context).textTheme.headline4,
              ),
              Container(
                width: MediaQuery.of(context).size.width * 0.9,
                height: MediaQuery.of(context).size.height * 0.3,
                color: Colors.black,
              ),
              Expanded(
                child: ListView.builder(
                    itemCount: vets.length,
                    itemBuilder: (context, index) {
                      return VetCard(
                          id: vets[index].id,
                          name: vets[index].name,
                          telephoneNumber: vets[index].telephoneNumber,
                          address: vets[index].address,
                          websiteUrl: vets[index].websiteUrl);
                    }),
              )
            ],
          ),
        ),
      ),
      /*floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: const Icon(Icons.add),
      ),*/ // This trailing comma makes auto-formatting nicer for build methods.
    );
  }
}
