# 02: Додавання каналу

Part of [#1](https://github.com/virus231/channel-radar/issues/1).

**What to build:** Користувач додає `@durov` у формі, відразу бачить стан збору,
а за секунди на теплому сервісі — збережені пости та counters із Telegram-прев’ю.

**Blocked by:** [#2](https://github.com/virus231/channel-radar/issues/2).

**Status:** implemented; live acceptance pending

## Acceptance criteria

- [x] Username нормалізується; POST повертає 202 до завершення зовнішніх запитів, а повторний username — 200 з існуючим каналом.
- [x] Всі Telegram-запити спрямовані на `t.me/s/<username>` без Bot API, Telegram credentials і довільних URL.
- [x] Парсер нормалізує текст, message IDs, дати, підписників, перегляди й доступні реакції; відсутні counters залишаються null.
- [x] Збереження використовує природний ключ поста й timestamp спостереження; перший збір читає останню сторінку, без повного backfill.
- [x] React polling показує pending/collecting/ready/unavailable/error; порожній публічний канал відрізняється від недоступного.
- [x] Offline fixtures покривають K/M counters, multiline, media-only, ID gaps, missing metrics і сторінку без прев’ю.
- [x] Offline API та UI тести перевіряють повторне додавання, polling і недоступне джерело; текст постів рендериться без raw HTML.
- [ ] На deployed URL додано реальний канал і виміряно час до перших даних; обмеження холодного старту описано чесно.

## Verification

Pytest із заблокованою мережею та mocked Telegram transport; Vitest/React Testing
Library з mocked API; реальне додавання `@durov` у deployed браузері й перевірка
збережених даних у PostgreSQL.

## Поточні докази — 2026-10-08

- 11 offline backend tests, 9 frontend tests, TypeScript/production build.
- PostgreSQL: migration `0002_first_collection`, Alembic check без drift.
- Локальний браузер: `@durov`, 20 реальних постів, mobile 390 px без overflow.
- Code review від `3705adb`: Standards — 0 порушень/зауважень; Spec — 0 дефектів коду.
- Live deployment і вимірювання першого результату залишаються перед закриттям задачі.
