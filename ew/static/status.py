from . import cfg as ewcfg

from ..model.status import EwStatusEffectDef


status_effect_list = [
	EwStatusEffectDef(
		id_status = ewcfg.status_burning_id,
		time_expire = ewcfg.time_expire_burn,
		str_acquire = '{name_player}\'s body is engulfed in flames.',
		str_describe = 'They are burning.',
		str_describe_self = 'You are burning.'
	),
	EwStatusEffectDef(
		id_status = ewcfg.status_acid_id,
		time_expire = ewcfg.time_expire_burn,
		str_acquire = '{name_player}\'s body is drenched in acid.',
		str_describe = 'Their body is being melted down by acid.',
		str_describe_self = 'Your body is being melted down by acid.'
	),
	EwStatusEffectDef(
		id_status = ewcfg.status_spored_id,
		time_expire = ewcfg.time_expire_burn,
		str_acquire = '{name_player}\'s body is riddled with spores.',
		str_describe = 'Their body is being consumed by spores.',
		str_describe_self = 'Your body is being consumed by spores.'
	),
	EwStatusEffectDef(
		id_status = ewcfg.status_badtrip_id,
		time_expire = 5,
		str_acquire = '{name_player} begins to suffer from a bad trip.',
		str_describe = 'They are suffering from the effects of a bad trip.',
		str_describe_self = 'You are suffering from a bad trip.'
	),
	EwStatusEffectDef(
		id_status = ewcfg.status_stoned_id,
		time_expire = 30,
		str_acquire = '{name_player} starts to get stoned as fuck, brooooo.',
		str_describe = 'Their movements are sluggish and weak due to being stoned.',
		str_describe_self = 'Your movements are sluggish and weak due to being stoned.'
	),
	EwStatusEffectDef(
		id_status = ewcfg.status_baked_id,
		time_expire = 30,
		str_acquire = '{name_player} has become absolutely *baked!*',
		str_describe = 'They can barely move a muscle due to how fucking baked they are.',
		str_describe_self = 'You can barely move a muscle due to how fucking baked you are.'
	),
	EwStatusEffectDef(
		id_status = ewcfg.status_ghostbust_id,
		time_expire = 86400,
		str_describe_self = 'The coleslaw in your stomach allows you to bust ghosts.'
	),
	EwStatusEffectDef(
		id_status = ewcfg.status_strangled_id,
		time_expire = 5,
		str_describe = 'They are being strangled.'
	),
	EwStatusEffectDef(
		id_status = ewcfg.status_stunned_id,
		str_describe = 'They are stunned.'
	),
	EwStatusEffectDef(
		id_status = ewcfg.status_repelled_id,
		time_expire = ewcfg.time_expire_repel_base,
		str_acquire = 'You spray yourself with the FUCK ENERGY Body Spray.',
		str_describe = 'They smell like shit, much to the displeasure of slime beasts.',
		str_describe_self = 'You smell like shit, much to the displeasure of slime beasts.'
	),
	EwStatusEffectDef(
		id_status = ewcfg.status_repelaftereffects_id,
		time_expire = 2,
		str_acquire = 'You try and shake off the body spray, but its stench still lingers, if only for a brief moment.',
		str_describe = 'Their surroundings give off a slightly foul odor.',
		str_describe_self = 'Your surroundings give off a slightly foul odor.'
	),
	EwStatusEffectDef(
		id_status = ewcfg.status_high_id,
		time_expire = ewcfg.time_expire_high,
		str_describe = "They are as high as a kite.",
		str_describe_self = "You are as high as a kite."
	),
	EwStatusEffectDef(
		id_status = ewcfg.status_evasive_id,
		time_expire = 10,
		str_describe = "They have assumed an evasive stance.",
		str_describe_self = "You have assumed an evasive stance.",
		hit_chance_mod = -0.25
	),
	EwStatusEffectDef(
		id_status = ewcfg.status_taunted_id,
		time_expire = 10,
		str_describe = "They are fuming with rage.",
		str_describe_self = "You are fuming with rage.",
		hit_chance_mod_self = -0.25
	),
	EwStatusEffectDef(
		id_status = ewcfg.status_aiming_id,
		time_expire = 10,
		str_describe = "They are taking careful aim.",
		str_describe_self = "You are taking careful aim.",
		hit_chance_mod_self = 0.1,
		crit_mod_self = 0.2
	),
	EwStatusEffectDef(
		id_status = ewcfg.status_sapfatigue_id,
		time_expire = 60,
		str_describe = "They are suffering from sap fatigue.",
		str_describe_self = "You are suffering from sap fatigue.",
	),
	EwStatusEffectDef(
		id_status = ewcfg.status_rerollfatigue_id,
	),
	EwStatusEffectDef(
		id_status = ewcfg.status_injury_head_id,
		str_describe = "Their head looks {severity}",
		str_describe_self = "Your head looks {severity}",
		hit_chance_mod_self = -0.05,
		crit_mod_self = -0.1,
		hit_chance_mod = 0.01,
		crit_mod = 0.01,
	),
	EwStatusEffectDef(
		id_status = ewcfg.status_injury_torso_id,
		str_describe = "Their torso looks {severity}",
		str_describe_self = "Your torso looks {severity}",
	),
	EwStatusEffectDef(
		id_status = ewcfg.status_injury_arms_id,
		str_describe = "Their arms look {severity}",
		str_describe_self = "Your arms look {severity}",
		hit_chance_mod_self = -0.05,
		crit_mod_self = -0.1,
	),
	EwStatusEffectDef(
		id_status = ewcfg.status_injury_legs_id,
		str_describe = "Their legs look {severity}",
		str_describe_self = "Your legs look {severity}",
		hit_chance_mod = 0.06,
		crit_mod = 0.03,
	),
	EwStatusEffectDef(
		id_status = ewcfg.status_modelovaccine_id,
		time_expire = 86400,
		str_acquire = "You shoot the vaccine but… nothing happens. On the surface, anyway. The vaccine has successfully dissolved throughout your bloodstream, and you will now “cure” all those who come into contact with your pure, righteous slime. Meaning, it’s time to conduct some straight up genocide.",
		str_describe_self = "The modelovirus vaccine running through your veins allows you to cure shamblers!"
	),
    EwStatusEffectDef(
		id_status = ewcfg.status_slapped_id,
		time_expire = 300,
		str_acquire = "You're tuckered out. Better not get slapped for awhile.",
		str_describe_self = "You got ditch slapped recently and are really feeling it."
	),
    EwStatusEffectDef(
		id_status = ewcfg.status_foodcoma_id,
		time_expire = 300,
		str_acquire = "Calorie-induced rage consumes you! You could drink gasoline and get shot and not feel a damn thing!",
		str_describe_self = "You're in the middle of a raging food coma.",
        dmg_mod = -0.4
	),
    EwStatusEffectDef(
		id_status = ewcfg.status_n1,
		time_expire = 86400,
		str_acquire = "",
		str_describe_self = "You are god's gift to malice.",
		str_describe = "He is god's gift to malice.",
        dmg_mod = -0.5,
		dmg_mod_self = 1,
		hit_chance_mod_self = +.2,
		hit_chance_mod = -.35
	),
    EwStatusEffectDef(
		id_status = ewcfg.status_n2,
		time_expire = 86400,
		str_acquire = "",
		str_describe_self = "You shred like nobody's business.",
		str_describe = "They shred like nobody's business.",
        dmg_mod = -0.5,
		hit_chance_mod_self = +.2,
		hit_chance_mod = -.5
	),
    EwStatusEffectDef(
		id_status = ewcfg.status_n4,
		time_expire = 86400,
		str_acquire = "",
		str_describe_self = "Sorry, you can't let them do that.",
		str_describe = "Sorry, they can't let you do this.",
        dmg_mod = -1,
		dmg_mod_self = -.5,
	),
    EwStatusEffectDef(
		id_status = ewcfg.status_n8,
		time_expire = 86400,
		str_acquire = "",
		str_describe_self = "You're itching to move on from this.",
        dmg_mod_self = -0.5,
		dmg_mod = 0.5,
		crit_mod_self = .3
	),
    EwStatusEffectDef(
		id_status = ewcfg.status_n11,
		time_expire = 86400,
		str_acquire = "",
		str_describe_self = "You're feeling like putting your cronies to the test.",
		str_describe = "You're afraid of this guy.",
        dmg_mod = -0.5,
		dmg_mod_self = 0.5,

		crit_mod_self = .5
	),
    EwStatusEffectDef(
		id_status = ewcfg.status_n12,
		time_expire = 86400,
		str_acquire = "",
		str_describe_self = "Time to get nasty.",
		str_describe = "She barely looks human.",
        dmg_mod = -0.5,
		dmg_mod_self = 0.7,
		crit_mod_self = .75
	),
	EwStatusEffectDef(
		id_status=ewcfg.status_n13,
		time_expire=86400,
		str_acquire="",
		str_describe_self="They're really starting to get on your nerves.",
		str_describe= "You're really starting to get on his nerves.",
		dmg_mod=-0.5,
		dmg_mod_self=0.5,
		crit_mod_self=.5
	),

	#EwStatusEffectDef(
	#	id_status = ewcfg.status_juviemode_id,
	#	time_expire = 86400,
	#	str_acquire = "",
	#	str_describe_self = "You're carrying slime under the legal limit."
	#),
	EwStatusEffectDef(
		id_status = ewcfg.status_kevlarattire_id,
		time_expire = 86400,
		str_acquire = "",
		str_describe_self = "You're dressed to the nines in the latest Kevlar work attire.",
		dmg_mod = -0.2
	),
	EwStatusEffectDef(
		id_status = ewcfg.status_hogtied_id,
		str_acquire= "They're tied up like a hog on a summer sunday.",
		str_describe_self= "You're tied up like a hog on a summer sunday."
	),
]

status_effects_def_map = {}

for status in status_effect_list:
	status_effects_def_map[status.id_status] = status

