# init.py -- MERGED bootstrap (injection) + bot loader (first in-game). eXLib runs this file TWICE:
#   call 1 (injection, PythonModule.cpp) -> bootstrap half; call 2 (App.cpp, first in-game) -> loader half.
# Phase-guarded via a sys flag. An if/else does NOT create a scope in Python, so all the module-level
# names in each half stay module-level exactly as before. /rah is unaffected (it reloads OpenBot modules,
# not this file). script.py is kept on disk as a backup but is no longer executed by eXLib.
import sys
if not getattr(sys, '_ubot_init_phase2', False):
    sys._ubot_init_phase2 = True
    # ===================== BOOTSTRAP (was init.py) =====================
    import ui, sys, os
    import eXLib
    import chr,app
    exec ('import sys')
    _chr = chr

    b = sys.modules.keys()
    for i in range (len(b)):
            h=b[i]
            r=0
            for g in range(len(h)):
                    if h[g] != '.':
                            r=r+1
                            if r==len(h):
                                    a=dir(__import__(b[i]))
                                    for y in range(len(a)):
                                            if a[y]=='GetMainCharacterIndex' or 'MAX_HP' or 'SetSingleDIKKeyState' or 'INVENTORY_PAGE_SIZE' or 'INVENTORY_SLOT_COUNT':
                                                    playerm=b[i]
                                            if a[y]=='GetVIDInfo':
                                                    chrmgrm=b[i]
                                            if a[y]=='SendShopEndPacket':
                                                    netm=b[i]
                                            if a[y]=='AppendChat':
                                                    chatm=b[i]
    imp='import '

    try:
            exec (imp+chatm+' as _chat')
    except:
            pass
    try:
            exec (imp+netm+' as _net')
    except:
            pass
    try:
            exec (imp+playerm+' as _player')
    except:
            pass
    try:
            exec (imp+chrmgrm+' as _chrmgr')
    except:
            pass


    sys.modules['player'] = _player
    sys.modules['net'] = _net
    sys.modules['chat'] = _chat
    sys.modules['chrmgr'] = _chrmgr

    def SetSingleDIKKeyState(key,state):
        if state == 1:
            _player.OnKeyDown(key)
        else:
            _player.OnKeyUp(key)

    def SetAttackKeyState(state):
        if state == 1:
            _player.OnKeyDown(app.DIK_SPACE)
        else:
            _player.OnKeyUp(app.DIK_SPACE)

    setattr(chr, 'GetPixelPosition', eXLib.GetPixelPosition)
    setattr(chr, 'MoveToDestPosition', eXLib.MoveToDestPosition)
    setattr(_player, 'SetSingleDIKKeyState', SetSingleDIKKeyState)
    setattr(_player, 'SetAttackKeyState', SetAttackKeyState)

    #Set Path
    folder = eXLib.PATH+"OpenBot"
    command = 'mklink /d OpenBot "' + folder +'"'

    sys.path.append(os.path.join(eXLib.PATH))
    sys.path.append(os.path.join(eXLib.PATH, 'OpenBot'))
    sys.path.append(os.path.join(eXLib.PATH, 'OpenBot', 'lib'))
    sys.path.append(os.path.join(eXLib.PATH, 'OpenBot', 'Modules'))

else:
    # ===================== BOT LOADER (was script.py) =====================
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

    from OpenBot.Modules import FileManager, UIComponents, ShopSearcher, Settings, Shopcreator, KeyBot, Skillbot, ChannelSwitcher, EnergyBot, StoneCompass, AutoHunting
    from OpenBot.Modules.Actions import ActionBot
    import eXLib, Data

    DEBUG = False
    if DEBUG:
        from OpenBot.Modules import Filter, MiningBot

    class OpenBotHackbarDialog(ui.ScriptWindow):                            

        Hackbar = 0
        comp = UIComponents.Component()
        energy_bot = EnergyBot.instance

        def __init__(self):
            self.OpenBotBoard = ui.ThinBoard(layer="TOP_MOST")
            self.OpenBotBoard.SetPosition(0, 100)
            if DEBUG:
                self.OpenBotBoard.SetSize(51, 500)
            else:
                self.OpenBotBoard.SetSize(51, 340)
            self.OpenBotBoard.AddFlag("float")
            self.OpenBotBoard.AddFlag("movable")
            self.OpenBotBoard.Hide()

            self.ShowHackbarButton = self.comp.Button(None, '', 'Show Hackbar', 10, 60, self.OpenHackbar, eXLib.PATH + 'OpenBot/Images/Shortcuts/show_0.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/show_1.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/show_0.tga')
            self.HideHackbarButton = self.comp.HideButton(None, '', 'Hide Hackbar', 10, 60, self.OpenHackbar, eXLib.PATH + 'OpenBot/Images/Shortcuts/hide_0.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/hide_1.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/hide_0.tga')
            self.SettingsButton = self.comp.Button(self.OpenBotBoard, '', 'Settings', 9, 10, self.Generel, eXLib.PATH + 'OpenBot/Images/Hackbar/sett_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/sett_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/sett_2.tga')
            self.SearchBotButton = self.comp.Button(self.OpenBotBoard, '', 'SearchBot', 10, 45, self.SearchBot, eXLib.PATH + 'OpenBot/Images/Hackbar/search_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/search_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/search_0.tga')
            self.ShopCreatorButton = self.comp.Button(self.OpenBotBoard, '', 'Shopbot', 8, 78, self.ShopCreator, eXLib.PATH + 'OpenBot/Images/Hackbar/shop_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/shop_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/shop_0.tga')
            self.SkillbotButton = self.comp.Button(self.OpenBotBoard, '', 'Auto-Hunt', 8, 113, self.OnSkillbot, eXLib.PATH + 'OpenBot/Images/Hackbar/auto_hunt_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/auto_hunt_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/auto_hunt_0.tga')
            self.StoneCompassButton = self.comp.Button(self.OpenBotBoard, '', 'Stone Compass', 8, 147, self.OnStoneCompass, eXLib.PATH + 'OpenBot/Images/Hackbar/compass_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/compass_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/compass_0.tga')
            self.ZoomButton = self.comp.Button(self.OpenBotBoard, '', 'Zoom-Hack', 10, 183, self.Zoom, eXLib.PATH + 'OpenBot/Images/Shortcuts/zoom_0.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/zoom_1.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/zoom_0.tga')
            self.EnergyBotButton = self.comp.Button(self.OpenBotBoard, '', 'EnergyBot', 10, 216, self.OnEnergyBot, eXLib.PATH + 'OpenBot/Images/Hackbar/energy_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/energy_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/energy_0.tga')
            self.CrashButton = self.comp.Button(self.OpenBotBoard, '', 'Exit', 10, 300, self.CloseRequest, eXLib.PATH + 'OpenBot/Images/Shortcuts/close_0.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/close_1.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/close_0.tga')

        def OpenHackbar(self):
            if self.Hackbar:
                self.Hackbar = 0
                self.ShowHackbarButton.Show()
                self.HideHackbarButton.Hide()
                self.OpenBotBoard.Hide()
            else:
                self.Hackbar = 1
                self.ShowHackbarButton.Hide()
                self.HideHackbarButton.Show()
                self.OpenBotBoard.Show()

        def Generel(self):
            Settings.switch_state()

        def OnChannelSwitcher(self):
            ChannelSwitcher.switch_state()

        def SearchBot(self):
            ShopSearcher.switch_state()

        def ShopCreator(self):
            Shopcreator.switch_state()

        def OnSkillbot(self):
            # Repointed: the Skillbot hackbar button now opens the Auto-Attack (auto-hunt) window,
            # a legit clone of the client's official Auto-Atac (no teleport / no hacky packets).
            AutoHunting.switch_state()

        def Zoom(self):
            app.SetCameraMaxDistance(12000)

        def OnEnergyBot(self):
            self.energy_bot.switch_state()

        def OnStoneCompass(self):
            StoneCompass.switch_state()

        def Close(self):
            app.Abort()

        def CancelQuestionDialog(self):
            self.QuestionDialog.Close()
            self.QuestionDialog = None

        def CloseRequest(self):
            self.QuestionDialog = uiCommon.QuestionDialog()
            self.QuestionDialog.SetText("Do You want to quit Metin2 immediately?")
            self.QuestionDialog.SetAcceptEvent(ui.__mem_func__(self.Close))
            self.QuestionDialog.SetCancelEvent(ui.__mem_func__(self.CancelQuestionDialog))
            self.QuestionDialog.Open()

    try:
        app.Shop.Close()
    except:
        pass
    app.Shop = OpenBotHackbarDialog()
    KeyBot.instance.enableButton.SetOn()
    KeyBot.instance.Start()

    # Master debug switch: gates the phase-replay status chat below AND the diagnostics
    # ticker / Phase1Diag.txt further down. Keep False for release (no chat, no log file).
    PHASE1_DEBUG = False

    # --- Replay the game-phase event uBot's net.SetPhaseWindow hook missed ---
    # eXLib triggers script.py via in-game map-name detection, AFTER the login->game transition,
    # so uBot's net.SetPhaseWindow hook never saw PHASE_GAME and the phase callbacks that START
    # ActionBot / init Data.mainVID / arm Skillbot etc. never fired. Replay them once here.
    try:
        import Hooks as _Hooks
        _Hooks.CURRENT_PHASE = 5  # OpenLib.PHASE_GAME
        for _cid in list(_Hooks.phaseCallbacks.keys()):
            _cb = _Hooks.phaseCallbacks[_cid]
            if callable(_cb):
                try:
                    _cb(5, _Hooks.GAME_WINDOW)
                except Exception as _e:
                    try:
                        if PHASE1_DEBUG: chat.AppendChat(3, "[P1] phaseCB %s ERR: %s" % (str(_cid), str(_e)))
                    except:
                        pass
        try:
            # _afterLoadPhase can fail on enableActionBot.SetOn() before reaching Start();
            # start the executor explicitly so queued bot actions actually run.
            if ActionBot.instance.State == 0:
                ActionBot.instance.Start()
            if PHASE1_DEBUG: chat.AppendChat(3, "[P1] phase-replay done; ActionBot.State=%s (expect 1)" % str(ActionBot.instance.State))
        except Exception as _e2:
            try:
                if PHASE1_DEBUG: chat.AppendChat(3, "[P1] ActionBot start ERR: %s" % str(_e2))
            except:
                pass
    except Exception as _e:
        try:
            if PHASE1_DEBUG: chat.AppendChat(3, "[P1] phase-replay ERR: %s" % str(_e))
        except:
            pass

    # ============================ PHASE 1 DIAGNOSTICS ============================
    # Temporary instrumentation: logs which eXLib walker/instance methods work in-game.
    # Writes detail to <uBot>/Phase1Diag.txt and a 1-line summary to game chat.
    # Dumps once on load, then every ~8s (walk near NPCs/mobs to see InstancesList change).
    import time as _p1time
    _P1_LOG = eXLib.PATH + "\\Phase1Diag.txt"
    _p1_move_issued = [True]  # auto walk-test DISABLED (framework proven); set [False] to re-run it
    # PHASE1_DEBUG is defined above (before the phase-replay block) so it can gate that chat too.

    def _p1write(rows):
        try:
            f = open(_P1_LOG, "a")
            for s in rows:
                f.write(s + "\n")
            f.close()
        except:
            pass

    def Phase1Diag():
        out = ["===== PHASE1 DIAG t=" + str(_p1time.time()) + " ====="]
        mapName = "?"
        try:
            mapName = background.GetCurrentMapName()
            out.append("map = " + repr(mapName))
        except Exception as e:
            out.append("map ERR: " + str(e))
        mainVID = 0
        try:
            mainVID = player.GetMainCharacterIndex()
            out.append("mainVID(player.GetMainCharacterIndex) = " + repr(mainVID))
        except Exception as e:
            out.append("mainVID ERR: " + str(e))
        try:
            out.append("player.GetMainCharacterPosition() = " + repr(player.GetMainCharacterPosition()))
        except Exception as e:
            out.append("player.GetMainCharacterPosition ERR: " + str(e))
        try:
            out.append("chr.GetPixelPosition(mainVID)[eXLib] = " + repr(chr.GetPixelPosition(mainVID)))
        except Exception as e:
            out.append("chr.GetPixelPosition(main) ERR: " + str(e))
        cnt = -1
        vids = []
        try:
            il = eXLib.InstancesList
            for v in il:
                vids.append(v)
            cnt = len(vids)
            out.append("InstancesList type=" + type(il).__name__ + " count=" + str(cnt))
            out.append("VIDs = " + repr(vids[:40]))
            shown = 0
            for vid in vids:
                if shown >= 12:
                    break
                shown += 1
                row = "  vid=" + repr(vid)
                try:
                    chr.SelectInstance(vid)
                    row += " race=" + repr(chr.GetRace())
                except Exception as e:
                    row += " race_ERR=" + str(e)
                try:
                    row += " name=" + repr(chr.GetNameByVID(vid))
                except Exception as e:
                    row += " name_ERR=" + str(e)
                try:
                    row += " dead=" + repr(eXLib.IsDead(vid))
                except Exception as e:
                    row += " dead_ERR=" + str(e)
                try:
                    row += " pos=" + repr(chr.GetPixelPosition(vid))
                except Exception as e:
                    row += " pos_ERR=" + str(e)
                out.append(row)
        except Exception as e:
            out.append("InstancesList ERR: " + str(e))
        try:
            dealer = None
            for vid in vids:
                try:
                    chr.SelectInstance(vid)
                    if chr.GetRace() == 9001:
                        dealer = vid; break
                except:
                    pass
            if dealer is not None:
                out.append("WEAPON DEALER(race 9001) vid=%s pos=%s" % (repr(dealer), repr(chr.GetPixelPosition(dealer))))
            else:
                out.append("WEAPON DEALER(race 9001) NOT in InstancesList")
        except Exception as e:
            out.append("dealer-find ERR: " + str(e))
        try:
            mp = player.GetMainCharacterPosition()
            px = int(mp[0]); py = int(mp[1])
            try:
                path = eXLib.FindPath(px, py, px + 3000, py + 3000)
                out.append("FindPath((%d,%d)->+3000) len=%d head=%s" % (px, py, len(path), repr(path[:3])))
            except Exception as e:
                out.append("FindPath ERR: " + str(e))
            try:
                out.append("IsPositionBlocked(my) = " + repr(eXLib.IsPositionBlocked(px, py)))
            except Exception as e:
                out.append("IsPositionBlocked ERR: " + str(e))
        except Exception as e:
            out.append("pos-for-path ERR: " + str(e))
        # one-shot WALK TEST: exercise the FULL Movement framework (mapMovement -> Movement -> MoveToDestPosition)
        try:
            if (not _p1_move_issued[0]) and cnt > 0 and mainVID:
                _p1_move_issued[0] = True
                tgt = None
                for _v in vids:
                    try:
                        chr.SelectInstance(_v)
                        if chr.GetRace() == 9001:
                            _dp = chr.GetPixelPosition(_v); tgt = (int(_dp[0]), int(_dp[1])); break
                    except:
                        pass
                if tgt:
                    from OpenBot.Modules import Movement as _Mv
                    out.append("WALK TEST: Movement.GoToPositionAvoidingObjects(%d,%d) [walk to weapon dealer via framework]" % (tgt[0], tgt[1]))
                    _r = _Mv.GoToPositionAvoidingObjects(tgt[0], tgt[1])
                    out.append("WALK TEST returned: " + repr(_r))
                else:
                    out.append("WALK TEST: no race-9001 dealer found")
        except Exception as e:
            out.append("WALK TEST ERR: " + repr(e))
        # bot/framework states
        try:
            from OpenBot.Modules.Actions import ActionBot as _AB
            from OpenBot.Modules import Movement as _MvS
            _ca = _AB.instance.currActionObject
            out.append("STATES: ActionBot.State=%s queue=%d curAction=%s | Movement.state=%s pathlen=%s" % (
                str(_AB.instance.State), len(_AB.instance.currActionsQueue),
                (_ca.function.__name__ if _ca else None),
                str(_MvS.Movement.state), str(len(_MvS.Movement.path))))
        except Exception as e:
            out.append("STATES ERR: " + repr(e))
        out.append("")
        _p1write(out)
        try:
            if PHASE1_DEBUG: chat.AppendChat(3, "[P1] map=%s instVids=%s mainVID=%s -> Phase1Diag.txt" % (str(mapName), str(cnt), str(mainVID)))
        except:
            pass

    class _Phase1DiagWindow(ui.ScriptWindow):
        def __init__(self):
            ui.ScriptWindow.__init__(self)
            self.last = 0.0
            self.Show()
        def OnUpdate(self):
            try:
                now = _p1time.clock()
                if now - self.last > 8.0:
                    self.last = now
                    Phase1Diag()
            except:
                pass

    def _DumpServerInfo():
        # One-shot dump of the GF client's serverInfo + channel data so we can adapt
        # ChannelSwitcher.GetChannels() to the real structure.
        rows = ["===== SERVERINFO / CHANNEL DUMP ====="]
        try:
            import serverInfo as _si
        except Exception as e:
            rows.append("import serverInfo ERR: %r" % e); _p1write(rows); return
        try:
            from OpenBot.Modules import OpenLib as _OL
            rows.append("OpenLib.GetCurrentServer() = %r" % (_OL.GetCurrentServer(),))
            try:
                rows.append("OpenLib.GetCurrentChannel() = %r" % (_OL.GetCurrentChannel(),))
            except Exception as e:
                rows.append("GetCurrentChannel ERR: %r" % e)
        except Exception as e:
            rows.append("OpenLib/GetCurrentServer ERR: %r" % e)
        try:
            rows.append("serverInfo attrs: %r" % [a for a in dir(_si) if not a.startswith('_')])
        except Exception as e:
            rows.append("dir(serverInfo) ERR: %r" % e)
        for _name in ["REGION_DICT", "REGION_AUTH_SERVER_DICT", "MARKADDR_DICT", "REGION_NAME_DICT", "SERVER_DICT"]:
            try:
                v = getattr(_si, _name, "<MISSING>")
                if isinstance(v, dict):
                    rows.append("%s: dict keys=%r" % (_name, list(v.keys())))
                    for k in list(v.keys())[:2]:
                        sub = v[k]
                        if isinstance(sub, dict):
                            rows.append("  [%r]: dict keys=%r" % (k, list(sub.keys())))
                            for k2 in list(sub.keys())[:3]:
                                rows.append("    [%r][%r] = %r" % (k, k2, sub[k2]))
                        else:
                            rows.append("  [%r] = %r" % (k, sub))
                else:
                    rows.append("%s = %r (%s)" % (_name, v, type(v).__name__))
            except Exception as e:
                rows.append("%s dump ERR: %r" % (_name, e))
        try:
            import net as _net
            try:
                rows.append("net.GetServerInfo() = %r" % (_net.GetServerInfo(),))
            except Exception as e:
                rows.append("net.GetServerInfo() ERR: %r" % e)
            for _fn in ["GetServerInfo", "GetMainActorRace", "GetMainActorSkillGroup", "GetEmpireID", "GetMainActorVID"]:
                rows.append("net.%s exists=%s" % (_fn, hasattr(_net, _fn)))
        except Exception as e:
            rows.append("net dump ERR: %r" % e)
        try:
            from OpenBot.Modules import Data as _D
            rows.append("Data.serverInfo = %r" % (_D.serverInfo,))
        except Exception as e:
            rows.append("Data.serverInfo ERR: %r" % e)
        _p1write(rows)

    if PHASE1_DEBUG:
        try:
            f = open(_P1_LOG, "w"); f.write("Phase1Diag log start\n"); f.close()
        except:
            pass
        try:
            _DumpServerInfo()
        except Exception as e:
            _p1write(["serverinfo-dump ERR: " + str(e)])
        try:
            Phase1Diag()  # one-shot immediately
        except Exception as e:
            _p1write(["one-shot ERR: " + str(e)])
        try:
            p1_diag_window = _Phase1DiagWindow()
        except Exception as e:
            _p1write(["diag-window ERR (timer off, one-shot only): " + str(e)])
    # ========================== END PHASE 1 DIAGNOSTICS ==========================


    # ============================ /rah IN-GAME HOT-RELOAD ============================
    # Type "/rah" in chat to hot-reload the auto-hunt python WITHOUT restarting the client. This intercepts
    # the outgoing chat (net.SendChatPacket is what the client + Spambot use to send chat), swallows "/rah"
    # so it is never sent to the server, and reload()s the modules below. AutoHunting's module bottom is
    # reload-safe: it rebinds the LIVE instance's class -> new methods take effect while the open window +
    # state are kept (no duplicate window). OpenLib function edits take effect immediately (callers look up
    # OpenLib.<fn> per call). NOTE: window-LAYOUT edits (BuildWindow) need "/rah-ui" instead: it reloads the
    # same modules AND rebuilds the AutoHunting window in place (tears down + re-runs BuildWindow), so new
    # slot positions/sizes appear without a client/window restart. Plain "/rah" leaves the built widgets as-is.
    # The hook lives in script.py (run once, never reloaded) so it survives every /rah.
    # deps first. The main hot-reloaded features: OpenLib (shared), ShopSearcher (trading glass) + EnergyBot,
    # then AutoHunting. All are reload-safe (class-rebind singletons) so /rah swaps their LOGIC in place.
    _RAH_RELOAD_LIST = ['OpenBot.Modules.OpenLib', 'OpenBot.Modules.ShopSearcher',
                        'OpenBot.Modules.EnergyBot', 'OpenBot.Modules.AutoHunting',
                        'OpenBot.Modules.StoneCompass']

    def _rahReload():
        import sys as _sys
        try:
            import chat as _chat
            _info = buildin.getattr(_chat, 'CHAT_TYPE_INFO', 3)
        except:
            _chat = None; _info = 3
        done = []
        for _name in _RAH_RELOAD_LIST:
            _m = _sys.modules.get(_name)
            if _m is None:
                continue
            try:
                reload(_m)
                done.append(_name.split('.')[-1])
            except Exception as _e:
                if _chat:
                    try: _chat.AppendChat(_info, '[uBot] /rah reload ERR %s: %s' % (_name.split('.')[-1], _e))
                    except: pass
        if _chat:
            try: _chat.AppendChat(_info, '[uBot] /rah reloaded: ' + (', '.join(done) if done else '(nothing loaded)'))
            except: pass

    def _rahReloadUI():
        # /rah-ui = /rah (reload logic, incl. new BuildWindow code) + rebuild the AutoHunting window IN PLACE
        # so window-LAYOUT edits take effect without a close+reopen or client restart. Reload first (so the
        # live instance runs the NEW _rebuildWindow/BuildWindow), then call it on the module's live instance.
        _rahReload()
        import sys as _sys
        try:
            import chat as _chat
            _info = buildin.getattr(_chat, 'CHAT_TYPE_INFO', 3)
        except:
            _chat = None; _info = 3
        # rebuild every reloaded feature window that supports it (AutoHunting + EnergyBot + ShopSearcher).
        # Each is independent + guarded; each module exposes `instance` (ShopSearcher aliases searchDialog).
        _done = []
        for _modname in ('OpenBot.Modules.AutoHunting', 'OpenBot.Modules.EnergyBot', 'OpenBot.Modules.ShopSearcher'):
            try:
                _m = _sys.modules.get(_modname)
                _inst = buildin.getattr(_m, 'instance', None) if _m is not None else None
                if _inst is not None and buildin.hasattr(_inst, '_rebuildWindow'):
                    _inst._rebuildWindow()
                    _done.append(_modname.split('.')[-1])
            except Exception as _e:
                if _chat:
                    try: _chat.AppendChat(_info, '[uBot] /rah-ui rebuild ERR %s: %s' % (_modname.split('.')[-1], _e))
                    except: pass
        if _chat:
            try: _chat.AppendChat(_info, '[uBot] /rah-ui rebuilt: ' + (', '.join(_done) if _done else '(none)'))
            except: pass

    try:
        import net as _rah_net
        if not buildin.getattr(_rah_net, '_rah_hooked', False):
            _rah_orig_sendchat = _rah_net.SendChatPacket
            def _rah_sendchat(*args, **kw):
                # scan every positional arg (arg order text-vs-type can vary by call site) for the /rah command
                try:
                    for _a in args:
                        if buildin.isinstance(_a, (str, unicode)):
                            _cmd = _a.strip().lower()
                            if _cmd in ('/rah-ui', '/rahui'):
                                _rahReloadUI()
                                return
                            if _cmd == '/rah':
                                _rahReload()
                                return
                except:
                    pass
                return _rah_orig_sendchat(*args, **kw)
            _rah_net.SendChatPacket = _rah_sendchat
            _rah_net._rah_hooked = True   # guard: never double-wrap even if script.py is somehow re-run
    except Exception:
        pass
    # ========================== END /rah IN-GAME HOT-RELOAD ==========================

