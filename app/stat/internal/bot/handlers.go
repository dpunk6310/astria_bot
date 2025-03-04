package bot

import tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"

func (t *telegramBot) sendStartMsg(update tgbotapi.Update) {
	msg := tgbotapi.NewMessage(update.Message.Chat.ID, t.getStartMessage())
	_, err := t.bot.Send(msg)
	if err != nil {
		t.log.Errorf("Error sending message to telegram: %v", err)
		return
	}
}
