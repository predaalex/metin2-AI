
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

from BotBase import BotBase
from UIComponents import Component, TabWindow
import Movement, Data
import OpenLib
import eXLib
import re


class Radar(BotBase):

    def __init__(self):
        BotBase.__init__(self, 0.5)
        self.all_vids = []
        self.showOre = True
        self.showMetins = True
        self.showPlayers = True
        self.showBoss = True
        self.showNPC = True

        self.entities = []

        self.lastTime = 0
        Data.time_Radar_lastTimeClearedList = 0
        self.BuildWindow()

    def BuildWindow(self):
        self.Board = ui.BoardWithTitleBar()
        self.Board.SetSize(290, 255)
        self.Board.SetPosition(52, 40)
        self.Board.AddFlag('movable')
        self.Board.SetTitleName('Radar')
        self.Board.SetCloseEvent(self.switch_state)
        self.Board.Hide()

        comp = Component()

        self.TabWidget = TabWindow(10, 30, 275, 220, self.Board, ['Settings', 'Entities'])

        self.settings_tab = self.TabWidget.GetTab(0)
        self.entities_list = self.TabWidget.GetTab(1)



        # Settings Tab
        self.enableButton = comp.OnOffButton(self.settings_tab, '', '', 15, 40,
                                             OffUpVisual=eXLib.PATH + 'OpenBot/Images/start_0.tga',
                                             OffOverVisual=eXLib.PATH + 'OpenBot/Images/start_1.tga',
                                             OffDownVisual=eXLib.PATH + 'OpenBot/Images/start_2.tga',
                                             OnUpVisual=eXLib.PATH + 'OpenBot/Images/stop_0.tga',
                                             OnOverVisual=eXLib.PATH + 'OpenBot/Images/stop_1.tga',
                                             OnDownVisual=eXLib.PATH + 'OpenBot/Images/stop_2.tga',
                                             funcState=self._start, defaultValue=False)
        self.showNPCButton = comp.OnOffButton(self.settings_tab,
                                              '\t\t\t\t\t\tShow npc',
                                              '', 80, 20, funcState=self.switch_npc_button,
                                              defaultValue=self.showNPC)
        self.showOreButton = comp.OnOffButton(self.settings_tab,
                                              '\t\t\t\t\t\tShow ore',
                                              '', 80, 40, funcState=self.switch_ore_button,
                                              defaultValue=self.showOre)

        self.showMetinsButton = comp.OnOffButton(self.settings_tab,
                                              '\t\t\t\t\t\tShow metins',
                                              '', 80, 60,  funcState=self.switch_metins_button,
                                              defaultValue=self.showMetins)
        self.showPlayersButton = comp.OnOffButton(self.settings_tab,
                                              '\t\t\t\t\t\tShow players',
                                              '', 80, 80, funcState=self.switch_player_button, defaultValue=self.showPlayers)

        self.showBossButton = comp.OnOffButton(self.settings_tab,
                                               '\t\t\t\t\t\tShow boss', '', 80, 100,
                                               funcState=self.switch_boss_button,
                                               defaultValue=self.showBoss)

        self.showDebugButton = comp.OnOffButton(self.settings_tab,
                                               '\t\t\t\t\t\tDebug mode', '', 80, 120,
                                               funcState=self.switch_debug_button,
                                               defaultValue=False)                                  


        x_size = 235
        y_size = 100

        # Metins Tab
        self.barEntities, self.fileListBoxEntities, self.ScrollBarEntities = comp.ListBoxEx2(self.entities_list, 10,
                                                                                             30, x_size, y_size)
        self.teleportButton = comp.Button(self.entities_list, 'Warp', '', 10, 150, self.warpToSelectedFileListBoxEntities,
                                          'd:/ymir work/ui/public/middle_button_01.sub',
                                          'd:/ymir work/ui/public/middle_button_02.sub',
                                          'd:/ymir work/ui/public/middle_button_03.sub')

    def addToFileListBoxEntities(self, vid, instance_type=OpenLib.NONE_TYPE):
        x, y, z = eXLib.GetPixelPosition(vid)
        name = chr.GetNameByVID(vid)
        entity = {
            'type': instance_type,
            'vid': vid,
            'x': x,
            'y': y,
            'name': name
        }
        self.entities.append(entity)
        self.updateFileListBoxEntities()

    def getTypeName(self, instance_type):
        if instance_type == OpenLib.NONE_TYPE:
            return '[ NONE ] '
        elif instance_type == OpenLib.ORE_TYPE:
            return '[ ORE ] '
        elif instance_type == OpenLib.METIN_TYPE:
            return '[ METIN ] '
        elif instance_type == OpenLib.BOSS_TYPE:
            return '[ BOSS ] '
        elif instance_type == OpenLib.PLAYER_TYPE:
            return '[ PLAYER ] '
        elif instance_type == OpenLib.OBJECT_TYPE:
            return '[ NPC ] '

    def updateFileListBoxEntities(self):
        self.fileListBoxEntities.RemoveAllItems()
        for entity in self.entities:
            if not entity['name'] == 'None':
                self.fileListBoxEntities.AppendItem(OpenLib.Item(self.getTypeName(entity['type']) + entity['name']))

    def warpToSelectedFileListBoxEntities(self):
        _item = self.fileListBoxEntities.GetSelectedItem()
        if _item is None:
            return
        item_text = _item.GetText()
        type_words_patterns = '[ [A-Z]+ ] '
        type = re.findall(type_words_patterns, item_text)
        name = item_text.split(type[0])

        for entity in self.entities:
            if entity['name'] == str(name[1]):
                Movement.TeleportToPosition(entity['x'], entity['y'])

    def switch_npc_button(self, val):
        self.showNPC = val

    def switch_ore_button(self, val):
        self.showOre = val

    def switch_metins_button(self, val):
        self.showMetins = val

    def switch_player_button(self, val):
        self.showPlayers = val

    def switch_boss_button(self, val):
        self.showBoss = val

    def switch_debug_button(self, val):
        return

    def _start(self, val):
        if val:
            self.Start()
        else:
            self.Stop()

    def AddNewEntity(self, vid, instance_type=OpenLib.NONE_TYPE):
        self.addToFileListBoxEntities(vid, instance_type=instance_type)

    def IsThisEntityNew(self, vid):
        for entity in self.entities:
            if entity['vid'] == vid:
                return False
        return True

    def Frame(self):
        MAIN_CHAR_VID = player.GetMainCharacterIndex()
        
        self.all_vids = eXLib.InstancesList
        val, Data.time_Radar_lastTimeClearedList = OpenLib.timeSleep(Data.time_Radar_lastTimeClearedList, 5)
        if val:
            self.clear_lists()
        for vid in self.all_vids:
            if MAIN_CHAR_VID != vid:
                if self.showDebugButton.isOn:
                    chr.SelectInstance(vid)
                    chat.AppendChat(3, str(chr.GetInstanceType(vid)) + ' ' + str(chr.GetRace()) + ' ' + str(chr.GetName(vid)) + ' ' + str(eXLib.GetPixelPosition(vid))   + ' ' + str(vid) )

                if self.IsThisEntityNew(vid):
                    if self.showOre:
                        if OpenLib.IsThisOre(vid):
                            self.AddNewEntity(vid, OpenLib.ORE_TYPE)
                    if self.showMetins:
                        if OpenLib.IsThisMetin(vid):
                            self.AddNewEntity(vid, OpenLib.METIN_TYPE)
                    if self.showPlayers:
                        if OpenLib.IsThisPlayer(vid):
                            self.AddNewEntity(vid, OpenLib.PLAYER_TYPE)
                    if self.showBoss:
                        if OpenLib.IsThisBoss(vid):
                            self.AddNewEntity(vid, OpenLib.BOSS_TYPE)
                    if self.showNPC:
                        if OpenLib.IsThisNPC(vid):
                            self.AddNewEntity(vid, OpenLib.OBJECT_TYPE)

    def clear_lists(self):
        self.fileListBoxEntities.RemoveAllItems()
        self.entities = []

    def switch_state(self):
        if self.Board.IsShow():
            self.Board.Hide()
        else:
            self.Board.Show()

def switch_state():
    radar.switch_state()

radar = Radar()