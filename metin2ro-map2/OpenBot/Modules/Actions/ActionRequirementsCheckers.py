
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

from OpenBot.Modules import OpenLib
from OpenBot.Modules.OpenLog import DebugPrint
import eXLib

# REQUIREMENTS
IS_NEAR_POSITION = 'IS_NEAR_POSITION'
HAS_ENOUGH_MONEY = 'HAS_ENOUGH_MONEY'
IS_ON_POSITION = 'IS_ON_POSITION'
IS_IN_MAP = 'IS_IN_MAP'
IS_ABOVE_LVL = 'IS_ABOVE_LVL'
IS_UNDER_LVL = 'IS_UNDER_LVL'
IS_NEAR_INSTANCE = 'IS_NEAR_INSTANCE'
IS_RACE_NEARLY = 'IS_RACE_NEARLY'
IS_IN_CHANNEL = 'IS_IN_CHANNEL'
IS_CHAR_READY_TO_MINE = 'IS_CHAR_READY_TO_MINE'
IS_DEAD = 'IS_DEAD'
HAS_ITEM = 'HAS_ITEM'
HAS_ITEM_IN_COUNT = 'HAS_ITEM_IN_COUNT'


req_list = [IS_NEAR_POSITION, HAS_ENOUGH_MONEY, IS_ON_POSITION, IS_IN_MAP, IS_ABOVE_LVL, IS_NEAR_INSTANCE, IS_RACE_NEARLY, IS_IN_CHANNEL, IS_DEAD, HAS_ITEM, HAS_ITEM_IN_COUNT]
interrupt_list = [IS_NEAR_POSITION, HAS_ENOUGH_MONEY, IS_ON_POSITION, IS_IN_MAP, IS_ABOVE_LVL, IS_NEAR_INSTANCE, IS_RACE_NEARLY, IS_IN_CHANNEL, IS_DEAD, HAS_ITEM, HAS_ITEM_IN_COUNT]

def hasEnoughMoney(amount):
    """
     Checking if main character has enough money
        Args:
            amount (int)

    """
    return int(player.GetMoney()) < int(amount)

def isAboveLVL(lvl):
    """
     Checking is main character above level
        Args:
            lvl (int)

    """
    
    
    if player.GetStatus(player.LEVEL) < lvl:
        return False
    return True

def isUnderLVL(lvl):
    if player.GetStatus(player.LEVEL) > lvl:
        return False
    return True   

def isInMaps(maps):
    """
        Checking is main character on any of map in list
        Args:
            maps ['map_name_1' (str), 'map_name_2' (str)] (list)

    """
    for mapName in maps:
        if str(background.GetCurrentMapName()) == mapName:
            return True
    return False

def isNearInstance(vid, max_dist=200):
    return OpenLib.isPlayerCloseToInstance(vid, max_dist)

def isNearPosition(position):
    """
        Checking is main character near position.
        Args:
            position [x (int), y(int), max_dist(int)](list)

    """
    x, y = position[0], position[1]
    if len(position) < 3:
        max_dist = 150
    else:
        max_dist = position[2]
    return OpenLib.isPlayerCloseToPosition(x, y, max_dist)

def isOnPosition(position):
    """
        Checking is main character on current position.
        Args:
            position [x (int), y(int), max_dist(int)](list)

    """
    x, y = position[0], position[1]
    if len(position) < 3:
        max_dist = 200
    else:
        max_dist = position[2]
    if OpenLib.isPlayerCloseToPosition(x, y, max_dist):
        return True
    return False

def isMetinNearly(args=0):
    for vid in eXLib.InstancesList:
        if OpenLib.IsThisMetin(vid) and not eXLib.IsDead(vid):
            if not OpenLib.isPathToVID(vid):
                continue
            return True
    return False

def isOreNearly(args=0):
    for vid in eXLib.InstancesList:
        if OpenLib.IsThisOre(vid) and not eXLib.IsDead(vid):
            if not OpenLib.isPathToVID(vid):
                continue
            return True
    return False

def isRaceNearly(races_list):
    for vid in eXLib.InstancesList:
        chr.SelectInstance(vid)
        if chr.GetRace() in races_list:
            return True
    return False

def isCharReadyToMine(ore_vid):

    if eXLib.IsDead(ore_vid):
        return False

    if not OpenLib.isPlayerCloseToInstance(ore_vid):
        return False
    
    if not OpenLib.IsWeaponPickaxe():
        return False

    return True

def HasItem(item_id):
    if OpenLib.GetItemByID(item_id) > -1:
        return True
    return False

def HasItemInCount(item_id, item_count):
    item_slot = OpenLib.GetItemByID(item_id)
    if item_slot > -1:
        if player.GetItemCount(item_slot) >= item_count:
            return True
        return False
    return False

def IsDead(vid):
    return eXLib.IsDead(vid)

def IsInChannel(channel):
    if OpenLib.GetCurrentChannel() == channel:
        return True
    return False