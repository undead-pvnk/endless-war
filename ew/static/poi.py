import os
import json

from . import cfg as ewcfg

from ..model.poi import EwPoi, EwTransportLine
from ..model.poi import EwEventDef
from ..model.poi import EwDungeonScene

#load EwPois from json to poi_list
poi_list = []
with open(os.path.join('json', 'poi.json')) as f:
	pois = json.load(f)
	for i in pois:
		i = pois[i]
		poi_list.append(
			EwPoi(
				id_poi = i['id_poi'], 
				alias = i['alias'], 
				str_name = i['str_name'], 
				str_desc = i['str_desc'], 
				str_in = i['str_in'], 
				str_enter = i['str_enter'], 
				coord = i['coord'], 
				coord_alias = i['coord_alias'], 
				channel = i['channel'], 
				role = i['role'], 
				major_role = i['major_role'], 
				minor_role = i['minor_role'], 
				permissions = i['permissions'], 
				pvp = i['pvp'], 
				factions = i['factions'], 
				life_states = i['life_states'], 
				closed = i['closed'], 
				str_closed = i['str_closed'], 
				vendors = i['vendors'], 
				property_class = i['property_class'], 
				is_district = i['is_district'], 
				is_gangbase = i['is_gangbase'], 
				is_capturable = i['is_capturable'], 
				is_subzone = i['is_subzone'], 
				is_apartment = i['is_apartment'], 
				is_street = i['is_street'], 
				mother_districts = i['mother_districts'], 
				father_district = i['father_district'], 
				is_transport = i['is_transport'], 
				transport_type = i['transport_type'], 
				default_line = i['default_line'], 
				default_stop = i['default_stop'], 
				is_transport_stop = i['is_transport_stop'], 
				transport_lines = set(), 
				is_outskirts = i['is_outskirts'], 
				community_chest = i['community_chest'], 
				is_pier = i['is_pier'], 
				pier_type = i['pier_type'], 
				is_tutorial = i['is_tutorial'], 
				has_ads = i['has_ads'], 
				write_manuscript = i['write_manuscript'], 
				max_degradation = i['max_degradation'], 
				neighbors = i['neighbors'], 
				topic = i['topic'], 
				wikipage = i['wikipage']
			))


# if you're looking for poi_map, here it is
id_to_poi = {}
coord_to_poi = {}
chname_to_poi = {}
alias_to_coord = {}
capturable_districts = []
transports = []
transport_stops = []
transport_stops_ch = []
piers = []
outskirts = []
outskirts_edges = []
outskirts_middle = []
outskirts_depths = []
streets = []
tutorial_pois = []
zine_mother_districts = []

for poi in poi_list:

	# Assign permissions for all locations in the poi list.
	if poi.permissions == None:
		poi.permissions = {('{}'.format(poi.id_poi)): permissions_general}

	# Assign all the correct major and minor roles.
	
	# Districts and streets need their minor roles to see (read-only) all of their subzones.
	if poi.is_district or poi.is_street or poi.id_poi in [ewcfg.poi_id_mine, ewcfg.poi_id_cv_mines, ewcfg.poi_id_tt_mines]:
		poi.minor_role = '{}_minor'.format(poi.id_poi)

	# Districts need their major roles for their specific LAN (voice/text) channels.
	if poi.is_district:
		poi.major_role = '{}_major'.format(poi.id_poi)
		streets_resp = ''
		"""
		district_streets_list = []
		for street_poi in poi_list:
			if street_poi.father_district == poi.id_poi:
				district_streets_list.append(street_poi.str_name)
			
		if len(district_streets_list) > 0:
			poi.str_desc += " This area is connected to "
			if len(district_streets_list) == 1:
				poi.str_desc += district_streets_list[0]
			else:
				for i in range(len(district_streets_list)):
		
					if i == (len(district_streets_list) - 1):
						poi.str_desc += 'and {}.'.format(district_streets_list[i])
					else:
						poi.str_desc += '{}, '.format(district_streets_list[i])
		"""
						
	placeholder_channel_names_used = False
		
	# Subzones and streets need the same major roles as their mother/father districts.
	if poi.is_street:
		if poi.father_district != "" and poi.father_district != None:
			for father_poi in poi_list:
				if father_poi.id_poi == poi.father_district:
					poi.major_role = father_poi.major_role
					poi.property_class = father_poi.property_class
					
					if placeholder_channel_names_used:
						if 'streeta' in poi.id_poi:
							poi.channel = father_poi.channel + '-street-a'
						elif 'streetb' in poi.id_poi:
							poi.channel = father_poi.channel + '-street-b'
						elif 'streetc' in poi.id_poi:
							poi.channel = father_poi.channel + '-street-c'
						elif 'streetd' in poi.id_poi:
							poi.channel = father_poi.channel + '-street-d'
						elif 'streete' in poi.id_poi:
							poi.channel = father_poi.channel + '-street-e'
						elif 'streetf' in poi.id_poi:
							poi.channel = father_poi.channel + '-street-f'
							
					break
			
			father_district = ''
			connected_streets_and_districts = []
			connected_subzones = []
			for neighbor_poi in poi_list:
				if neighbor_poi.id_poi in poi.neighbors:
					if neighbor_poi.id_poi == poi.father_district:
						father_district = neighbor_poi.str_name
					elif neighbor_poi.is_street or (neighbor_poi.is_district and neighbor_poi.id_poi != poi.father_district):
						connected_streets_and_districts.append(neighbor_poi.str_name)
					elif neighbor_poi.is_subzone:
						connected_subzones.append(neighbor_poi.str_name)
			
			if father_district != '':
				poi.str_desc += " This street connects back into {}.".format(father_district)
			
				if len(connected_streets_and_districts) >= 1:
					poi.str_desc += " This street is connected to "
					if len(connected_streets_and_districts) == 1:
						poi.str_desc += connected_streets_and_districts[0]
					else:
						for i in range(len(connected_streets_and_districts)):
					
							if i == (len(connected_streets_and_districts) - 1):
								poi.str_desc += 'and {}.'.format(connected_streets_and_districts[i])
							else:
								poi.str_desc += '{}, '.format(connected_streets_and_districts[i])

				if len(connected_subzones) >= 1:
					poi.str_desc += " This street also exits into "
					if len(connected_subzones) == 1:
						poi.str_desc += connected_subzones[0]
					else:
						for i in range(len(connected_subzones)):
		
							if i == (len(connected_subzones) - 1):
								poi.str_desc += 'and {}.'.format(connected_subzones[i])
							else:
								poi.str_desc += '{}, '.format(connected_subzones[i])
		else:
			print('Error: No father POI found for {}'.format(poi.id_poi))
	
	mother_roles_dict = {}
	if poi.is_subzone:
		
		for mother_poi in poi_list:
			if mother_poi.id_poi in poi.mother_districts:
				if mother_poi.major_role != None:
					poi.major_role = mother_poi.major_role
					break
		
	if poi.major_role == None:
		#print('Null Major Role give to {}'.format(poi.id_poi))
		poi.major_role = role_null_major_role
	if poi.minor_role == None:
		#print('Null Minor Role give to {}'.format(poi.str_name))
		poi.minor_role = role_null_minor_role
	
	# poi coords cause json import problems because poi.coords imports as a list type 
	#if poi.coord != None:
	#	# Populate the map of coordinates to their point of interest, for looking up from the map.
	#	coord_to_poi[poi.coord] = poi
	#	
	#	# for poi_2 in poi_list:
	#	# 	if (poi.coord == poi_2.coord) and (poi.id_poi != poi_2.id_poi):
	#	# 		print('{} has same coords as {}, please fix this.'.format(poi.id_poi, poi_2.id_poi))
	#
	#	# Populate the map of coordinate aliases to the main coordinate.
	#	for coord_alias in poi.coord_alias:
	#		alias_to_coord[coord_alias] = poi.coord
	#		coord_to_poi[coord_alias] = poi

	# Populate the map of point of interest names/aliases to the POI.
	id_to_poi[poi.id_poi] = poi
	for alias in poi.alias:
		for poi_2 in poi_list:
			if alias in poi_2.alias and poi.id_poi != poi_2.id_poi:
				print('alias {} is already being used by {}'.format(alias, poi_2.id_poi))

		id_to_poi[alias] = poi

	# if it's a district and not RR, CK, or JR, add it to a list of capturable districts
	if poi.is_capturable:
		capturable_districts.append(poi.id_poi)

	if poi.is_transport:
		transports.append(poi.id_poi)

	if poi.is_transport_stop:
		transport_stops.append(poi.id_poi)
		transport_stops_ch.append(poi.channel)

	if poi.is_pier:
		piers.append(poi.id_poi)

	if poi.is_outskirts:
		outskirts.append(poi.id_poi)
		# For spawning purposes. Rarer enemies will spawn more often in the father layers of the 18 outskirts.
		
		# It's a bit of a simplistic solution, but this way we don't have to add an attribute to EwPoi
		if 'edge' in poi.str_name.lower():
			outskirts_edges.append(poi.id_poi)
			#print(poi.channel)
		elif 'depths' in poi.str_name.lower():
			outskirts_depths.append(poi.id_poi)
			#print(poi.channel)
		else:
			outskirts_middle.append(poi.id_poi)
		
		if len(poi.neighbors) > 0:
			poi.str_desc += " This outskirt is connected to "
			
			neighbor_index = 0
			for neighbor_id in poi.neighbors.keys():
				
				current_neighbor = None
				
				for outskirt_neighbor in poi_list:
					if neighbor_id == outskirt_neighbor.id_poi:
						current_neighbor = outskirt_neighbor
						
				if current_neighbor != None:
					if neighbor_index == (len(poi.neighbors.keys()) - 1):
						poi.str_desc += 'and {}.'.format(current_neighbor.str_name)
					else:
						poi.str_desc += '{}, '.format(current_neighbor.str_name)
				
				neighbor_index += 1
		
	if poi.is_street:
		streets.append(poi.id_poi)
		#print(poi.minor_role)

	if poi.is_tutorial:
		tutorial_pois.append(poi.id_poi)

	if poi.write_manuscript:
		for mother_poi in poi.mother_districts:
			zine_mother_districts.append(id_to_poi.get(mother_poi))

	chname_to_poi[poi.channel] = poi


landmark_pois = [
	ewcfg.poi_id_dreadford,
	ewcfg.poi_id_charcoalpark,
	ewcfg.poi_id_slimesend,
	ewcfg.poi_id_assaultflatsbeach,
	ewcfg.poi_id_wreckington,
]

non_district_non_subzone_pvp_areas = [
	ewcfg.poi_id_thevoid
]

# Places on the map that should result in a user being flagged for PVP
vulnerable_districts = outskirts + streets
for poi in poi_list:
	if (poi.is_subzone or poi.id_poi in non_district_non_subzone_pvp_areas) and poi.pvp:
		vulnerable_districts.append(poi.id_poi)
# for vul in vulnerable_districts:
#     print('vulnerable area: {}'.format(vul))

# maps districts to their immediate neighbors
poi_neighbors = {}

transport_lines = [
	EwTransportLine( # ferry line from wreckington to vagrant's corner
		id_line = ewcfg.transport_line_ferry_wt_to_vc,
		alias = [
			"vagrantscornerferry",
			"vagrantsferry",
			"vcferry",
			"ferrytovagrantscorner",
			"ferrytovagrants",
			"ferrytovc"
			],
		first_stop = ewcfg.poi_id_wt_port,
		last_stop = ewcfg.poi_id_vc_port,
		next_line = ewcfg.transport_line_ferry_vc_to_wt,
		str_name = "The ferry line towards Vagrant's Corner",
		schedule = {
			ewcfg.poi_id_wt_port : [60, ewcfg.poi_id_slimesea],
			ewcfg.poi_id_slimesea : [120, ewcfg.poi_id_vc_port]
			}

		),
	EwTransportLine( # ferry line from vagrant's corner to wreckington
		id_line = ewcfg.transport_line_ferry_vc_to_wt,
		alias = [
			"wreckingtonferry",
			"wreckferry",
			"wtferry",
			"ferrytowreckington",
			"ferrytowreck",
			"ferrytowt"
			],
		first_stop = ewcfg.poi_id_vc_port,
		last_stop = ewcfg.poi_id_wt_port,
		next_line = ewcfg.transport_line_ferry_wt_to_vc,
		str_name = "The ferry line towards Wreckington",
		schedule = {
			ewcfg.poi_id_vc_port : [60, ewcfg.poi_id_slimesea],
			ewcfg.poi_id_slimesea : [120, ewcfg.poi_id_wt_port]
			}
		),
	EwTransportLine( # yellow subway line from south sleezeborough to arsonbrook
		id_line = ewcfg.transport_line_subway_yellow_northbound,
		alias = [
			"northyellowline",
			"northyellow",
			"yellownorth",
			"yellowtoarsonbrook",
			"yellowtoarson",
			"yellowtoab"
			],
		first_stop = ewcfg.poi_id_ssb_subway_station,
		last_stop = ewcfg.poi_id_ab_subway_station,
		next_line = ewcfg.transport_line_subway_yellow_southbound,
		str_name = "The yellow subway line towards Arsonbrook",
		schedule = {
			ewcfg.poi_id_ssb_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_kb_subway_station],
			ewcfg.poi_id_kb_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_dt_subway_station],
			ewcfg.poi_id_dt_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_sb_subway_station],
			ewcfg.poi_id_sb_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_ab_subway_station]
			}

		),
	EwTransportLine( # yellow subway line from arsonbrook to south sleezeborough
		id_line = ewcfg.transport_line_subway_yellow_southbound,
		alias = [
			"southyellowline",
			"southyellow",
			"yellowsouth",
			"yellowtosouthsleezeborough",
			"yellowtosouthsleeze",
			"yellowtossb"
			],
		first_stop = ewcfg.poi_id_ab_subway_station,
		last_stop = ewcfg.poi_id_ssb_subway_station,
		next_line = ewcfg.transport_line_subway_yellow_northbound,
		str_name = "The yellow subway line towards South Sleezeborough",
		schedule = {
			ewcfg.poi_id_ab_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_sb_subway_station],
			ewcfg.poi_id_sb_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_dt_subway_station],
			ewcfg.poi_id_dt_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_kb_subway_station],
			ewcfg.poi_id_kb_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_ssb_subway_station]
			}

		),
	EwTransportLine( # red subway line from cratersville to toxington
		id_line = ewcfg.transport_line_subway_red_northbound,
		alias = [
			"northredline",
			"northred",
			"rednorth",
			"redtotoxington",
			"redtotox",
			"redtott"
			],
		first_stop = ewcfg.poi_id_cv_subway_station,
		last_stop = ewcfg.poi_id_tt_subway_station,
		next_line = ewcfg.transport_line_subway_red_southbound,
		str_name = "The red subway line towards Toxington",
		schedule = {
			ewcfg.poi_id_cv_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_wt_subway_station],
			ewcfg.poi_id_wt_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_rr_subway_station],
			ewcfg.poi_id_rr_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_dt_subway_station],
			ewcfg.poi_id_dt_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_ck_subway_station],
			ewcfg.poi_id_ck_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_gd_subway_station],
			ewcfg.poi_id_gd_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_ah_subway_station],
			ewcfg.poi_id_ah_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_tt_subway_station]
			}

		),
	EwTransportLine( # red subway line from toxington to cratersville
		id_line = ewcfg.transport_line_subway_red_southbound,
		alias = [
			"southredline",
			"southred",
			"redsouth",
			"redtocratersville",
			"redtocraters",
			"redtocv"
			],
		first_stop = ewcfg.poi_id_tt_subway_station,
		last_stop = ewcfg.poi_id_cv_subway_station,
		next_line = ewcfg.transport_line_subway_red_northbound,
		str_name = "The red subway line towards Cratersville",
		schedule = {
			ewcfg.poi_id_tt_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_ah_subway_station],
			ewcfg.poi_id_ah_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_gd_subway_station],
			ewcfg.poi_id_gd_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_ck_subway_station],
			ewcfg.poi_id_ck_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_dt_subway_station],
			ewcfg.poi_id_dt_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_rr_subway_station],
			ewcfg.poi_id_rr_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_wt_subway_station],
			ewcfg.poi_id_wt_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_cv_subway_station]
			}

		),
	EwTransportLine( # green subway line from smogsburg to west glocksbury
		id_line = ewcfg.transport_line_subway_green_eastbound,
		alias = [
			"greeneastline",
			"greeneast",
			"eastgreen",
			"greentosmogsburg",
			"greentosmogs",
			"greentosb"
			],
		first_stop = ewcfg.poi_id_wgb_subway_station,
		last_stop = ewcfg.poi_id_sb_subway_station,
		next_line = ewcfg.transport_line_subway_green_westbound,
		str_name = "The green subway line towards Smogsburg",
		schedule = {
			ewcfg.poi_id_wgb_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_jp_subway_station],
			ewcfg.poi_id_jp_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_nsb_subway_station],
			ewcfg.poi_id_nsb_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_kb_subway_station],
			ewcfg.poi_id_kb_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_dt_subway_station],
			ewcfg.poi_id_dt_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_sb_subway_station]
			}

		),
	EwTransportLine( # green subway line from west glocksbury to smogsburg
		id_line = ewcfg.transport_line_subway_green_westbound,
		alias = [
			"greenwestline",
			"greenwest",
			"westgreen",
			"greentowestglocksbury",
			"greentowestglocks",
			"greentowgb"
			],
		first_stop = ewcfg.poi_id_sb_subway_station,
		last_stop = ewcfg.poi_id_wgb_subway_station,
		next_line = ewcfg.transport_line_subway_green_eastbound,
		str_name = "The green subway line towards West Glocksbury",
		schedule = {
			ewcfg.poi_id_sb_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_dt_subway_station],
			ewcfg.poi_id_dt_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_kb_subway_station],
			ewcfg.poi_id_kb_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_gb_subway_station],
			ewcfg.poi_id_gb_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_wgb_subway_station]
			}

		),
	EwTransportLine( # blue subway line from downtown to assault flats beach
		id_line = ewcfg.transport_line_subway_blue_eastbound,
		alias = [
			"blueeastline",
			"blueeast",
			"eastblue",
			"bluetoassaultflatsbeach",
			"bluetoassaultflats",
			"bluetobeach",
			"bluetoafb"
			],
		first_stop = ewcfg.poi_id_dt_subway_station,
		last_stop = ewcfg.poi_id_afb_subway_station,
		next_line = ewcfg.transport_line_subway_blue_westbound,
		str_name = "The blue subway line towards Assault Flats Beach",
		schedule = {
			ewcfg.poi_id_dt_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_gld_subway_station],
			ewcfg.poi_id_gld_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_jr_subway_station],
			ewcfg.poi_id_jr_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_vc_subway_station],
			ewcfg.poi_id_vc_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_afb_subway_station]
			}

		),
	EwTransportLine( # blue subway line from assault flats beach to downtown
		id_line = ewcfg.transport_line_subway_blue_westbound,
		alias = [
			"bluewestline",
			"bluewest",
			"westblue",
			"bluetodowntown",
			"bluetodt"
			],
		first_stop = ewcfg.poi_id_afb_subway_station,
		last_stop = ewcfg.poi_id_dt_subway_station,
		next_line = ewcfg.transport_line_subway_blue_eastbound,
		str_name = "The blue subway line towards Downtown NLACakaNM",
		schedule = {
			ewcfg.poi_id_afb_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_vc_subway_station],
			ewcfg.poi_id_vc_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_jr_subway_station],
			ewcfg.poi_id_jr_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_gld_subway_station],
			ewcfg.poi_id_gld_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_dt_subway_station]
			}

		),
#	EwTransportLine( # white subway line from downtown to juvies row
#	 	id_line = ewcfg.transport_line_subway_white_eastbound,
#	 	alias = [
#	 		"whiteeastline",
#			"whiteeast",
#	 		"eastwhite",
#	 		"whitetojuviesrow",
#	 		"whitetojuvies",
#	 		"whitetojr"
#	 	    ],
#	 	first_stop = ewcfg.poi_id_underworld_subway_station,
#	 	last_stop = ewcfg.poi_id_jr_subway_station,
#	 	next_line = ewcfg.transport_line_subway_white_westbound,
#	 	str_name = "The white subway line towards Juvie's Row",
#	 	schedule = {
#	 		ewcfg.poi_id_underworld_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_dt_subway_station],
#	 		ewcfg.poi_id_dt_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_rr_subway_station],
#	 		ewcfg.poi_id_rr_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_jr_subway_station]
#	 	    }
#	 	),
#	EwTransportLine( # white subway line from juvies row to downtown
#	 	id_line = ewcfg.transport_line_subway_white_westbound,
#	 	alias = [
#	 		"whitewestline",
#	 		"whitewest",
#	 		"westwhite",
#	 		"whitetounderworld",
#	 		"whitetouw"
#	 	    ],
#	 	first_stop = ewcfg.poi_id_jr_subway_station,
#	 	last_stop = ewcfg.poi_id_underworld_subway_station,
#	 	next_line = ewcfg.transport_line_subway_white_eastbound,
#	 	str_name = "The white subway line towards The Underworld",
#	 	schedule = {
#	 		ewcfg.poi_id_jr_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_rr_subway_station],
#	 		ewcfg.poi_id_rr_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_dt_subway_station],
#	 		ewcfg.poi_id_dt_subway_station : [ewcfg.time_movesubway, ewcfg.poi_id_underworld_subway_station],
#	 	    }
#	 	),
	EwTransportLine( # blimp line from dreadford to assault flats beach
		id_line = ewcfg.transport_line_blimp_df_to_afb,
		alias = [
			"assaultflatsbeachblimp",
			"assaultflatsblimp",
			"beachblimp",
			"afbblimp",
			"blimptoassaultflatsbeach",
			"blimptoassaultflats",
			"blimptobeach",
			"blimptoafb"
			],
		first_stop = ewcfg.poi_id_df_blimp_tower,
		last_stop = ewcfg.poi_id_afb_blimp_tower,
		next_line = ewcfg.transport_line_blimp_afb_to_df,
		str_name = "The blimp line towards Assault Flats Beach",
		schedule = {
			ewcfg.poi_id_df_blimp_tower : [60, ewcfg.poi_id_jaywalkerplain],
			ewcfg.poi_id_jaywalkerplain : [40, ewcfg.poi_id_northsleezeborough],
			ewcfg.poi_id_northsleezeborough : [40, ewcfg.poi_id_krakbay],
			ewcfg.poi_id_krakbay : [40, ewcfg.poi_id_downtown],
			ewcfg.poi_id_downtown : [40, ewcfg.poi_id_greenlightdistrict],
			ewcfg.poi_id_greenlightdistrict : [40, ewcfg.poi_id_vagrantscorner],
			ewcfg.poi_id_vagrantscorner : [40, ewcfg.poi_id_afb_blimp_tower]
			}

		),
	EwTransportLine( # blimp line from assault flats beach to dreadford
		id_line = ewcfg.transport_line_blimp_afb_to_df,
		alias = [
			"dreadfordblimp",
			"dreadblimp",
			"dfblimp",
			"blimptodreadford",
			"blimptodread",
			"blimptodf"
			],
		first_stop = ewcfg.poi_id_afb_blimp_tower,
		last_stop = ewcfg.poi_id_df_blimp_tower,
		next_line = ewcfg.transport_line_blimp_df_to_afb,
		str_name = "The blimp line towards Dreadford",
		schedule = {
			ewcfg.poi_id_afb_blimp_tower : [60, ewcfg.poi_id_vagrantscorner],
			ewcfg.poi_id_vagrantscorner : [40, ewcfg.poi_id_greenlightdistrict],
			ewcfg.poi_id_greenlightdistrict : [40, ewcfg.poi_id_downtown],
			ewcfg.poi_id_downtown : [40, ewcfg.poi_id_krakbay],
			ewcfg.poi_id_krakbay : [40, ewcfg.poi_id_northsleezeborough],
			ewcfg.poi_id_northsleezeborough : [40, ewcfg.poi_id_jaywalkerplain],
			ewcfg.poi_id_jaywalkerplain : [40, ewcfg.poi_id_df_blimp_tower]
			}

		),
]

id_to_transport_line = {}

for line in transport_lines:
	id_to_transport_line[line.id_line] = line
	for alias in line.alias:
		id_to_transport_line[alias] = line

	for poi in transport_stops:
		poi_data = id_to_poi.get(poi)
		if (poi in line.schedule.keys()) or (poi == line.last_stop):
			poi_data.transport_lines.add(line.id_line)



landlocked_destinations ={
	ewcfg.poi_id_maimridge:ewcfg.poi_id_wreckington,
	ewcfg.poi_id_wreckington: ewcfg.poi_id_maimridge,
	ewcfg.poi_id_cratersville:ewcfg.poi_id_arsonbrook,
	ewcfg.poi_id_arsonbrook:ewcfg.poi_id_cratersville,
	ewcfg.poi_id_oozegardens:ewcfg.poi_id_brawlden,
	ewcfg.poi_id_brawlden:ewcfg.poi_id_oozegardens,
	ewcfg.poi_id_southsleezeborough:ewcfg.poi_id_newnewyonkers,
	ewcfg.poi_id_newnewyonkers:ewcfg.poi_id_southsleezeborough,
	ewcfg.poi_id_dreadford:ewcfg.poi_id_assaultflatsbeach,
	ewcfg.poi_id_assaultflatsbeach:ewcfg.poi_id_dreadford,
	ewcfg.poi_id_crookline:ewcfg.poi_id_assaultflatsbeach,
	ewcfg.poi_id_jaywalkerplain:ewcfg.poi_id_vagrantscorner,
	ewcfg.poi_id_vagrantscorner:ewcfg.poi_id_jaywalkerplain,
	ewcfg.poi_id_westglocksbury:ewcfg.poi_id_slimesendcliffs,
	ewcfg.poi_id_slimesendcliffs:ewcfg.poi_id_westglocksbury,
	ewcfg.poi_id_poloniumhill:ewcfg.poi_id_slimesend,
	ewcfg.poi_id_slimesend:ewcfg.poi_id_poloniumhill,
	ewcfg.poi_id_charcoalpark:ewcfg.poi_id_ferry,
	ewcfg.poi_id_ferry:ewcfg.poi_id_charcoalpark,
	ewcfg.poi_id_toxington:ewcfg.poi_id_ferry,
	ewcfg.poi_id_thevoid:ewcfg.poi_id_themoon,
	ewcfg.poi_id_themoon:ewcfg.poi_id_thevoid
}

world_events = [
	EwEventDef(
		event_type = ewcfg.event_type_slimeglob,
		str_event_start = "You mined an extra big glob of slime! {}".format(ewcfg.emote_slime1),
	),
	EwEventDef(
		event_type = ewcfg.event_type_slimefrenzy,
		str_event_start = "You hit a dense vein of slime! Double slimegain for the next 30 seconds.",
		str_event_end = "The double slime vein dried up.",
	),
	EwEventDef(
		event_type = ewcfg.event_type_poudrinfrenzy,
		str_event_start = "You hit a dense vein of poudrins! Guaranteed poudrin on every {} for the next 5 seconds.".format(ewcfg.cmd_mine),
		str_event_end = "The poudrin vein dried up.",
	),
	EwEventDef(
		event_type = ewcfg.event_type_minecollapse,
		str_event_start = "The mineshaft starts collapsing around you.\nGet out of there quickly! ({cmd} {captcha})",
	),
	EwEventDef(
		event_type = ewcfg.event_type_voidhole,
		str_event_start = "You hit a sudden gap in the stone, with a scary looking drop. You see what looks like a trampoline on a building's roof at the bottom. Do you **{}** in?".format(ewcfg.cmd_jump),
		str_event_end = "The wall collapses.",
	),
	EwEventDef(
		event_type = ewcfg.event_type_shambaquarium,
		str_event_start = "Holy. Fucking. SHIT. You spot some brainz. Grab 'em all with **{}** {} before they get washed away by the current!",
		str_event_end = "The brainz drift away into the endless expanse of the Slime Sea. Cringe.",
	),
]

event_type_to_def = {}

for event in world_events:
	event_type_to_def[event.event_type] = event

dungeon_tutorial = [
	#00
	EwDungeonScene(
		text = "You're fucked.\n\nYou'd been dreaming of the day when you'd finally get your hands on some **SLIME**," \
			   " the most precious resource in New Los Angeles City, aka Neo Milwaukee (NLACakaNM).\n\nAs a humble, " \
			   "pitiful Juvenile, or Juvie as they say on the mean streets, it seemed like a pipe dream. Then one day, " \
			   "it happened: you saw a molotov cocktail blow open the hull of a SLIMECORP™ Freight Unit, sending barrels " \
			   "of sweet, beautiful SLIME rolling out across the pavement. You grabbed the first one you could lay your " \
			   "hands on and bolted.\n\nIt was more slime than you'd ever seen before in your wretched Juvie life. But " \
			   "it was not to last. SLIMECORP™ has eyes everywhere. It wasn't long before a SLIMECORP™ death squad kicked " \
			   "in your door, recovered their stolen assets, and burned your whole place to the ground.\n\nTale as old as " \
			   "time.\n\nAs for you, they dumped you in this run-down facility in downtown NLACakaNM called the Detention " \
			   "Center. Supposedly it exists to re-educate wayward youths like yourself on how to be productive citizens. " \
			   "*BARF*\n\nSome guy in a suit brought you to an empty classroom and handcuffed you to a desk. That was like " \
			   "seven hours ago.",
		options = {"escape": 2, "suicide": 3,"wait": 4},
		poi = ewcfg.poi_id_tutorial_classroom,
		life_state = ewcfg.life_state_juvenile,
	),
	#01
	EwDungeonScene(
		text = "Defeated, you reunite your ghost with your body. Alas, death is not the end in NLACakaNM.\n\nAlive " \
			   "once more, the man puts his stogie out and grabs you. He drags you to a new empty classroom, " \
			   "handcuffs you to a new desk, and promptly leaves.",
		options = {"escape": 2, "suicide": 3,"wait": 4},
		poi = ewcfg.poi_id_tutorial_classroom,
		life_state = ewcfg.life_state_juvenile,

	),
	#02
	EwDungeonScene(
		text = "You yank on the handcuffs that hold you to the desk. Being rusted and eroded from years of radiation " \
			   "exposure, the chain snaps instantly. You're free.\n\nYou have two possible routes of escape: the door " \
			   "that you came in through which leads to a hallway, or the window which leads to a courtyard.",
		options = {"goto door": 8, "goto window": 9},
		poi = ewcfg.poi_id_tutorial_classroom,
		life_state = ewcfg.life_state_juvenile,

	),
	#03
	EwDungeonScene(
		text = "You fumble inside the desk and find exactly what you need: a pencil.\n\nYou stab the pencil into " \
			   "the desk so it's standing up straight. You're pretty sure you saw this in a movie once.\n\nWith " \
			   "all your might, you slam your head onto the desk. The pencil has disappeared! Congratulations, you " \
			   "are dead.\n\nHowever, before your ghost can make its way out of the room, a guy in a SLIMECORP™ " \
			   "jumpsuit with a bizarre-looking machine on his back kicks in the door and blasts you with some kind " \
			   "of energy beam, then traps you in a little ghost-box.\n\nHe grabs your body and drags it out of the " \
			   "room, down a series of hallways and several escalators, into a dark room full of boilers and pipes, " \
			   "and one large vat containing a phosphorescent green fluid. He tosses your body, and the box containing " \
			   "your ghost, into the vat, where they land with a SPLOOSH. Then he sits down in a nearby chair and " \
			   "lights up a fat SLIMECORP™-brand cigar.",
		options = {"revive": 1, "wait": 10},
		poi = ewcfg.poi_id_tutorial_ghostcontainment,
		life_state = ewcfg.life_state_corpse,

	),
	#04
	EwDungeonScene(
		text = "You sit and wait for the authorities to decide your fate like a well-behaved little Juvie." \
			   "\n\nYou wait for another hour. Nothing happens.",
		options = {"escape": 2, "suicide": 3,"wait": 5},
		poi = ewcfg.poi_id_tutorial_classroom,
		life_state = ewcfg.life_state_juvenile,

	),
	#05
	EwDungeonScene(
		text = "You sit and wait for the authorities to decide your fate like a well-behaved little Juvie." \
			   "\n\nYou wait for another hour. Still, nothing happens.",
		options = {"escape": 2, "suicide": 3,"wait": 6},
		poi = ewcfg.poi_id_tutorial_classroom,
		life_state = ewcfg.life_state_juvenile,

	),
	#06
	EwDungeonScene(
		text = "You sit and wait for the authorities to decide your fate like a well-behaved little Juvie.\n\n" \
			   "You wait for another hour. You begin to hear a faint commotion through the door. There are " \
			   "distant voices yelling in the hallway outside.",
		options = {"escape": 2, "suicide": 3,"wait": 7},
		poi = ewcfg.poi_id_tutorial_classroom,
		life_state = ewcfg.life_state_juvenile,

	),
	#07
	EwDungeonScene(
		text = "You wait and listen, trying to discern what's going on in the hallway.\n\nThe voices grow louder. " \
			   "You begin to discern more clearly... there are voices frantically shouting, mostly voices that " \
			   "sound like Juvies your age, but some strangely inhuman.\n\nSuddenly you hear gunshots.\n\nA " \
			   "deafening fury erupts as you hear from the hallway a hail of gunfire and the clanging of metal." \
			   "\n\nA sudden explosion demolishes the classroom wall and sends you flying. The desk you were " \
			   "handcuffed to is smashed apart... you're free!\n\nYou have two possible routes of escape: the " \
			   "hole blown in the wall which leads out to the hallway, or the window which leads to a courtyard.",
		options = {"goto hole": 11, "goto window": 9},
		poi = ewcfg.poi_id_tutorial_classroom,
		life_state = ewcfg.life_state_juvenile,

	),
	#08
	EwDungeonScene(
		text = "You go to the door and open it. You step out into the hallway. It is completely empty. " \
			   "You can make out faint voices shouting in the distance.",
		options = {"goto left": 12, "goto right": 12},
		poi = ewcfg.poi_id_tutorial_hallway,
		life_state = ewcfg.life_state_juvenile,

	),
	#09
	EwDungeonScene(
		text = "You make for the window. It slides open easily and you jump out into the courtyard. " \
			   "The grass here is completely dry and dead. A few faintly glowing green thorny weeds " \
			   "grow in patches here and there. Across the lawn you see a high chain-link fence " \
			   "topped with barbed wire. You break into a run hoping to hop the fence and escape.\n\n" \
			   "You make it about 20 feet from the window before a gun turret mounted on the Detention " \
			   "Center roof gets a clear shot at you. A torrent of bullets rips through you and you " \
			   "fall to the ground, directly onto one of the many, many landmines buried here. The " \
			   "explosion blows your body into meaty chunks, and the force is to powerful that even " \
			   "your ghost is knocked unconscious.\n\nWhen you regain consciousness, you realize that" \
			   " you are contained in a tiny ghost-box that's floating in a vat of phosphorescent green " \
			   "fluid along with a collection of bloody meat-chunks that are presumably what's left of " \
			   "your body. Across the dark room, a man in a SLIMECORP™ jumpsuit sits and smokes a " \
			   "SLIMECORP™-brand cigar, apparently waiting for something.",
		options = {"revive": 1, "wait": 10},
		poi = ewcfg.poi_id_tutorial_ghostcontainment,
		life_state = ewcfg.life_state_corpse,

	),
	#10
	EwDungeonScene(
		text = "You and your body float in the glowing green liquid. Nothing happens.",
		options = {"revive": 1, "wait": 10},
		poi = ewcfg.poi_id_tutorial_ghostcontainment,
		life_state = ewcfg.life_state_corpse,

	),
	# 11
	EwDungeonScene(
		text="You peer through the charred hole in the classroom wall and into the hallway.",
		options={"proceed": 15},
		poi = ewcfg.poi_id_tutorial_hallway,
		life_state = ewcfg.life_state_juvenile,

	),
	# 12
	EwDungeonScene(
		text="You make your way down the hallway, hoping to find an exit. The shouting voices grow louder."
			 "\n\nYou come to a split in the hallway. You can go left or right.",
		options={"goto left": 13, "goto right": 13},
		poi = ewcfg.poi_id_tutorial_hallway,
		life_state = ewcfg.life_state_juvenile,

	),
	# 13
	EwDungeonScene(
		text="You make your way down the hallway, hoping to find an exit. The shouting voices grow even "
			 "louder.\n\nYou come to another split. Left or right?",
		options={"goto left": 14, "goto right": 14},
		poi = ewcfg.poi_id_tutorial_hallway,
		life_state = ewcfg.life_state_juvenile,

	),
	# 14
	EwDungeonScene(
		text="You make your way down the hallway, hoping to find an exit.\n\nAs you come to the next "
			 "split in the hallway, a gunshot rings out. Suddenly, there is an explosion of noise as "
			 "more and more guns fire, and you hear the clang of metal against metal.",
		options={"proceed": 15},
		poi = ewcfg.poi_id_tutorial_hallway,
		life_state = ewcfg.life_state_juvenile,

	),
	# 15
	EwDungeonScene(
		text="It looks like a fucking war has erupted. Bullets are flying through the air and bodies, blood, " \
			 "and slime are all smeared across the floor and the walls.\n\nDown the hallway in both directions " \
			 "are groups of people waging what you now realize must be GANG WARFARE. These must be gang " \
			 "members here to capture some territory for their KINGPINS.\n\nTo your right, a throng of terrifying " \
			 "freaks in pink gleefully !thrash about, swinging spiked bats and firing automatic weapons with " \
			 "wild abandon. You've heard about them... the deadly ROWDYS.\n\nTo your left, a shadowy mass of " \
			 "sinister-looking purple-clad ne'er-do-wells !dab defiantly in the face of death, blades and guns " \
			 "gleaming in the fluorescent light. These must be the dreaded KILLERS.\n\nAnd in the middle, " \
			 "where the two gangs meet, weapons clash and bodies are smashed open, slime splattering everywhere " \
			 "as the death count rises.\n\nA little bit gets on you. It feels good.",
		options={"scavenge": 16, "kill": 17, "goto left": 18, "goto right": 19},
		poi = ewcfg.poi_id_tutorial_hallway,
		life_state = ewcfg.life_state_juvenile,

	),
	# 16
	EwDungeonScene(
		text="You surreptitiously try to scrape up as much of the dropped slime as you can without " \
			 "alerting the gang members to your presence. It's not much, but you stuff what little " \
			 "you can gather into your pockets.\n\nGod you fucking love slime so much.",
		options={"scavenge": 16, "kill": 17, "goto left": 18, "goto right": 19},
		poi = ewcfg.poi_id_tutorial_hallway,
		life_state = ewcfg.life_state_juvenile,

	),
	# 17
	EwDungeonScene(
		text="You itch to get in on the action. But unfortunately, you're still a mere Juvenile. " \
			 "Violence is simply beyond your capability... for now.\n\nYou make a mental note to " \
			 "!enlist in a gang at the first possible opportunity. You'll need to escape the " \
			 "Detention Center first though, and get some slime.",
		options={"scavenge": 16, "kill": 17, "goto left": 18, "goto right": 19},
		poi = ewcfg.poi_id_tutorial_hallway,
		life_state = ewcfg.life_state_juvenile,

	),
	# 18
	EwDungeonScene(
		text="You're certain any individual member of either side of this conflict could obliterate " \
				"you with a mere thought. With no safe options available, you decide to make a break " \
				"for it to the left, through the ranks of the KILLERS.\n\nYou sprint down the hall " \
				"and pray that none of the whizzing bullets connect with your tender and slimeless Juvie " \
				"body.\n\nReaching the Killer front lines, you make a running leap. A curved scythe " \
				"blade that you think must be sharp enough to split atoms whizzes millimeters above " \
				"your head.\n\nMiraculously, you land still intact on the other side of the Killers, who " \
				"pay you no further mind. You break into a run.\n\nYou run through through hallway after " \
				"hallway riddled with the burned craters and bullet holes left in the wake of the Killers. " \
				"Purple graffiti is scrawled on the walls everywhere. \"!DAB\" is written over and over, " \
				"along with the occasional \"ROWDYS IS BUSTAHS\", drawings of bizarre slimy-looking creatures, " \
				"and pictures of a hooded man in a beanie accompanied by the message \"FOR THE COP KILLER\".\n\n" \
				"This \"Cop Killer\" must be a pretty cool guy, you decide.\n\nAt last, when you're nearing " \
				"exhaustion, you come to a large burnt hole in the wall that leads outside. The Killers must " \
				"have blown the wall open to make their assault.\n\nCould it be? Sweet freedom at last??",
		options={"escape": 20},
		poi = ewcfg.poi_id_tutorial_hallway,
		life_state = ewcfg.life_state_juvenile,

	),
	# 19
	EwDungeonScene(
		text="You're certain any individual member of either side of this conflict could obliterate " \
			"you with a mere thought. With no safe options available, you decide to make a break for " \
			"it to the right, through the ranks of the ROWDYS.\n\nYou sprint down the hall and pray " \
			"that none of the whizzing bullets connect with your tender and slimeless Juvie body.\n\n" \
			"Reaching the Rowdy front lines, you make a running leap. A wildly swung nun-chuck packing " \
			"the force of an eighteen-wheeler whizzes millimeters above your head.\n\nMiraculously, " \
			"you land still intact on the other side of the Rowdys, who pay you no further mind. You " \
			"break into a run.\n\nYou run through through hallway after hallway riddled with the burned " \
			"craters and bullet holes left in the wake of the Rowdys. Pink graffiti is scrawled on the " \
			"walls everywhere. \"!THRASH\" is written over and over, along with the occasional \"KILLERS " \
			"GET FUCKED\", drawings of bizarre slimy-looking creatures, and pictures of a man in a " \
			"jester's cap accompanied by the message \"FOR THE ROWDY FUCKER\".\n\nThis \"Rowdy Fucker\" " \
			"must be a pretty cool guy, you decide.\n\nAt last, when you're nearing exhaustion, you come " \
			"to a large burnt hole in the wall that leads outside. The Rowdys must have blown the wall " \
			"open to make their assault.\n\nCould it be? Sweet freedom at last??",
		options={"escape": 20},
		poi = ewcfg.poi_id_tutorial_hallway,
		life_state = ewcfg.life_state_juvenile,

	),
	# 20
	EwDungeonScene(
		text="You exit through the hole in the wall into the front parking lot of the Detention " \
				"Center. Behind you you can still hear screams and gunshots echoing through the halls." \
				"\n\nMoving quickly, you sprint across the parking lot, lest some SLIMECORP™ security " \
				"camera alert a guard to your presence. Fortunately, it seems that all available Detention " \
				"Center personel are dealing with the Gang Warfare currently raging inside.\n\nUpon " \
				"reaching the high chain link fence encircling the facility, you find that a large hole " \
				"has been torn open in it, through which you quickly make your escape.\n\nYou take a " \
				"moment to survey the scene before you. Downtown NLACakaNM bustles and hums with activity " \
				"and you hear the familiar clicking of the Geiger Counters on every street corner. Over " \
				"the skyline you see it... the towering green obelisk, ENDLESS WAR. Taker of Life, " \
				"Bringer of Slime. Your heart swells with pride and your eyes flood with tears at the " \
				"sight of His glory.\n\nBehind you, SLIMECORP™ helicopters circle overhead. You know " \
				"what that means. Things are about to get hot. Time to skedaddle.\n\nYou leave the " \
				"Detention Center and head into Downtown.\n\nIt's time to resume your life in NLACakaNM.",
		dungeon_state = False,
		poi = ewcfg.poi_id_downtown,
		life_state = ewcfg.life_state_juvenile,

	),
]

