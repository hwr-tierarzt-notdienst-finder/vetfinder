from typing import TypeAlias, Literal

from . import string

Weekday: TypeAlias = Literal["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
Timezone: TypeAlias = str
Region: TypeAlias = Literal[
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
]
VetVisibility: TypeAlias = Literal[
    "software_test",
    "test",
    "public",
]
VetVerificationStatus: TypeAlias = Literal[
    "unverified",
    "verified",
]
