class Keyboard:
    import vk_api
    from vk_api.keyboard import VkKeyboard

    keyboard = VkKeyboard(one_time=False, inline=False)

    buttonsColor = "positive"
    registrationButtonText = "Регистрация на мероприятие"
    eventButtonText = "Мои мероприятия"

    keyboard.add_button(registrationButtonText, buttonsColor)
    keyboard.add_button(eventButtonText, buttonsColor)

    def get_keyboard():
        return keyboard.get_keyboard()


