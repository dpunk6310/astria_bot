package config

import (
	"log"
	"sync"

	"github.com/ilyakaznacheev/cleanenv"
)

type Config struct {
	AppConfig struct {
		Telegram struct {
			TelegramBotToken string `env:"TELEGRAM_BOT_TOKEN_STAT"`
		}
		PostgresSQL struct {
			Username string `env:"POSTGRES_USER"`
			Password string `env:"POSTGRES_PASSWORD"`
			Host     string `env:"POSTGRES_HOST"`
			Port     string `env:"POSTGRES_PORT" env-default:"5432"`
			Database string `env:"POSTGRES_DB"`
		}
	}
}

var instance *Config
var once sync.Once

func GetConfig() *Config {
	once.Do(func() {

		instance = &Config{}

		if err := cleanenv.ReadConfig(".env", instance); err != nil {
			helpText := "Pingwin stat bot"
			help, _ := cleanenv.GetDescription(instance, &helpText)
			log.Print(help)
			log.Fatal(err)
		}
	})
	return instance
}
