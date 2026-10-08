import { useQuery } from '@tanstack/react-query';
import { getChannels } from './api';

export function App() {
  const channels = useQuery({ queryKey: ['channels'], queryFn: getChannels });

  return (
    <div className="shell">
      <header className="header">
        <a className="brand" href="/" aria-label="Channel Radar — головна">
          <span className="brand-mark" aria-hidden="true">◉</span>
          Channel <span className="brand-accent">Radar</span>
        </a>
        <span className="version">Стартова версія</span>
      </header>
      <main>
        <div className="intro">
          <div>
            <p className="eyebrow">ВАШ ІНФОРМАЦІЙНИЙ ПРОСТІР</p>
            <h1>Огляд каналів</h1>
            <p className="subtitle">Пости й динаміка Telegram-каналів в одному місці.</p>
          </div>
          <div className="counter">
            <span>Каналів у радарі</span>
            <strong>{channels.data?.length ?? '—'}</strong>
          </div>
        </div>
        <section className="panel" aria-labelledby="channels-title">
          <div className="panel-header">
            <h2 id="channels-title">Ваші канали</h2>
            <span className="panel-label">Публічні джерела</span>
          </div>
          {channels.isPending && <div className="state" role="status"><span className="loading-dot" />Завантажуємо канали…</div>}
          {channels.isError && (
            <div className="state" role="alert">
              <h3>Не вдалося завантажити канали</h3>
              <p>Перевірте з’єднання та повторіть спробу.</p>
              <button onClick={() => void channels.refetch()}>Спробувати ще раз</button>
            </div>
          )}
          {channels.data?.length === 0 && (
            <div className="state empty-state">
              <div className="radar" aria-hidden="true"><span /></div>
              <h3>Поки що немає каналів</h3>
              <p>Тут з’являться канали, за якими ви стежите.<br />Додавання каналів ще готується.</p>
              <span className="empty-caption">Ваш огляд починається тут</span>
            </div>
          )}
          {!!channels.data?.length && (
            <ul className="channel-list">
              {channels.data.map((channel) => (
                <li key={channel.id}>
                  <span className="channel-avatar" aria-hidden="true">{(channel.title || channel.username)[0].toUpperCase()}</span>
                  <div><h3>{channel.title || channel.username}</h3><p>@{channel.username}</p></div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
      <footer>Channel Radar <span>Дивіться ширше. Помічайте зміни.</span></footer>
    </div>
  );
}
