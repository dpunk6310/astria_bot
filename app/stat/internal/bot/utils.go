package bot

import tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"

func (t *telegramBot) getUserData(update tgbotapi.Update) (
	int64, string, string, string, string,
) {
	userId := update.SentFrom().ID
	firstName := update.SentFrom().FirstName
	lastName := update.SentFrom().LastName
	username := update.SentFrom().UserName
	languageCode := update.SentFrom().LanguageCode

	return userId, firstName, lastName, username, languageCode
}

func (t *telegramBot) deleteOldMessage(update tgbotapi.Update) {
	msg := update.Message
	if msg == nil {
		msg = update.CallbackQuery.Message
	}
	for i := 0; i <= 10; i++ {
		mI := msg.MessageID - i
		delMsg := tgbotapi.NewDeleteMessage(update.FromChat().ID, mI)
		_, err := t.bot.Request(delMsg)
		if err != nil {
			continue
		}
	}
}

func (t *telegramBot) deleteCurrentUserMessage(update tgbotapi.Update) error {
	chatID := update.FromChat().ID
	delMsg := tgbotapi.NewDeleteMessage(chatID, update.Message.MessageID)
	_, err := t.bot.Request(delMsg)
	if err != nil {
		return err
	}
	return nil
}
