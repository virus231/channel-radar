# Issue tracker: GitHub

Репозиторій: `virus231/channel-radar`. Специфікації та задачі публікуються як GitHub
Issues через `gh`. Виконуйте команди з кореня клону або передавайте
`--repo virus231/channel-radar`.

## Джерела й статуси

- `docs/spec.md` — авторитетний текст специфікації; головна Issue містить його копію.
- `docs/issues/` — версіоновані тексти шести задач; кожна має GitHub Issue.
- `docs/development-plan.md` — порядок, перевірки та посилання на Issues.
- Зміна узгодженої вимоги оновлює файл і відповідну Issue разом.
- `ready-for-agent` означає, що задача описана; починати її можна після закриття
  всіх блокерів. Задача залишається відкритою, доки не виконані її критерії.
- Навіть за готового плану розробку не починають у межах задачі підготовки.
- Skills `triage` немає; окремий процес тріажу й п’ять triage labels не налаштовані.
- **PRs as a request surface: no.**

## Операції

- Прочитати: `gh issue view NUMBER --json number,title,body,labels,comments`.
- Створити: `gh issue create --title 'TITLE' --body-file BODY.md --label ready-for-agent`.
- Оновити: `gh issue edit NUMBER --body-file BODY.md`.
- Список: `gh issue list --state open --json number,title,labels,assignees`.
- Зв’язок із головною специфікацією: GitHub sub-issue і посилання `Part of #NUMBER`.
- Залежності: GitHub native blocked-by та явний `Blocked by: #NUMBER` у тексті.
  Для роботи використовуються тільки задачі з усіма закритими блокерами.
- Закрити після перевірки: `gh issue close NUMBER --comment 'Результат і перевірки'`.

Для native relationships використовуйте database ID Issue, а не її номер:
`gh api repos/virus231/channel-radar/issues/NUMBER --jq .id`.

Додати дочірню Issue:

```sh
gh api --method POST repos/virus231/channel-radar/issues/PARENT/sub_issues -F sub_issue_id=CHILD_ID
```

Додати блокер:

```sh
gh api --method POST repos/virus231/channel-radar/issues/CHILD/dependencies/blocked_by -F issue_id=BLOCKER_ID
```

Головну Issue закривають лише після виконання всіх задач і перевірки живого сервісу.
