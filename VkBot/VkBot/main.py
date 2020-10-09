import VkBot

if __name__ == "__main__":
    bot = VkBot.VkBot()
    while(True):
        try:
            bot.startBot()
        except Exception as e:
            print(e)
            bot = VkBot.VkBot()
            bot.startBot()
