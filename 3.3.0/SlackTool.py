import asyncio
import requests
import wizwalker
from wizwalker import Keycode, HotkeyListener, ModifierKeys, utils, XYZ
from wizwalker.client_handler import ClientHandler, Client
from wizwalker.extensions.scripting import teleport_to_friend_from_list
import os
import time
import sys
import subprocess
from loguru import logger
import datetime
from configparser import ConfigParser
import statistics
from SlackFighter import SlackFighter
from teleport_math import navmap_tp, calc_Distance
# from SlackQuester import SlackQuester
from SlackSigil import SlackSigil
from utils import is_visible_by_path, is_free
# import PySimpleGUI as sg

tool_version = '3.3.0'
tool_name = 'SlackTool'

type_format_dict = {
"char": "<c",
"signed char": "<b",
"unsigned char": "<B",
"bool": "?",
"short": "<h",
"unsigned short": "<H",
"int": "<i",
"unsigned int": "<I",
"long": "<l",
"unsigned long": "<L",
"long long": "<q",
"unsigned long long": "<Q",
"float": "<f",
"double": "<d",
}


def remove_if_exists(file_name : str, sleep_after : float = 0.1):
	if os.path.exists(file_name):
		os.remove(file_name)
		time.sleep(sleep_after)


def download_file(url: str, file_name : str, delete_previous: bool = False, debug : str = True):
	if delete_previous:
		remove_if_exists(file_name)
	if debug:
		print(f'Downloading {file_name}...')
	with requests.get(url, stream=True) as r:
		with open(file_name, 'wb') as f:
			for chunk in r.iter_content(chunk_size=128000):
				f.write(chunk)


# reading hotkeys from config
parser = ConfigParser()


def read_config(config_name : str):
	global x_press_key
	# global space_press_key
	global sync_locations_key
	global quest_teleport_key
	global mass_quest_teleport_key
	global toggle_speed_key
	global friend_teleport_key
	global kill_tool_key
	global toggle_auto_combat_key
	# global up_noclip_key
	# global forward_noclip_key
	# global down_noclip_key
	global toggle_auto_dialogue_key
	global toggle_auto_sigil_key
	global toggle_freecam_key
	# global toggle_auto_questing_key
	global speed_multiplier
	global auto_updating
	global use_team_up
	global version
	parser.read(config_name)
	auto_updating = parser.getboolean('settings', 'auto_updating')
	use_team_up = parser.getboolean('settings', 'use_team_up', fallback=False)
	x_press_key = parser.get('hotkeys', 'x_press', fallback='X')
	# space_press_key = parser.get('hotkeys', 'spacebar_press', fallback='F2')
	sync_locations_key = parser.get('hotkeys', 'sync_client_locations', fallback='F8')
	quest_teleport_key = parser.get('hotkeys', 'quest_teleport', fallback='F7')
	mass_quest_teleport_key = parser.get('hotkeys', 'mass_quest_teleport', fallback='F6')
	toggle_speed_key = parser.get('hotkeys', 'toggle_speed_multiplier', fallback='F5')
	friend_teleport_key = parser.get('hotkeys', 'friend_teleport', fallback='EIGHT')
	kill_tool_key = parser.get('hotkeys', 'kill_slacktool', fallback='F9')
	toggle_auto_combat_key = parser.get('hotkeys', 'toggle_auto_combat', fallback='NINE')
	# up_noclip_key = parser.get('hotkeys', 'up_noclip', fallback='ONE')
	# forward_noclip_key = parser.get('hotkeys', 'forward_noclip', fallback='TWO')
	# down_noclip_key = parser.get('hotkeys', 'down_noclip', fallback='THREE')
	speed_multiplier = parser.getfloat('settings', 'speed_multiplier', fallback=5.0)
	toggle_auto_dialogue_key = parser.get('hotkeys', 'toggle_auto_dialogue', fallback='F4')
	# toggle_auto_questing_key = parser.get('hotkeys', 'toggle_auto_questing', fallback='F3')
	toggle_auto_sigil_key = parser.get('hotkeys', 'toggle_auto_sigil', fallback='F2')
	toggle_freecam_key = parser.get('hotkeys', 'toggle_freecam', fallback='F1')
	version = parser.get('version', 'current_version', fallback=tool_version)


while True:
	if not os.path.exists(f'{tool_name}-config.ini'):
		download_file(f'https://raw.githubusercontent.com/Slackaduts/{tool_name}/main/{tool_name}-config.ini', f'{tool_name}-config.ini')
	time.sleep(0.1)
	try:
		read_config(f'{tool_name}-config.ini')
	except:
		logger.critical('Error found in the config. Redownloading the config to prevent further issues.')
		# sg.Popup(f'{tool_name} Error', 'Error found in the config. Redownloading the config to prevent further issues.', non_blocking=True)
		os.remove(f'{tool_name}-config.ini')
		time.sleep(0.1)
	else:
		break


speed_status = False
combat_status = False
dialogue_status = False
sigil_status = False
freecam_status = False
# questing_status = False


def file_len(filepath):
	# return the number of lines in a file
	f = open(filepath, "r")
	return len(f.readlines())


def read_webpage(url):
	# return a list of lines from a hosted file
	try:
		response = requests.get(url, allow_redirects=True)
		page_text = response.text
		line_list = page_text.splitlines()
	except:
		return []
	else:
		return line_list


def generate_timestamp():
	# generates a timestamp and makes the symbols filename-friendly
	time = str(datetime.datetime.now())
	time_list = time.split('.')
	time_stamp = str(time_list[0])
	time_stamp = time_stamp.replace('/', '-').replace(':', '-')
	return time_stamp


def config_update_rewrite(tool_name : str = tool_name):
	config_url = f'https://raw.githubusercontent.com/Slackaduts/{tool_name}/main/{tool_name}-config.ini'
	if not os.path.exists(f'{tool_name}-config.ini'):
		download_file(url=config_url, file_name=f'{tool_name}-config.ini')
		time.sleep(0.1)
	if not os.path.exists(f'README.txt'):
		download_file(f'https://raw.githubusercontent.com/Slackaduts/{tool_name}/main/README.txt', 'README.txt')
	download_file(url=config_url, file_name=f'{tool_name}-Testconfig.ini', delete_previous=True, debug=False)
	time.sleep(0.1)
	comparison_parser = ConfigParser()
	comparison_parser.read(f'{tool_name}-Testconfig.ini')
	comparison_sections = comparison_parser.sections()
	for i in comparison_sections:
		if not parser.has_section(i):
			print(f'Config file lacks section "{i}", adding it.')
			parser.add_section(i)
		comparison_options = comparison_parser.options(i)
		for b in comparison_options:
			if not parser.has_option(i, b):
				print(f'Config file lacks option "{b}", adding it and its default value.')
				parser.set(i, b, str(comparison_parser.get(i, b)))
	with open(f'{tool_name}-config.ini', 'w') as new_config:
		parser.write(new_config)
	remove_if_exists(f'{tool_name}-Testconfig.ini')
	time.sleep(0.1)
	read_config(f'{tool_name}-config.ini')
	print('\n')


def run_updater(tool_name : str = tool_name):
	download_file(url=f"https://raw.githubusercontent.com/Slackaduts/{tool_name}/main/{tool_name}Update.exe", file_name=f'{tool_name}Update.exe', delete_previous=True)
	time.sleep(0.1)
	subprocess.Popen(f'{tool_name}Update.exe')
	sys.exit()


def auto_update_rewrite(tool_name : str = tool_name):
	remove_if_exists(f'{tool_name}-copy.exe')
	remove_if_exists(f'{tool_name}Update.exe')
	time.sleep(0.1)
	try:
		update_server = read_webpage(f"https://raw.githubusercontent.com/Slackaduts/{tool_name}/main/LatestVersion.txt")
	except:
		time.sleep(0.1)
	else:
		if len(update_server) >= 2:
			if auto_updating and update_server[0] == 'True':
				if version != update_server[1]:
					parser.set('version', 'current_version', update_server[1])
					with open(f'{tool_name}-config.ini', 'w') as new_config:
						parser.write(new_config)
					run_updater()
			elif not auto_updating and update_server[0] == 'True':
				if tool_version != version:
					run_updater()


async def mass_key_press(foreground_client : Client, background_clients : list[Client], pressed_key_name: str, key, duration : float = 0.1, debug : bool = False):
	# sends a given keystroke to all clients, handles foreground client seperately
	if debug and foreground_client:
		key_name = str(key)
		key_name = key_name.replace('Keycode.', '')
		logger.debug(f'{pressed_key_name} key pressed, sending {key_name} key press to all clients.')
	await asyncio.gather(*[p.send_key(key=key, seconds=duration) for p in background_clients])
	# only send foreground key press if there is a client in foreground
	if foreground_client:
		await foreground_client.send_key(key=key, seconds=duration)


async def sync_camera(client: Client, xyz: XYZ = None, yaw: float = None):
	# Teleports the freecam to a specified position, yaw, etc.
	if not xyz:
		xyz = await client.body.position()

	if not yaw:
		yaw = await client.body.yaw()

	xyz.z += 200

	camera = await client.game_client.free_camera_controller()
	await camera.write_position(xyz)
	await camera.write_yaw(yaw)


async def xyz_sync(foreground_client : Client, background_clients : list[Client], turn_after : bool = True, debug : bool = False):
	# syncs client XYZ up with the one in foreground, doesn't work across zones or realms
	if background_clients:
		if debug:
			logger.debug(f'{sync_locations_key} key pressed, syncing client locations.')
		if foreground_client:
			xyz = await foreground_client.body.position()
		else:
			first_background_client = background_clients[0]
			xyz = await first_background_client.body.position()

		await asyncio.gather(*[p.teleport(xyz) for p in background_clients])
		if turn_after:
			await asyncio.gather(*[p.send_key(key=Keycode.A, seconds=0.1) for p in background_clients])
			await asyncio.gather(*[p.send_key(key=Keycode.D, seconds=0.1) for p in background_clients])
		await asyncio.sleep(0.3)


async def navmap_teleport(foreground_client : wizwalker.Client, background_clients : list[Client], mass_teleport: bool = False, debug : bool = False):
	# teleports foreground client or all clients using the navmap.
	xyz = None
	# nested function that allows for the gathering of the teleports for each client
	async def client_navmap_teleport(client: Client, xyz: XYZ = None):
		if not xyz:
			xyz = await client.quest_position.position()
		await navmap_tp(client, xyz)
		# except:
		# 	# skips teleport if there's no navmap, this should just switch to auto adjusting teleport
		# 	logger.error(f'{client.title} encountered an error during navmap tp, most likely the navmap for the zone did not exist. Skipping teleport.')

	if debug:
		if mass_teleport:
			logger.debug(f'{mass_quest_teleport_key} key pressed, teleporting all clients to quests.')
		else:
			logger.debug(f'{quest_teleport_key} key pressed, teleporting client {foreground_client.title} to quest.')
	clients_to_port = []
	if foreground_client:
		clients_to_port.append(foreground_client)
	if mass_teleport:
		for b in background_clients:
			clients_to_port.append(b)
		# decide which client's quest XYZ to obey. Chooses the most common Quest XYZ across all clients, if there is none and all clients are in the same zone then it obeys the foreground client. If the zone differs, each client obeys their own quest XYZ.
		list_modes = statistics.multimode([await c.quest_position.position() for c in clients_to_port])
		zone_names = [await p.zone_name() for p in clients_to_port]
		if len(list_modes) == 1:
			xyz = list_modes[0]
		else:
			if zone_names.count(zone_names[0]) == len(zone_names):
				if foreground_client:
					xyz = await foreground_client.quest_position.position()

	# if mass teleport is off and no client is selected, this will default to p1
	if len(clients_to_port) == 0:
		if background_clients:
			clients_to_port.append(background_clients[0])
	
	# all clients teleport at the same time
	await asyncio.gather(*[client_navmap_teleport(p, xyz) for p in clients_to_port])


async def toggle_speed(debug : bool = False):
	# toggles a bool for the speed multiplier. Speed multiplier task handles the actual logic, this just enables/disables it.
	global speed_status
	speed_status ^= True
	if debug:
		if speed_status:
			logger.debug(f'{toggle_speed_key} key pressed, enabling speed multiplier.')
		else:
			logger.debug(f'{toggle_speed_key} key pressed, disabling speed multiplier.')


async def friend_teleport_sync(clients : list[wizwalker.Client], debug: bool):
	# uses the util for porting to friend via the friends list. Sends every client to p1. I really don't like this function, or this code, but it works and people want it so I have to have it in here sadly. Might rewrite it someday.
	if debug:
		logger.debug(f'{friend_teleport_key} key pressed, friend teleporting all clients to p1.')
	child_clients = clients[1:]
	try:
		await asyncio.gather(*[p.mouse_handler.activate_mouseless() for p in child_clients])
	except:
		await asyncio.sleep(0)
	await asyncio.sleep(0.25)
	try:
		[await teleport_to_friend_from_list(client=p, icon_list=1, icon_index=50) for p in child_clients]
	except:
		await asyncio.sleep(0)
	try:
		await asyncio.gather(*[p.mouse_handler.deactivate_mouseless() for p in child_clients])
	except:
		await asyncio.sleep(0)


async def kill_tool(debug: bool):
	# raises KeyboardInterrupt, forcing the tool to exit.
	if debug:
		logger.debug(f'{kill_tool_key} key pressed, killing {tool_name}.')
	await asyncio.sleep(0)
	await asyncio.sleep(0)
	raise KeyboardInterrupt


async def toggle_combat(debug: bool):
	global combat_status
	combat_status ^= True
	if debug:
		if combat_status:
			logger.debug(f'{toggle_auto_combat_key} key pressed, enabling auto combat.')
		else:
			logger.debug(f'{toggle_auto_combat_key} key pressed, disabling auto combat.')


# async def noclip_up(foreground_client : wizwalker.Client, speed_constant : int = 580, speed_adjusted : bool = True, down : bool = False, debug : bool = False):
# 	# teleports the client up/down in accordance with their speed multiplier.
# 	if down:
# 		speed_constant *= -1
# 		if debug:
# 			logger.debug(f'{down_noclip_key} key pressed, noclipping down.')
# 	else:
# 		if debug:
# 			logger.debug(f'{up_noclip_key} key pressed, noclipping up.')

# 	if foreground_client:
# 		up_xyz = await calc_up_XYZ(foreground_client , speed_constant=speed_constant, speed_adjusted=speed_adjusted)
# 		await foreground_client.teleport(up_xyz, move_after=False)
# 	else:
# 		logger.error('Foreground client does not exist, skipping teleport.')


# async def noclip_forward(foreground_client : wizwalker.Client, speed_constant : int = 580, speed_adjusted : bool = True, backward : bool = False, debug : bool = False):
# 	# teleports the client forward/backward in accordance with their speed multiplier.
# 	if debug:
# 		if not backward:
# 			logger.debug(f'{forward_noclip_key} key pressed, noclipping forward.')
# 		else:
# 			logger.debug(f'{forward_noclip_key} key pressed, noclipping backward.')
# 			speed_constant *= -1

# 	if foreground_client:
# 		frontal_xyz = await calc_FrontalVector(foreground_client , speed_constant=speed_constant, speed_adjusted=speed_adjusted)
# 		await foreground_client.teleport(frontal_xyz)
# 	else:
# 		logger.error('Foreground client does not exist, skipping teleport.')


async def toggle_dialogue(debug: bool):
	# automatically clicks through dialogue, and rejects sidequests.
	global dialogue_status
	dialogue_status ^= True
	if debug:
		if dialogue_status:
			logger.debug(f'{toggle_auto_dialogue_key} key pressed, enabling auto dialogue.')
		else:
			logger.debug(f'{toggle_auto_dialogue_key} key pressed, disabling auto dialogue.')


# async def toggle_questing(debug: bool):
# 	# toggles auto questing
# 	global questing_status
# 	questing_status ^= True
# 	if debug:
# 		if questing_status:
# 			logger.debug(f'{toggle_auto_questing_key} key pressed, enabling auto questing.')
# 		else:
# 			logger.debug(f'{toggle_auto_questing_key} key pressed, disabling auto questing.')


async def toggle_sigil(debug: bool):
	# toggles auto sigil
	global sigil_status
	sigil_status ^= True
	if debug:
		if sigil_status:
			logger.debug(f'{toggle_auto_sigil_key} key pressed, enabling auto sigil.')
		else:
			logger.debug(f'{toggle_auto_sigil_key} key pressed, disabling auto sigil.')



@logger.catch()
async def main():
	listener = HotkeyListener()
	foreground_client = None
	background_clients = []


	async def tool_finish():
		if speed_status:
			await asyncio.gather(*[p.client_object.write_speed_multiplier(client_speeds[p]) for p in walker.clients])
		for p in walker.clients:
			p.title = 'Wizard101'
			if await p.game_client.is_freecam():
				await p.camera_elastic()
			# if await p.game_client.is_free
			try:
				await p.mouse_handler.deactivate_mouseless()
			except:
				await asyncio.sleep(0)
		logger.remove(current_log)
		await listener.stop()
		await walker.close()
		await asyncio.sleep(0)


	async def x_press_hotkey():
		await mass_key_press(foreground_client, background_clients, x_press_key, Keycode.X, duration=0.1, debug=True)

	# async def space_press_hotkey():
	# 	await mass_key_press(foreground_client, background_clients, space_press_key, Keycode.SPACEBAR, duration=0.1, debug=True)

	async def xyz_sync_hotkey():
		await xyz_sync(foreground_client, background_clients, turn_after=True, debug=True)

	async def navmap_teleport_hotkey():
		if not freecam_status:
			await navmap_teleport(foreground_client, background_clients, mass_teleport=False, debug=True)

	async def mass_navmap_teleport_hotkey():
		if not freecam_status:	
			await navmap_teleport(foreground_client, background_clients, mass_teleport=True, debug=True)

	async def toggle_speed_hotkey():
		if not freecam_status:
			await toggle_speed(debug=True)

	async def friend_teleport_sync_hotkey():
		if not freecam_status:
			await friend_teleport_sync(walker.clients, debug=True)

	async def kill_tool_hotkey():
		await kill_tool(debug=True)

	async def toggle_combat_hotkey():
		if not freecam_status:
			for p in walker.clients:
				p.combat_status ^= True
			await toggle_combat(debug=True)

	# async def noclip_forward_hotkey():
	# 	if not freecam_status:
	# 		await noclip_forward(foreground_client, debug=True)

	# async def noclip_up_hotkey():
	# 	if not freecam_status:
	# 		await noclip_up(foreground_client, debug=True)

	# async def noclip_down_hotkey():
	# 	if not freecam_status:
	# 		await noclip_up(foreground_client, down=True, debug=True)

	async def toggle_dialogue_hotkey():
		if not freecam_status:
			await toggle_dialogue(debug=True)

	async def toggle_sigil_hotkey():
		if not freecam_status:
			for p in walker.clients:
				p.sigil_status ^= True
			await toggle_sigil(debug=True)

	async def toggle_freecam_hotkey():
		# async def camera_switcher(client: Client):
		global freecam_status
		if foreground_client:
			if await is_free(foreground_client):
				if await foreground_client.game_client.is_freecam():
					logger.debug(f'{toggle_freecam_key} key pressed, disabling freecam.')
					await foreground_client.camera_elastic()
					freecam_status = False
				else:
					logger.debug(f'{toggle_freecam_key} key pressed, enabling freecam.')
					freecam_status = True
					await sync_camera(foreground_client)
					await foreground_client.camera_freecam()

		# await asyncio.gather(*[camera_switcher(p) for p in walker.clients])

	async def tp_to_freecam_hotkey():
		if foreground_client:
			logger.debug(f'Shift + {toggle_freecam_key} key pressed, teleporting foreground client to freecam position.')
			if await foreground_client.game_client.is_freecam():
				camera = await foreground_client.game_client.free_camera_controller()
				camera_pos = await camera.position()
				await foreground_client.teleport(camera_pos, wait_on_inuse=True, purge_on_after_unuser_fixer=True)

	# async def toggle_questing_hotkey():
	# 	await toggle_questing(debug=True)


	async def enable_hotkeys(exclude_freecam: bool = False):
		# adds every hotkey
		if not freecam_status:
			await listener.add_hotkey(Keycode[x_press_key], x_press_hotkey, modifiers=ModifierKeys.NOREPEAT)
			# await listener.add_hotkey(Keycode[space_press_key], space_press_hotkey, modifiers=ModifierKeys.NOREPEAT)
			await listener.add_hotkey(Keycode[sync_locations_key], xyz_sync_hotkey, modifiers=ModifierKeys.NOREPEAT)
			await listener.add_hotkey(Keycode[quest_teleport_key], navmap_teleport_hotkey, modifiers=ModifierKeys.NOREPEAT)
			await listener.add_hotkey(Keycode[mass_quest_teleport_key], mass_navmap_teleport_hotkey, modifiers=ModifierKeys.NOREPEAT)
			await listener.add_hotkey(Keycode[toggle_speed_key], toggle_speed_hotkey, modifiers=ModifierKeys.NOREPEAT)
			await listener.add_hotkey(Keycode[friend_teleport_key], friend_teleport_sync_hotkey, modifiers=ModifierKeys.NOREPEAT)
			await listener.add_hotkey(Keycode[toggle_auto_combat_key], toggle_combat_hotkey, modifiers=ModifierKeys.NOREPEAT)
			# await listener.add_hotkey(Keycode[forward_noclip_key], noclip_forward_hotkey, modifiers=ModifierKeys.NOREPEAT)
			# await listener.add_hotkey(Keycode[up_noclip_key], noclip_up_hotkey, modifiers=ModifierKeys.NOREPEAT)
			# await listener.add_hotkey(Keycode[down_noclip_key], noclip_down_hotkey, modifiers=ModifierKeys.NOREPEAT)
			await listener.add_hotkey(Keycode[toggle_auto_dialogue_key], toggle_dialogue_hotkey, modifiers=ModifierKeys.NOREPEAT)
			await listener.add_hotkey(Keycode[toggle_auto_sigil_key], toggle_sigil_hotkey, modifiers=ModifierKeys.NOREPEAT)
			if not exclude_freecam:
				await listener.add_hotkey(Keycode[toggle_freecam_key], toggle_freecam_hotkey, modifiers=ModifierKeys.NOREPEAT)
				await listener.add_hotkey(Keycode[toggle_freecam_key], tp_to_freecam_hotkey, modifiers=ModifierKeys.SHIFT | ModifierKeys.NOREPEAT)
			# await listener.add_hotkey(Keycode[toggle_auto_questing_key], toggle_questing_hotkey, modifiers=ModifierKeys.NOREPEAT)


	async def disable_hotkeys(exclude_freecam: bool = False):
		# removes every hotkey
		if not freecam_status:
			await listener.remove_hotkey(Keycode[x_press_key], modifiers=ModifierKeys.NOREPEAT)
			# await listener.remove_hotkey(Keycode[space_press_key], modifiers=ModifierKeys.NOREPEAT)
			await listener.remove_hotkey(Keycode[sync_locations_key], modifiers=ModifierKeys.NOREPEAT)
			await listener.remove_hotkey(Keycode[quest_teleport_key], modifiers=ModifierKeys.NOREPEAT)
			await listener.remove_hotkey(Keycode[mass_quest_teleport_key], modifiers=ModifierKeys.NOREPEAT)
			await listener.remove_hotkey(Keycode[toggle_speed_key], modifiers=ModifierKeys.NOREPEAT)
			await listener.remove_hotkey(Keycode[friend_teleport_key], modifiers=ModifierKeys.NOREPEAT)
			# await listener.remove_hotkey(Keycode[kill_tool_key], modifiers=ModifierKeys.NOREPEAT)
			await listener.remove_hotkey(Keycode[toggle_auto_combat_key], modifiers=ModifierKeys.NOREPEAT)
			# await listener.remove_hotkey(Keycode[forward_noclip_key], modifiers=ModifierKeys.NOREPEAT)
			# await listener.remove_hotkey(Keycode[up_noclip_key], modifiers=ModifierKeys.NOREPEAT)
			# await listener.remove_hotkey(Keycode[down_noclip_key], modifiers=ModifierKeys.NOREPEAT)
			await listener.remove_hotkey(Keycode[toggle_auto_dialogue_key], modifiers=ModifierKeys.NOREPEAT)
			await listener.remove_hotkey(Keycode[toggle_auto_sigil_key], modifiers=ModifierKeys.NOREPEAT)
			if not exclude_freecam:
				await listener.add_hotkey(Keycode[toggle_freecam_key], modifiers=ModifierKeys.NOREPEAT)
				await listener.add_hotkey(Keycode[toggle_freecam_key], modifiers=ModifierKeys.SHIFT | ModifierKeys.NOREPEAT)
			# await listener.remove_hotkey(Keycode[toggle_auto_questing_key], modifiers=ModifierKeys.NOREPEAT)


	async def foreground_client_switching():
		await asyncio.sleep(2)
		# enable hotkeys if a client is selected, disable if none are
		while True:
			await asyncio.sleep(0.1)
			if foreground_client == None and not freecam_status:
				logger.debug('Client not selected, stopping hotkey listener.')
				await disable_hotkeys()
				while foreground_client == None:
					await asyncio.sleep(0.1)
				logger.debug('Client selected, starting hotkey listener.')
				await enable_hotkeys()


	async def assign_foreground_clients():
		# assigns the foreground client and a list of background clients
		nonlocal foreground_client
		nonlocal background_clients
		while True:
			if not freecam_status:
				foreground_client_list = [c for c in walker.clients if c.is_foreground]
				if len(foreground_client_list) > 0:
					foreground_client = foreground_client_list[0]
				else:
					foreground_client = None
				background_clients = [c for c in walker.clients if not c.is_foreground]
			await asyncio.sleep(0.1)


	async def speed_switching():
		# handles updating the speed multiplier if a zone or realm change happens
		nonlocal client_speeds
		for c in walker.clients:
			client_speeds[c] = await c.client_object.speed_multiplier()
		modified_speed = (int(speed_multiplier) - 1) * 100
		while True:
			await asyncio.sleep(0.1)
			# if speed multiplier is enabled, rewrite the multiplier value if the speed changes. If speed mult is disabled, rewrite the original untouched speed multiplier only if it equals the multiplier speed
			if not freecam_status:
				if speed_status:
					await asyncio.sleep(0.1)
					for c in walker.clients:
						if speed_status and await c.client_object.speed_multiplier() != modified_speed:
							await c.client_object.write_speed_multiplier(modified_speed)
				else:
					for c in walker.clients:
						if await c.client_object.speed_multiplier() == modified_speed:
							await c.client_object.write_speed_multiplier(client_speeds[c])


	async def is_client_in_combat_loop():
		async def async_in_combat(client: Client):
			# battle = SlackFighter(client)
			# while True:
			# 	if await battle.is_fighting():
			# 		client.in_combat = True
			# 	else:
			# 		client.in_combat = False
			# 	await asyncio.sleep(0.1)
			while True:
				if not freecam_status:
					client.in_combat = await client.in_battle()
				await asyncio.sleep(0.1)
				

		await asyncio.gather(*[async_in_combat(p) for p in walker.clients])


	async def combat_loop():
		# waits for combat for every client and handles them seperately.
		async def async_combat(client: Client):
			while True:
				await asyncio.sleep(1)
				if client in walker.clients and not freecam_status:
					while ((not client.in_combat) or not combat_status) and client in walker.clients:
						await asyncio.sleep(1)
					if client.in_combat and combat_status and client in walker.clients:
						logger.debug(f'Client {client.title} in combat, handling combat.')
						battle = SlackFighter(client)
						await battle.wait_for_combat()

		await asyncio.gather(*[async_combat(p) for p in walker.clients])


	async def dialogue_loop():
		# auto advances dialogue for every client, individually and concurrently
		advance_dialog_path = ['WorldView', 'wndDialogMain', 'btnRight']
		decline_quest_path = ['WorldView', 'wndDialogMain', 'btnLeft']
		async def async_dialogue(client: Client):
			while True:
				if dialogue_status and not freecam_status:
					if await is_visible_by_path(client, advance_dialog_path):
						if await is_visible_by_path(client, decline_quest_path):
							await client.send_key(key=Keycode.ESC)
							await asyncio.sleep(0.1)
							await client.send_key(key=Keycode.ESC)
						else:
							await client.send_key(key=Keycode.SPACEBAR)
				await asyncio.sleep(0.1)

		await asyncio.gather(*[async_dialogue(p) for p in walker.clients])


	# async def questing_loop():
	# 	# Auto questing on a per client basis.
	# 	# TODO: Team logic for auto questing, absolutely no clue how I'll handle this, so this is either a notfaj or future slack problem
	# 	async def async_questing(client: Client):
	# 		while True:
	# 			await asyncio.sleep(1)
	# 			if client in walker.clients and questing_status:
	# 				logger.debug(f'Client {client.title} - Handling questing.')
	# 				battle = SlackQuester(client, questing_status)
	# 				# TODO: Put SlackQuester's loop function here

	# 	await asyncio.gather(*[async_questing(p) for p in walker.clients])


	async def sigil_loop():
		# Auto sigil on a per client basis.
		async def async_sigil(client: Client):
			while True:
				await asyncio.sleep(1)
				if client in walker.clients and client.sigil_status and not freecam_status:
					sigil = SlackSigil(client)
					await sigil.farm_sigil()
		
		await asyncio.gather(*[async_sigil(p) for p in walker.clients])


	async def anti_afk_loop():
		# anti AFK implementation on a per client basis.
		async def async_anti_afk(client: Client):
			# await client.root_window.debug_print_ui_tree()
			# print(await client.body.position())
			while True:
				await asyncio.sleep(0.1)
				if not freecam_status:
					client_xyz = await client.body.position()
					await asyncio.sleep(350)
					client_xyz_2 = await client.body.position()
					if calc_Distance(client_xyz, client_xyz_2) < 5 and not await client.in_combat:
						logger.debug(f"Client {client.title} - AFK client detected, moving slightly.")
						await client.send_key(key=Keycode.A)
						await asyncio.sleep(0.1)
						await client.send_key(key=Keycode.D)
		await asyncio.gather(*[async_anti_afk(p) for p in walker.clients])


	await asyncio.sleep(0)
	listener.start()
	await asyncio.sleep(0)
	walker = ClientHandler()
	# walker.clients = []
	walker.get_new_clients()
	await asyncio.sleep(0)
	await asyncio.sleep(0)
	print('SlackTool now has a discord! Join here:')
	print('https://discord.gg/59UrPJwYDm')
	print('Be sure to join the WizWalker discord, as this project is built using it. Join here:')
	print('https://discord.gg/JHrdCNK')
	print('\n')
	logger.debug(f'Welcome to SlackTool version {tool_version}!')


	async def hooking_logic(default_logic : bool = False):
		await asyncio.sleep(0.1)
		if not default_logic:
			if not walker.clients:
				logger.debug('Waiting for a Wizard101 client to be opened...')
				while not walker.clients:
					walker.get_new_clients()
					await asyncio.sleep(0)
					await asyncio.sleep(1)

			# p1, p2, p3, p4 = [*clients, None, None, None, None][:4]
			# child_clients = clients[1:]
			for i, p in enumerate(walker.clients, 1):
				title = 'p' + str(i)
				p.title = title

			logger.debug('Activating hooks for all clients, please be patient...')
			try:
				await asyncio.gather(*[p.activate_hooks() for p in walker.clients])
			except wizwalker.errors.PatternFailed:
				logger.critical('Error occured in the hooking process. Please restart all Wizard101 clients.')
				# sg.Popup('SlackTool Error', 'Error occured in the hooking process. Please restart all Wizard101 clients.', non_blocking=True)
				clients_check = walker.clients
				async def refresh_clients(delay: float = 0.5):
					walker.remove_dead_clients()
					walker.get_new_clients()
					await asyncio.sleep(delay)

				logger.debug('Waiting for all Wizard101 clients to be closed...')
				while walker.clients:
					await refresh_clients()
					await asyncio.sleep(0.1)
				logger.debug('Waiting for all previous Wizard101 clients to be reopened...')
				while not walker.clients:
					await refresh_clients()
					await asyncio.sleep(0.1)
				while len(walker.clients) != len(clients_check):
					await refresh_clients()
					await asyncio.sleep(0.1)
				await hooking_logic()
	
	await hooking_logic()


	logger.debug('Hooks activated. Setting up hotkeys...')
	# set initial speed for speed multipler so it knows what to reset to. Instead I should just have this track changes in speed multiplier per-client.
	client_speeds = {}
	for p in walker.clients:
		client_speeds[p] = await p.client_object.speed_multiplier()
		p.combat_status = False
		p.questing_status = False
		p.sigil_status = False
		p.use_team_up = use_team_up


	await listener.add_hotkey(Keycode[kill_tool_key], kill_tool_hotkey, modifiers=ModifierKeys.NOREPEAT)
	await enable_hotkeys()
	logger.debug('Hotkeys ready!')
	try:
		foreground_client_switching_task = asyncio.create_task(foreground_client_switching())
		assign_foreground_clients_task = asyncio.create_task(assign_foreground_clients())
		speed_switching_task = asyncio.create_task(speed_switching())
		combat_loop_task = asyncio.create_task(combat_loop())
		dialogue_loop_task = asyncio.create_task(dialogue_loop())
		anti_afk_loop_task = asyncio.create_task(anti_afk_loop())
		sigil_loop_task = asyncio.create_task(sigil_loop())
		in_combat_loop_task = asyncio.create_task(is_client_in_combat_loop())
		# questing_loop_task = asyncio.create_task(questing_loop()))
		while True:
			await asyncio.wait([foreground_client_switching_task, speed_switching_task, combat_loop_task, assign_foreground_clients_task, dialogue_loop_task, anti_afk_loop_task, sigil_loop_task, in_combat_loop_task])

	finally:
		await tool_finish()

if __name__ == "__main__":
	config_update_rewrite()
	auto_update_rewrite()
	current_log = logger.add(f"logs/{tool_name} - {generate_timestamp()}.log", encoding='utf-8', enqueue=True)
	if not os.path.exists(r'C:\Program Files (x86)\Steam\steamapps\common\Wizard101'):
		utils.override_wiz_install_location(r'C:\ProgramData\KingsIsle Entertainment\Wizard101')
	else:
		utils.override_wiz_install_location(r'C:\Program Files (x86)\Steam\steamapps\common\Wizard101')
	asyncio.run(main())
