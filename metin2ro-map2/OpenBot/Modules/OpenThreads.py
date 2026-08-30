
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
import thread,time,chat


class OpenThread:

    
    thread_names = []
    

    def createThread(self,method, args):

        """
        Creates a new Thread with the passed method. This thread is anonymous, 
        cannot be controled and will exit itself when method execution is done.
        """

        arg_list = []
        for arg in args:
            arg_list.append(arg)

        thread.start_new_thread(method, tuple(arg_list))

    def createLoopedThread(self, method, method_args, print_result, debugLog_result, save_result, threadName):
        """
        This will create a looped Thread with the specified Method and the specified args.
        After each execution the result is Printed, logged, and/or saved inside an Array in the Thread Object with the passedThreadName + "Result" 
        -> threadName = "test" -> self.testResult <- Array!  

        The Method needs to import any necessary modules itself, otherwise pass them along as arguments where applicable.
        Do not pass "Self" as Argument - Keep argument empty if only self.
        """

        args = (method,method_args,print_result,debugLog_result,save_result,threadName,)
        if not threadName in self.thread_names:
            self.thread_names.append(threadName)
            thread.start_new_thread(self.loopMethod,args)
        else:
            chat.appendChat(7,"Error: ThreadName already in use. Aborting." )

    def createLoopedThread_buffered(self, pauseTime, print_result, debugLog_result, save_result, threadName):
        """
        This will create a buffered looped Thread. An Array called "threadName_Buffer" will be created in the Thread instance (self).
        This thread will sleep in loop until an methodObj is added to the list. see OpenThreads.methodObj(method, args) for more details.
        After each execution the result is Printed, logged, and/or saved inside an Array in the Thread Object with the passedThreadName + "Result" 
        -> threadName = "test" -> self.testResult <- Array!  

        The Method needs to import any necessary modules itself, otherwise pass them along as arguments where applicable.

        Do not pass "Self" as Argument - Keep argument empty if only self.
        """

        args = (print_result,pauseTime, debugLog_result,save_result,threadName,)
        if not threadName in self.thread_names:

            self.thread_names.append(threadName)
            thread.start_new_thread(self.loopMethod_buffered,args)
        else: 
            chat.appendChat(7,"Error: ThreadName already in use. Aborting.")

    def loopMethod(self, method, method_args, print_result, debugLog_result, save_result, threadName ):
        import OpenLog, eXLib, OpenLib, Movement, Settings
        """
        Do not Call manually. Use createLoopedThread instead.
        """
        arg_list = []
        for arg in method_args:
            arg_list.append(arg)

        chat.AppendChat(7,"______")
        chat.AppendChat(7,str(method))
        chat.AppendChat(7,str(arg_list))

        if(save_result):
            setattr(self, threadName+"Results", [])
            x = getattr(self, threadName + "Results")
        
        
        while threadName in self.thread_names:
            
            result = None
            try:
                result = method(*arg_list)
            except Exception as e:
                OpenLog.DebugPrint("Exception in Loop method: " + str(e))
                chat.AppendChat(7,str(e))
            if not None == result:
                for s in result:
                    if(print_result):
                        chat.AppendChat(7, str(s))
                    if(debugLog_result):
                        OpenLog.DebugPrint(str(s))
                    if(save_result):
                        x.append(s)
        
        chat.AppendChat(7,"Thread with name " + threadName + " interrupted and stopped.")


    def loopMethod_buffered(self, pauseTime, print_result, debugLog_result, save_result, threadName ):
        import OpenLog,eXLib, OpenLib, Movement, Settings
        """
        Do not Call manually. Use createLoopedThread_buffered instead.
        """
        
        setattr(self, threadName+"_Buffer", [])
        buffer = getattr(self,threadName+"_Buffer")

        if(save_result):
            setattr(self, threadName+"Results", [])
            x = getattr(self, threadName + "Results")

        while threadName in self.thread_names:
            
            arg_list = []
            method = None

            if len(buffer)<1:
                time.sleep(pauseTime)
                continue
            else:
                pass
                obj = buffer.pop(0)

                for arg in obj.args:
                    arg_list.append(arg)


            if not None == obj.method:
                result = method(*arg_list)
            else:
                chat.AppendChat(7,"Warning: loop-method got object without method!")
                OpenLog.DebugPrint("Warning: loop-method got object without method! Printing Arg_List: " + str(arg_list))
            
            if not None == result:
                for s in result:
                    if(print_result):
                        chat.AppendChat(7, str(s))
                    if(debugLog_result):
                        OpenLog.DebugPrint(str(s))
                    if(save_result):
                        x.append(s)
            time.sleep(pauseTime)
            
        chat.AppendChat(7,"Debug: Thread " + threadName + " interrupted and stopped.")

    
    def stopThread(self,name):
        chat.AppendChat(7,"stopThread executed")
        if (name in self.thread_names):
            self.thread_names.remove(name)
        else :
            chat.AppendChat(7,"Thread Name not defined.")


#Wrapper Class for methods, to be able to create array "Buffer" containing those objects. 
class methodObj: 
    def __init__(self,method, method_args):
        self.method = method
        self.args = method_args


threadInstance = OpenThread()