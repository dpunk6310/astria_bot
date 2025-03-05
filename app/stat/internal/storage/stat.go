package storage

import (
	"context"

	"github.com/dpunk6310/astria_bot/app/stat/internal/entity"
)

func (s *Storage) GetReferalStats(ctx context.Context, tgUserID string) (int64, int64, error) {
	var referralCount int64
	var countReferralPurchases int64
	var referralPurchasesAmount float64

	// Подсчет количества рефералов
	if err := s.db.WithContext(ctx).
		Model(&entity.TGUser{}).
		Where("referal = ?", tgUserID).
		Count(&referralCount).Error; err != nil {
		return 0, 0, err
	}

	// Подсчет количества первых успешных платежей у рефералов
	if err := s.db.WithContext(ctx).
		Model(&entity.Payment{}).
		Joins("JOIN tg_users ON tg_users.tg_user_id = payments.tg_user_id").
		Where("tg_users.referal = ? AND payments.is_first_payment = ? AND payments.status = ?", tgUserID, true, true).
		Count(&countReferralPurchases).Error; err != nil {
		return 0, 0, err
	}

	if err := s.db.WithContext(ctx).
		Model(&entity.Payment{}).
		Joins("JOIN tg_users ON tg_users.tg_user_id = payments.tg_user_id").
		Where("tg_users.referal = ? AND payments.is_first_payment = ? AND payments.status = ?", tgUserID, true, true).
		Select("COALESCE(SUM(CAST(payments.amount AS numeric)), 0)").
		Scan(&referralPurchasesAmount).Error; err != nil {
		return 0, 0, err
	}

	// Обновление полей ReferralCount и ReferralPurchases у пользователя
	if err := s.db.WithContext(ctx).
		Model(&entity.TGUser{}).
		Where("tg_user_id = ?", tgUserID).
		Updates(map[string]interface{}{
			"referral_count":            referralCount,
			"referral_purchases":        countReferralPurchases,
			"reward_generations":        20 * countReferralPurchases,
			"referral_purchases_amount": referralPurchasesAmount,
		}).Error; err != nil {
		return 0, 0, err
	}

	return referralCount, countReferralPurchases, nil
}

func (s *Storage) GetPaymentStats(ctx context.Context, tgUserID string) (int64, float64, error) {
	var count int64
	var totalAmount float64

	// Подсчет количества успешных платежей
	if err := s.db.WithContext(ctx).
		Model(&entity.Payment{}).
		Where("tg_user_id = ? AND status = ?", tgUserID, true).
		Count(&count).Error; err != nil {
		return 0, 0, err
	}

	// Подсчет суммы успешных платежей
	if err := s.db.WithContext(ctx).
		Model(&entity.Payment{}).
		Where("tg_user_id = ? AND status = ?", tgUserID, true).
		Select("COALESCE(SUM(CAST(amount AS DECIMAL(10,2))), 0)").
		Scan(&totalAmount).Error; err != nil {
		return 0, 0, err
	}

	// Обновление данных пользователя
	if err := s.db.WithContext(ctx).
		Model(&entity.TGUser{}).
		Where("tg_user_id = ?", tgUserID).
		Updates(entity.TGUser{
			UserPurchasesCount:  uint(count),
			UserPurchasesAmount: totalAmount,
		}).Error; err != nil {
		return 0, 0, err
	}

	return count, totalAmount, nil
}

func (s *Storage) GetUserInfo(ctx context.Context, tgUserID string) (map[string]interface{}, error) {
	var user entity.TGUser

	tx := s.db.WithContext(ctx).Begin()
	defer func() {
		if r := recover(); r != nil {
			tx.Rollback()
		}
	}()
	if err := tx.Error; err != nil {
		return nil, err
	}

	if err := tx.Model(&entity.TGUser{}).
		Where("tg_user_id = ?", tgUserID).
		First(&user).Error; err != nil {
		return nil, err
	}

	userInfo := map[string]interface{}{
		"TgUserID":                user.TgUserID,
		"FirstName":               user.FirstName,
		"Username":                user.Username,
		"CountGenerations":        user.CountGenerations,
		"CountVideoGenerations":   user.CountVideoGenerations,
		"Subscribe":               user.Subscribe.String(),
		"RewardGenerations":       user.RewardGenerations,
		"ReferralPurchasesAmount": user.ReferralPurchasesAmount,
	}

	if err := tx.Commit().Error; err != nil {
		return nil, err
	}

	return userInfo, nil
}
