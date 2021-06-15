import random

from ..utils import core as ewutils

def generate_negaslimeoid_name():
	titles = ["Angel", "Emissary", "Gaping Maw", "Apostle", "Nemesis", "Harbinger", "Reaper", "Incarnation", "Wanderer", "Berserker", "Outcast", "Monarch", "Anomaly"]
	domains = ["Curses", "Doom", "Oblivion", "Darkness", "Madness", "the Void", "the Deep", "Nightmares", "Wrath", "Pestilence", "the End", "Terror", "Sorrow", "Pain", "Despair", "Souls", "Secrets", "Ruin", "Hatred", "Shadows", "the Night"]
	title = "{} of {}".format(random.choice(titles), random.choice(domains))
	name_length = random.randrange(5,min(10,30-len(title)))
	consonants = random.choice(["chlt","crwx","fhlt","bghl","brpq"])
	vowels = "aeuuooyy"
	num_vowels = random.randrange(int(name_length / 4), int(name_length/3)+1)
	name_list = []
	for i in range(name_length):
		if i < num_vowels:
			name_list.append(random.choice(vowels))
		else:
			name_list.append(random.choice(consonants))
	random.shuffle(name_list)
	apostrophe = random.randrange(1,name_length)
	name = ewutils.flattenTokenListToString(name_list[:apostrophe]) + "'" + ewutils.flattenTokenListToString(name_list[apostrophe:])
	name = name.capitalize()
	full_name = "{}, {}".format(name, title)
	return full_name
