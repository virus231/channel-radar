# 05: Кешований AI-дайджест

Part of [#1](https://github.com/virus231/channel-radar/issues/1).

**What to build:** Користувач отримує український дайджест вибраного періоду з
темами й посиланнями на використані пости; повтор незміненого запиту використовує
кеш, а помилка Gemini не зупиняє дашборд.

**Blocked by:** [#5](https://github.com/virus231/channel-radar/issues/5).

**Status:** ready-for-agent

## Acceptance criteria

- [ ] Перед підключенням перевірено доступність gemini-3.5-flash-lite/free quota для ключа; секрет є тільки в backend environment.
- [ ] Вхід — збережені текстові пости за published_at; 100 постів, 2 000 символів/пост і 40 000 символів загалом є верхніми межами.
- [ ] Порожній період не викликає Gemini; обрізаний зріз явно показує покриття.
- [ ] LLM повертає теми й резюме з відомими message IDs; backend відхиляє невідомі IDs і сам формує original links.
- [ ] Cache key містить канал, період, fingerprint фактичного текстового входу та модель; зміна тільки counters не скидає кеш.
- [ ] UI показує generating/ready/error, polling і явне повторення; попередній успішний результат лишається доступним як stale.
- [ ] Timeout 20 секунд, 429/5xx і невалідна відповідь впливають лише на дайджест; автоматичного retry loop немає.
- [ ] Offline tests використовують mocked AI success/cache/error/timeout/invalid IDs; загальний API працює після AI-помилки.
- [ ] Окремий реальний запит на deployed сервісі підтверджує змістовний дайджест і коректні посилання.

## Verification

Pytest із заблокованою мережею для AI operation і кешу; frontend UI tests для
генерації й помилки; один свідомий live Gemini acceptance check поза test suite.
