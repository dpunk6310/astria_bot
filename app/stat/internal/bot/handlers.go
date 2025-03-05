package bot

import (
	"fmt"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
)

func (t *telegramBot) sendStartMsg(update tgbotapi.Update) {

	msg := tgbotapi.NewMessage(update.Message.Chat.ID, t.getStartMessage())
	_, err := t.bot.Send(msg)
	if err != nil {
		t.log.Errorf("Error sending message to telegram: %v", err)
		return
	}
}

func (t *telegramBot) sendStatMsg(update tgbotapi.Update) {
	totalProfit, err := t.st.CalculateTotalProfit(t.ctx)
	if err != nil {
		t.log.Errorln(err)
		return
	}
	userCount, err := t.st.CountUsersWithSuccessfulPayments(t.ctx)
	if err != nil {
		t.log.Errorln(err)
		return
	}
	msgText := fmt.Sprintf(
		"Общая прибыль: %.2f\nКол-во пользователей, сделавшие минимум 1 покупку: %d",
		totalProfit, userCount,
	)
	msg := tgbotapi.NewMessage(update.Message.Chat.ID, msgText)
	_, err = t.bot.Send(msg)
	if err != nil {
		t.log.Errorf("Error sending message to telegram: %v", err)
		return
	}
}

func (t *telegramBot) handleTgUserIdMessage(update tgbotapi.Update, tgID string) {
	countPayments, totalAmountPayments, err := t.st.GetPaymentStats(t.ctx, tgID)
	t.log.Infoln(countPayments, totalAmountPayments)
	if err != nil {
		t.log.Errorln(err)
		return
	}
	referralCount, countReferralPurchases, err := t.st.GetReferalStats(t.ctx, tgID)
	t.log.Infoln(referralCount, countReferralPurchases)
	if err != nil {
		t.log.Errorln(err)
		return
	}
	userInfo, err := t.st.GetUserInfo(t.ctx, tgID)
	if err != nil {
		t.log.Errorln(err)
		return
	}

	msgText := fmt.Sprintf(
		"Telegram ID: %s\nИмя: %s\nUsername: %s\nКол-во генераций фото: %d\nКол-во генераций видео: %d\nПодписка: %s\nНачислено генераций от рефералов: %d\nКол-во покупок: %d\nСумма покупок: %.2f руб.\nКол-во рефералов: %d\nКол-во покупок рефералов: %d\nСумма покупок рефералов: %.2f руб.",
		userInfo["TgUserID"], userInfo["FirstName"], userInfo["Username"], userInfo["CountGenerations"], userInfo["CountVideoGenerations"], userInfo["Subscribe"], userInfo["RewardGenerations"], countPayments, totalAmountPayments, referralCount, countReferralPurchases, userInfo["ReferralPurchasesAmount"],
	)

	msg := tgbotapi.NewMessage(update.Message.Chat.ID, msgText)
	_, err = t.bot.Send(msg)
	if err != nil {
		t.log.Errorf("Error sending message to telegram: %v", err)
		return
	}
}
