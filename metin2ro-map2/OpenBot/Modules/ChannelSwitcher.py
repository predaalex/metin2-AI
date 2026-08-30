
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

import OpenLib, UIComponents, Hooks, Settings, OpenLog
import serverInfo, introLogin # introLogin gives ServerStateChecker module


def __PhaseChangeChannelCallback(phase,phaseWnd):
    global instance
    if instance.currState == STATE_NONE:
        return
    else:
        if phase == OpenLib.PHASE_GAME:
            instance.SetStateNone()
        elif phase == OpenLib.PHASE_SELECT:
            OpenLib.SetTimerFunction(0.5,phaseWnd.SelectStart)


def getCallBackWithArg(func, arg):
    return lambda: func(arg)

STATE_NONE = 0
STATE_CHANGING_CHANNEL = 1

class ChannelSwitcher:

    def __init__(self):
        self.channels = {}
        self.currChannel = 0
        self.currState = STATE_NONE
        self.selectedChannel = 0

    def BuildWindow(self, board):
        self.component = UIComponents.Component()
        self.Board = board

        self.refreshButton = self.component.Button(self.Board, 'Refresh', '', 90, 150, self.OnRefreshButton,
                                          'd:/ymir work/ui/public/large_Button_01.sub',
                                          'd:/ymir work/ui/public/large_Button_02.sub',
                                          'd:/ymir work/ui/public/large_Button_03.sub')

    def OnRefreshButton(self):
        self.GetChannels()
        #self.fileListBox.RemoveAllItems()
        x = 65
        y = 50
        for id in sorted(self.channels): #.items():
            self.channels[id]['btn'] = self.component.Button(self.Board, 'CH ' + str(id), '', x, y,
                                                            getCallBackWithArg(self.OnConnectButton, int(id)),
                                                            'd:/ymir work/ui/public/small_Button_01.sub',
                                                            'd:/ymir work/ui/public/small_Button_02.sub',
                                                            'd:/ymir work/ui/public/small_Button_03.sub')
            
            x += 50
            if x >= 200:
                x = 65
                y += 30

    def OnConnectButton(self,id):
        _channel = id#self.fileListBox.GetSelectedItem().text
        if not _channel:
            chat.AppendChat(3, '[ChannelSwitcher] You did not select a channel')
            return

        if self.IsSpecialMap():
           chat.AppendChat(1, "[ChannelSwitcher] Sorry in this area you cannot change channel without logout!")
           return

        self.ChangeChannelById(_channel)

    def GetRegionID(self):
        # FOR EU IS 0
        return 0

    def GetServerID(self):
        server_name = OpenLib.GetCurrentServer()
        region_id = self.GetRegionID()
        if server_name:
            for server in serverInfo.REGION_DICT[region_id].keys():
                if serverInfo.REGION_DICT[region_id][server]['name'].strip() == str(server_name).strip():
                    return int(server)

    def GetChannels(self):
        del self.channels
        self.channels = {}
        region_id = self.GetRegionID()
        server_id = self.GetServerID()

        try:
            channelDict = serverInfo.REGION_DICT[region_id][server_id]['channel']
        except Exception as _ce:
            # CHANNEL DIAG: the GF client likely structures serverInfo differently (or
            # GetCurrentServer() doesn't match). Dump details to Log.txt so we can adapt.
            try:
                _srv = OpenLib.GetCurrentServer()
            except Exception as _e0:
                _srv = "GetCurrentServer ERR:" + str(_e0)
            OpenLog.DebugPrint("[ChannelDiag] GetChannels FAILED: %r | region_id=%r server_id=%r GetCurrentServer=%r" % (_ce, region_id, server_id, _srv))
            try:
                OpenLog.DebugPrint("[ChannelDiag] REGION_DICT type=%s keys=%r" % (type(serverInfo.REGION_DICT).__name__, list(serverInfo.REGION_DICT.keys())))
            except Exception as _e1:
                OpenLog.DebugPrint("[ChannelDiag] REGION_DICT access ERR: " + str(_e1))
            try:
                _reg = serverInfo.REGION_DICT[region_id]
                OpenLog.DebugPrint("[ChannelDiag] REGION_DICT[%r] type=%s keys=%r" % (region_id, type(_reg).__name__, list(_reg.keys())))
                for _sk in list(_reg.keys())[:10]:
                    try:
                        _sv = _reg[_sk]
                        OpenLog.DebugPrint("[ChannelDiag]   server %r: name=%r keys=%r channelKeys=%r" % (_sk, _sv.get('name'), list(_sv.keys()), list(_sv.get('channel', {}).keys())))
                    except Exception as _e2:
                        OpenLog.DebugPrint("[ChannelDiag]   server %r dump ERR: %s" % (_sk, _e2))
            except Exception as _e3:
                OpenLog.DebugPrint("[ChannelDiag] REGION_DICT[region] access ERR: " + str(_e3))
            chat.AppendChat(3, '[ChannelSwitcher] Error while get channels. (details in Log.txt -> [ChannelDiag])')
            return

        for channelID, channelDataDict in channelDict.items():

            self.channels[int(channelID)] = {
                'id': int(channelID),
                'name': channelDataDict['name'],
                'ip': channelDataDict['ip'],
                'port': channelDataDict['tcp_port'],
                'acc_ip' : serverInfo.REGION_AUTH_SERVER_DICT[region_id][server_id]['ip'],
                'acc_port' : serverInfo.REGION_AUTH_SERVER_DICT[region_id][server_id]['port']
            }

    def IsSpecialMap(self):
        maps = {
            "season1/metin2_map_oxevent",
            "season2/metin2_map_guild_inside01",
            "season2/metin2_map_empirewar01",
            "season2/metin2_map_empirewar02",
            "season2/metin2_map_empirewar03",
            "metin2_map_dragon_timeattack_01",
            "metin2_map_dragon_timeattack_02",
            "metin2_map_dragon_timeattack_03",
            "metin2_map_skipia_dungeon_boss",
            "metin2_map_skipia_dungeon_boss2",
            "metin2_map_devilsCatacomb",
            "metin2_map_deviltower1",
            "metin2_map_t1",
            "metin2_map_t2",
            "metin2_map_t3",
            "metin2_map_t4",
            "metin2_map_t5",
            "metin2_map_wedding_01",
            "metin2_map_duel"
        }
        if str(background.GetCurrentMapName()) in maps:
            return True
        return False

    def ConnectToChannel(self):
        net.Disconnect()
        net.ConnectTCP(self.selectedChannel["ip"],self.selectedChannel["port"])

    def ConnectToGame(self):
        net.SendEnterGamePacket()

    def ChangeChannelById(self, id):
        if int(id) not in self.channels:
            chat.AppendChat(3, "[Channel-Switcher] - Channel " + str(id) + " doesn't exist")
            return

        self.selectedChannel = self.channels[int(id)]
        self.currState = STATE_CHANGING_CHANNEL
        self.ConnectToChannel()


    def SetStateNone(self):
        self.selectedChannel = 0
        self.currState = STATE_NONE


    def __del__(self):
        Hooks.deletePhaseCallback("channelCallback")

    def switch_state(self):
        if self.Board.IsShow():
            self.Board.Hide()
        else:
            self.OnRefreshButton()
            self.Board.Show()


def switch_state():
    instance.switch_state()

def SwitchChannel(val):
    instance.ChangeChannelById(val)

def GetNextChannel():
	current_channel = OpenLib.GetCurrentChannel()

	if not current_channel:
		return 0
	if current_channel + 1 > len(instance.channels):
		current_channel = 1
	else:
		current_channel += 1
	
	return current_channel

instance = ChannelSwitcher()
Hooks.registerPhaseCallback("channelCallback", __PhaseChangeChannelCallback)
OpenLog.DumpObject(instance)