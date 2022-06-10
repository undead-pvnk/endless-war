from . import cfg as ewcfg

from ..model.weather import EwWeather

# All weather effects in the game.
weather_list = [
    EwWeather(
        name=ewcfg.weather_sunny,
        sunrise="The smog is beginning to clear in the sickly morning sunlight.",
        day="The sun is blazing on the cracked streets, making the air shimmer.",
        sunset="The sky is darkening, the low clouds an iridescent orange.",
        night_new="Stars pierce through the atmosphere as factories belch smoke all through the night.",
        night_waxing_start="The moon's horns pierce through the sky as factories belch smoke all through the night.",
        night_waxing_end="The moon's maw crunches through the sky as factories belch smoke all through the night.",
        night_full="The crescent moon looms yellow as factories belch smoke all through the night.",
        night_waning_start="The moon's mandibles gnash through the sky as factories belch smoke all through the night.",
        night_waning_end="A curved sliver of the moon scratches the sky as factories belch smoke all through the night.",
        night_special="Factories are illuminated green as the eerie moon casts its glow through the night sky."
    ),
    EwWeather(
        name=ewcfg.weather_rainy,
        sunrise="Rain gently beats against the pavement as the sky starts to lighten.",
        day="Rain pours down, collecting in oily rivers that run down sewer drains.",
        sunset="Distant thunder rumbles as it rains, the sky now growing dark.",
        night_new="Silverish clouds coat the sky, and the night is black in the heavy rain.",
        night_waxing_start="Silverish clouds hide the moon's horns, and the night is black in the heavy rain.",
        night_waxing_end="Silverish clouds hide the moon's maw, and the night is black in the heavy rain.",
        night_full="Silverish clouds hide the crescent moon, and the night is black in the heavy rain.",
        night_waning_start="Silverish clouds hide the moon's mandibles, and the night is black in the heavy rain.",
        night_waning_end="Silverish clouds hide a sliver of the moon, and the night is black in the heavy rain.",
        night_special="Pearlescent clouds coat the sky, the olive rain a pule from the dim green moon."
    ),
    EwWeather(
        name=ewcfg.weather_windy,
        sunrise="Wind whips through the city streets as the sun crests over the horizon.",
        day="Paper and debris are whipped through the city streets by the winds, buffetting pedestrians.",
        sunset="The few trees in the city bend and strain in the wind as the sun slowly sets.",
        night_new="The dark streets howl, battering apartment windows with vicious night winds.",
        night_waxing_start="The dark streets howl, battering apartment windows with vicious night winds.",
        night_waxing_end="The dark streets howl, battering apartment windows with vicious night winds.",
        night_full="The night winds tumble through the sky, spinning the crescent moon on its axis.",
        night_waning_start="The dark streets howl, battering apartment windows with vicious night winds.",
        night_waning_end="The dark streets howl, battering apartment windows with vicious night winds.",
        night_special="The otherworldly green landscape is being torn away by the night winds."
    ),
    EwWeather(
        name=ewcfg.weather_lightning,
        sunrise="An ill-omened morning dawns as lighting streaks across the sky in the sunrise.",
        day="Flashes of bright lightning and peals of thunder periodically startle the citizens out of their usual stupor.",
        sunset="Bluish white arcs of electricity tear through the dusky, deep-red sky.",
        night_new="The dark night periodically lights with bright whitish-green bolts that flash off the metal and glass of skyscrapers.",
        night_waxing_start="The horns of the moon send off destructive bolts that flash off the metal and glass of skyscrapers.",
        night_waxing_end="The dark night periodically lights with bright whitish-green bolts that seem to erupt from the moon's open maw.",
        night_full="The dark night periodically lights with bright whitish-green bolts that curve around the cleaving sickle of the crescent moon .",
        night_waning_start="The dark night periodically crunches with bright whitish-green bolts that flash off the metal and glass of skyscrapers.",
        night_waning_end="The dark night is periodically pierced by bright whitish-green bolts, framing the sliver of the moon.",
        night_special="Skyscrapers stand jade as sparks fly freely through the air from occasional bolts crashing into the ground."
    ),
    EwWeather(
        name=ewcfg.weather_cloudy,
        sunrise="The dim morning light spreads timidly across the thickly clouded sky.",
        day="The air hangs thick, and the pavement is damp with mist from the clouds overhead.",
        sunset="The dusky light blares angry red on a sky choked with clouds and smog.",
        night_new="Everything is black and still but the roiling clouds, reflecting the city's eerie light.",
        night_waxing_start="Everything is dark and still but the roiling clouds, reflecting the city's eerie light.",
        night_waxing_end="Everything is dark and still but the roiling clouds, reflecting the city's eerie light.",
        night_full="Everything is dim and still but the roiling clouds, reflecting the city's eerie light. A single gap reveals the grand crescent moon above.",
        night_waning_start="Everything is dark and still but the roiling clouds, reflecting the city's eerie light.",
        night_waning_end="Everything is dark and still but the roiling clouds, reflecting the city's eerie light.",
        night_special="Everything is dark and still but the roiling clouds, reflecting the city's eerie light. A single gap streams chartreuse light from the the dim green moon above."
    ),
    EwWeather(
        name=ewcfg.weather_snow,
        sunrise="The morning sun glints off the thin layer of powdery snow that blankets the city.",
        day="Flakes of snow clump together and whip through the bitter cold air in the winter wind.",
        sunset="The chilly air grows colder as the sky darkens and snow piles higher in the streets.",
        night_new="Icy winds whip through the city, white snowflakes glittering in the black of night.",
        night_waxing_start="Horns of ice fall from the night sky, piercing directly into pedestrians' skulls.",
        night_waxing_end="Flurries of snow sweep garbage off the street as the moon's gaping maw hangs above.",
        night_full="The crescent moon illuminates the still snowy night. Sparse snowflakes blanket the quiet city streets.",
        night_waning_start="The streets are covered with thick sheets of sleet, covered with a light blanket of snow.",
        night_waning_end="Icy winds whip through the city, white snowflakes glittering from the sliver of moonlight.",
        night_special="Verdigris snow streams through open windows as the green moon casts its dim glow."
    ),
    EwWeather(
        name=ewcfg.weather_foggy,
        sunrise="Fog hangs thick in the air, stubbornly refusing to dissipate as the sun clears the horizon.",
        day="You can barely see to the next block in the sickly greenish NLACakaNM smog.",
        sunset="Visibility only grows worse in the fog as the sun sets and the daylight fades.",
        night_new="Everything is obscured by the darkness of night and the thick city smog.",
        night_waxing_start="Everything is obscured by the darkness of night and the thick city smog.",
        night_waxing_end="Everything is obscured by the darkness of night and the thick city smog.",
        night_full="The only things visible from the thick fog are ENDLESS WAR and the crescent moon directly above.",
        night_waning_start="Everything is obscured by the darkness of night and the thick city smog.",
        night_waning_end="Everything is obscured by the darkness of night and the thick city smog.",
        night_special="The glowing-green night casts a haze unpierceable."
    ),
    # EwWeather(
    #  	name = ewcfg.weather_bicarbonaterain,
    #  	sunrise = "Accursed bicarbonate soda and sugar rain blocks out the morning sun.",
    #  	day = "The bicarbonate rain won't let up. Thank the lord that blue weasel is dead.",
    #  	sunset = "The deadly rain keeps beating down mercilessly. You have a feeling it's going to be a long night.",
    #  	night_new = "Clouds of doom obscure the moon as they dispense liquid death from above.",
    #  	night_waxing_start = "Clouds of doom obscure the moon as they dispense liquid death from above.",
    #  	night_waxing_end = "Clouds of doom obscure the moon as they dispense liquid death from above.",
    #  	night_full = "Clouds of doom obscure the moon as they dispense liquid death from above.",
    #  	night_waning_start = "Clouds of doom obscure the moon as they dispense liquid death from above.",
    #  	night_waning_end = "Clouds of doom obscure the moon as they dispense liquid death from above.",
    #  	night_special = "Clouds of doom obscure the moon as they dispense liquid death from above."
    # ),
]

# A map of name to EwWeather objects.
weather_map = {}
for weather in weather_list:
    weather_map[weather.name] = weather
