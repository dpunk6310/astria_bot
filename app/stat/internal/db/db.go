package database

import (
	"fmt"

	"github.com/dpunk6310/astria_bot/app/stat/internal/config"
	"github.com/dpunk6310/astria_bot/app/stat/pkg/logging"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func NewPostgresDB(cfg *config.Config, log *logging.Logger) (*gorm.DB, error) {
	dsn := fmt.Sprintf(
		"postgres://%s:%s@%s:%s/%s",
		cfg.AppConfig.PostgresSQL.Username,
		cfg.AppConfig.PostgresSQL.Password,
		cfg.AppConfig.PostgresSQL.Host,
		cfg.AppConfig.PostgresSQL.Port,
		cfg.AppConfig.PostgresSQL.Database,
	)
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatalf("Error connection database: %v", err)
		return nil, err
	}

	// if err := migrate(db); err != nil {
	// 	log.Errorln("Error migrate database")
	// 	return nil, err
	// }

	return db, nil
}

// func migrate(db *gorm.DB) error {
// 	if err := db.AutoMigrate(); err != nil {
// 		return err
// 	}
// 	return nil
// }
