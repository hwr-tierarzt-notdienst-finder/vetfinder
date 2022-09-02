class Veterinarian {
  const Veterinarian(
      {required this.id,
      required this.name,
      required this.telephoneNumber,
      required this.address,
      required this.websiteUrl})
      : super();

  final String id;
  final String name;
  final String telephoneNumber;
  final String address;
  final String websiteUrl;
}

List<Veterinarian> getVeterinarians() {
  List<Veterinarian> vets = [];
  vets.add(const Veterinarian(
      id: '0',
      name: 'Mr. Happy',
      address: 'Berliner Straße 8',
      telephoneNumber: '+49 123 456 789',
      websiteUrl: 'https://www.google.com'));
  vets.add(const Veterinarian(
      id: '1',
      name: 'Mr. Sad',
      address: 'Hamburger Straße 2',
      telephoneNumber: '+49 123 456 789',
      websiteUrl: 'https://www.google.com'));
  vets.add(const Veterinarian(
      id: '2',
      name: 'Mr. Angry',
      address: 'Hotdog Straße 3',
      telephoneNumber: '+49 123 456 789',
      websiteUrl: 'https://www.google.com'));
  vets.add(const Veterinarian(
      id: '3',
      name: 'Mr. Angy',
      address: 'Pommes Straße 1',
      telephoneNumber: '+49 123 456 789',
      websiteUrl: 'https://www.google.com'));
  vets.add(const Veterinarian(
      id: '4',
      name: 'Mr. Rainbow',
      address: 'Pommes Straße 3',
      telephoneNumber: '+49 123 456 789',
      websiteUrl: 'https://www.google.com'));

  return vets;
}

Veterinarian getVeterinarianById(String id) {
  List<Veterinarian> vets = getVeterinarians();
  for (var vet in vets) {
    if (vet.id == id) {
      return vet;
    }
  }
  throw 'Could not find veterinarian with id $id';
}
