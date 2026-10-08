# Project-local Matt Pocock skills

Джерело: https://github.com/mattpocock/skills

Ревізія: `b0618bc436ad893b3c5e84e55fba86586d34a404`.
Встановлено 2026-10-08 через стандартний Codex `skill-installer` із явними `--ref`
та `--dest .agents/skills`. Усі папки скопійовані повністю й без зміни вмісту;
MIT-ліцензія джерела збережена як `.agents/skills/LICENSE`.

| Skill | Шлях у джерелі | Призначення |
|---|---|---|
| setup-matt-pocock-skills | skills/engineering/setup-matt-pocock-skills | Конфігурація tracker і domain docs |
| grill-with-docs | skills/engineering/grill-with-docs | Узгодження нових рішень і документація |
| to-spec | skills/engineering/to-spec | Перетворення узгоджених вимог на специфікацію |
| to-tickets | skills/engineering/to-tickets | Вертикальні задачі й залежності |
| implement | skills/engineering/implement | Реалізація погодженої задачі |
| code-review | skills/engineering/code-review | Перевірка стандартів і відповідності специфікації |
| tdd | skills/engineering/tdd | Тести поведінки й короткі red/green цикли |
| codebase-design | skills/engineering/codebase-design | Межі модулів і тестові інтерфейси |
| domain-modeling | skills/engineering/domain-modeling | Словник і ADR |
| grilling | skills/productivity/grilling | Довідковий процес уточнення рішень |
| writing-for-agents | skills/productivity/writing-for-agents | Короткі інструкції для агентів |

Налаштування `setup-matt-pocock-skills` уже виконане за затвердженим планом:
GitHub Issues, `CLAUDE.md`, один словник та кореневі ADR. Повторне налаштування
потрібне лише при зміні цих домовленостей.

Skills зберігаються в Git і доступні після звичайного клонування без перевстановлення.
Новий сеанс Codex у папці проєкту знаходить їх у `.agents/skills`. Глобальні папки
skills не змінювалися. Для агента, який не підтримує цей каталог, відкрийте потрібний
`SKILL.md` безпосередньо та виконайте його в межах поточної задачі.

Оновлення skills — окрема явна дія: вибрати нову ревізію, перевірити зміни,
замінити локальні копії й оновити цей запис. Автоматичних оновлень немає.
