package main

import (
	"context"

	"github.com/dpunk6310/astria_bot/app/stat/internal/bot"
	"github.com/dpunk6310/astria_bot/app/stat/internal/config"
	database "github.com/dpunk6310/astria_bot/app/stat/internal/db"
	st "github.com/dpunk6310/astria_bot/app/stat/internal/storage"
	"github.com/dpunk6310/astria_bot/app/stat/pkg/logging"
	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
)

func main() {
	logging.Init()
	log := logging.GetLogger()
	log.Infoln("init logger successfully")

	// Init Config
	cfg := config.GetConfig()
	log.Infoln("init config successfully")

	// Init Context
	ctx := context.Background()

	db, err := database.NewPostgresDB(cfg, &log)
	if err != nil {
		log.Fatalf("error init database: %s", err.Error())
	}
	log.Infoln("init database successfully")

	tgBot, err := initTelegramBot(log, cfg)
	if err != nil {
		log.Panicln("Failed to initialize telegram bot (initTelegramBot)", err)
	}
	log.Infoln("init tgBot successfully")

	storage := st.NewStorage(log, db)
	log.Infoln("init storage successfully")

	tgBotHandler := bot.NewTelegramBot(ctx, tgBot, log, storage)
	log.Infoln("init tgBotHandler successfully")

	u := tgbotapi.NewUpdate(0)
	u.Timeout = 60
	updates := tgBot.GetUpdatesChan(u)

	tgBotHandler.HandleUpdates(log, tgBot, updates)
}

func initTelegramBot(
	log logging.Logger,
	cfg *config.Config,
) (*tgbotapi.BotAPI, error) {
	tgBot, err := tgbotapi.NewBotAPI(cfg.AppConfig.Telegram.TelegramBotToken)
	if err != nil {
		log.Fatalln("Failed to initialize Telegram bot:", err)
		return nil, err
	}

	tgBot.Debug = true

	u := tgbotapi.NewUpdate(0)
	u.Timeout = 60

	return tgBot, nil
}
