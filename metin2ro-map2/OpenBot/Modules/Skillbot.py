
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

import UIComponents
from BotBase import BotBase

import OpenLib, eXLib, FileManager
import Hooks, Data
from OpenBot.Modules.Actions import ActionBot




def __PhaseChangeSkillCallback(phase,phaseWnd):
    global instance
    if phase == OpenLib.PHASE_GAME:
        instance.resetSkillsUI()
        instance.LoadSettings()
        if instance.shouldWait:
            instance.startUpWait = True
        if instance.enableButton.isOn:
            instance.Start()
        else:
            instance.Stop()


class Skillbot(BotBase):

    ACTIVE_SKILL_IDS = {
        109,
        110,
        111,
        174,
        175,
        19,
        34,
        49,
        63,
        64,
        65,
        78,
        79,
        94,
        95,
        96,
        3,
        4,

    }

    def __init__(self):
        BotBase.__init__(self)
        Data.time_Skillbot_startUpWaitTime = 0
        self.shouldWait = False
        self.startUpWait = False
        self.mode = True
        self.currentSkillSet = []

        self.isOn = False
        self.BuildWindow()
        self.resetSkillsUI()

    def BuildWindow(self):

        self.comp = UIComponents.Component()
        self.Board = ui.BoardWithTitleBar()
        self.Board.SetSize(235, 150)
        self.Board.SetPosition(52, 40)
        self.Board.AddFlag('movable')
        self.Board.SetTitleName('Skillbot')
        self.Board.SetCloseEvent(self.switch_state)
        self.Board.Hide()

        self.enableButton = self.comp.OnOffButton(self.Board, '', '', 18, 40,
                                                  OffUpVisual=eXLib.PATH + 'OpenBot/Images/start_0.tga',
                                                  OffOverVisual=eXLib.PATH + 'OpenBot/Images/start_1.tga',
                                                  OffDownVisual=eXLib.PATH + 'OpenBot/Images/start_2.tga',
                                                  OnUpVisual=eXLib.PATH + 'OpenBot/Images/stop_0.tga',
                                                  OnOverVisual=eXLib.PATH + 'OpenBot/Images/stop_1.tga',
                                                  OnDownVisual=eXLib.PATH + 'OpenBot/Images/stop_2.tga',
                                                  funcState=self._start, defaultValue=self.isOn)

        self.showModeButton = self.comp.OnOffButton(self.Board, '\t\t\t\tCast instant', 'Not working with every class', 18, 105,
                                                         defaultValue=self.mode)

    def switch_should_wait(self, val):
        self.shouldWait = val

    def SaveSettings(self):
        for skill in self.currentSkillSet:
            FileManager.WriteConfig(str(skill['id']), str(skill['icon'].isOn), file=FileManager.CONFIG_SKILLBOT)
            skillTimer = getattr(self, 'edit_line'+str(skill['id'])).GetText()
            FileManager.WriteConfig('skillTimer'+str(skill['id']), skillTimer, file=FileManager.CONFIG_SKILLBOT)
        FileManager.WriteConfig('IsTurnedOn', str(self.enableButton.isOn), file=FileManager.CONFIG_SKILLBOT)
        FileManager.WriteConfig('ShouldWaitAfterLogout', str(self.shouldWait), file=FileManager.CONFIG_SKILLBOT)
        FileManager.Save(file=FileManager.CONFIG_SKILLBOT)

    def LoadSettings(self):
        is_turned_on = FileManager.boolean(FileManager.ReadConfig('IsTurnedOn', file=FileManager.CONFIG_SKILLBOT))
        if is_turned_on:
            self.enableButton.SetOn()
        else:
            self.enableButton.SetOff()

        for skill in self.currentSkillSet:
            is_skill_turned_on = FileManager.boolean(FileManager.ReadConfig(str(skill['id']), file=FileManager.CONFIG_SKILLBOT))
            skill_edit_line_timer = getattr(self, 'edit_line'+str(skill['id']))
            skill_edit_line_timer.SetText(FileManager.ReadConfig('skillTimer'+str(skill['id']), file=FileManager.CONFIG_SKILLBOT))
            if is_skill_turned_on:
                if not skill['icon'].isOn:
                    skill['icon'].OnChange()

    def resetSkillsUI(self):
        current_class = OpenLib.GetClass()
        if current_class == OpenLib.SKILL_SET_NONE:
            return
        skillIds = OpenLib.GetClassSkillIDs(current_class)
        del self.currentSkillSet[:]
        self.currentSkillSet = []
        pos_x = 0
        for i, id in enumerate(skillIds):
            if id in self.ACTIVE_SKILL_IDS:
                slot_bar, edit_line = self.comp.EditLine(self.Board, '40', 78 + 35 * pos_x, 75, 25, 15, 25)
                self.currentSkillSet.append({
                    "icon": self.comp.OnOffButton(self.Board, '', '', 75 + 35 * pos_x, 45, image=OpenLib.GetSkillIconPath(id)),
                    "id": id,
                    "slot": i + 1,
                    'is_turned_on': False,
                })
                setattr(self, 'slot_bar'+str(id), slot_bar)
                setattr(self, 'edit_line'+str(id), edit_line)
                pos_x += 1
        self.LoadSettings()

    def _start(self, val):
        if val:
            self.Start()
        else:
            self.Stop()

    def addCallbackToWaiter(self, skill):
        def wait_to_use_skill():
            skill['is_turned_on'] = False
        return wait_to_use_skill

    def is_text_validate(self, text):
        try:
            int(text)
        except ValueError:
            chat.AppendChat(3, '[Skillbot] - The value must be a digit')
            return False
        if int(text) < 0:
            chat.AppendChat(3, '[Skillbot] - The value must be in range 0 to infinity')
            return False
        return True

    def Frame(self):
        if not self.startUpWait:
            for skill in self.currentSkillSet:
                if self.showModeButton.isOn:
                    waiter_time = getattr(self, 'edit_line'+str(skill['id'])).GetText()
                    if not self.is_text_validate(waiter_time):
                        continue
                    if not skill['is_turned_on'] and skill['icon'].isOn and not player.IsSkillCoolTime(skill['slot']):
                        if not player.IsMountingHorse():
                            eXLib.SendUseSkillPacket(skill['id'], Data.mainVID)
                        else:
                            net.SendCommandPacket(net.PLAYER_CMD_RIDE_DOWN)
                            eXLib.SendUseSkillPacket(skill['id'], Data.mainVID)
                            net.SendCommandPacket(net.PLAYER_CMD_RIDE)
                        skill['is_turned_on'] = True
                        ActionBot.instance.AddNewWaiter(int(waiter_time), self.addCallbackToWaiter(skill))
                else:
                    if not skill['is_turned_on'] and skill['icon'].isOn \
                        and not player.IsSkillCoolTime(skill['slot']):
                        if not player.IsMountingHorse():
                            eXLib.SendUseSkillPacketBySlot(skill['slot'])
                        else:
                            net.SendCommandPacket(net.PLAYER_CMD_RIDE_DOWN)
                            eXLib.SendUseSkillPacketBySlot(skill['slot'])
                            net.SendCommandPacket(net.PLAYER_CMD_RIDE)
        else:
            time_to_wait = 2
            text = self.edit_lineWaitingTime.GetText()
            if self.is_text_validate(text):
                time_to_wait = int(text)
            else:
                self.startUpWait = False
                return

            val, Data.time_Skillbot_startUpWaitTime = OpenLib.timeSleep(Data.time_Skillbot_startUpWaitTime, time_to_wait)
            if val:
                self.startUpWait = False

    def switch_state(self):
        if self.Board.IsShow():
            self.SaveSettings()
            self.Board.Hide()
        else:
            self.resetSkillsUI()
            self.Board.Show()

    def __del__(self):
        Hooks.deletePhaseCallback("skillCallback")

def switch_state():
    instance.switch_state()

instance = Skillbot()
Hooks.registerPhaseCallback("skillCallback", __PhaseChangeSkillCallback)
