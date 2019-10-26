import ewutils
from ewcfg import cmd_prefix

class EwDungeonScene:

    # The text sent when a scene starts
    text = ""

    # Whether or not the dungeon is active
    dungeon_state = True

    # Commands that can be used in a scene, and what scene ID that leads to
    options = {}

    def __init__(
            self,
            text="",
            dungeon_state=True,
            options={},
    ):
        self.text = text
        self.dungeon_state = dungeon_state
        self.options = options


dungeon_01 = [
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
        options = {"escape": 2, "suicide": 3,"wait": 4}
    ),
    #01
    EwDungeonScene(
        text = "Defeated, you reunite your ghost with your body. Alas, death is not the end in NLACakaNM.\n\nAlive " \
               "once more, the man puts his stogie out and grabs you. He drags you to a new empty classroom, " \
               "handcuffs you to a new desk, and promptly leaves.",
        options = {"escape": 2, "suicide": 3,"wait": 4}
    ),
    #02
    EwDungeonScene(
        text = "You yank on the handcuffs that hold you to the desk. Being rusted and eroded from years of radiation " \
               "exposure, the chain snaps instantly. You're free.\n\nYou have two possible routes of escape: the door " \
               "that you came in through which leads to a hallway, or the window which leads to a courtyard.",
        options = {"goto door": 8, "goto window": 9}
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
        options = {"revive": 1, "wait": 10}
    ),
    #04
    EwDungeonScene(
        text = "You sit and wait for the authorities to decide your fate like a well-behaved little Juvie." \
               "\n\nYou wait for another hour. Nothing happens.",
        options = {"escape": 2, "suicide": 3,"wait": 5}
    ),
    #05
    EwDungeonScene(
        text = "You sit and wait for the authorities to decide your fate like a well-behaved little Juvie." \
               "\n\nYou wait for another hour. Still, nothing happens.",
        options = {"escape": 2, "suicide": 3,"wait": 6}
    ),
    #06
    EwDungeonScene(
        text = "You sit and wait for the authorities to decide your fate like a well-behaved little Juvie.\n\n" \
               "You wait for another hour. You begin to hear a faint commotion through the door. There are " \
               "distant voices yelling in the hallway outside.",
        options = {"escape": 2, "suicide": 3,"wait": 7}
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
        options = {"goto hole": 11, "goto window": 9}
    ),
    #08
    EwDungeonScene(
        text = "You go to the door and open it. You step out into the hallway. It is completely empty. " \
               "You can make out faint voices shouting in the distance.",
        options = {"goto left": 12, "goto right": 12}
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
        options = {"revive": 1, "wait": 10}
    ),
    #10
    EwDungeonScene(
        text = "You and your body float in the glowing green liquid. Nothing happens.",
        options = {"revive": 1, "wait": 10}
    ),
    # 11
    EwDungeonScene(
        text="You peer through the charred hole in the classroom wall and into the hallway.",
        options={"proceed": 15}
    ),
    # 12
    EwDungeonScene(
        text="You make your way down the hallway, hoping to find an exit. The shouting voices grow louder."
             "\n\nYou come to a split in the hallway. You can go left or right.",
        options={"goto left": 13, "goto right": 13}
    ),
    # 13
    EwDungeonScene(
        text="You make your way down the hallway, hoping to find an exit. The shouting voices grow even "
             "louder.\n\nYou come to another split. Left or right?",
        options={"goto left": 14, "goto right": 14}
    ),
    # 14
    EwDungeonScene(
        text="You make your way down the hallway, hoping to find an exit.\n\nAs you come to the next "
             "split in the hallway, a gunshot rings out. Suddenly, there is an explosion of noise as "
             "more and more guns fire, and you hear the clang of metal against metal.",
        options={"proceed": 15}
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
        options={"scavenge": 16, "kill": 17, "goto left": 18, "goto right": 19}
    ),
    # 16
    EwDungeonScene(
        text="You surreptitiously try to scrape up as much of the dropped slime as you can without " \
             "alerting the gang members to your presence. It's not much, but you stuff what little " \
             "you can gather into your pockets.\n\nGod you fucking love slime so much.",
        options={"scavenge": 16, "kill": 17, "goto left": 18, "goto right": 19}
    ),
    # 17
    EwDungeonScene(
        text="You itch to get in on the action. But unfortunately, you're still a mere Juvenile. " \
             "Violence is simply beyond your capability... for now.\n\nYou make a mental note to " \
             "!enlist in a gang at the first possible opportunity. You'll need to escape the " \
             "Detention Center first though, and get some slime.",
        options={"scavenge": 16, "kill": 17, "goto left": 18, "goto right": 19}
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
        options={"escape": 21}
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
        options={"escape": 21}
    ),
    # 20
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
        options={"escape": 21}
    ),
    # 21
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
        dungeon_state = False
    ),
]

async def dungeon_test(cmd):
    response = "Starting tutorial..."
    await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
    dungeon_state = True
    scene_id = 0
    while dungeon_state:
        scene = dungeon_01[scene_id]
        response = scene.text
        if scene.dungeon_state:
            response += "\n\nWhat do you do?\n\n**>options: "
            for path in scene.options.keys():
                response += "!{}, ".format(path)
            response += "**"
            await ewutils.send_message(cmd.client, cmd.message.author, ewutils.formatMessage(cmd.message.author, response))
            try:
		msg = await cmd.client.wait_for_message(timeout = 120, author = member, check = check)

		if msg != None:
		    if message.content[1:] in scene.options.keys():
			scene_id = scene.options
		    else:
                        response = "You can't do that."
                        await ewutils.send_message(cmd.client, cmd.message.author, ewutils.formatMessage(cmd.message.author, response))
                    continue
            except:
		return
