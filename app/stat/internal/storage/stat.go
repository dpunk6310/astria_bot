package storage

import (
	"context"

	"github.com/dpunk6310/astria_bot/app/stat/internal/entity"
)

func (s *Storage) GetReferalStats(ctx context.Context, tgUserID string) (int64, float64, error) {
	var referralCount int64
	var totalReferralPurchases float64

	tx := s.db.WithContext(ctx).Begin()
	defer func() {
		if r := recover(); r != nil {
			tx.Rollback()
		}
	}()
	if err := tx.Error; err != nil {
		return 0, 0, err
	}

	// Подсчет количества рефералов
	if err := tx.Model(&entity.TGUser{}).Where("referal = ?", tgUserID).Count(&referralCount).Error; err != nil {
		return 0, 0, err
	}

	// Сумма покупок рефералов
	if err := tx.Model(&entity.TGUser{}).
		Where("referal = ?", tgUserID).
		Select("SUM(user_purchases_amount)").
		Scan(&totalReferralPurchases).Error; err != nil {
		return 0, 0, err
	}

	if err := tx.Commit().Error; err != nil {
		return 0, 0, err
	}

	return referralCount, totalReferralPurchases, nil
}

func (s *Storage) GetPaymentStats(ctx context.Context, tgUserID string) (int64, float64, error) {
	var count int64
	var totalAmount float64

	tx := s.db.WithContext(ctx).Begin()
	defer func() {
		if r := recover(); r != nil {
			tx.Rollback()
		}
	}()
	if err := tx.Error; err != nil {
		return 0, 0, err
	}

	if err := tx.Model(&entity.Payment{}).Where("tg_user_id = ? AND status = ?", tgUserID, true).Count(&count).Error; err != nil {
		return 0, 0, err
	}

	if err := tx.Model(&entity.Payment{}).
		Where("tg_user_id = ? AND status = ?", tgUserID, true).
		Select("SUM(CAST(amount AS DECIMAL(10,2)))").
		Scan(&totalAmount).Error; err != nil {
		return 0, 0, err
	}

	if err := tx.Commit().Error; err != nil {
		return 0, 0, err
	}

	return count, totalAmount, nil
}
