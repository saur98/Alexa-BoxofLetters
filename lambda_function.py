import ask_sdk_core
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk.standard import StandardSkillBuilder
from ask_sdk_core.utils import is_intent_name, is_request_type
from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response, ui
from bs4 import BeautifulSoup
import requests
import random

sb = StandardSkillBuilder(table_name="BoxOfLetters", auto_create_table=True)

@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    per_attributes = handler_input.attributes_manager.persistent_attributes
    response_builder = handler_input.response_builder
    session_attr = handler_input.attributes_manager.session_attributes
    if not per_attributes:
        per_attributes["games_played"] = 0
        per_attributes["game_state"] = "ENDED"
        per_attributes["ended_session_count"] = 0
    session_attr["Points"] = 0
    session_attr["games_played"] = 0
    session_attr["box_opened"]=0
    handler_input.attributes_manager.persistent_attributes = per_attributes
    handler_input.attributes_manager.session_attributes = session_attr
    say = "<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_intro_01'/>Welcome to the Box of letters<break/>I am alexa your host for the game<break/>Would you like to open a box<break/>Say yes or no ?"
    response_builder.set_card(ui.SimpleCard("Box Of Letters", content="WELCOME TO BOX OF LETTERS.WOULD YOU LIKE TO OPEN ONE?"))
    reprompt = "Say yes to Open or no to keep the Box closed"
    return response_builder.speak(say).ask(reprompt=reprompt).set_should_end_session(False).response

@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    say = "The game is to form more and more words output from the given letters<break/>Just open the box and let the game begin<break/>Do you want to open the box?Say yes to open or no to exit." 
    return handler_input.response_builder.speak(say).ask(say).response

@sb.request_handler(can_handle_func=is_intent_name("AMAZON.FallbackIntent"))
def fallback_handler(handler_input):
    speech = (
        '<say-as interpret-as="interjection">achoo!</say-as>'
        "The box is having issues you have said the wrong SPELL."
        "You can say alexa launch Box Of Letters or just continue with the words if the box if open")
    reprompt = "You can say alexa launch box of letters."
    handler_input.response_builder.speak(speech).ask(reprompt)
    return handler_input.response_builder.response  

def currently_playing(handler_input):
    """Function that acts as can handle for game state."""
    # type: (HandlerInput) -> bool
    is_currently_playing = False
    session_attr = handler_input.attributes_manager.session_attributes

    if ("game_state" in session_attr
            and session_attr['game_state'] == "STARTED"):
        is_currently_playing = True

    return is_currently_playing

@sb.request_handler(
    can_handle_func=lambda input:
        is_intent_name("AMAZON.CancelIntent")(input) or
        is_intent_name("AMAZON.StopIntent")(input))
def cancel_and_stop_intent_handler(handler_input):
    """Single handler for Cancel and Stop Intent."""
    # type: (HandlerInput) -> Response
    speech_text = "Thanks for playing!!"
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr["wordformed"]=''
    handler_input.attributes_manager.session_attributes=session_attr
    handler_input.response_builder.speak(
        speech_text).set_should_end_session(True)
    return handler_input.response_builder.response

@sb.request_handler(can_handle_func=is_intent_name("AMAZON.YesIntent"))
def yes_intent(handler_input):
    response_builder = handler_input.response_builder
    session_attr = handler_input.attributes_manager.session_attributes
    if session_attr["box_opened"]==1:
        say="Please close the box first<break/> you can say skip to close the box or complete all the words<break/>"
        handler_input.attributes_manager.session_attributes = session_attr
        return response_builder.speak(say).ask(reprompt="Say yes or no").set_should_end_session(False).response
    while 1==1:
        say = '<say-as interpret-as="interjection">abracadabra!</say-as>Okay Spell caster so you have opened the box'+"<audio src='soundbank://soundlibrary/magic/amzn_sfx_fairy_melodic_chimes_01'/>"
        box=[]
        dict1={}
        rand=random.randint(5,8)
        for i in range(rand+1):
            letter=random.randint(0,25)
            box.append(chr(letter+97))
        url="http://www.allscrabblewords.com/unscramble/"
        letterlist=''
        for i in range(rand):
            letterlist+=box[i]
            url=url+box[i]+"%20"
        req=requests.get(url)
        soup= BeautifulSoup(req.text, 'html.parser')
        c = soup.find_all('div', attrs={"class": "panel panel-info"})
        for each in c:
            if each != None:
                c1=each.find('div', attrs={"class": "panel-heading"})
                if c1 != None:
                    c11=c1.find('h3', attrs={"class": "panel-title"})
                    if c11 != None:
                        str1=c11.text[0]
                        if int(str1)<3:
                            continue
                        dict1[str1]=[]
                    c2=each.find('div', attrs={"class": "panel-body unscrambled"})
                    if c2 != None:
                        c22=c2.find('ul', attrs={"class": "list-inline"})
                        if c22 != None:
                            c222=c22.find_all('li')
                            for i in c222:
                                if i != None:
                                    word=i.find('a')
                                    dict1[str1].append(word.text)
                                    #print(word.text)
        if(bool(dict1)==False):
            continue
        else:
            break
    #passlevel1()
    #print("hi")
    st=''
    for i in letterlist:
        st+=i+" "
    session_attr["letterlist1"]=st
    say1="LETTERS ARE AS FOLLOWS "+st
    st=''
    for i in letterlist:
        st+=i+" <break/>"
    letterlist=st
    say+='The letters are <break/> <prosody volume="+6dB">'+letterlist+'<break strength="strong"/> </prosody> Guess the words <break strength="strong"/> Enter your guess <prosody volume="+5dB">letter by letter </prosody><break/>Such as the letter b or the letter l<break strength="x-strong"/> at last <break/> say <prosody volume="+5dB">done</prosody><break/>you can say done when you think the box is empty.<break strength="x-strong"/> If you want to skip a box say <prosody volume="+5dB">skip</prosody>'
    session_attr["wordlist"] = dict1
    session_attr["letterlist"]=letterlist
    session_attr["wordmaking"] = 1
    session_attr["wordformed"]=''
    session_attr["game_state"]="STARTED"
    session_attr["box_opened"]=1
    handler_input.attributes_manager.session_attributes = session_attr
    response_builder.set_card(ui.SimpleCard(title="Box Of Letters",content=say1))
    return response_builder.speak(say).ask(reprompt="say a letter").set_should_end_session(False).response

@sb.request_handler(can_handle_func=is_intent_name("AMAZON.NoIntent"))
def no_handler(handler_input):
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr["game_state"] = "ENDED"
    session_attr["wordformed"]="null"
    handler_input.attributes_manager.session_attributes = session_attr

    speech_text = "<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_outro_01'/>Ok See you next time!!"

    handler_input.response_builder.speak(speech_text)
    return handler_input.response_builder.response

@sb.request_handler(can_handle_func=is_intent_name("HintIntent"))
def hint_intent(handler_input):
    response_builder = handler_input.response_builder
    session_attr = handler_input.attributes_manager.session_attributes
    if session_attr["box_opened"]==0:
        say="Please open a box first<break/>Say yes to open or no to quit"
        reprompt="Please open a box first<break/>Say yes to open or no to quit"
    else:
        dict1=session_attr["wordlist"]
        session_attr["wordformed"]=''
        for i in range(9):
                if str(i) in dict1 and bool(dict1[str(i)])==True:
                    good=1
        if good==1:
            c=0
            for i in dict1:
                for j in dict1[i]:
                    c=c+1
            r=random.randint(1,c)
            for i in dict1:
                for j in dict1[i]:
                    r=r-1
                    if r==0:
                        say="One of the words are <break/>" +'<say-as interpret-as="characters">'+j+'</say-as>'+"<break/>But you cannont use it now<break/>."
                        if c==1:
                            say+='<say-as interpret-as="interjection">hurray!</say-as>Congratulations you have completed all the words<break strength="strong"/>Your points are {}<break strength="strong"/>Would you like to open another box ?<break/>say yes to open or no to keep the box closed<break/>'.format(session_attr["Points"])
                            session_attr["box_opened"]=0
                        else:
                            say+="<break/>Continue Guessing"
                            st=session_attr["letterlist1"]
                            say+="<break/>YOUR LETTERS ARE AS FOLLOWS\n"+st
                            dict1[i].remove(j)
                        break
            reprompt="Enjoy the game"
        else:
            say='<say-as interpret-as="interjection">hurray!</say-as>Congratulations you have completed all the words<break strength="strong"/>Your points are {}<break strength="strong"/>Would you like to open another box ?<break/>say yes to open or no to keep the box closed<break/>'.format(session_attr["Points"])
            reprompt="Say yes to open or no to quit"
            session_attr["box_opened"]=0
    handler_input.attributes_manager.persistent_attributes = session_attr
    return response_builder.speak(say).ask(reprompt=reprompt).set_should_end_session(False).response

@sb.request_handler(can_handle_func=is_intent_name("PlayGameIntent"))
def play_game_intent(handler_input):
    #print("in game")
    response_builder = handler_input.response_builder
    session_attr = handler_input.attributes_manager.session_attributes
    if session_attr["box_opened"]==0:
        say='The box is closed<break strength="strong"/>'+"Say Yes if you want to open it <break/>or<break/> say No to skip it"
        reprompt = "Say yes to Open or no to keep the Box closed"
        handler_input.attributes_manager.session_attributes = session_attr
        return response_builder.speak(say).ask(reprompt=reprompt).set_should_end_session(False).response
    dict1=session_attr["wordlist"]
    st=session_attr["letterlist1"]
    letterlist=session_attr["letterlist"]
    good=0
    string1=''
    say1="YOUR LETTERS ARE AS FOLLOWS\n"+st
    if session_attr["wordmaking"]==1:
        guessed_letter = handler_input.request_envelope.request.intent.slots["inputLetter"].value
        print(guessed_letter)
        guessed_letter = guessed_letter.lower()
        if guessed_letter=="skip" or guessed_letter=="Skip" or guessed_letter=="SKIP":
            stri=''
            for i in dict1:
                stri+=i+" letter words are : "
                for j in dict1[i]:
                    stri+=j+"<break/> "
                stri+='<break strength="strong"/>'
            say1=''
            for i in dict1:
                say1+=i+" letter words are : "
                for j in dict1[i]:
                    say1+=j+" "
            say="Your points are {}".format(session_attr["Points"])
            say+="<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_bridge_02'/>"+'<say-as interpret-as="interjection">all righty!</say-as><break/>The words left were<break/>'+stri+"<break/>Would you like to play another game?"
            reprompt = "Say yes to Open or no to keep the Box closed"
            session_attr["games_played"] += 1
            session_attr["game_state"] = "ENDED"
            session_attr["wordformed"]= "null"
            session_attr["box_opened"]=0
            handler_input.attributes_manager.persistent_attributes = session_attr
            handler_input.attributes_manager.save_persistent_attributes()
            response_builder.set_card(ui.SimpleCard(title="Box Of Letters", content=say1))
            return response_builder.speak(say).ask(reprompt=reprompt).set_should_end_session(False).response
        elif guessed_letter=="DONE" or guessed_letter=="done" or guessed_letter=="Done":
            session_attr["wordmaking"]=0
        else:
            guessed_letter=guessed_letter[0]
            string1=session_attr["wordformed"]
            string1=string1+guessed_letter
            session_attr["wordformed"]=string1
            say="<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_player1_01'/>"+"Say done when your word is completed <break/> The word formed till now is <break/>"+'<say-as interpret-as="characters">'+string1+'</say-as>'
            response_builder.set_card(ui.SimpleCard(title="Box Of Letters", content=say1+"\n"+string1))
            return response_builder.speak(say).ask(reprompt="Say a letter").set_should_end_session(False).response
    length=len(session_attr["wordformed"])
    if length<3 or str(length) not in dict1:
        print(dict1,length,string1)
        session_attr["wordmaking"] = 1
        session_attr["wordformed"]=''
        say="<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_negative_response_02'/>"+'<say-as interpret-as="interjection">aw man!</say-as>The box didn'+"'t approve Try Again <break/> the letters are <break/>"+letterlist
        response_builder.set_card(ui.SimpleCard(title="Box Of Letters", content=say1))
        return response_builder.speak(say).ask(reprompt="Say a letter").set_should_end_session(False).response
    else:
        f=0
        for i in dict1[str(length)]:
            if i==session_attr["wordformed"]:
                f=1
                session_attr["Points"]=session_attr["Points"]+1
                dict1[str(length)].remove(i)
                session_attr["wordlist"] = dict1
                break
        if f==1:
            for i in range(9):
                if str(i) in dict1 and bool(dict1[str(i)])==True:
                    good=1
            if good==1:
                session_attr["wordmaking"] = 1
                session_attr["wordformed"]=''
                say="<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_positive_response_02'/>"+'<say-as interpret-as="interjection">bingo!</say-as><break/>Fantastic, you guessed it right <break/>The box is happy<break/> Now enter your next guess <break/> the letters are<break/>'+letterlist
                response_builder.set_card(ui.SimpleCard(title="Box Of Letters", content=say1))
                return response_builder.speak(say).ask(reprompt="Say a letter").set_should_end_session(False).response
            else:
                say='<say-as interpret-as="interjection">hurray!</say-as>Congratulations you have completed all the words<break strength="strong"/>Your points are {}<break strength="strong"/>Would you like to open another box ?<break/>say yes to open or no to keep the box closed<break/>'.format(session_attr["Points"])
                reprompt = "Say yes to Open or no to keep the Box closed"
                response_builder.set_card(ui.SimpleCard(title="Box Of Letters", content="VOCAB KING"))
                session_attr["games_played"] += 1
                session_attr["game_state"] = "ENDED"
                session_attr["wordformed"]= "null"
                session_attr["box_opened"]=0
                handler_input.attributes_manager.persistent_attributes = session_attr
                handler_input.attributes_manager.save_persistent_attributes()
                return response_builder.speak(say).ask(reprompt=reprompt).set_should_end_session(False).response                
        if f==0:
            session_attr["wordmaking"] = 1
            session_attr["wordformed"]=''
            say="<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_negative_response_02'/>"+'<say-as interpret-as="interjection">aw man!</say-as>The box didnt approve<break/> Try Again <break/> the letters are <break/>'+letterlist
            response_builder.set_card(ui.SimpleCard(title="Box Of Letters", content=say1))
            return response_builder.speak(say).ask(reprompt="Say a letter").set_should_end_session(False).response
    
@sb.request_handler(can_handle_func=lambda input: True)
def unhandled_intent_handler(handler_input):
    """Handler for all other unhandled requests."""
    say ="If you have opened the box continue guessing the words if you haven't<break/> NO,problem<break/>Say yes to open or no to Exit"
    handler_input.response_builder.speak(say).ask(say)
    return handler_input.response_builder.response


lambda_handler = sb.lambda_handler()



     
