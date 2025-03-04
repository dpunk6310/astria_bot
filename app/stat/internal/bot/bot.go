package bot

import (
	"context"

	"github.com/dpunk6310/astria_bot/app/stat/internal/storage"
	"github.com/dpunk6310/astria_bot/app/stat/pkg/logging"
	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
)

type telegramBot struct {
	ctx context.Context
	bot *tgbotapi.BotAPI
	log logging.Logger
	st  *storage.Storage
}

func NewTelegramBot(
	ctx context.Context,
	bot *tgbotapi.BotAPI,
	log logging.Logger,
	st *storage.Storage,
) *telegramBot {
	return &telegramBot{
		ctx: ctx,
		bot: bot,
		log: log,
		st:  st,
	}
}

func (t *telegramBot) HandleUpdates(log logging.Logger, bot *tgbotapi.BotAPI, updates tgbotapi.UpdatesChannel) {
	for update := range updates {
		if update.Message != nil {
			switch update.Message.Command() {
			case "start":
				t.sendStartMsg(update)
			default:
				err := t.deleteCurrentUserMessage(update)
				if err != nil {
					t.log.Errorln(err)
					return
				}
			}
		}
		if update.CallbackQuery != nil {
			// if update.CallbackQuery.Data == "promote" {
			// 	t.sendPromoteHandlerCallback(update)
			// }

			// count, totalAmount, err := storage.GetPaymentStats(ctx, "758103378")
			// log.Infoln(count, totalAmount)

			// referralCount, totalReferralPurchases, err := storage.GetReferalStats(ctx, "939392408")
			// log.Infoln(referralCount, totalReferralPurchases)
		}
	}
}
