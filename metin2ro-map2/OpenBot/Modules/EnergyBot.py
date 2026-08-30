
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

from OpenBot.Modules.OpenLog import DebugPrint
import UIComponents, eXLib, FileManager
from OpenBot.Modules import OpenLib, Movement
from FileManager import boolean
from BotBase import BotBase

# Diagnostics while we validate spec 3 (dialog option count). Chat only -- no log file is written to the client
# root (the old EnergyBot.log is gone). Flip EB_DEBUG=False for release.
EB_DEBUG = False

def _dbg(msg):
    if not EB_DEBUG:
        return
    try:
        chat.AppendChat(3, "[EB] " + msg)
    except:
        pass

# =============================================================================
# EnergyBot -- SELF-CONTAINED rewrite (decoupled from ActionBot).
#
# The old bot pushed actions onto ActionBot's always-running queue, so Stop from
# the EnergyBot window left the current walk/buy running until ActionBot finished
# it. This version owns its whole loop: it walks with Movement directly, buys/gives
# with net.* directly, and Stop() immediately halts Movement + closes any open shop
# and freezes the state machine (BotBase drops Frame when stopped). No ActionBot.
#
# Loop (spec 1): if we already hold givable items AND we're closer to the alchemist
# than to the weapon dealer -> go exchange first (skip a wasted trip); otherwise go
# to the weapon dealer, fill the inventory, then walk to the alchemist and exchange
# the items for energy fragments. Repeat.
#
# Spec 2 (DONE): inventory range is dynamic (_invSize reads player.INVENTORY_PAGE_SIZE *
# INVENTORY_PAGE_COUNT live each cycle) and filling is REACTIVE (buy until holdings stop
# growing), so it covers every unlocked page + adapts to mid-run expansion without treating
# locked cells as free. See _invSize / the S_BUY block.
# TODO(spec 3 - needs live-client RE): the weapon-dealer dialog nav is a best-effort
# placeholder (_openWeaponDealer). Replace with "always click the second-to-last
# option" (last is Close) once the live dialog option-count is confirmed via CE.
# =============================================================================

# Cheap gear the alchemist converts into energy fragments (Cat Bite Knife, Fear Mask,
# Orc Hood, Horned Helmet, Cardinal's Hat, Godsend Helmet -- +0..+4 each).
ALL_GIVABLE_ITEMS = [
    1040, 1041, 1042, 1043, 1044,
    12260, 12261, 12262, 12263, 12264,
    12390, 12391, 12392, 12393, 12394,
    12530, 12531, 12532, 12533, 12534,
    12670, 12671, 12672, 12673, 12674,
    21530, 21531, 21532, 21533, 21534,
]

WEAPON_RACE    = 9001     # weapon dealer (sells the givable gear)
ALCHEMIST_RACE = 20001    # alchemist (converts gear -> energy fragments)
BUY_SHOP_SLOT  = 4        # shop slot holding the givable item at the weapon dealer

# Per-map NPC world positions (weapon dealer + alchemist), lifted from the old stage
# schema. Coords are in GetMainCharacterPosition() world units.
NPC_POSITIONS = {
    'metin2_map_a1': {'weapon': (60100, 56100), 'alchemist': (62200, 51600)},
    'metin2_map_b1': {'weapon': (67700, 65600), 'alchemist': (65900, 72800)},
    'metin2_map_c1': {'weapon': (42800, 61200), 'alchemist': (29700, 81500)},
}

MIN_YANG    = 25000   # need at least this much yang to keep buying
ARRIVE_DIST = 350     # close enough to interact with an NPC
# The server rate-limits shop buys to ~1/sec, so buy at a throttled pace (no 15/frame spam) and only
# declare the inventory FULL after a sustained stall -- a single-frame "no new item" just means the last
# buy is still in flight, NOT that we're out of room (that was the "leaves with 1 item" bug).
BUY_INTERVAL = 0.5    # min seconds between buy packets
BUY_STALL    = 3.0    # no NEW givable item for this long WHILE buying -> all unlocked slots full
DIALOG_WAIT_MAX = 10  # frames to wait for the dealer dialog's option count to populate before falling back (~4s)

# state machine
S_STOP, S_TO_WEAPON, S_OPEN_SHOP, S_WAIT_DIALOG, S_BUY, S_TO_ALCH, S_GIVE = range(7)


class EnergyBot(BotBase):
    def __init__(self):
        BotBase.__init__(self, 0.4, onlyGamePhase=False, waitIsPlayerDead=False)
        self.state = S_STOP
        self._shopTries = 0
        self._noMoneyNotice = 0.0
        # spec 3 fallback (RESTORED): the proven "I have weapon shop mission" toggle stays the ACTIVE
        # dialog method until GetDialogAnswerCount is validated by the logs.
        self.weaponShopQuest = boolean(FileManager.ReadConfig("HasWeaponShopQuest"))
        self.BuildWindow()
        _dbg("loaded (build spec1+2 + toggle restored); weaponShopQuest=%s" % self.weaponShopQuest)

    # ------------------------------------------------------------------ UI ----
    def BuildWindow(self):
        comp = UIComponents.Component()
        self.Board = ui.BoardWithTitleBar()
        self.Board.SetSize(235, 195)
        self.Board.SetPosition(52, 40)
        self.Board.AddFlag('movable')
        self.Board.SetTitleName('EnergyBot')
        self.Board.SetCloseEvent(self.switch_state)
        self.Board.Hide()

        # RESTORED toggle: proven weapon-dealer dialog method (kept until spec-3 GetDialogAnswerCount is validated)
        self.hasWeaponShopQuest = comp.OnOffButton(self.Board, '\t\t\t\t\t\t\t\t\t\t I have Weapon Shop mission', '', 20, 45,
            funcState=self.WeaponShopQuestOnOff, defaultValue=int(self.weaponShopQuest))

        self.lInfo = comp.TextLine(self.Board, 'Stopped', 20, 95, comp.RGB(255, 255, 0))
        self.enableEnergyBot = comp.OnOffButton(self.Board, '', '', 100, 130,
            OffUpVisual=eXLib.PATH + 'OpenBot/Images/start_0.tga',
            OffOverVisual=eXLib.PATH + 'OpenBot/Images/start_1.tga',
            OffDownVisual=eXLib.PATH + 'OpenBot/Images/start_2.tga',
            OnUpVisual=eXLib.PATH + 'OpenBot/Images/stop_0.tga',
            OnOverVisual=eXLib.PATH + 'OpenBot/Images/stop_1.tga',
            OnDownVisual=eXLib.PATH + 'OpenBot/Images/stop_2.tga',
            funcState=self.SwitchEnableEnergyBot, defaultValue=False)

    def switch_state(self):
        if self.Board.IsShow():
            self.Board.Hide()
        else:
            self.Board.Show()

    def WeaponShopQuestOnOff(self, val):
        self.weaponShopQuest = val
        try:
            FileManager.WriteConfig("HasWeaponShopQuest", str(self.weaponShopQuest))
            FileManager.Save()
        except:
            pass
        _dbg("weaponShopQuest toggle -> %s" % val)

    def _msg(self, s):
        try:
            self.lInfo.SetText(s)
        except:
            pass

    # ------------------------------------------------------------ control ----
    def SwitchEnableEnergyBot(self, val):
        if val:
            self._startBot()
        else:
            self._stopBot()

    def _startBot(self):
        npcs = self._mapNpcs()
        if not npcs:
            chat.AppendChat(3, "[EnergyBot] Not on a supported map (metin2_map_a1/b1/c1).")
            try: self.enableEnergyBot.SetOff()
            except: pass
            return
        self._shopTries = 0
        self.Start()   # BotBase -> Frame begins running
        # closest-NPC decision: already holding gear AND nearer the alchemist -> exchange
        # first and skip a pointless walk back to the dealer; otherwise go fill up.
        have = self._countGivable()
        free = self._freeCells()
        canBuy = free >= 2   # room for at least one more givable item (helmets/knives are ~2-3 cells)
        dAlch = self._dist(npcs['alchemist']); dWpn = self._dist(npcs['weapon'])
        _dbg("START map=%s cap=%d givable=%d free=%d canBuy=%s dAlch=%.0f dWpn=%.0f" %
             (background.GetCurrentMapName(), self._invSize(), have, free, canBuy, dAlch, dWpn))
        # Go exchange FIRST when we hold items AND (the inventory is full -> buying is pointless, OR we're
        # simply closer to the alchemist). Only head to the dealer when there's actually room to buy.
        if have > 0 and (not canBuy or dAlch < dWpn):
            self.state = S_TO_ALCH
            _dbg("decision: exchange first (%s)" % ("inventory full" if not canBuy else "closer to alchemist"))
        else:
            self.state = S_TO_WEAPON
            _dbg("decision: -> weapon dealer to fill")
        self._msg('Running')

    def _stopBot(self):
        # IMMEDIATE stop: freeze the state machine, halt the walker, close any shop, drop the quest hook.
        self.state = S_STOP
        try: Movement.StopMovement()
        except: pass
        # StopMovement only stops issuing NEW moves; the last MoveToDestPosition is still running server-side
        # (char keeps walking to the next path point). Send a move-to-CURRENT-position to cancel it -> stop now.
        try:
            mx, my = self._pos()
            chr.MoveToDestPosition(player.GetMainCharacterIndex(), int(mx), int(my))
        except: pass
        self._unhookQuest()
        try:
            if shop.IsOpen():
                net.SendShopEndPacket()
        except: pass
        self.Stop()    # BotBase -> Frame stops being called
        self._msg('Stopped')
        _dbg("STOP -> in-flight move cancelled + shop closed + quest unhooked + frame stopped (immediate)")

    # --------------------------------------------------------- helpers ----
    def _mapNpcs(self):
        try:
            return NPC_POSITIONS.get(background.GetCurrentMapName())
        except:
            return None

    def _pos(self):
        x, y, z = player.GetMainCharacterPosition()
        return x, y

    def _dist(self, p):
        mx, my = self._pos()
        return OpenLib.dist(mx, my, p[0], p[1])

    def _invSize(self):
        # Spec 2: cover EVERY inventory page the client actually has, read LIVE each call so a mid-run
        # expansion (player keys open a 5-slot row in page 3/4) is picked up immediately -- never a
        # cached snapshot. INVENTORY_PAGE_COUNT is the client's real capacity (the source hardcodes 2;
        # the live GF client reports more). Fall back to the old fixed cap if the constants are absent.
        try:
            n = int(player.INVENTORY_PAGE_SIZE) * int(player.INVENTORY_PAGE_COUNT)
            if n > 0:
                return n
        except:
            pass
        return OpenLib.MAX_INVENTORY_SIZE

    def _countGivable(self):
        n = 0
        for i in range(self._invSize()):
            if player.GetItemIndex(i) in ALL_GIVABLE_ITEMS:
                n += 1
        return n

    def _nextGivableSlot(self):
        for i in range(self._invSize()):
            if player.GetItemIndex(i) in ALL_GIVABLE_ITEMS:
                return i
        return -1

    def _freeCells(self):
        # "Is there room to buy?" -- use OpenLib.GetNumberOfFreeSlots(), which scans the BASE pages
        # (MAX_INVENTORY_SIZE) only. Crucial: player.INVENTORY_PAGE_COUNT is the CAPACITY (4), NOT the
        # unlocked count (2) -- scanning the full capacity counts LOCKED pages 3-4 as free and always reads
        # "has space". The base-page scan reads 0 when the unlocked inventory is full. (A fully-correct
        # any-unlock-level check needs the client's unlocked-slot count -> pending CE RE.)
        try:
            return OpenLib.GetNumberOfFreeSlots()
        except:
            return 999

    def _walkTo(self, p):
        # keep re-issuing the walk each frame; arrival is detected by proximity (the
        # Movement return code can't distinguish moving vs reached on this build).
        if OpenLib.isPlayerCloseToPosition(p[0], p[1], ARRIVE_DIST):
            Movement.StopMovement()
            return True
        Movement.GoToPositionAvoidingObjects(p[0], p[1])
        return False

    def _unhookQuest(self):
        # restore normal quest-dialog rendering (undo the hook set in _openWeaponDealer)
        if getattr(self, '_questHooked', False):
            self._questHooked = False
            try: OpenLib.showAnswers()
            except: pass

    def _openWeaponDealer(self):
        # Spec 3: DO NOT hook the quest render here. OpenQuestWindow (what the old hook suppressed) is exactly
        # what drives event.UpdateEventSet -> ProcessEventSet -> MakeQuestion, and MakeQuestion is where
        # TEventSet.nAnswer is set. Hooking it means nAnswer is never set -> GetDialogAnswerCount reads 0. So we
        # let the dialog open, read the option count in S_WAIT_DIALOG, and immediately answer the second-to-last
        # option -- which closes the dialog within a frame or two (a brief flash, not the old stuck-dialog bug).
        # FORCE-UNHOOK: questHook is a module singleton in Hooks.py; an earlier run (old code) could have left it
        # hooked (shop never opened -> S_BUY's unhook never ran), and /rah doesn't reload Hooks.py -> the render
        # stays suppressed and nAnswer stays 0. showAnswers() is a safe no-op if it isn't hooked.
        try: OpenLib.showAnswers()
        except: pass
        self._questHooked = False

    # ------------------------------------------------------------ loop ----
    def Frame(self):
        try:
            if not background.GetCurrentMapName():
                return
            if not player.GetMainCharacterIndex():
                return
        except:
            return

        npcs = self._mapNpcs()
        if not npcs:
            self._msg('Left supported map - stopping')
            self._stopBot()
            try: self.enableEnergyBot.SetOff()
            except: pass
            return
        weapon = npcs['weapon']
        alchemist = npcs['alchemist']

        if self.state == S_TO_WEAPON:
            self._msg('Walking to weapon dealer')
            if self._walkTo(weapon):
                self._shopTries = 0
                self.state = S_OPEN_SHOP
                _dbg("arrived at weapon dealer -> open shop")

        elif self.state == S_OPEN_SHOP:
            try:
                have = int(player.GetMoney())
            except:
                have = 0
            if have < MIN_YANG:
                self._notifyNoMoney(have)
                return   # wait here (frame-throttled) until the player has yang
            vid = OpenLib.GetInstanceByID(WEAPON_RACE)
            if vid < 0:
                return   # dealer not in sight yet
            net.SendOnClickPacket(vid)
            self._openWeaponDealer()          # hook the render; DON'T pre-send an answer
            self._dialogWait = 0
            self.state = S_WAIT_DIALOG

        elif self.state == S_WAIT_DIALOG:
            # Spec 3: read the LIVE dialog option count and pick the SECOND-TO-LAST option -- the dealer's
            # "Open store", which always sits right above "Close" no matter how many quest options stack on
            # top. Answers are 0-indexed (the old toggle sent 0 for a 2-option menu, 1 for a 3-option one), so
            # second-to-last = count-2. Wait for the server's reply to populate the event-set (count>=2);
            # reading in the same frame as the click yields 0 (no dialog yet).
            cnt = -1
            try: cnt = eXLib.GetDialogAnswerCount()
            except: cnt = -1
            if isinstance(cnt, int) and cnt >= 2:
                _dbg("weapon dialog open: count=%d -> select second-to-last idx %d" % (cnt, cnt - 2))
                try: event.SelectAnswer(1, cnt - 2)
                except Exception as e: _dbg("SelectAnswer(1,%d) failed: %s" % (cnt - 2, e))
                self._shopTries = 0
                self._lastGivable = -1; self._buyProgressAt = 0.0; self._lastBuyAt = 0.0
                self.state = S_BUY
            else:
                self._dialogWait = getattr(self, '_dialogWait', 0) + 1
                if self._dialogWait > DIALOG_WAIT_MAX:
                    # count never populated -> FALLBACK to the proven toggle answer so the run isn't stuck.
                    # If this ever fires, GetDialogAnswerCount isn't seeing the live dialog (investigate).
                    _dbg("dialog count still %s after %d frames -> FALLBACK to toggle answer=%d"
                         % (cnt, self._dialogWait, int(self.weaponShopQuest)))
                    try: event.SelectAnswer(1, int(self.weaponShopQuest))
                    except: pass
                    self._shopTries = 0
                    self._lastGivable = -1; self._buyProgressAt = 0.0; self._lastBuyAt = 0.0
                    self.state = S_BUY

        elif self.state == S_BUY:
            if not shop.IsOpen():
                # shop hasn't opened yet -> retry the click a few times, then bail to
                # walking (avoids getting wedged if the dealer moved out of range).
                self._shopTries += 1
                if self._shopTries > 6:
                    self._shopTries = 0
                    self.state = S_OPEN_SHOP
                return
            self._unhookQuest()   # shop is open -> the dealer dialog is resolved, restore normal quest UI
            # Spec 2: fill REACTIVELY + TIME-BASED. GetNumberOfFreeSlots would count LOCKED cells (in
            # partially-unlocked pages 3/4) as free -> buy forever; so instead watch whether our givable
            # holdings actually GROW. But the server buys ~1/sec while Frame runs ~2.5x/sec, so a single
            # "no increase" frame just means the last buy is still in flight -- only a sustained STALL
            # (BUY_STALL) means all UNLOCKED slots are full. Buy one item per BUY_INTERVAL (no spam).
            now = OpenLib.GetTime()
            have = self._countGivable()
            if have > getattr(self, '_lastGivable', -1):   # a new item landed -> real progress
                self._lastGivable = have
                self._buyProgressAt = now
            if now - getattr(self, '_buyProgressAt', now) > BUY_STALL:
                net.SendShopEndPacket()
                self._msg('Inventory full (%d) -> alchemist' % have)
                _dbg("S_BUY full: no new item for %.1fs at have=%d (cap %d) -> alchemist"
                     % (BUY_STALL, have, self._invSize()))
                self.state = S_TO_ALCH
                return
            if now - getattr(self, '_lastBuyAt', 0.0) > BUY_INTERVAL:
                self._lastBuyAt = now
                net.SendShopBuyPacket(BUY_SHOP_SLOT)
                self._msg('Buying... (have %d)' % have)

        elif self.state == S_TO_ALCH:
            self._msg('Walking to alchemist')
            if self._walkTo(alchemist):
                self.state = S_GIVE
                _dbg("arrived at alchemist -> exchange (%d givable to give)" % self._countGivable())

        elif self.state == S_GIVE:
            slot = self._nextGivableSlot()
            if slot < 0:
                self._msg('Exchanged all -> refill')
                _dbg("exchanged all givables -> back to weapon dealer to refill")
                self.state = S_TO_WEAPON   # nothing left to give -> go refill
                return
            vid = OpenLib.GetInstanceByID(ALCHEMIST_RACE)
            if vid < 0:
                return   # alchemist not in sight yet
            self._msg('Exchanging for energy')
            net.SendGiveItemPacket(vid, player.SLOT_TYPE_INVENTORY, slot, player.GetItemCount(slot))
            OpenLib.skipAnswers([0, 0], True)   # confirm the give (mirrors the old flow)

    def _notifyNoMoney(self, have):
        try:
            now = time.clock()
            if now - self._noMoneyNotice > 5.0:
                self._noMoneyNotice = now
                chat.AppendChat(3, "[EnergyBot] Needs at least %d yang to run (you have %d). Waiting."
                    % (MIN_YANG, have))
        except:
            pass
        self._msg('Need %d yang' % MIN_YANG)

    def _rebuildWindow(self):
        # /rah-ui: rebuild the window in place so BuildWindow LAYOUT edits show without a client restart.
        wasShown = False
        try: wasShown = self.Board.IsShow()
        except: pass
        try: self.Board.Hide()
        except: pass
        for a in ('Board', 'lInfo', 'enableEnergyBot', 'hasWeaponShopQuest'):
            try: setattr(self, a, None)
            except: pass
        self.BuildWindow()
        if wasShown:
            try: self.Board.Show()
            except: pass


# reload-safe (for /rah): on RELOAD the singleton still exists -> just rebind its class so it picks up
# new methods while KEEPING its window + state (no duplicate window). /rah-ui additionally rebuilds it.
try:
    instance
    instance.__class__ = EnergyBot
except NameError:
    instance = EnergyBot()
