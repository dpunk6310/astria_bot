package storage

import (
	"github.com/dpunk6310/astria_bot/app/stat/pkg/logging"
	"gorm.io/gorm"
)

type Storage struct {
	db  *gorm.DB
	log logging.Logger
}

func NewStorage(log logging.Logger, db *gorm.DB) *Storage {
	return &Storage{
		db:  db,
		log: log,
	}
}
