
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

import eXLib
import OpenLib,FileManager,Movement,UIComponents, Settings, Data
from FileManager import boolean
import OpenThreads


CLOUD_SKILL_STATE_WAITING = 0
CLOUD_SKILL_STATE_READY = 1
CLOUD_SKILL_STATE_USED = 2


class DmgHacksInstance(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)
		self.threadInstance = OpenThreads.threadInstance
		self.BuildWindow()
		

	def __del__(self):
		ui.Window.__del__(self)

	def BuildWindow(self):
		self.Board = ui.BoardWithTitleBar()
		self.Board.SetSize(300, 260)
		self.Board.SetCenterPosition()
		self.Board.AddFlag('movable')
		self.Board.AddFlag('float')
		self.Board.SetTitleName('WaitHack')
		self.Board.SetCloseEvent(self.Close)
		self.Board.Hide()
		self.comp = UIComponents.Component()

		self.enableButton = self.comp.OnOffButton(self.Board, '', '', 130, 210, OffUpVisual=eXLib.PATH + 'OpenBot/Images/start_0.tga', OffOverVisual=eXLib.PATH + 'OpenBot/Images/start_1.tga', OffDownVisual=eXLib.PATH + 'OpenBot/Images/start_2.tga',OnUpVisual=eXLib.PATH + 'OpenBot/Images/stop_0.tga', OnOverVisual=eXLib.PATH + 'OpenBot/Images/stop_1.tga', OnDownVisual=eXLib.PATH + 'OpenBot/Images/stop_2.tga',funcState=self.OnOffBtnState )
		self.playerClose = self.comp.OnOffButton(self.Board, '', '', 130, 50)
		self.wallBtn = self.comp.OnOffButton(self.Board, '\t\t\t\tCheck is wall', 'Dont attack mobs with wall in between', 170, 30)
		self.cloudBtn = self.comp.OnOffButton(self.Board, '\t\t\t\tCloud exploit', 'Only on dagger ninja', 170, 50)
		self.attackPlayerBtn = self.comp.OnOffButton(self.Board, '\t\t\t\tAttack players', '', 170, 70)
		self.attackBlockedMonsters = self.comp.OnOffButton(self.Board, '\t\t\t\t', '', 130, 70)
		self.AttackBlockedMonsers = self.comp.TextLine(self.Board, 'Attack blocked monsters', 13, 70, self.comp.RGB(255, 255, 255))
		self.RangeLabel = self.comp.TextLine(self.Board, 'Range', 13, 102, self.comp.RGB(255, 255, 255))
		self.SpeedLabel = self.comp.TextLine(self.Board, 'Speed', 13, 136, self.comp.RGB(255, 255, 255))
		self.MonsterLabel = self.comp.TextLine(self.Board, 'Monsters', 13, 170, self.comp.RGB(255, 255, 255))
		self.PlayerLabel = self.comp.TextLine(self.Board, 'Stop when player close', 12, 51, self.comp.RGB(255, 255, 255))
		self.rangeNum = self.comp.TextLine(self.Board, '100', 254, 102, self.comp.RGB(255, 255, 255))
		self.speedNum = self.comp.TextLine(self.Board, '100 ms', 254, 136, self.comp.RGB(255, 255, 255))
		self.monsterNum = self.comp.TextLine(self.Board, '100', 254, 170, self.comp.RGB(255, 255, 255))
		self.RangeSlider = self.comp.SliderBar(self.Board, 0.0, self.Range_func, 73, 104)
		self.SpeedSlider = self.comp.SliderBar(self.Board, 0.0, self.Speed_func, 73, 137)
		self.MonsterSlider = self.comp.SliderBar(self.Board, 0.0, self.Monster_func, 73, 171)
		self.enableButton.SetOff()

		self.loadSettings()

		self.range = 0
		self.speed = 0
		Data.time_DmgHacks_lasttime = 0
		Data.time_DmgHacks_lastcloud = 0
		Data.time_DmgHacks_lastpotion = 0
		self.maxMonster = 0
		self.cloudSkillState = CLOUD_SKILL_STATE_READY
		self.Speed_func()
		self.Range_func()
		self.Monster_func()

	def loadSettings(self):
		self.MonsterSlider.SetSliderPos(float(FileManager.ReadConfig("WaitHack_MaxMonsters")))
		self.SpeedSlider.SetSliderPos(float(FileManager.ReadConfig("WaitHack_Speed")))
		self.RangeSlider.SetSliderPos(float(FileManager.ReadConfig("WaitHack_Range")))
		self.cloudBtn.SetValue(boolean(FileManager.ReadConfig("WaitHack_CloudExploit")))
		self.attackPlayerBtn.SetValue(boolean(FileManager.ReadConfig('WaitHack_attackPlayer')))
		self.playerClose.SetValue(boolean(FileManager.ReadConfig("WaitHack_PlayerClose")))
	
	def saveSettings(self):
		FileManager.WriteConfig("WaitHack_MaxMonsters", str(self.MonsterSlider.GetSliderPos()))
		FileManager.WriteConfig("WaitHack_Speed", str(self.SpeedSlider.GetSliderPos()))
		FileManager.WriteConfig("WaitHack_Range", str(self.RangeSlider.GetSliderPos()))
		FileManager.WriteConfig("WaitHack_PlayerClose", str(self.playerClose.isOn))
		FileManager.WriteConfig("WaitHack_attackPlayer", str(self.attackPlayerBtn.isOn))
		FileManager.WriteConfig("WaitHack_CloudExploit", str(self.cloudBtn.isOn))

		FileManager.Save()
	
	
	def Monster_func(self):
		self.maxMonster = int(self.MonsterSlider.GetSliderPos()*1000)
		self.monsterNum.SetText(str(self.maxMonster))
  
	def Range_func(self):
		self.range = int(self.RangeSlider.GetSliderPos()*10000)
		self.rangeNum.SetText(str(self.range))
	
	def Speed_func(self):
		self.speed = float(self.SpeedSlider.GetSliderPos())
		self.speedNum.SetText(str(int(self.speed*1000)) + ' ms')

	def OnOffBtnState(self,val):
		if(val):
			eXLib.BlockAttackPackets()
			#self.threadInstance.createLoopedThread(self.waithackThreadMethod,(),0,False,False,False,'waithack')
		else:
			eXLib.UnblockAttackPackets()
			#self.threadInstance.stopThread('waithack')
	
	
	def OpenWindow(self):
		if self.Board.IsShow():
			self.Board.Hide()
		else:
			self.Board.Show()
   
	def TeleportAttack(self,lst,x,y):
		Movement.TeleportStraightLine(self.lastPos[0],self.lastPos[1],x,y)
		self.lastPos = (x,y)
		#eXLib.SendStatePacket(x,y,0,eXLib.CHAR_STATE_STOP,0)
		vid_hits = 0
		for vid in lst:
			mob_x, mob_y = (1, 1)
			if OpenLib.dist(x,y,mob_x,mob_y) < OpenLib.ATTACK_MAX_DIST_NO_TELEPORT:
				#chat.AppendChat(3,"Sent Attack, X:" + str(mob_x) + " Y:" + str(mob_y) + "VID: " +str(vid))
				eXLib.SendAttackPacket(vid,0)
				lst.remove(vid)
				vid_hits+=1
		
		return vid_hits
		#chat.AppendChat(3,"After: " + str(len(lst)))

	def __sendUseSkill(self):
		Dmg.cloudSkillState = CLOUD_SKILL_STATE_READY

	def AttackArch(self,lst,x,y):
		vid_hits = 0
		#chat.AppendChat(3,"Attacking with arch")
		for enemy in lst:
			x,y = (1, 1)
			eXLib.SendAddFlyTarget(enemy,x,y)
			eXLib.SendShoot(eXLib.COMBO_SKILL_ARCH)
			lst.remove(enemy)
			vid_hits+=1
		return vid_hits

	
	def AttackCloud(self,lst,x,y):
		#chat.AppendChat(3,"Attacking with arch")
		Movement.TeleportStraightLine(self.lastPos[0],self.lastPos[1],x,y)
		self.lastPos = (x,y)
		#eXLib.SendStatePacket(x,y,0,eXLib.CHAR_STATE_STOP,0)
		vid_hits = 0
		for vid in lst:
			if OpenLib.dist(x,y,self.lastPos[0],self.lastPos[1]) < OpenLib.ATTACK_MAX_DIST_NO_TELEPORT:
				if not player.IsSkillCoolTime(5):
					#chat.AppendChat(7, "No Cooldown. Checking mana. ")
					if player.GetStatus(player.SP) >  OpenLib.GetSkillManaNeed(35,5):
						#chat.AppendChat(7, "Enough Mana -Attempting Cast!")
						val, Data.time_DmgHacks_lastcloud = OpenLib.timeSleep(Data.time_DmgHacks_lastcloud,5)
						if val:
							eXLib.SendUseSkillPacketBySlot(5,vid)
							#chat.AppendChat(7, "Casted!")
					else:
						#chat.AppendChat(7, "Not Enough Mana to cast.")
						#chat.AppendChat(7, "Attempting Potion Drinking.")
						val, Data.time_DmgHacks_lastpotion = OpenLib.timeSleep(Data.time_DmgHacks_lastpotion,5)
						if val:
							OpenLib.UseAnyItemByID(Settings.instance.BLUE_POTIONS_IDS)
							#chat.AppendChat(7, "Potion used.")
						return 99999999

				eXLib.SendAddFlyTarget(vid,self.lastPos[0],self.lastPos[1])
				eXLib.SendShoot(35)
				eXLib.SendAttackPacket(vid,0)
				lst.remove(vid)
				vid_hits+=1

		return vid_hits
    
				
	def OnUpdate(self):
		val, Data.time_DmgHacks_lasttime = OpenLib.timeSleep(Data.time_DmgHacks_lasttime,self.speed)
		if not val:
			return
		if not IsOn():
			return
		if OpenLib.GetCurrentPhase() != OpenLib.PHASE_GAME:
			return

		main_vid = Data.mainVID
		if not eXLib.IsDead(main_vid):
			isArch = OpenLib.IsWeaponArch()
			self.lastPos = (1,1)
			x,y = (1,1)
			lst = list()

			inst_list = eXLib.InstancesList.copy()
			inst_list.pop(main_vid,0) # removing main vid from list, default 0 to ignore errors if not in list.
			for vid in inst_list:
				if not chr.HasInstance(vid):
					continue

				if self.playerClose.isOn and OpenLib.IsThisPlayer(vid):
					return

				if OpenLib.IsThisNPC(vid):
					continue

				if self.attackPlayerBtn.isOn and OpenLib.IsThisPlayer(vid):
					continue

				if player.GetCharacterDistance(vid) < self.range and not eXLib.IsDead(vid):
					lst.append(vid)
						

			hit_counter = 0
			i = 0
			#chat.AppendChat(3,str(len(lst)))
			while len(lst) > 0 and hit_counter < self.maxMonster:
				vid = lst[0]
				mob_x, mob_y = (1, 1)
				if not self.attackBlockedMonsters.isOn:
					if eXLib.IsPositionBlocked(mob_x,mob_y):
						lst.remove(vid)
						continue
				if self.wallBtn.isOn:
					if eXLib.IsPathBlocked(x, y, mob_x, mob_y):
						lst.remove(vid)
						continue
				if self.cloudBtn.isOn and OpenLib.GetClass() == OpenLib.SKILL_SET_DAGGER_NINJA:
					hit_counter+=self.AttackCloud(lst,mob_x, mob_y)
				elif isArch:
					hit_counter+=self.AttackArch(lst,mob_x, mob_y)
				else:
					hit_counter+=self.TeleportAttack(lst,mob_x, mob_y)
				i+=1
			if(OpenLib.dist(x,y,self.lastPos[0],self.lastPos[1]) >=50):
				Movement.TeleportStraightLine(self.lastPos[0], self.lastPos[1], x, y)
	
	def Close(self):
		self.Board.Hide()
		self.saveSettings()


def Pause():
	"""
	Pauses the damage hack.
	"""
	Dmg.enableButton.SetOff()

def Resume():
	"""
	Resumes damage hack.
	"""
	Dmg.enableButton.SetOn()

def IsOn():
	return Dmg.enableButton.isOn

def switch_state():
	"""
	Open's or closes the UI window.
	"""
	Dmg.OpenWindow()

Dmg = DmgHacksInstance()
Dmg.Show()
# Dmg.OpenWindow()