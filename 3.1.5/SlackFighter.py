import asyncio
from wizwalker.combat import CombatHandler, CombatMember
from wizwalker.memory.memory_objects.enums import DuelPhase
from loguru import logger

HIT_ENCHANTS = ['Strong', 'Giant', 'Monstrous', 'Gargantuan', 'Colossal', 'Epic', 'Keen Eyes', 'Accurate', 'Sniper', 'Unstoppable', 'Extraordinary']
HEAL_ENCHANTS = ['Primordial', 'Radical']
BLADE_ENCHANTS = ['Sharpened Blade']
TRAP_ENCHANTS = ['Potent Trap']
HIT_AURAS = ['Virulence', 'Frenzy', 'Beserk', 'Flawless', 'Infallible', 'Amplify', 'Magnify', 'Vengeance', 'Chastisement', 'Devotion', 'Furnace', 'Galvanic Field', 'Punishment', 'Reliquary', 'Sleet Storm', 'Reinforce', 'Eruption', 'Acrimony', 'Outpouring', 'Apologue', 'Rage', 'Intensify', 'Icewind', 'Recompense', 'Upheaval', 'Quicken']
DEFENSE_AURAS = ['Fortify', 'Brace', 'Bulwark', 'Conviction']
HEAL_AURAS = ['Cycle of Life', 'Mend', 'Renew', 'Empowerment', 'Adapt']
SELECT_SHIELDS = ['Frozen Armor', 'Stun Block', 'Tower Shield', 'Death Shield', 'Life Shield', 'Myth Shield', 'Fire Shield', 'Ice Shield', 'Storm Shield', 'Dream Shield', 'Legend Shield', 'Elemental Shield', 'Spirit Shield', 'Shadow Shield', 'Glacial Shield', 'Volcanic Shield', 'Ether Shield', 'Thermic Shield']
AOE_SHIELDS = ['Legion Shield', 'Mass Tower Shield']
SELECT_BLADES = ['Fireblade', 'Deathblade', 'Iceblade', 'Stormblade', 'Lifeblade', 'Mythblade', 'Balanceblade', 'Precision', 'Dark Pact', 'Shadowblade', 'Elemental Blade', 'Spirit Blade', 'Aegis Deathblade', 'Aegis Mythblade', 'Aegis Lifeblade', 'Aegis Stormblade', 'Aegis Fireblade', 'Aegis Iceblade', 'Aegis Balanceblade']
AOE_BLADES = ['Bladestorm', 'Dragonlance', 'Blade Dance', 'Ion Wind', 'Chromatic Blast']
SELECT_PIERCE = ['Deathspear', 'Lifespear', 'Mythspear', 'Firespear', 'Icespear', 'Stormspear', 'Spirit Spear', 'Elemental Spear', 'Balancespear']
SELECT_TRAPS = ['Hex', 'Curse', 'Spirit Trap', "Elemental Blade", 'Death Trap', 'Life Trap', 'Myth Trap', 'Storm Trap', 'Fire Trap', 'Backdraft', 'Feint', 'Ice Trap']
AOE_TRAPS = ['Mass Death Trap', 'Mass Life Trap', 'Mass Feint', 'Mass Myth Trap', 'Mass Fire Trap', 'Mass Ice Trap', 'Mass Storm Trap', 'Mass Hex', 'Malediction']
GLOBALS = ['Age of Reckoning', 'Astraphobia', 'Balance of Power', 'Balefrost', 'Circle of Thorns', 'Combustion', 'Counterforce', 'Darkwind', 'Deadzone', 'Doom and Gloom', 'Elemental Surge', 'Katabatic Wind', 'Namaste', 'Power Play', 'Saga of Heroes', 'Sanctuary', 'Spiritual Attunement', 'Time of Legend', 'Tide of Battle', 'Wyldfire', 'Elemental Surge']
SELECT_DOTS = ['Link', 'Power Link', 'Inferno Salamander', 'Burning Rampage', 'Heck Hound', 'Wrath of Hades', 'Storm Hound', 'Frost Hound', 'Thunderstorm', 'Avenging Fossil', 'Frostbite', 'Spinysaur', 'Lightning Elf', 'Basilisk', 'Poison', 'Skeletal Dragon']
SELECT_HITS = ['Death Scarab', 'Immolate', 'Efreet', 'King Artorius', 'Scion of Fire', "S'more Machine", 'Fire from Above', 'Sun Serpent', 'Brimstone Revenant', 'Hephaestus', 'Krampus', 'Nautilus Unleashed', 'Fire Cat', 'Fire Elf', 'Sunbird', 'Phoenix', 'Naphtha Scarab', 'Elemental Golem', 'Spirit Golem', 'Dream Golem', 'Ether Golem', 'Legend Golem', 'Volcanic Golem', 'Thermic Golem', 'Glacial Golem', 'Helephant', 'Frost Beetle', 'Snow Serpent', 'Evil Snowman', 'Ice Wyvern', 'Thieving Dragon', 'Colossus', 'Angry Snowpig', 'Handsome Fomori', 'Winter Moon', 'Woolly Mammoth', 'Lord of Winter', 'Abominable Weaver', 'Scion of Ice', 'Shatterhorn', 'Frostfeather', 'Imp', 'Leprechaun', 'Seraph', 'Sacred Charge', 'Centaur', 'Infestation', "Nature's Wrath", 'Goat Monk', 'Luminous Weaver', 'Gnomes!', 'Hungry Caterpillar', 'Grrnadier', 'Thunder Snake', 'Lightning Bats', 'Storm Shark', 'Kraken', 'Stormzilla', 'Stormwing', 'Triton', 'Catalan', 'Queen Calypso', 'Catch of the Day', 'Hammer of Thor', 'Wild Bolt', 'Insane Bolt', 'Leviathan', 'Storm Owl', 'Scion of Storm', "Rusalka's Wrath", 'Thunderman', 'Blood Bat', 'Troll', 'Cyclops', 'Minotaur', 'Vermin Virtuoso', 'Gobbler', 'Athena Battle Sight', 'Keeper of the Flame', 'Ninja Pigs', 'Splashsquatch', 'Medusa', 'Celestial Calendar', 'Scion of Myth', "Witch's House Call", 'Tatzlewurm Terror', 'Dark Sprite', 'Ghoul', 'Banshee', 'Vampire', 'Skeletal Pirate', 'Crimson Phantom', 'Wraith', 'Monster Mash', 'Headless Horseman', 'Lord of Night', "Dr. Von's Monster", 'Winged Sorrow', 'Scion of Death', 'Snack Attack', 'Scarab', 'Scorpion', 'Locust Swarm', 'Spectral Blast', 'Hydra', 'Loremaster', 'Ninja Piglets', 'Samoorai', 'Savage Paw', 'Spiritual Tribunal', 'Judgement', 'Vengeful Seraph', 'Chimera', 'Supernova', 'Mana Burn', 'Sabertooth', 'Gaze of Fate', 'Scion of Balance', 'Mockenspiel', 'Beary Surprise', 'Camp Bandit', 'Obsidian Colossus', 'Grim Reader', 'Dark & Stormy', "Barbarian's Saga", 'Quartermane', 'The Bantam', 'The Shadoe', 'Mandar', 'Dog Tracy', 'Buck Gordon', 'Duck Savage', 'Caldera Jinn', 'Infernal Oni', 'Iceburn Jinn', 'Everwinter Oni', 'Thundering Jinn', 'Turmoil Oni', 'Macabre Jinn', 'Doom Oni', 'Verdurous Jinn', 'Primal Oni', 'Phantastic Jinn', 'Trickster Oni', 'Duststorm Jinn', 'Tribunal Oni', 'Hunting Wyrm', 'Shift Piscean', 'Shift Grendel', 'Shift Rattlebones', 'Shift Greenoak', 'Shift Thornpaw', 'Shift Ogre', 'Shift Dread Paladin', 'Shift Sugar Glider', 'Shift Fire Dwarf', 'Van Der Borst', 'Shift Bunferatu', 'Shift Ghulture', 'Frost Minotaur', 'Deadly Minotaur', 'Lively Minotaur', 'Natural Attack', 'Storm Sweep', 'Cat Scratch', 'Colossal Uppercut', 'Colossus Crunch', 'Cursed Flame', 'Ignite', 'Flame Strike', 'Firestorm', 'Storm Strike', 'Maelstrom', 'Taco Toss', 'Stinky Salute', 'Ice Breaker', 'Ritual Blade', 'Mander Blast', 'Death Ninja Pig', 'Ninja Slice', 'Ninja Slam', 'Thunder Spike', 'Stomp', 'Swipe', 'Wrath of Aquila', 'Wrath of Cronus', 'Wrath of Apollo', 'Wrath of Zeus', 'Wrath of Poseidon', 'Wrath of Ares']
AOE_DOTS = ['Scald', 'Wings of Fate', 'Rain of Fire', 'Fire Dragon', 'Reindeer Knight', 'Snow Angel', 'Deer Knight', 'Iron Curse']
AOE_HITS = ['Colossafrog', 'Raging Bull', 'Meteor Strike', 'Blizzard', 'Snowball Barrage', 'Frost Giant', "Ratatoskr's Spin", 'Forest Lord', 'Tempest', 'Storm Lord', 'Sirens', 'Glowbug Squall', 'Sound of Musicology', 'Humongofrog', 'Earthquake', 'Orthrus', 'Mystic Colossus', 'Ship of Fools', 'Scarecrow', 'Call of Khrulhu', 'Leafstorm', 'Sandstorm', 'Power Nova', 'Ra', 'Nested Fury', 'Squall Wyvern', "Morganthe's Will", 'Steel Giant', 'Lycian Chimera', 'Lernaean Hydra', 'Lord of Atonement', "Morganthe's Venom", 'Eirkur Axebreaker', 'Wildfire Treant', 'Lava Giant', 'Fiery Giant', 'Lava Lord', 'Lord of Blazes', 'Snowball Strike', "Morganthe's Gaze", 'Tundra Lord', "Morganthe's Angst", 'Squall Wyvern', 'Lord of the Squall', "Morganthe's Ardor", 'Enraged Forest Lord', "Morganthe's Requiem", 'Death Seraph', 'Ominous Scarecrow', 'Bonetree Lord', 'Fable Lord', 'Lord Humongofrog', 'Noble Humongofrog', "Morganthe's Deceit", 'Lord of the Jungle', 'Freeze Ray', "Old One's Endgame", 'Blast Off!', 'Lava Giant', 'Lava Lord', 'Snowball Strike']
MINIONS = ['Mander Minion', 'Nerys', 'Spectral Minion', 'Animate', 'Malduit', 'Fire Elemental', 'Sir Lamorak', 'Ice Guardian', 'Freddo', 'Sprite Guardian', 'Sir Bedevere', 'Golem Minion', 'Troll Minion', 'Cyclops Minion', 'Minotaur Minion', 'Talos', 'Vassanji', 'Water Elemental', 'Mokompo']
OFFENSE_SHADOW = ['Shadow Shrike', 'Shadow Trickster']
DEFENSE_SHADOW = ['Shadow Sentinel']
HEAL_SHADOW = ['Shadow Seraph']
SELECT_SHADOW_HITS = ['Ultra Shadowstrike', 'Dark Nova', 'Shadowplume']
AOE_SHADOW_HITS = ['Dark Fiend', 'Dark Shepherd']
DISPELS = ['Quench', 'Melt', 'Dissipate', 'Vaporize', 'Entangle', 'Strangle', 'Unbalance', 'Spirit Defuse', 'Elemental Defuse']
SELECT_HEALS = ['Fairy', 'Dryad', 'Satyr', 'Guardian Spirit', 'Regenerate', 'Scion of Life', 'Minor Blessing', 'Healing Current', 'Sacrifice', 'Helping Hands', 'Availing Hands', "Grendel's Amends", 'Blessing', 'Cleansing Current', 'Gobble']
AOE_HEALS = ['Pixie', 'Unicorn', 'Sprite Swarm', 'Pigsie', 'Rebirth', 'Hamadryad', 'Kiss of Death', 'Helping Hands', 'Availing Hands', 'Cat Nap', 'Restoring Hands']
SELECT_STUNS = ['Freeze', 'Stun']
AOE_STUNS = ['Petrify', 'Choke', 'Blinding Light', 'Blinding Freeze', 'Wall of Smoke', 'Shockwave']
MINION_ENCHANTS = ['Golem: Taunt']
DETONATES = ['Detonate', 'Solomon Crane']
AOE_DETONATES = ['Incindiate']
SELECT_PRISMS = ['Elemental Prism', 'Spirit Prism', 'Death Prism', 'Life Prism', 'Myth Prism', 'Ice Prism', 'Fire Prism', 'Storm Prism']
AOE_PRISMS = ['Mass Elemental Prism', 'Mass Spirit Prism', 'Mass Fire Prism', 'Mass Ice Prism', 'Mass Storm Prism', 'Mass Death Prism', 'Mass Life Prism', 'Mass Myth Prism']
DIVIDE_HITS = ["Qismah's Curse", 'Iron Sultan', 'Sand Wurm', 'Snake Charmer', 'Climcaclysm', 'Scorching Scimitars', 'Lamassu']
AOE_DEBUFFS = ['Plague', 'Virulent Plague', 'Smokescreen', 'Malediction', 'Mass Infection', 'Muzzle']
SELECT_DEBUFFS = ['Weakness', 'Black Mantle', 'Bad Juju', 'Infection', 'Threefold Fever']
SELECT_MINION_UTILITIES = ['Shield Minion', 'Buff Minion', 'Siphon Health', 'Mend Minion', 'Draw Power', 'Dimension Shift', 'Steal Health', 'Sap Health', 'Take Power', 'Draw Health', 'Drain Health', 'Sap Power']
SELECT_PACIFIES = ['Mega Pacify', 'Mega Distract', 'Mega Subdue', 'Mega Soothe', 'Mega Tranquilize', 'Mega Calm']
AOE_PACIFIES = ['Pacify', 'Distract', 'Calm', 'Subdue', 'Soothe', 'Tranquilize']
AOE_TAUNTS = ['Taunt', 'Mega Taunt', 'Provoke']
AOE_POLYMORPHS = ['Polymorph Jaguar', 'Polymorph Gobbler', 'Polymorph Beet', 'Polymorph Carrot', 'Polymorph Cat Bandit', 'Polymorph Colossus', 'Polymorph Disparagus', 'Polymorph Draconian', 'Polymorph Elemental', 'Polymorph Icehorn', 'Polymorph Mander', 'Polymorph Hound', 'Polymorph Ninja', 'Polymorph Peas', 'Polymorph Ptera', 'Polymorph Treant', 'Hatch']
AOE_HEAL_BLADES = ['Guidance', 'Brilliant Light']
SELECT_HEAL_BLADES = ['Guiding Light', 'Precision', 'Guiding Armor']

master_list = [HIT_ENCHANTS, HEAL_ENCHANTS, BLADE_ENCHANTS, TRAP_ENCHANTS, HIT_AURAS, DEFENSE_AURAS, HEAL_AURAS, SELECT_SHIELDS, AOE_SHIELDS, SELECT_BLADES, AOE_BLADES, SELECT_PIERCE, SELECT_TRAPS, AOE_TRAPS, GLOBALS, SELECT_DOTS, SELECT_HITS, AOE_DOTS, AOE_HITS, MINIONS, OFFENSE_SHADOW, DEFENSE_SHADOW, HEAL_SHADOW, SELECT_SHADOW_HITS, AOE_SHADOW_HITS, DISPELS, SELECT_HEALS, AOE_HEALS, SELECT_STUNS, AOE_STUNS, MINION_ENCHANTS, DETONATES, SELECT_PRISMS, AOE_PRISMS, DIVIDE_HITS, AOE_DEBUFFS, SELECT_DEBUFFS, SELECT_MINION_UTILITIES, SELECT_PACIFIES, AOE_PACIFIES, AOE_TAUNTS, AOE_DETONATES, AOE_POLYMORPHS, AOE_HEAL_BLADES, SELECT_HEAL_BLADES]

master_list_expanded = [x for l in master_list for x in l]

# define hitter strategies for each school (SCRAPPED FOR NOW, totally unfinished anyways)
# ice_hitter_strategy = ['AOE Blade', 'Ally Select Blade', 'AOE Trap', 'Enemy Select Trap', 'Enemy Select Stun', 'AOE Stun', 'AOE Global', 'AOE Offensive Shadow Creature','AOE Hit Aura', 'AOE DOT', 'AOE Hit', 'Enemy Select DOT', 'Enemy Select Hit']
# life_hitter_strategy = ['AOE Blade', 'Ally Select Blade', 'AOE Trap', 'Enemy Select Trap', 'Enemy Select Stun', 'AOE Global', 'AOE Offensive Shadow Creature','AOE Hit Aura', 'AOE DOT', 'AOE Hit', 'Enemy Select DOT', 'Enemy Select Hit']
# myth_hitter_strategy = ['AOE Minion', 'AOE Blade','Ally Select Blade', 'AOE Trap', 'Enemy Select Trap', 'Enemy Select Stun', 'AOE Stun', 'AOE Global', 'AOE Offensive Shadow Creature','AOE Hit Aura', 'AOE DOT', 'AOE Hit', 'Enemy Select DOT', 'Enemy Select Hit']
# death_hitter_strategy = []
# balance_hitter_strategy = ['AOE Hit', 'AOE DOT', 'Enemy Select DOT', 'Enemy Select Hit', 'AOE Blade', 'Ally Select Blade', 'Ally Select Shield', 'Enemy Select Trap','AOE Hit Aura', 'AOE Global', 'AOE Hit', 'Enemy Select Hit']
# storm_hitter_strategy = ['AOE Hit Aura', 'AOE Defense Aura', 'AOE Offensive Shadow Creature', 'AOE Hit', 'Enemy Select Hit','Ally Select Shield', 'Ally Select Blade', 'Enemy Select Trap', 'AOE Trap']
# fire_hitter_strategy = ['Select Shield', 'Ally Select Blade', 'AOE Blade','Enemy Select Trap', 'AOE Trap', 'AOE Global', '', 'AOE DOT', 'Enemy Select DOT', 'Enemy Select Detonate', 'AOE Hit', 'Enemy Select Hit', 'AOE Stun']

# define the master hitting strategy
master_strategy = ['Ally Select Blade', 'Enemy Select Trap', 'AOE Minion', 'AOE Global', 'AOE Blade', 'AOE Trap', 'AOE Hit Aura', 'AOE Offensive Shadow Creature', 'AOE DOT', 'AOE Hit', 'Enemy Select DOT', 'Enemy Select Hit', 'Enemy Select Hit Divide', 'AOE Polymorph']
# TODO: Change the master strategy based on if there's just a boss, just mobs, or mixture of both. Mobs only strat should be AOE spamming.

@logger.catch
class SlackFighter(CombatHandler):
	def __init__(self, client):
		self.client = client
		self._spell_check_boxes = None
		self.prev_hit_type = []

	# From WizWalker 2.0 Branch and wizfighter
	async def get_members_on_team(self, same_as_client: bool = True) -> list[CombatMember]:
		client_member = await self.get_client_member()
		part = await client_member.get_participant()
		client_team_id = await part.team_id()

		async def _on_other_team(member):
			member_part = await member.get_participant()
			member_team_id = await member_part.team_id()

			return member_team_id != client_team_id

		async def _on_same_team(member):
			member_part = await member.get_participant()
			member_team_id = await member_part.team_id()

			return member_team_id == client_team_id
		if same_as_client:
			thing_to_return = await self.get_members_with_predicate(_on_same_team)

		else:
			thing_to_return = await self.get_members_with_predicate(_on_other_team)
		return thing_to_return

	async def handle_round(self):
		should_pass = False
		# From wizfighter
		async def get_school_template_name(member: CombatMember):
			part = await member.get_participant()
			school_id = await part.primary_magic_school_id()
			return await self.client.cache_handler.get_template_name(school_id)

		try:
			await self.client.mouse_handler.activate_mouseless()
		except:
			await asyncio.sleep(0)
		# get mobs, and create participant/stat dictionaries
		mobs = await self.get_members_on_team(same_as_client=False)
		mob_participants = {}
		mob_stats = {}
		for m in mobs:
			mob_participants[m] = await m.get_participant()
			mob_stats[m] = await m.get_stats()

		# get ally member, participants, and stats
		allies = await self.get_members_on_team(same_as_client=True)
		ally_participants = {}
		ally_stats = {}
		for a in allies:
			ally_participants[a] = await a.get_participant()
			ally_stats[a] = await a.get_stats()

		# auto discard any spell that isn't in the master spell list
		while True:
			cards = await self.get_cards()
			if len(cards) != 0:
				for c in cards:
					card_name = await c.display_name()
					if card_name not in master_list_expanded:
						await c.discard(sleep_time=0.25)
						await asyncio.sleep(0.25)
						break
					else:
						pass
				else:
					break
			else:
				break

		while True:
			await asyncio.sleep(0.1)
			cards = await self.get_cards()
			castable_cards = [c for c in cards if await c.is_castable()]
			if len(castable_cards) != 0:
				# assigns spell type for all spells
				type_assigned_spells = {}
				for c in castable_cards:
					card_name = await c.display_name()
					if card_name in HIT_ENCHANTS:
						type_assigned_spells[c] = 'Hit Enchant'
					elif card_name in HEAL_ENCHANTS:
						type_assigned_spells[c] = 'Heal Enchant'
					elif card_name in BLADE_ENCHANTS:
						type_assigned_spells[c] = 'Blade Enchant'
					elif card_name in TRAP_ENCHANTS:
						type_assigned_spells[c] = 'Trap Enchant'
					elif card_name in HIT_AURAS:
						type_assigned_spells[c] = 'AOE Hit Aura'
					elif card_name in DEFENSE_AURAS:
						type_assigned_spells[c] = 'AOE Defense Aura'
					elif card_name in HEAL_AURAS:
						type_assigned_spells[c] = 'AOE Heal Aura'
					elif card_name in SELECT_SHIELDS:
						type_assigned_spells[c] = 'Ally Select Shield'
					elif card_name in AOE_SHIELDS:
						type_assigned_spells[c] = 'AOE Shield'
					elif card_name in SELECT_BLADES:
						type_assigned_spells[c] = 'Ally Select Blade'
					elif card_name in AOE_BLADES:
						type_assigned_spells[c] = 'AOE Blade'
					elif card_name in SELECT_PIERCE:
						type_assigned_spells[c] = 'Ally Select Pierce'
					elif card_name in SELECT_TRAPS:
						type_assigned_spells[c] = 'Enemy Select Trap'
					elif card_name in AOE_TRAPS:
						type_assigned_spells[c] = 'AOE Trap'
					elif card_name in GLOBALS:
						type_assigned_spells[c] = 'AOE Global'
					elif card_name in SELECT_DOTS:
						type_assigned_spells[c] = 'Enemy Select DOT'
					elif card_name in SELECT_HITS:
						type_assigned_spells[c] = 'Enemy Select Hit'
					elif card_name in AOE_DOTS:
						type_assigned_spells[c] = 'AOE DOT'
					elif card_name in AOE_HITS:
						type_assigned_spells[c] = 'AOE Hit'
					elif card_name in MINIONS:
						type_assigned_spells[c] = 'AOE Minion'
					elif card_name in OFFENSE_SHADOW:
						type_assigned_spells[c] = 'AOE Offensive Shadow Creature'
					elif card_name in DEFENSE_SHADOW:
						type_assigned_spells[c] = 'AOE Defensive Shadow Creature'
					elif card_name in HEAL_SHADOW:
						type_assigned_spells[c] = 'AOE Heal Shadow Creature'
					elif card_name in DISPELS:
						type_assigned_spells[c] = 'Enemy Select Dispel'
					elif card_name in SELECT_HEALS:
						type_assigned_spells[c] = 'Ally Select Heal'
					elif card_name in AOE_HEALS:
						type_assigned_spells[c] = 'AOE Heal'
					elif card_name in SELECT_STUNS:
						type_assigned_spells[c] = 'Enemy Select Stun'
					elif card_name in AOE_STUNS:
						type_assigned_spells[c] = 'AOE Stun'
					elif card_name in DETONATES:
						type_assigned_spells[c] = 'Enemy Select Detonate'
					elif card_name in SELECT_PRISMS:
						type_assigned_spells[c] = 'Enemy Select Prism'
					elif card_name in AOE_PRISMS:
						type_assigned_spells[c] = 'AOE Prism'
					elif card_name in DIVIDE_HITS:
						type_assigned_spells[c] = 'Enemy Select Hit Divide'
					elif card_name in AOE_DEBUFFS:
						type_assigned_spells[c] = 'AOE Debuff'
					elif card_name in SELECT_DEBUFFS:
						type_assigned_spells[c] = 'Enemy Select Debuff'
					elif card_name in AOE_SHADOW_HITS:
						type_assigned_spells[c] = 'AOE Hit Shadow'
					elif card_name in SELECT_SHADOW_HITS:
						type_assigned_spells[c] = 'Enemy Select Hit Shadow'
					elif card_name in SELECT_MINION_UTILITIES:
						type_assigned_spells[c] = 'Ally Select Minion Utility'
					elif card_name in SELECT_PACIFIES:
						type_assigned_spells[c] = 'Ally Select Pacify'
					elif card_name in AOE_PACIFIES:
						type_assigned_spells[c] = 'AOE Pacify'
					elif card_name in AOE_TAUNTS:
						type_assigned_spells[c] = 'AOE Taunt'
					elif card_name in AOE_DETONATES:
						type_assigned_spells[c] = 'AOE Detonate'
					elif card_name in AOE_POLYMORPHS:
						type_assigned_spells[c] = 'AOE Polymorphs'
					elif card_name in AOE_HEAL_BLADES:
						type_assigned_spells[c] = 'AOE Heal Blade'
					elif card_name in SELECT_HEAL_BLADES:
						type_assigned_spells[c] = 'Ally Select Heal Blade'


			# enchant everything that can be enchanted out of castable cards, keep in mind this is being repeated since you lose a card when you enchant something, changing the positions of all cards
			for e in castable_cards:
				match type_assigned_spells[e]:
					case 'Hit Enchant':
						enchantable_list = ['Enemy Select DOT', 'Enemy Select Hit', 'AOE Hit', 'AOE DOT', 'Enemy Select Hit Divide']
						for s in castable_cards:
							if type_assigned_spells[s] in enchantable_list and not await s.is_item_card() and not await s.is_enchanted():
								logger.debug(f"Client {self.client.title} - Enchanting {await s.display_name()} with {await e.display_name()}")
								await e.cast(s, sleep_time=0.25)
								await asyncio.sleep(0.1)
								break
						else:
							continue
						break
					case 'Blade Enchant':
						enchantable_list = ['Ally Select Blade', 'AOE Blade']
						for s in castable_cards:
							if type_assigned_spells[s] in enchantable_list and not await s.is_item_card() and not await s.is_enchanted():
								logger.debug(f"Client {self.client.title} - Enchanting {await s.display_name()} with {await e.display_name()}")
								await e.cast(s, sleep_time=0.25)
								await asyncio.sleep(0.1)
								break
						else:
							continue
						break
					case 'Trap Enchant':
						enchantable_list = ['Enemy Select Trap', 'AOE Trap']
						for s in castable_cards:
							logger.debug(f"Client {self.client.title} - Enchanting {await s.display_name()} with {await e.display_name()}")
							if type_assigned_spells[s] in enchantable_list and not await s.is_item_card() and not await s.is_enchanted():
								await e.cast(s, sleep_time=0.25)
								await asyncio.sleep(0.1)
								break
						else:
							continue
						break
					case 'Heal Enchant':
						enchantable_list = ['Ally Select Heal', 'AOE Heal']
						for s in castable_cards:
							if type_assigned_spells[s] in enchantable_list and not await s.is_item_card() and not await s.is_enchanted():
								logger.debug(f"Client {self.client.title} - Enchanting {await s.display_name()} with {await e.display_name()}")
								await e.cast(s, sleep_time=0.25)
								await asyncio.sleep(0.1)
								break
						else:
							continue
						break
					case _:
						pass
			else:
				break

		non_enchant_castable_cards = [c for c in castable_cards if 'Enchant' not in type_assigned_spells[c]]
		# enemy selection
		# TODO: Prism logic (maybe using resistances?), and shield logic. That shouldn't go here though.
		if len(non_enchant_castable_cards) != 0:
			selected_enemy = None
			if len([m for m in mobs if await m.is_boss()]) == 0:
				mob_health = {}
				for m in mobs:
					mob_health[m] = await m.health()
				selected_enemy = max(mob_health, key= lambda x: mob_health[x])
			elif len([m for m in mobs if await m.is_boss()]) > 1:
				bosses = [m for m in mobs if await m.is_boss()]
				boss_health = {}
				for b in bosses:
					boss_health[b] = await b.health()
				selected_enemy = max(boss_health, key= lambda x: boss_health[x])
			else:
				selected_enemy = [m for m in mobs if await m.is_boss()][0]
			# hopefully this fixes the insertions in the strategy list persisting across rounds, and causing heal chains.
			strategy_raw = master_strategy
			selected_spell = None
			to_clear = ['Heal', 'Prism', 'Dispel']
			strategy = []
			for s in strategy_raw:
				for x in to_clear:
					if x not in s:
						pass
					else:
						break
				else:
					strategy.append(s)
			# ally selection, only does self for now
			# TODO: Make this select based on who's the hitter, this should be done when you decide to do teamwork based combat.
			selected_ally = await self.get_client_member()

			if any([type_assigned_spells[c] == 'Ally Select Minion Utility' for c in castable_cards]):
				if any([await m.is_minion() for m in allies]):
					if (float(await selected_ally.health()) / float(await selected_ally.max_health())) < 0.51:
						strategy.append('AOE Pacify')
					else:
						strategy.append('Ally Select Pacify')
						strategy.append('AOE Taunt')
					strategy.append('Ally Select Minion Utility')

			strategy.append('AOE Hit')
			strategy.append('Enemy Select Hit')
			strategy.append('Enemy Select Hit Divide')

			if self.prev_hit_type:
				if 'Enemy Select DOT' in self.prev_hit_type:
					strategy.insert(0, 'Enemy Select Detonate')
				if 'AOE DOT' in self.prev_hit_type:
					strategy.insert(0, 'AOE Detonate')
				for t in self.prev_hit_type:
					if t in strategy:
						strategy.remove(t)
					strategy.append(t)

			# strategy = [s for s in strategy_raw if x not in s for x in to_clear]
			if await get_school_template_name(await self.get_client_member()) == await get_school_template_name(selected_enemy):
				# prism logic
				prism_list = ['Enemy Select Prism', 'AOE Prism', 'Ally Select Pierce', 'Enemy Select Dispel']
				[strategy.insert(0, h) for h in prism_list]

			# heal ally/self logic
			if (float(await selected_ally.health()) / float(await selected_ally.max_health())) < 0.66:
				selected_ally = a
				heal_list = ['AOE Defense Aura', 'AOE Defensive Shadow Creature', 'AOE Shield', 'Enemy Select Debuff', 'AOE Debuff', 'AOE Stun', 'Enemy Select Stun', 'Ally Select Shield']
				[strategy.insert(0, h) for h in heal_list]

			if (float(await selected_ally.health()) / float(await selected_ally.max_health())) < 0.51:
				selected_ally = a
				heal_list = ['AOE Heal Blade', 'Ally Select Heal Blade', 'AOE Heal Shadow Creature', 'AOE Heal', 'Ally Select Heal']
				[strategy.insert(0, h) for h in heal_list]
			# spell selection
			selected_spells = []
			for i in strategy:
				for c in castable_cards:
					if type_assigned_spells[c] == i:
						selected_spells.append(c)
				if len(selected_spells) != 0:
					break
			if len(selected_spells) != 0:
				selected_spell_ranks = {}
				for s in selected_spells:
					g_spell = await s.get_graphical_spell()
					regular_rank = await g_spell.read_value_from_offset(176 + 72, "unsigned char")
					shadow_rank = await g_spell.read_value_from_offset(176 + 73, "unsigned char")
					card_rank = regular_rank + (4 * shadow_rank)
					selected_spell_ranks[s] = int(card_rank)
				selected_spell = max(selected_spell_ranks, key= lambda x: selected_spell_ranks[x])
			else:
				non_castable_card_names = ['Enchant', 'Heal', 'Prism', 'Dispel']
				for c in castable_cards:
					for n in non_castable_card_names:
						if n in type_assigned_spells[c]:
							break
						else:
							pass
					else:
						selected_spell = c
						break
				else:
					should_pass = True
			minion_only_spell_types = ['Ally Select Minion Utility', 'Ally Select Pacify', 'AOE Pacify', 'AOE Taunt']
			if type_assigned_spells[selected_spell] in minion_only_spell_types:
				selected_ally = [m for m in allies if await m.is_minion()][0]

			# casting logic
			while True:
				if not should_pass:
					if 'AOE' in type_assigned_spells[selected_spell]:
						logger.debug(f"Client {self.client.title} - Casting {await selected_spell.display_name()}")
						await selected_spell.cast(None, sleep_time=0.25)
					elif 'Enemy Select' in type_assigned_spells[selected_spell]:
						logger.debug(f"Client {self.client.title} - Casting {await selected_spell.display_name()} on {await selected_enemy.name()}")
						await selected_spell.cast(selected_enemy, sleep_time=0.25)
					else:
						logger.debug(f"Client {self.client.title} - Casting {await selected_spell.display_name()} on {await selected_ally.name()}")
						await selected_spell.cast(selected_ally, sleep_time=0.25)
					# divide hit confirm
					if 'Divide' in type_assigned_spells[selected_spell]:
						try:
							await self.client.mouse_handler.click_window_with_name(name='ConfirmTargetsConfirm')
						except:
							await asyncio.sleep(0)
					# add just casted spell type to the anti spam list, doesn't account for stuns
					self.prev_hit_type.append(type_assigned_spells[selected_spell])
				else:
					logger.debug(f'Client {self.client.title} - No viable spells, passing.')
					await self.pass_button()
				break
				# await asyncio.sleep(2)
				# if await self.client.duel.duel_phase() == DuelPhase.planning:
				# 	pass
				# else:
				# 	break
			strategy = []
			strategy = master_strategy
		else:
			logger.debug(f'Client {self.client.title} - No castable spells, passing.')
			await self.pass_button()
		strategy = []
		strategy = master_strategy
		await asyncio.sleep(0.1)
		try:
			await self.client.mouse_handler.deactivate_mouseless()
		except:
			await asyncio.sleep(0)
