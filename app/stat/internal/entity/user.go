package entity

import (
	"time"
)

type TGUser struct {
	TgUserID                string     `gorm:"size:30;uniqueIndex;column:tg_user_id"`
	FirstName               string     `gorm:"size:200;column:first_name"`
	LastName                string     `gorm:"size:200;column:last_name"`
	Username                string     `gorm:"size:200;uniqueIndex;column:username"`
	CountGenerations        uint       `gorm:"default:0;column:count_generations"`
	CountVideoGenerations   uint       `gorm:"default:0;column:count_video_generations"`
	IsLearnModel            bool       `gorm:"default:true;column:is_learn_model"`
	GodMod                  bool       `gorm:"default:false;column:god_mod"`
	Referal                 string     `gorm:"size:30;column:referal"`
	Effect                  string     `gorm:"size:100;column:effect"`
	TuneID                  string     `gorm:"size:30;column:tune_id"`
	GodModText              string     `gorm:"type:text;column:god_mod_text"`
	Category                string     `gorm:"size:300;column:category"`
	Gender                  string     `gorm:"size:300;column:gender"`
	LastActivity            time.Time  `gorm:"autoUpdateTime;column:last_activity"`
	HasPurchased            bool       `gorm:"default:true;column:has_purchased"`
	Subscribe               *time.Time `gorm:"column:subscribe"`
	MaternityPaymentID      string     `gorm:"size:200;column:maternity_payment_id"`
	ReferralCount           uint       `gorm:"default:0;column:referral_count"`
	RewardGenerations       uint       `gorm:"default:0;column:reward_generations"`
	ReferralPurchases       uint       `gorm:"default:0;column:referral_purchases"`
	ReferralPurchasesAmount float64    `gorm:"type:decimal(10,2);default:0;column:referral_purchases_amount"`
	UserPurchasesCount      uint       `gorm:"default:0;column:user_purchases_count"`
	UserPurchasesAmount     float64    `gorm:"type:decimal(10,2);default:0;column:user_purchases_amount"`
}
