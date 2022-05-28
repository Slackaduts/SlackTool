import asyncio
from wizwalker import Keycode, Client, XYZ
from loguru import logger
from teleport_math import navmap_tp, calc_FrontalVector, are_xyzs_within_threshold
from utils import get_window_from_path, is_visible_by_path, click_window_by_path, wait_for_zone_change, auto_potions, logout_and_in, is_free
from sprinty_client import SprintyClient


quest_name_path =[ "WorldView", "windowHUD" , "QuestHelperHud", "ElementWindow", "" ,"txtGoalName"]
team_up_button_path = ['WorldView', 'NPCRangeWin', 'imgBackground', 'TeamUpButton']
team_up_confirm_path = ['WorldView', 'TeamUpConfirmationWindow', 'TeamUpConfirmationBackground', 'TeamUpButton']
npc_range_path = ['WorldView', 'NPCRangeWin']
advance_dialog_path = ['WorldView', 'wndDialogMain', 'btnRight']
dungeon_warning_path = ['MessageBoxModalWindow', 'messageBoxBG', 'messageBoxLayout', 'AdjustmentWindow', 'Layout', 'centerButton']
cancel_chest_roll_path = ['WorldView', 'Container', 'background', '', 'CancelButton']


class SlackSigil():
	def __init__(self, client: Client):
		self.client = client


	async def record_sigil(self):
		self.sigil_xyz = await self.client.body.position()
		self.sigil_zone = await self.client.zone_name()
		# mark location
		await self.client.send_key(Keycode.PAGE_DOWN, 0.1)


	async def get_quest_name(self):
		while not await is_free(self.client):
			await asyncio.sleep(0.1)
		quest_name_window = await get_window_from_path(self.client.root_window, quest_name_path)
		while not await is_visible_by_path(self.client, quest_name_path):
			await asyncio.sleep(0.1)
		quest_objective = await quest_name_window.maybe_text()
		return quest_objective


	async def record_quest(self):
		self.original_quest = await self.get_quest_name()


	async def team_up(self):
		# Wait for team up to be visible in case it isnt
		while not await is_visible_by_path(self.client, team_up_button_path):
			await asyncio.sleep(0.25)
		# click team up button
		await click_window_by_path(self.client, team_up_button_path, True)
		await asyncio.sleep(0.5)
		if await is_visible_by_path(self.client, team_up_confirm_path):
			await click_window_by_path(self.client, team_up_confirm_path, True)
			while not await self.client.is_loading():
				await asyncio.sleep(0.1)
			await wait_for_zone_change(self.client, True)
		else:
			while not await self.client.is_loading():
				await asyncio.sleep(0.1)
			await wait_for_zone_change(self.client, True)


	async def join_sigil(self):
		# joins sigil using
		if self.client.use_team_up:
			await self.team_up()
		else:
			await self.client.send_key(Keycode.X, seconds=0.1)
			await asyncio.sleep(0.5)
			if await is_visible_by_path(self.client, dungeon_warning_path):
				await self.client.send_key(Keycode.ENTER, 0.1)
			await wait_for_zone_change(self.client)


	async def go_through_zone_changes(self):
		while await self.client.zone_name() != self.sigil_zone:
			# teleport to quest, will NOT work if the user has no quest up
			quest_xyz = await self.client.quest_position.position()
			await navmap_tp(self.client, quest_xyz)

			# walk forward until we get a zone change
			while not await self.client.is_loading():
				await self.client.send_key(Keycode.W, seconds=0.1)
			await wait_for_zone_change(self.client, True)
			await asyncio.sleep(1)


	async def collect_wisps(self):
		# Collects all the wisps in the current area, only works within the entity draw distance.
		wisps = []
		wisps += await SprintyClient(self.client).get_health_wisps()
		wisps += await SprintyClient(self.client).get_mana_wisps()
		wisps += await SprintyClient(self.client).get_gold_wisps()
		if wisps:
			for entity in wisps:
				wisp_xyz = await entity.location()
				await self.client.teleport(wisp_xyz)
				await asyncio.sleep(0.1)


	async def wait_for_combat_finish(self, await_combat: bool = True, collect_wisps: bool = True):
		if await_combat:
			while not self.client.in_combat:
				await asyncio.sleep(0.1)
		while self.client.in_combat:
			await asyncio.sleep(0.1)
		if collect_wisps:
			await self.collect_wisps()


	async def movement_checked_teleport(self, xyz: XYZ):
		current_xyz = await self.client.body.position()
		frontal_xyz = await calc_FrontalVector(client=self.client, speed_constant=200, speed_adjusted=False)
		await self.client.goto(frontal_xyz)
		if not await are_xyzs_within_threshold(current_xyz, await self.client.body.position(), threshold=20):
			await self.client.teleport(xyz)


	async def farm_sigil(self):
		# Main loop for farming a sigil, includes setup

		while not await is_visible_by_path(self.client, team_up_button_path):
			await asyncio.sleep(1)
		logger.debug(f'Client {self.client.title} at sigil, farming it.')
		await self.record_sigil()
		await self.record_quest()

		while self.client.sigil_status:
			while not await is_visible_by_path(self.client, team_up_button_path):
				await asyncio.sleep(0.1)

			# Automatically use and buy potions if needed
			await auto_potions(self.client)

			# Join sigil and wait for the zone to change either via team up or sigil countdown
			await self.join_sigil()
			
			# if quest objective is same, we know it's a short dungeon, most likely with 1 room
			if await self.get_quest_name() == self.original_quest:
				start_xyz = await self.client.body.position() 
				second_xyz = await calc_FrontalVector(self.client, speed_constant=200, speed_adjusted=False)
				await SprintyClient(self.client).tp_to_closest_mob()

				await self.wait_for_combat_finish()

				await asyncio.sleep(0.1)

				after_xyz = await calc_FrontalVector(self.client, speed_constant=450, speed_adjusted=False)

				await self.collect_wisps()

				await self.client.teleport(after_xyz)
				await asyncio.sleep(0.1)
				while True:
					await self.client.goto(second_xyz.x, second_xyz.y)
					await asyncio.sleep(0.1)
					await self.client.goto(start_xyz.x, start_xyz.y)
					past_zone_change_xyz = await calc_FrontalVector(self.client, speed_adjusted=False)
					await self.client.goto(past_zone_change_xyz.x, past_zone_change_xyz.y)
					counter = 0
					while not await self.client.is_loading() and counter < 35:
						await asyncio.sleep(0.1)
						counter += 1
					if counter >= 35:
						await self.client.teleport(after_xyz)
						pass
					else:
						break

				logger.debug(f'Client {self.client.title} - Awaiting loading')
				while await self.client.is_loading():
					await asyncio.sleep(0.1)

			else:
				# TODO: Logic for dungeons with questlines
				while True:
					await asyncio.sleep(1)
					if await is_free(self.client):
						quest_xyz = await self.client.quest_position.position()
						if await self.get_quest_name() != self.original_quest:
							try:
								await navmap_tp(self.client, quest_xyz)
							except ValueError:
								pass

						await asyncio.sleep(0.25)

						if await is_visible_by_path(self.client, cancel_chest_roll_path):
							click_window_by_path(self.client, cancel_chest_roll_path)

						if await is_visible_by_path(self.client, npc_range_path):
							await self.client.send_key(Keycode.X, 0.1)

						if await self.get_quest_name() == self.original_quest:
							await asyncio.sleep(1)
							break

				while not await is_free(self.client):
					await asyncio.sleep(0.1)
				await logout_and_in(self.client)

			while not await is_free(self.client):
				await asyncio.sleep(0.1)
			await asyncio.sleep(1)
			await self.client.teleport(self.sigil_xyz)
			await self.client.send_key(Keycode.A, 0.1)