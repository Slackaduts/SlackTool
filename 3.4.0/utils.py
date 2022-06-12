import asyncio
from wizwalker import Client, Keycode, XYZ
from wizwalker.memory import Window
from loguru import logger

spiral_door_reset_path = ['WorldView', '', 'messageBoxBG', 'ControlSprite', 'optionWindow', 'leftButton']
spiral_door_cycle_path = ['WorldView', '', 'messageBoxBG', 'ControlSprite', 'optionWindow', 'rightButton']
spiral_door_teleport_path = ['WorldView', '', 'messageBoxBG', 'ControlSprite', 'teleportButton']
spiral_door_world_path = ['WorldView', '', 'messageBoxBG', 'ControlSprite']
spiral_door_selected_path = ['WorldView', '', 'messageBoxBG', 'ControlSprite', 'selectedWorldCheckMark']
spiral_door_path = ['WorldView', '', 'messageBoxBG', 'ControlSprite', 'optionWindow']

potion_shop_base_path = ['WorldView', 'main']
potion_buy_path = ['WorldView', 'main', 'buyAction']
potion_fill_all_path = ['WorldView', 'main', 'fillallpotions']
potion_exit_path = ['WorldView', 'main', 'exit']
potion_usage_path = ['WorldView', 'windowHUD', 'btnPotions']

quit_button_path = ['WorldView', 'DeckConfiguration', 'SettingPage', 'QuitButton']
play_button_path = ['WorldView', 'mainWindow', 'btnPlay']

dungeon_warning_path = ['MessageBoxModalWindow', 'messageBoxBG', 'messageBoxLayout', 'AdjustmentWindow', 'Layout', 'centerButton']

advance_dialog_path = ['WorldView', 'wndDialogMain', 'btnRight']

# FOR REFERENCE
valid_worlds = [
	'Krokotopia',
	'Grizzleheim',
	'DragonSpire',
	'MooShu',
	'Marleybone',
	'WizardCity',
	'Celestia',
	'Wysteria',
	'Karamelle',
	'Zafaria',
	'Avalon',
	'Azteca',
	'Khrysalis',
	'Polaris',
	'Arcanum',
	'Aquila',
	'Mirage',
	'Empyrea',
	'Karamelle',
	'Lemuria'
]


async def attempt_activate_mouseless(client: Client, sleep_time: float = 0.1):
	# Attempts to activate mouseless, in a try block in case it's already on for this client
	if not client.mouseless_status:
		await client.mouse_handler.activate_mouseless()
		client.mouseless_status = True
	await asyncio.sleep(sleep_time)


async def attempt_deactivate_mouseless(client: Client, sleep_time: float = 0.1):
	# Attempts to deactivate mouseless, in a try block in case it's already off for this client
	if client.mouseless_status:
		await client.mouse_handler.deactivate_mouseless()
		client.mouseless_status = False
	await asyncio.sleep(sleep_time)

async def get_window_from_path(root_window: Window, name_path: list[str]) -> Window:
	# FULL CREDIT TO SIROLAF FOR THIS FUNCTION
	async def _recurse_follow_path(window, path):
		if len(path) == 0:
			return window
		for child in await window.children():
			if await child.name() == path[0]:
				found_window = await _recurse_follow_path(child, path[1:])
				if not found_window is False:
					return found_window

		return False

	return await _recurse_follow_path(root_window, name_path)


async def is_visible_by_path(client: Client, path: list[str]):
	# FULL CREDIT TO SIROLAF FOR THIS FUNCTION
	# checks visibility of a window from the path
	root = client.root_window
	windows = await get_window_from_path(root, path)
	if windows == False:
		return False
	elif await windows.is_visible():
		return True
	else:
		return False


async def click_window_by_path(client: Client, path: list[str], hooks: bool = False):
	# FULL CREDIT TO SIROLAF FOR THIS FUNCTION
	# clicks window from path, must actually exist in the UI tree
	if hooks:
		await attempt_activate_mouseless(client)
	root = client.root_window
	windows = await get_window_from_path(root, path)
	if windows:
		await client.mouse_handler.click_window(windows)
	else:
		await asyncio.sleep(0.1)
	if hooks:
		await attempt_deactivate_mouseless(client)


async def text_from_path(client: Client, path: list[str]) -> str:
	# Returns text from a window via the window path
	window = await get_window_from_path(client.root_window, path)
	return await window.maybe_text()


async def wait_for_loading_screen(client: Client):
	# Wait for a loading screen, then wait until the loading screen has finished.
	logger.debug(f'Client {client.title} - Awaiting loading')
	while not await client.is_loading():
		await asyncio.sleep(0.1)
	while await client.is_loading():
		await asyncio.sleep(0.1)


async def wait_for_zone_change(client: Client, loading_only: bool = False):
	# Wait for zone to change, allows for waiting in team up forever without any extra checks
	logger.debug(f'Client {client.title} - Awaiting loading')
	if not loading_only:
		current_zone = await client.zone_name()
		while current_zone == await client.zone_name():
			await asyncio.sleep(0.1)

	# Second loading check incase theres some sort of phantom zone loading screens put us into
	while await client.is_loading():
		await asyncio.sleep(0.1)


async def spiral_door(client: Client, open_window: bool = True, cycles: int = 0, opt: int = 0):
	# optionally open the spiral door window

	if open_window:
		while not await is_visible_by_path(client, spiral_door_path):
			await asyncio.sleep(0.1)
		await client.send_key(Keycode.X, 0.1)

	# bring menu back to first page
	for i in range(5):
		await client.send_key(Keycode.LEFT_ARROW, 0.1)
		await asyncio.sleep(0.25)

	# navigate menu to proper world
	world_path = spiral_door_path.copy()
	world_path.append(f'opt{opt}')
	await asyncio.sleep(0.5)
	for i in range(cycles):
		if i != 0:
			await client.send_key(Keycode.RIGHT_ARROW, 0.1)
			await asyncio.sleep(0.25)

	await click_window_by_path(client, world_path, True)
	await asyncio.sleep(1)
	await click_window_by_path(client, spiral_door_teleport_path, True)
	await wait_for_zone_change(client)


async def navigate_to_commons(client: Client):
	# navigates to commons from anywhere in the game

	await client.send_key(Keycode.HOME, 0.1)
	await wait_for_zone_change(client)
	use_spiral_door = False
	bartleby_navigation = True
	match await client.zone_name():
		# Handling for dorm room
		case "WizardCity/Interiors/WC_Housing_Dorm_Interior":
			await client.goto(70.15016174316406, 9.419374465942383)
			while not await client.is_loading():
				await client.send_key(Keycode.S, 0.1)
			await wait_for_zone_change(client, True)
			bartleby_navigation = False

		# Handling for arcanum apartment
		case "Housing_AR_Dormroom/Interior":
			while not await client.is_loading():
				await client.send_key(Keycode.S, 0.1)
			await wait_for_zone_change(client, True)
			await asyncio.sleep(0.5)
			await client.teleport(XYZ(x=-19.1153507232666, y=-6312.8994140625, z=-2.00579833984375))
			await client.send_key(Keycode.D, 0.1)
			use_spiral_door = True

		# Any other house in the game
		case _:
			await client.send_key(Keycode.S, 0.1)
			use_spiral_door = True

	# Navigate through spiral door if needed
	if use_spiral_door:
		while not await is_visible_by_path(client, spiral_door_teleport_path):
			await client.send_key(Keycode.X, 0.1)
			await asyncio.sleep(0.25)
		await spiral_door(client)

	# Navigate through bartleby if needed
	if bartleby_navigation:
		await client.goto(-9.711, -2987.212)
		await client.send_key(Keycode.W, 0.1)
		await wait_for_zone_change(client)
	
	# walk to ravenwood exit
	await client.goto(-19.549846649169922, -297.7527160644531)
	await client.goto(-5.701, -1536.491)
	while not await client.is_loading():
		await client.send_key(Keycode.W, 0.1)
	await wait_for_zone_change(client, True)


async def navigate_to_potions(client: Client):
	# Teleport to hilda brewer
	Hilda_XYZ = XYZ(-4398.70654296875, 1016.1954345703125, 229.00079345703125)
	await client.teleport(Hilda_XYZ)
	await client.send_key(Keycode.S, 0.1)


async def buy_potions(client: Client, recall: bool = True):
	# buy potions and close the potions menu, and recall if needed
	while not await is_visible_by_path(client, potion_shop_base_path):
		await client.send_key(Keycode.X, 0.1)
	await click_window_by_path(client, potion_fill_all_path, True)
	await click_window_by_path(client, potion_buy_path, True)
	while await is_visible_by_path(client, potion_shop_base_path):
		await click_window_by_path(client, potion_exit_path, True)
		await asyncio.sleep(0.5)
	if recall:
		await client.send_key(Keycode.PAGE_UP, 0.1)
		await wait_for_zone_change(client)
		await client.send_key(Keycode.PAGE_DOWN, 0.1)


async def use_potion(client: Client):
	# Uses a potion if we have one
	if await client.stats.potion_charge() >= 1.0:
		logger.debug(f'Client {client.title} - Using potion')
		await click_window_by_path(client, potion_usage_path, True)


async def auto_potions(client: Client, mark: bool = False, minimum_mana: int = 16):
	# Get client stats for mana/hp
	# TODO: FIX THE NON SPECIFIC HOME SPIRAL DOOR NAVIGATION, IT DOESNT CLICK (Try it with a house that isn't the arcanum apartment or dorm)
	mana = await client.stats.current_mana()
	max_mana = await client.stats.max_mana()
	health = await client.stats.current_hitpoints()
	max_health = await client.stats.max_hitpoints()
	client_level = await client.stats.reference_level()
	if minimum_mana > await client.stats.reference_level():
		minimum_mana = client_level
	combined_minimum_mana = int(0.23 * max_mana) + minimum_mana

	# If mana/health are below thresholds, use a potion if possible

	if mana < combined_minimum_mana or float(health) / float(max_health) < 0.55:
		await use_potion(client)

	# If we have less than 1 potion left, get potions
	if await client.stats.potion_charge() < 1.0:
		# mark if needed
		if mark:
			await client.send_key(Keycode.PAGE_UP, 0.1)

		# Navigate to commons
		await navigate_to_commons(client)

		# Navigate to hilda brewer
		await navigate_to_potions(client)

		# Buy potions
		await buy_potions(client)


async def wait_for_window_by_path(client: Client, path: list[str], hooks: bool = False, click: bool = True):
	while not await is_visible_by_path(client, path):
		await asyncio.sleep(0.1)
	if click or hooks:
		await click_window_by_path(client, path, hooks)


async def logout_and_in(client: Client):
	# Improved version of Major's logging out and in function
	await client.send_key(Keycode.ESC, 0.1)
	await wait_for_window_by_path(client, quit_button_path, True)
	await asyncio.sleep(0.25)
	if await is_visible_by_path(client, dungeon_warning_path):
		await client.send_key(Keycode.ENTER, 0.1)
	await wait_for_window_by_path(client, play_button_path, True)
	await asyncio.sleep(1.5)
	if await client.is_loading():
		await wait_for_loading_screen(client)


async def is_free(client: Client):
	# Returns True if not in combat, loading screen, or in dialogue.
	return not any([await client.is_loading(), await client.in_battle(), await is_visible_by_path(client, advance_dialog_path)])