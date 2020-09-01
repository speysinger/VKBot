import vk_api
import json
import VkKeyboard
from vk_api.longpoll import VkLongPoll, VkEventType

vk_session = vk_api.VkApi(token = "bc869b29041d5059d84fdb9bb230c55faafbfa6bfd210361a62e33d212dc7b0c90f393187a92f0f6a1803")
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)
keyboard = VkKeyboard.Keyboard

def sender(id, text):
    session_api.messages.send(user_id = id, message = text, random_id = 0, keyboard = keyboard.get_keyboard())
   
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            msg = event.text.lower()
            id = event.user_id
            print(id)
            if(msg == "1"):
                sender(id, "1")
            if(msg == keyboard.registrationButtonText):
                sender(id, "ya")
            elif(msg == keyboard.eventButtonText):
                sender(id, 'zero')