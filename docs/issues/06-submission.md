# 06: Перевірка здачі

Part of [#1](https://github.com/virus231/channel-radar/issues/1).

**What to build:** Рев’юер отримує доступ до репозиторію й робочого сервісу,
відтворює запуск/тести та проходить демонстраційний сценарій без додаткових пояснень.

**Blocked by:** [#6](https://github.com/virus231/channel-radar/issues/6).

**Status:** ready-for-agent

## Acceptance criteria

- [ ] Повна offline pytest suite, frontend tests, TypeScript check і production build проходять; звіт відрізняє mocks від live перевірок.
- [ ] Міграції й повторний збір перевірені на PostgreSQL; перезапуск не втрачає дані й не залишає завислих зборів.
- [ ] Публічний URL відповідає; перевірені холодний старт/наступний cron виклик та актуальні provider quotas.
- [ ] Browser smoke проходить додавання нового каналу, polling, графіки/період, деталі поста, оригінал і реальний дайджест.
- [ ] README починається з фактичного live URL, містить перевірені local commands, схему даних, AI failure policy й обмеження хостингу/покриття.
- [ ] CLAUDE.md і три ADR відповідають реалізації; вихідне TEST-TASK.md збережене без змін.
- [ ] Репозиторій публічний за рішенням користувача; рев’юер має обидва посилання перед здачею.
- [ ] Git history і tracked files перевірені на секрети; credentials не потрапили у frontend artifact або logs.
- [ ] Підготовлено обидва посилання, 3–5 речень про найважче рішення й сценарій 30-хвилинного дзвінка.

## Verification

Чистий клон для запуску за README; повні перевірки; browser acceptance на deployed
URL; стан cron jobs і quota meters; перевірка доступу рев’юера та секретів.
Після виконання критеріїв закрити цю задачу й головну специфікацію.
