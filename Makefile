# Makefile

.PHONY: up down build logs ps init-db restart

# Tüm servisleri build edip ayağa kaldır
up:
	docker compose up -d --build

# Tüm servisleri durdur
down:
	docker compose down

# Servisleri yeniden build et
build:
	docker compose build

# Çalışan container'ların loglarını takip et
logs:
	docker compose logs -f

# Container durumunu göster
ps:
	docker compose ps

# DB tablolarını initialize et (db_prep.py veya db.py __main__ çalıştırır)
init-db:
	docker compose run --rm app python db_prep.py

# Uygulama servisini yeniden başlat
restart:
	docker compose restart app
