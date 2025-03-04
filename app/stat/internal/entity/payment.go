package entity

import "time"

type Payment struct {
	TgUserID              string    `gorm:"size:30;column:tg_user_id"`                // TG User ID
	PaymentID             string    `gorm:"size:200;uniqueIndex;column:payment_id"`   // Payment ID (уникальный)
	Status                bool      `gorm:"default:false;column:status"`              // Статус платежа
	CountGenerations      uint      `gorm:"default:0;column:count_generations"`       // Кол-во генераций
	CountVideoGenerations uint      `gorm:"default:0;column:count_video_generations"` // Кол-во генераций видео
	Amount                string    `gorm:"size:20;column:amount"`                    // Сумма платежа
	LearnModel            bool      `gorm:"default:false;column:learn_model"`         // Обучение модели
	IsFirstPayment        bool      `gorm:"default:false;column:is_first_payment"`    // Первый платеж
	CreatedAt             time.Time `gorm:"autoCreateTime;column:created_at"`         // Дата создания
}
