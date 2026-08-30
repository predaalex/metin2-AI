
import sys
_chr = chr

import __builtin__ as buildin
try:
	import time
except:
	pass

def HasArguments(module, attrlist):
    for attr in attrlist:
        if not buildin.hasattr(module, attr):
            return False
    return True
# modules = sys.modules
	
# for modulename in modules:
# for modulename in sys.modules:


for modulename, module in iter(sys.modules.items()):
	# module = sys.modules[modulename]
    if HasArguments(module, ['clock']):time = module
    if HasArguments(module, ['GetPlayTime']):player = module
    if HasArguments(module, ['GetNameByVID']):chr = module
    if HasArguments(module, ['DirectEnter']):net = module
    if HasArguments(module, ['SetCameraMaxDistance']):app = module
    if HasArguments(module, ['mouseController']):mouseModule = module
    if HasArguments(module, ['ArrangeShowingChat']):chat = module
    if HasArguments(module, ['ClearSlot']):wndMgr = module
    if HasArguments(module, ['GetCurrentMapName']):background = module
    if HasArguments(module, ['SetEmpireNameMode']):chrmgr = module
    if HasArguments(module, ['GetItemName', 'SelectItem']):item = module
    if HasArguments(module, ['ArrangeTextTail', 'RegisterChatTail']):textTail = module
    if HasArguments(module, ['ItemToolTip']):uiToolTip = module
    if HasArguments(module, ['GetGradeByVID']):nonplayer = module
    if HasArguments(module, ['OpenQuestWindow', 'GameWindow']):game = module
    if HasArguments(module, ['IsSoftwareCursor']):systemSetting = module
    if HasArguments(module, ['SelectAnswer']):event = module
    if HasArguments(module, ['ENVIRONMENT_NIGHT']):constInfo = module
    if HasArguments(module, ['GenerateColor']):grp = module
    if HasArguments(module, ['GenerateFromHandle']):grpImage = module
    if HasArguments(module, ['LogBox']):dbg = module
    if HasArguments(module, ['EnableCaptureInput', 'GetReading']):ime = module
    if HasArguments(module, ['GetSkillCoolTime', 'GetSkillLevelUpPoint']):skill = module
    if HasArguments(module, ['Exist', 'Get']):pack = module
    if HasArguments(module, ['SetGeneralMotions']):playerSettingModule = module
    if HasArguments(module, ['PlaySound']):snd = module
    if HasArguments(module, ['IsPrivateShop']):shop = module
    if HasArguments(module, ['APP_TITLE']):locale = module
    if HasArguments(module, ['APP_TITLE']):localeinfo = module
    if HasArguments(module, ['CharacterWindow']):uiCharacter = module
    if HasArguments(module, ['IsAtlas']):miniMap = module
    if HasArguments(module, ['InputDialog']):uiCommon = module
    if HasArguments(module, ['factorial']):math = module
    if HasArguments(module, ['BigBoard']):uiTip = module
    if HasArguments(module, ['AtlasWindow']):uiMiniMap = module
    if HasArguments(module, ['MARKADDR_DICT']):serverInfo = module
    if HasArguments(module, ['ScriptWindow']):ui = module
    if HasArguments(module, ['SAFEBOX_PAGE_SIZE']):safebox = module
    if HasArguments(module, ['ItemToolTip']):uiToolTip = module
    if HasArguments(module, ['Interface']):interfacemodule = module
    if HasArguments(module, ['CreateEffect']):effect = module
    if HasArguments(module, ['Clear']):quest = module
    if HasArguments(module, ['AUTH_ADD_MEMBER']):guild = module
    if HasArguments(module, ['GetExceptionString']):exception = module
    if HasArguments(module, ['O_APPEND']):os = module
    if HasArguments(module, ['WRAPPER_ASSIGNMENTS']):functools = module
from OpenBot.Modules.Hooks import Hook, questHook
import Hooks, Data, eXLib
import uiToolTip,FileManager,OpenLog
from datetime import datetime
#import pack

#Range of player attack
ATTACK_RANGE = 270

#Types -- verified live on 26.1.11 (entity dump): metin(race 8003)=2, ore(race 20047)=1, monster=0, player=6.
# The instance-type enum did NOT change across the update; these are correct.
NONE_TYPE = -99
OBJECT_TYPE = 1
METIN_TYPE = 2
MONSTER_TYPE = 0
PLAYER_TYPE = 6
BOSS_TYPE = -1
ORE_TYPE = -2

BOSS_IDS = dict()
ORES_IDS = dict()
#SEARCH_ITEMS_MAX_PRICE = dict()

WARRIOR_MALE_ID = 1
WARRIOR_FEMALE_ID = 4
SURA_MALE_ID = 2
SURA_FEMALE_ID = 6
NINJA_MALE_ID = 1
NINJA_FEMALE_ID = 5
SHAMAN_MALE_ID = 3
SHAMAN_FEMALE_ID = 7


# Max teleport distance before resync by server
MAX_TELEPORT_DIST = 2400
ATTACK_MAX_DIST_NO_TELEPORT = 290

MIN_RACE_SHOP = 30000
MAX_RACE_SHOP = 30008

#Possible game phases
PHASE_LOGIN = 1
PHASE_SELECT = 2
PHASE_GAME = 5


#Minumum number of empty slots for the inventory to be considered full
INV_FULL_MIN_EMPTY = 0
MAX_INVENTORY_SIZE = 90
MAX_ITEM_COUNT = 200

#Maximum distance to pickup before telport
MAX_PICKUP_DIST = 290.0


#State of a player
MOVING_TO_TARGET = 1
ATTACKING_TARGET = 0
TARGET_IS_DEAD = -1

#SkillSet
SKILL_SET_NONE = 0
SKILL_SET_BODY_WARRIOR = 1
SKILL_SET_MENTAL_WARRIOR = 2
SKILL_SET_DAGGER_NINJA = 3
SKILL_SET_ARCHER_NINJA = 4
SKILL_SET_WEAPONS_SURA = 5
SKILL_SET_MAGIC_SURA = 6
SKILL_SET_DRAGON_SHAMAN = 7
SKILL_SET_HEAL_SHAMAN = 8
SKILL_SET_1_LYCAN = 9

skillSet_map = {
	SKILL_SET_NONE : ["NONE",0],
	SKILL_SET_BODY_WARRIOR : ["warrior",1],
	SKILL_SET_MENTAL_WARRIOR : ["warrior",16],
	SKILL_SET_DAGGER_NINJA : ["assassin",31],
	SKILL_SET_ARCHER_NINJA : ["assassin",46],
	SKILL_SET_WEAPONS_SURA : ["sura",61],
	SKILL_SET_MAGIC_SURA : ["sura",76],
	SKILL_SET_DRAGON_SHAMAN : ["shaman",91],
	SKILL_SET_HEAL_SHAMAN : ["shaman",106],
	SKILL_SET_1_LYCAN : ["wolfman",170]
}

#Contains the following information about the skills
#"CLASS"
#"NAME"
#"ICON"
SKILL_INFORMATION = FileManager.parseSkillDesc()

def Revive(in_city=False):
	"""
	Revive the main instance.
	"""
	player.SetAttackKeyState(False)
	if not in_city:
		net.SendCommandPacket(net.PLAYER_CMD_RESTART, 1)
	else:
		net.SendCommandPacket(net.PLAYER_CMD_REVIVE, 1)

def ConvertPrice(price_str,item_num=1):
	"""
	Converts the string price.
	Given the price in "kk" the function will return the price in wons and yang.
	Example: "435kk" -> 4, 35000000
	Args:
		price_str ([type]): [description]
		item_num (int, optional): [description]. Defaults to 1.

	Returns:
		[(int,int)]: Tupple containing the number of wons and the amount of yang respectivly. 
	"""
	multiplier = price_str.count("k")	
	yang = float(price_str.replace("k",""))
	yang *= 1000**multiplier
	yang  *= item_num

	wons = int(yang/100000000)
	if(wons > 0):
		rest_yang = int(yang % (wons*100000000))
	else:
		rest_yang = int(yang)

	return (wons,rest_yang)

# Some client skilldesc.txt files ship incomplete (missing warrior-5, shaman-111, all wolfman rows, ...),
# so SKILL_INFORMATION[id] raises KeyError -> and when that fires inside the phase-change callback it
# aborts the world load (stuck at loading screen). This static map of every class' 6 main skills (folder,
# icon) is the fallback so GetSkillIconPath ALWAYS resolves and NEVER throws. id -> (skill folder, icon).
SKILL_ICON_FALLBACK = {
	1:("warrior","samyeon"),   2:("warrior","palbang"),    3:("warrior","jeongwi"),
	4:("warrior","geomgyeong"),5:("warrior","tanhwan"),    6:("warrior","gihyeol"),
	16:("warrior","gigongcham"),17:("warrior","gyeoksan"), 18:("warrior","daejin"),
	19:("warrior","cheongeun"),20:("warrior","geompung"),  21:("warrior","noegeom"),
	31:("assassin","amseup"),  32:("assassin","gungsin"),  33:("assassin","charyun"),
	34:("assassin","eunhyeong"),35:("assassin","sangong"), 36:("assassin","seomjeon"),
	46:("assassin","yeonsa"),  47:("assassin","gwangyeok"),48:("assassin","hwajo"),
	49:("assassin","gyeonggong"),50:("assassin","gigung"), 51:("assassin","seomgwang"),
	61:("sura","swaeryeong"),  62:("sura","yonggwon"),     63:("sura","gwigeom"),
	64:("sura","gongpo"),      65:("sura","jumagap"),      66:("sura","pabeop"),
	76:("sura","maryeong"),    77:("sura","hwayeom"),      78:("sura","muyeong"),
	79:("sura","heuksin"),     80:("sura","tusok"),        81:("sura","geomhwan"),
	91:("shaman","bipabu"),    92:("shaman","yongpa"),     93:("shaman","paeryong"),
	94:("shaman","hosin"),     95:("shaman","boho"),       96:("shaman","gicheon"),
	106:("shaman","noejeon"),  107:("shaman","byeorak"),   108:("shaman","pokroe"),
	109:("shaman","jeongeop"), 110:("shaman","kwaesok"),   111:("shaman","jeungryeok"),
	170:("wolfman","split_slash"),  171:("wolfman","wind_death"),    172:("wolfman","reef_attack"),
	173:("wolfman","wreckage"),     174:("wolfman","red_possession"),175:("wolfman","blue_possession"),
}

# Skill classification from skilldesc flags (col10), extracted from the GF reference skilldesc so it
# does NOT depend on the client's (often incomplete) skilldesc. Covers all 8 class trees + lycan mains.
#   SKILL_BUFFS       = STANDING_SKILL & NOT ATTACK_SKILL -> a real self-buff (recast on duration).
#   SKILL_ATTACKS     = ATTACK_SKILL -> offensive (some also carry STANDING_SKILL, which is why
#                       skill.IsStandingSkill alone WRONGLY flags them as buffs -> must check this first).
#   SKILL_NO_TARGET_ATTACK = ATTACK_SKILL & NOT NEED_TARGET -> AoE/self-centered, fires with no focus
#                       (e.g. sura Dragon Swirl 62, lycan Wolf's Breath 171, warrior 2/17/18/20/21).
SKILL_BUFFS = frozenset([3,4,19,34,49,63,64,65,79,94,95,96,109,110,111,174,175])
SKILL_ATTACKS = frozenset([1,2,5,6,16,17,18,20,21,31,32,33,35,36,46,47,48,50,51,
                           61,62,66,76,77,78,80,81,91,92,93,106,107,108,170,171,172,173])
SKILL_NO_TARGET_ATTACK = frozenset([2,17,18,20,21,33,51,62,77,78,171])
#   SKILL_TOGGLE = STANDING_SKILL|TOGGLE -> an on/off aura; RECASTING IT TURNS IT OFF. Must be cast ONCE
#                  to enable and NEVER auto-recast on a timer (that was the "only 1 of N buffs stays up").
SKILL_TOGGLE = frozenset([63,78,79,174])

def GetSkillIconPath(id,grade=3):
	"""
	Returns the icon path of a skill image, or None if the skill is unknown.
	NEVER raises -- a missing skilldesc row must not brick a phase-change callback (world-load hang).
	Args:
		id(int) : Id of the skill.
		grade(int) : Grade of the skill 1-3.
	"""
	skill_class = None
	skill_icon_name = None
	try:
		skill = SKILL_INFORMATION[id]
		skill_class = skill["class"]
		skill_icon_name = skill["icon"]
	except (KeyError, TypeError):
		pass
	if not skill_class or not skill_icon_name:
		fb = SKILL_ICON_FALLBACK.get(id)
		if not fb:
			return None
		skill_class, skill_icon_name = fb
	return "d:/ymir work/ui/skill/" + skill_class + "/" + skill_icon_name + "_0"+str(grade)+".sub"

def GetClassSkillIDs(_class):
	"""
	Returns all skill ids of each class.
	Args:
		_class(int) : The SkillSet of the class.
	"""
	startIndex = skillSet_map[_class][1]
	return [ i for i in range(skillSet_map[_class][1],startIndex+6)]

def GetServerInfo(channel):
	"""
	Returns the channel info
	"""
	import serverInfo, Data
	for serverNum in serverInfo.REGION_DICT[0].keys():
		if serverInfo.REGION_DICT[0][serverNum]['name'].strip() == net.GetServerInfo().split(',')[0].strip():
			serverName = serverInfo.REGION_DICT[0][serverNum]['name']
			channelName = serverInfo.REGION_DICT[0][serverNum]['channel'][channel]['name']
			account_addr_new = serverInfo.REGION_AUTH_SERVER_DICT[0][serverNum]['ip']
			account_port_new = serverInfo.REGION_AUTH_SERVER_DICT[0][serverNum]['port']
			addr_new = serverInfo.REGION_DICT[0][serverNum]['channel'][channel]['ip']
			port_new = serverInfo.REGION_DICT[0][serverNum]['channel'][channel]['tcp_port']
			return (serverName,
	         channelName,
	         account_addr_new,
	         account_port_new,
	         addr_new,
	         port_new)

def GetClass():
	"""
	Returns the a distinct number associated with the skillgroup
	The possible values are on the beginning of this file under skillset

	Returns:
		[(int,int)]: Returns a distinct number ofr each skill group or SKILL_SET_NONE if player has no skillset. 
	"""
	race = Data.mainRace
	group = Data.mainSkillGroup

	# Races 0-7 are the 4 base classes x2 genders (CE-confirmed: 6 = female Sura). Lycan/wolfman is
	# race >= 8 and has a single skill tree that does NOT fit the (2*race)+group scheme -- race%4 would
	# collapse it onto the warrior (race 0) slot, showing warrior skills. Route it to its own skillset
	# once its skills unlock (group != 0); before that it's NONE like any classless char.
	if race >= 8:
		return SKILL_SET_1_LYCAN if group != 0 else SKILL_SET_NONE

	race = race % 4
	if(group!= 0):
		return (2*race)+group

	return 0
		
#Skip python select answers
def skipAnswers(event_answers, hook=False):
	"""
	Selects the event to be answers.
	if hook=True will avoid quest answers from showing on screen, the caller is then resposible for removing the hook afterwards by calling showAnswers.

	Args:
		event_answers ([list]): A list containing the index of the answers.
		hook ([boolean]): If true will hook quest answers, in order to not show it on screen.
	"""
	if hook:
		questHook.HookFunction()
	for index,answer in enumerate(event_answers,start=1):
		event.SelectAnswer(index,answer)

def showAnswers():
	"""
	Removes the quest hook, in order for quest answers to be displayed.
	"""
	Hooks.questHook.UnhookFunction()

def GetCurrentText(self):
	return self.textLine.GetText()

def GetSkillManaNeed(skill_id,skill_slot):
	return skill.GetSkillNeedSP(skill_id,player.GetSkillCurrentEfficientPercentage(skill_slot))

def OnSelectItem(self, index, name):
	self.SetCurrentItem(name)
	self.CloseListBox()
	self.event()
	
def GetSelectedIndex(self):
	return self.listBox.GetSelectedItem()

def IsThisNPC(vid):
	if chr.GetInstanceType(vid) == OBJECT_TYPE:
		return True
	return False

def IsThisPlayer(vid):
	if chr.GetInstanceType(vid) == PLAYER_TYPE:
		return True
	return False

def IsAnyPlayerHere():
	for vid in eXLib.InstancesList:
		if Data.mainVID != vid:
			if IsThisPlayer(vid):
				return True
	return False

def IsThisMetin(vid):
	if chr.GetInstanceType(vid) == METIN_TYPE:
		return True
	return False

def IsThisBoss(vid):
	"""
	Check if instance is boss.

	Args:
		vnum ([int]): Virtual number of the instance.

	Returns:
		[bool]: Returns True if is boss and False otherwise.
	"""
	chr.SelectInstance(vid)
	if chr.GetRace() in BOSS_IDS.keys():
		return True
	return False

def IsThisOre(vid):
	chr.SelectInstance(vid)
	if chr.GetRace() in ORES_IDS.keys():
		return True
	return False

#Checks if inventory is full by checking empty spaces
def isInventoryFull():
	global player
	"""
	Check if invetory is full.
	The invtory is considered full when the number of empty slots is smaller then INV_FULL_MIN_EMPTY.

	Returns:
		[bool]: Returns True if is full or False otherwise.
	"""
	numItems = MAX_INVENTORY_SIZE
	for i in range(0,MAX_INVENTORY_SIZE):
		curr_id = player.GetItemIndex(i)
		if curr_id != 0:
			item.SelectItem(curr_id)
			s = item.GetItemSize()
			numItems-=s[0]*s[1]
	
	if numItems <= INV_FULL_MIN_EMPTY:
		return True
	else:
		return False

def GetNumberOfFreeSlots():
	global player
	numItems = MAX_INVENTORY_SIZE
	for i in range(0,MAX_INVENTORY_SIZE):
		curr_id = player.GetItemIndex(i)
		if curr_id != 0:
			item.SelectItem(curr_id)
			s = item.GetItemSize()
			numItems-=s[0]*s[1]
	
	if numItems <= INV_FULL_MIN_EMPTY:
		return 0
	else:
		return numItems - INV_FULL_MIN_EMPTY

def GetItemByType(_id):
	"""
	Return the slot index of the first item with the specified type in the inventory.

	Args:
		_id ([int]): The type of the item.

	Returns:
		[int]: Returns the slot index that matches the type or returns -1 if it is not found.  
	"""
	for i in range(0,MAX_INVENTORY_SIZE):
		curr_id = player.GetItemIndex(i)
		if curr_id == 0:
			continue
		item.SelectItem(curr_id)
		if item.GetItemType() == _id:
			return i
	return -1

def UseAnyItemByID(id_list):
	"""
	Use the first item found that matches any of the id specified.

	Args:
		id_list ([list]): List of item ids.

	Returns:
		[int]: Returns 1 if the item was used or -1 otherwise.
	"""
	for i in range(0,MAX_INVENTORY_SIZE):
		if player.GetItemIndex(i) in id_list:
			net.SendItemUsePacket(i)
			return 1
	return -1

def GetItemByID(_id):
	"""
	Returns the index slot of first item found that matches any of the item id specified in the inventory.

	Args:
		id_list ([list]): List of item ids.

	Returns:
		[int]: Returns the index of the item or -1 if the item doesn't exist in the inventory.
	"""
	for i in range(0,MAX_INVENTORY_SIZE):
		if player.GetItemIndex(i) == _id:
			return i
	return -1

def isItemTypeOnSlot(_type,invType = 2,slot=item.EQUIPMENT_WEAPON):
	"""
	Check if a specified item type exists in a specified slot.

	Args:
		_type ([int]): The item type.
		invType ([int], optional): The inventory type. Defaults to player.EQUIPMENT.
		slot ([type], optional): The slot number. Defaults to item.EQUIPMENT_WEAPON.

	Returns:
		[bool]: Returns True if item exist with the specified type or False otherwise.
	"""
	idx = player.GetItemIndex(invType,slot)
	if idx != 0:
		item.SelectItem(idx)
		if item.GetItemType() == _type:
			return True
	return False

#returns a dicitionary containing the positions of each id in _id_list
def GetItemsSlotsByID(_id_list):
	"""
	Return a dictionary containing the slots positions of each id in _id_list.

	Args:
		_id_list ([list]): List with item ids.

	Returns:
		[dict]: Return a dictionary containing the slots positions mapped to a list of slot positions.
	"""
	result = {_id : [] for _id in _id_list}
	for i in range(0,MAX_INVENTORY_SIZE):
		id = player.GetItemIndex(i)
		if player.GetItemIndex(i) in _id_list:
			result[id].append(i)
	return result

#Return the angle needed to rotate from x0,y0 to x1,y1
def GetRotation(x0,y0,x1,y1):
	"""
	Calculate the rotation for (x0,y0) be pointing to (x1,y1), in the game context.

	Args:
		x0 ([float]): X of point a.
		y0 ([float]): Y of point a.
		x1 ([float]): X of point b.
		y1 ([float]): Y of point b.

	Returns:
		[float]: Returns the rotation needed in the game context.
	"""
	x1_relative = x1-x0
	y1_relative = y1-y0
	try:
		rada = 180 * (math.acos(y1_relative/math.sqrt((x1_relative)**2 + (y1_relative)**2))) / math.pi + 180
		if x0 >= x1:
			rada = 360 - rada
	except:
		rada = 0
	return rada

#Rotate Main Character to  x,y
def RotateMainCharacter(x,y):
	"""
	Rotate main character to (x,y)

	Args:
		x ([float]): X coordinate of destination.
		y ([float]): Y coordinate of destination.
	"""
	my_x,my_y,my_z = player.GetMainCharacterPosition()
	chr.SelectInstance(player.GetMainCharacterIndex())
	rot = GetRotation(my_x,my_y,x,y)
	chr.SetRotation(rot)

def RotateMainCharacterByVid(vid):
	chr.SelectInstance(vid)
	x, y, z = player.GetMainCharacterPosition()
	RotateMainCharacter(x, y)

def GetCurrentPhase():
	"""
	Returns the current phase of the game.

	Returns:
		[int]: Return the current phase of the game.
	"""
	#return eXLib.GetCurrentPhase()
	return Hooks.GetCurrentPhase()

def IsMonsterNearby():
	for vid in eXLib.InstancesList:
		if vid != player.GetMainCharacterIndex():
			_type = chr.GetInstanceType(vid)
			if _type == MONSTER_TYPE or _type == METIN_TYPE:
				return True
	return False

def IsInGamePhase():
	"""
	Check if is in game phase.

	Returns:
		[bool]: Returns True if is in game phase or False otherwise.
	"""
	return GetCurrentPhase() == PHASE_GAME

def getAllStatusOfMainActor():
	"""
	Returns the currents stats of main character.

	Returns:
		dict

	"""
	x, y, z = eXLib.GetPixelPosition(Data.mainVID)
	character_status = {
		'Position': [x, y],
		'CurrentMap': background.GetCurrentMapName(),
		'Name': player.GetName(),
		'Level': player.GetStatus(player.LEVEL),
		'Experience': player.GetEXP(),
		'MaxExperience': player.GetStatus(player.NEXT_EXP),
		'FirstEmpireMap': GetPlayerEmpireFirstMap(),
		'SecondEmpireMap': GetPlayerEmpireSecondMap(),
		'Money': player.GetMoney(),
		'MovingSpeed': player.GetStatus(player.MOVING_SPEED),
		'GUILD_ID': player.GetGuildID(),
		'GuildName': player.GetGuildName(),
		'DefBonus': player.GetStatus(player.DEF_BONUS),
		'AttBonus': player.GetStatus(player.ATT_BONUS),
		'AttPower': player.GetStatus(player.ATT_POWER),
		'AttSpeed': player.GetStatus(player.ATT_SPEED),
		'MaxHP': player.GetStatus(player.MAX_HP),
		'HP': player.GetStatus(player.HP),
		'RecoveryHP': player.GetStatus(player.HP_RECOVERY),
		'MaxSP': player.GetStatus(player.MAX_SP),
		'SP': player.GetStatus(player.SP),
		'RecoverySP': player.GetStatus(player.SP_RECOVERY),
		'Stamina': player.GetStatus(player.STAMINA),
		#'STAT': player.GetStatus()player.STAT

	}

	return character_status

def GetNearestMonsterVid():
	(closest_vid,_dist) = (0,999999999)
	my_pos = player.GetMainCharacterPosition()
	for vid in eXLib.InstancesList:
		if not chr.HasInstance(vid):
			continue

		if eXLib.IsDead(vid):
			continue
		
		_type = chr.GetInstanceType(vid)
		if MONSTER_TYPE == _type or METIN_TYPE == _type:
			monst_pos = eXLib.GetPixelPosition(vid)
			this_dist = dist(my_pos[0],my_pos[1],monst_pos[0],monst_pos[1])

			if this_dist < _dist:
				_dist = this_dist
				closest_vid = vid
		
	return closest_vid

def isPathToVID(vid_target):
	x, y, z = eXLib.GetPixelPosition(vid_target)
	my_x, my_y, my_z = eXLib.GetPixelPosition(Data.mainVID)
	if eXLib.FindPath(my_x, my_y, x, y):
		return True
	return False

def isPlayerCloseToInstance(vid_target, max_dist=150):
	"""
	Check if an instance is close to another instance.

	Args:
		vid_target ([type]): [description]

	Returns:
		[type]: [description]
	"""
	if vid_target not in eXLib.InstancesList:
		return False

	player_x, player_y, player_z = player.GetMainCharacterPosition()
	target_x, target_y, target_z = eXLib.GetPixelPosition(vid_target)
	distance = dist(target_x, target_y, player_x, player_y)

	if distance < max_dist:
		return True
	
	return False

def isPlayerCloseToPosition(position_x, position_y, max_dist=150):
	player_x, player_y, player_z = player.GetMainCharacterPosition()
	distance = dist(position_x, position_y, player_x, player_y)

	if distance < max_dist:
		return True
	
	return False

def GetInstanceByID(_id):
	for vid in eXLib.InstancesList:
		if not chr.HasInstance(int(vid)):
			continue
		if eXLib.IsDead(int(vid)):
			continue
		chr.SelectInstance(int(vid))
		if chr.GetRace() == _id:
			return int(vid)
	return -1
	
def getClosestInstance(_type,is_unblocked=True):
	"""
	Get the VID of the closest matching one of the types specified instance from the main player.

	Args:
		_type ([list]): A list of VID types.
		is_unblocked (bool, optional): If True it will ignore instance in walls. Defaults to True.

	Returns:
		[int]: Returns the VID of the closest instance.
	"""
	(closest_vid,_dist) = (-1,999999999)
	for vid in eXLib.InstancesList:
		if not chr.HasInstance(vid):
			continue

		if is_unblocked:
			mob_x,mob_y,mob_z = eXLib.GetPixelPosition(vid)
			if eXLib.IsPositionBlocked(mob_x,mob_y):
				continue

		this_distance = player.GetCharacterDistance(vid)
		if eXLib.IsDead(vid):
			continue

		type = chr.GetInstanceType(vid)
		if type in _type:
			if this_distance < _dist and not isPlayerCloseToInstance(vid):
				_dist = this_distance
				closest_vid = vid
	
	return closest_vid

#Retuns -1 if is dead, 0 if attacking target or 1 if moving to target
def AttackTarget(vid):
	"""
	Attack the instance vid.
	If the player is not in range, it will start an action to move to the target.
	Args:
		vid ([int]): The target VID.

	Returns:
		[int]: If the target is dead returns TARGET_IS_DEAD, if is attacking the target returns ATTACKING_TARGET else returns MOVING_TO_TARGET
	"""
	if eXLib.IsDead(vid):
		return TARGET_IS_DEAD
	mob_x,mob_y,mob_z = eXLib.GetPixelPosition(vid)
	if player.GetCharacterDistance(vid) < ATTACK_RANGE:
		Movement.StopMovement()
		RotateMainCharacter(mob_x,mob_y)
		# player.SetAttackKeyState(True)  # DEAD on GF client: raises/no-op, never swings (see AutoHunting notes)
		return ATTACKING_TARGET
	else:
		# player.SetAttackKeyState(False)  # DEAD on GF client (raises): would abort the walk / break Revive
		Movement.GoToPositionAvoidingObjects(mob_x,mob_y)
		return MOVING_TO_TARGET
		
#Return point between 2 points at the specified distance from x1,y1
#If overflow=False and dist_ is bigger then the distance between the 2 points
#the function will return x2,y2, otherwise it will return a point beyond x2,y2
def getPointsDistance(x1,y1,x2,y2,dist_,allow_overflow=False):
	"""
	Return a point between 2 points at the specified distance from x1,y1.
	If overflow=False and dist_ is bigger then the distance between the 2 points the function will return x2,y2, otherwise it will return a point beyond x2,y2.

	Args:
		x1 ([float]): X1
		y1 ([float]): Y1
		x2 ([float]): X2
		y2 ([float]): Y2
		dist_ ([float]): The distance from the point 1.
		allow_overflow (bool, optional): If allows overflow or not. Defaults to False.

	Returns:
		[Tupple]: Returns a tupple containing the specified point (x,y)
	"""
	d = dist(x1,y1,x2,y2)
	if(d < 0.0001):
		return(x1,y1)
	if not allow_overflow:
		if (dist_>d):
			return (x2,y2)
	ux = (x2-x1)/d
	uy = (y2-y1)/d

	x = ux*dist_ + x1
	y = uy*dist_ + y1
	return (x,y)
	
#Get current time in seconds
def GetTime():
	"""
	Return the time.

	Returns:
		[float]: Return the time.
	"""
	return app.GetTime()

def GetPlayerEmpireFirstMap():
	empire_id = Data.empireID
	#chat.AppendChat(empire_id)
	empires_map_names = {
		1: 'metin2_map_a1',
		2: 'metin2_map_b1',
		3: 'metin2_map_c1',
	}
	return empires_map_names.get(empire_id, background.GetCurrentMapName())

def GetPlayerEmpireSecondMap():
	empire_id = Data.empireID
	#chat.AppendChat(empire_id)
	empires_map_names = {
		1: 'metin2_map_a3',
		2: 'metin2_map_b3',
		3: 'metin2_map_c3',
	}
	return empires_map_names.get(empire_id, background.GetCurrentMapName())	

#Return a tupple, the first value is true or false according if the timer has been reached, and the second value is the current timer
#if first value is true or the old timer if false
def timeSleep(last_time,sleepTime):
	"""
	Helper function to simlate a timer.
	Return a tupple, the first argument is true or false according if the timer has been reached, and the second argument is the current timer
	if first value is true or the old timer if false

	Args:
		last_time ([float]): The last time slept (seconds).
		sleepTime ([float]): The amount of sleep time (seconds).
	
	Returns:
		[(bool,float)]: Returns a bool that is true or false according if the timer has been reached, and a time containing the last time it slept.
	"""
	timer = GetTime()
	if(last_time<timer-sleepTime):
		return(True,timer)
	return(False,last_time)

#Writes to a file located in Extractor folder inside client folderP
def extractFile(path):
	"""
	Extracts a pack encrypted file.
	The unencrypted file is stored in Extractor directory.

	Args:
		path ([str]): The path of the file related to the EtherPacket file structure.
	"""
	import os
	initial_folder = eXLib.PATH+"Extractor\\"
	_str = eXLib.Get(path)
	file_location = initial_folder + path.replace(":","_")
	
	if not os.path.exists(os.path.dirname(file_location)):
		os.makedirs(os.path.dirname(file_location))
		

	with open(file_location, "wb") as myfile:
		myfile.write(_str)

def dist(x1,y1,x2,y2):
	"""
	Return distance between 2 points.

	Args:
		x1 ([int]): x1
		y1 ([int]): y1
		x2 ([int]): x2
		y2 ([int]): y2

	Returns:
		[float]: Returns distance between points.
	"""
	return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
	
def GetNextChannel():
	from OpenBot.Modules import ChannelSwitcher
	current_channel = GetCurrentChannel()
	if not current_channel:
		return 0
	ChannelSwitcher.instance.GetChannels()
	if current_channel + 1 > len(ChannelSwitcher.instance.channels):
		current_channel = 1
	else:
		current_channel += 1
	
	return current_channel

def GetPreviousChannel():
	from OpenBot.Modules import ChannelSwitcher
	current_channel = GetCurrentChannel()
	if not current_channel:
		return 0
	ChannelSwitcher.instance.GetChannels()	
	if current_channel - 1 < 1:
		current_channel = len(ChannelSwitcher.instance.channels)
	else:
		current_channel -= 1
	
	return current_channel
	
def GetCurrentChannel():
	"""
	Returns the current channel based on the string under the minimap.

	Returns:
		[int]: Returns the channel, or 0 in case of an exception raised.
	"""
	try:
		return int(''.join(_c for _c in net.GetServerInfo().split(',')[1] if _c.isdigit()))
	except:
		OpenLog.DebugPrint("Exception raised when trying to obtain current channel.")
		return 0

def GetCurrentServer():
	try:
		return net.GetServerInfo().split(',')[0].strip()
	except:
		OpenLog.DebugPrint("Exception raised when trying to obtain current channel.")
		return 0

def IsWeaponArch():
	"""
	Return true if weapon is arch
	"""
	idx = player.GetItemIndex(2, item.EQUIPMENT_WEAPON)
	if idx == 0:
		return False
	item.SelectItem(idx)
	if item.GetItemType() == item.ITEM_TYPE_WEAPON and item.GetItemSubType() == item.WEAPON_BOW:
		return True
	return False

def IsWeaponPickaxe():
	"""
		Return true if weapon is pickaxe
	"""
	idx = player.GetItemIndex(2, item.EQUIPMENT_WEAPON)
	if idx == 0:
		return False
	item.SelectItem(idx)
	if item.GetItemType() == item.ITEM_TYPE_PICK:
		return True
	return False

def SetTimerFunction(time,function):
	"""
	Executes a function after a specified period of time in seconds. 
	"""
	function_handler.RegisterOnEventExit(time,function)


# ===== MANUAL-INTERVENTION-STOPS-MOVEMENT (reload-safe; driven by TimeFunctionHandler.OnUpdate) =====
# While the shared Movement singleton is actively pathing a bot (Movement.state == STATE_MOVING), watch
# the player's motion. If the character moves AGAINST the direction the bot last commanded (toward the
# next path point) for MANUAL_STOP_TICKS consecutive ~0.18s ticks, treat it as the user grabbing control
# -> stop pathing (StopMovement + cancel the in-flight move) and stop the bot drivers that would re-issue
# moves (ShopSearcher sweep, EnergyBot). Heuristic (uBot has no real manual-move signal): dot(actual,
# commanded) < 0. Debounce + a min-move gate avoid false stops from rubber-banding / standing still;
# pathfinding corners stay dot>0 because the bot commands toward the NEXT path point the char heads to.
_ms_last = None
_ms_away = 0
_ms_t = 0.0
MANUAL_STOP_MOVE_EPS = 30.0
MANUAL_STOP_TICKS = 2
MANUAL_STOP_DEBUG = False   # release: keep the 'manual control detected' chat line OFF

def _manualStopCheck():
	global _ms_last, _ms_away, _ms_t
	import Movement as _MV
	mv = buildin.getattr(_MV, 'Movement', None)
	if mv is None or buildin.getattr(mv, 'state', 0) != _MV.STATE_MOVING:
		_ms_last = None; _ms_away = 0
		return
	_now = GetTime()
	_dt = _now - _ms_t
	if 0.0 <= _dt < 0.18:
		return
	_ms_t = _now
	path = buildin.getattr(mv, 'path', None)
	if not path:
		_ms_last = None; _ms_away = 0
		return
	try:
		px, py, pz = player.GetMainCharacterPosition()
	except:
		return
	tx, ty = path[0]
	if _ms_last is None:
		_ms_last = (px, py); _ms_away = 0
		return
	lx, ly = _ms_last
	_ms_last = (px, py)
	mvx = px - lx; mvy = py - ly
	moved = (mvx*mvx + mvy*mvy) ** 0.5
	if moved < MANUAL_STOP_MOVE_EPS:
		_ms_away = 0
		return
	cvx = tx - lx; cvy = ty - ly
	dot = mvx*cvx + mvy*cvy
	if dot < 0.0:
		_ms_away = _ms_away + 1
	else:
		_ms_away = 0
	if _ms_away >= MANUAL_STOP_TICKS:
		_ms_away = 0
		_manualStopTrigger()

def _manualStopTrigger():
	try:
		import Movement as _MV
		_MV.StopMovement()
		try:
			px, py, pz = player.GetMainCharacterPosition()
			chr.MoveToDestPosition(player.GetMainCharacterIndex(), int(px), int(py))
		except: pass
	except: pass
	try:
		import ShopSearcher as _SS
		sd = buildin.getattr(_SS, 'searchDialog', None) or buildin.getattr(_SS, 'instance', None)
		if sd is not None and buildin.getattr(sd, 'sweeping', False):
			sd.StopSweep()
	except: pass
	try:
		import EnergyBot as _EB
		eb = buildin.getattr(_EB, 'instance', None)
		if eb is not None and buildin.hasattr(eb, '_stopBot'):
			_st = buildin.getattr(_EB, 'S_STOP', None)
			if _st is None or buildin.getattr(eb, 'state', None) != _st:
				eb._stopBot()
	except: pass
	if MANUAL_STOP_DEBUG:
		try:
			import chat as _c
			_c.AppendChat(3, '[uBot] manual control detected -> pathing stopped')
		except: pass

class TimeFunctionHandler(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.function_list = []


	def RegisterOnEventExit(self,time,function):
		self.function_list.append({"time":GetTime()+time,"function":function})

	def OnUpdate(self):
		try: _manualStopCheck()
		except: pass
		curTime = GetTime()
		to_del = []
		for i,func in enumerate(self.function_list):
			if curTime >= func["time"]:
				func["function"]()
				to_del.append(i)
		
		for i in to_del:
			del self.function_list[i]


class WaitingDialog(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.eventTimeOver = lambda *arg: None
		self.eventExit = lambda *arg: None

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Open(self, waitTime):
		curTime = time.clock()
		self.endTime = curTime + waitTime
		self.Show()		

	def Close(self):
		self.Hide()

	def SAFE_SetTimeOverEvent(self, event):
		self.eventTimeOver = ui.__mem_func__(event)

	def SAFE_SetExitEvent(self, event):
		self.eventExit = ui.__mem_func__(event)
		
	def OnUpdate(self):
		lastTime = max(0, self.endTime - time.clock())
		if 0 == lastTime:
			self.Close()
			self.eventTimeOver()
		else:
			return
		
	def OnPressExitKey(self):
		self.Close()
		return True
		
class Item(ui.ListBoxEx.Item):
	def __init__(self, fileName):
		ui.ListBoxEx.Item.__init__(self)
		self.canLoad=0
		self.text=fileName
		self.textLine=self.__CreateTextLine(fileName)          

	def __del__(self):
		ui.ListBoxEx.Item.__del__(self)

	def GetText(self):
		return self.text

	def SetSize(self, width, height):
		ui.ListBoxEx.Item.SetSize(self, 6*len(self.textLine.GetText()) + 4, height)

	def __CreateTextLine(self, fileName):
		textLine=ui.TextLine()
		textLine.SetParent(self)
		textLine.SetPosition(0, 0)
		textLine.SetText(fileName)
		textLine.Show()
		return textLine	

class EterPackOperator(object):

	def __init__(self, filename):
		#if not pack.Exist(filename):
			#raise IOError, 'No file or directory'
		self.data = self.GetTextFile(filename)
		self.data=_chr(10).join(self.data.split(_chr(13)+_chr(10)))
 
	def read(self, len = None):
		if not self.data:
			return ''
		if len:
			tmp = self.data[:len]
			self.data = self.data[len:]
			return tmp
		else:
			tmp = self.data
			self.data = ''
			return tmp

	def readlines(self):
		Array = str(self.data).split("\n")
		return Array
		
	def getline(self, line):
		return self.readlines()[line - 1]
		
	def getlinecount(self):
		return len(self.readlines())

	def GetTextFile(self, file):
		tmp = []
		try:
			Handle = app.OpenTextFile(file)
			CountLines = app.GetTextFileLineCount(Handle)
		except:
			return ""
		for i in xrange(CountLines):
			line = app.GetTextFileLine(Handle, i)
			if line != "":
				tmp.append(line + "\n")
		app.CloseTextFile()
		return("".join(tmp))

		
#LoadDictFile(CONFIG_PSHOP_AUTO_BUY,SEARCH_ITEMS_MAX_PRICE,float)
FileManager.LoadDictFile(FileManager.CONFIG_BOSSES_ID, BOSS_IDS, int)
FileManager.LoadDictFile(FileManager.CONFIG_ORES_ID, ORES_IDS, int)
# Hooks._debugHookFunctionArgs(event.SelectAnswer)  # debug-only: logged every dialog answer to debug.txt - disabled for release
# reload-safe (for the /rah in-game hot-reload): first load -> build+show the timer window; on RELOAD it
# already exists in this module dict, so REUSE it (rebind its class for the new OnUpdate code) instead of
# spawning a duplicate ScriptWindow that would keep firing. Keeps its pending function_list.
try:
    function_handler
    function_handler.__class__ = TimeFunctionHandler
except NameError:
    function_handler = TimeFunctionHandler()
    function_handler.Show()
import Movement
