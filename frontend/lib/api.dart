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
      address: 'Glücklich Straße 6',
      telephoneNumber: '+49 123 456 789',
      websiteUrl: 'https://www.google.com'));
  vets.add(const Veterinarian(
      id: '1',
      name: 'Mr. Unappy',
      address: 'Unglücklich Straße 6',
      telephoneNumber: '+49 123 456 789',
      websiteUrl: 'https://www.google.com'));
  vets.add(const Veterinarian(
      id: '2',
      name: 'Mr. Happy1',
      address: 'Glücklich Straße 6',
      telephoneNumber: '+49 123 456 789',
      websiteUrl: 'https://www.google.com'));
  vets.add(const Veterinarian(
      id: '3',
      name: 'Mr. Unappy2',
      address: 'Unglück2lich Straße 6',
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
