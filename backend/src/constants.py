from types_ import Weekday, Timezone, Region

WEEKDAYS: list[Weekday] = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
TIMEZONES: set[Timezone] = {"Europe/Berlin"}
REGIONS: set[Region] = {
     "Bundesland:Berlin",
     "Bundesland:Baden-Württemberg",
     "Bundesland:Bayern",
     "Bundesland:Brandenburg",
     "Bundesland:Bremen",
     "Bundesland:Hamburg",
     "Bundesland:Hessen",
     "Bundesland:Mecklenburg-Vorpommern",
     "Bundesland:Niedersachsen",
     "Bundesland:Nordrhein-Westfalen",
     "Bundesland:Rheinland-Pfalz",
     "Bundesland:Saarland",
     "Bundesland:Sachsen",
     "Bundesland:Sachsen-Anhalt",
     "Bundesland:Schleswig-Holstein",
     "Bundesland:Thüringen",
}
VET_COLLECTIONS: set[str] = {
     "hidden",
     "public",
}
