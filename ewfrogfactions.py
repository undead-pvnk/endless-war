import math
import time
import random

import ewutils
import ewcfg

from ew import EwUser


class EwFrogEnvironment:
	id_server = ""

	temperature = 0
	slime_viscosity = 0

	
class EwFrogFood:
	id_server = ""

	id_faction = ""
	food_type = ""

	amount = 0


class EwFrogFaction:
	
	id_server = ""
	id_user = ""
	id_faction = ""

	faction_level = 0
	
	size = 0
	speed = 0
	diet = 0

	population = 0
	evolution_points = 0
	technology_points = 0

	time_last_action = 0

class EwFrogEvolution:

	id_evolution = ""

	evolution_tree = ""

	prereq = []

	unlocks = []

class EwFrogEvolutionTree:

	id_tree = ""

	roots = []


