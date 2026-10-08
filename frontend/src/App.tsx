import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { addChannel, getChannels, getPosts, type Channel } from './api';

const statuses: Record<Channel['status'], string> = {
  pending: 'Очікує збору', collecting: 'Збираємо пости', ready: 'Готово',
  unavailable: 'Прев’ю недоступне', error: 'Помилка збору',
};
const number = new Intl.NumberFormat('uk-UA');
const date = (value: string) => new Date(value).toLocaleString('uk-UA');

export function App() {
  const queryClient = useQueryClient();
  const [username, setUsername] = useState('');
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const channels = useQuery({
    queryKey: ['channels'], queryFn: getChannels,
    refetchInterval: (query) => query.state.data?.some(channel => ['pending', 'collecting'].includes(channel.status)) ? 2000 : false,
  });
  const addition = useMutation({
    mutationFn: addChannel,
    onSuccess: (channel) => {
      queryClient.setQueryData<Channel[]>(['channels'], (saved = []) =>
        saved.some(item => item.id === channel.id) ? saved.map(item => item.id === channel.id ? channel : item) : [...saved, channel]);
      setSelectedId(channel.id);
      setUsername('');
      void queryClient.invalidateQueries({ queryKey: ['channels'] });
    },
  });
  const selected = channels.data?.find(channel => channel.id === selectedId);
  const posts = useQuery({
    queryKey: ['posts', selectedId], queryFn: () => getPosts(selectedId!),
    enabled: selectedId !== null && selected?.status === 'ready',
  });

  return (
    <div className="shell">
      <header className="header">
        <a className="brand" href="/" aria-label="Channel Radar — головна">
          <span className="brand-mark" aria-hidden="true">◉</span>
          Channel <span className="brand-accent">Radar</span>
        </a>
        <span className="version">Збір каналів</span>
      </header>
      <main>
        <div className="intro">
          <div>
            <p className="eyebrow">ВАШ ІНФОРМАЦІЙНИЙ ПРОСТІР</p>
            <h1>Огляд каналів</h1>
            <p className="subtitle">Пости й динаміка Telegram-каналів в одному місці.</p>
          </div>
          <div className="counter"><span>Каналів у радарі</span><strong>{channels.data?.length ?? '—'}</strong></div>
        </div>
        <form className="add-channel" onSubmit={(event) => { event.preventDefault(); addition.mutate(username); }}>
          <div>
            <label htmlFor="username">Username каналу</label>
            <input id="username" value={username} onChange={(event) => setUsername(event.target.value)} placeholder="@durov" maxLength={34} required autoCapitalize="none" autoCorrect="off" spellCheck={false} aria-describedby="username-help" />
            <p id="username-help">Публічний канал із доступним прев’ю. Telegram-ключі не потрібні.</p>
          </div>
          <button disabled={addition.isPending}>{addition.isPending ? 'Додаємо…' : 'Додати канал'}</button>
        </form>
        {addition.isError && <p className="form-error" role="alert">{addition.error.message}</p>}
        <section className="panel" aria-labelledby="channels-title">
          <div className="panel-header"><h2 id="channels-title">Ваші канали</h2><span className="panel-label">Публічні джерела</span></div>
          {channels.isPending && <div className="state" role="status"><span className="loading-dot" />Завантажуємо канали…</div>}
          {channels.isError && <div className="state" role="alert"><h3>Не вдалося завантажити канали</h3><p>Перевірте з’єднання та повторіть спробу.</p><button onClick={() => void channels.refetch()}>Спробувати ще раз</button></div>}
          {channels.data?.length === 0 && <div className="state empty-state"><div className="radar" aria-hidden="true"><span /></div><h3>Поки що немає каналів</h3><p>Додайте username у формі вище.<br />Перший збір покаже доступні пости.</p><span className="empty-caption">Ваш огляд починається тут</span></div>}
          {!!channels.data?.length && <ul className="channel-list">
            {channels.data.map(channel => <li key={channel.id}>
              <button className="channel-select" aria-pressed={selectedId === channel.id} onClick={() => setSelectedId(channel.id)}>
                <span className="channel-avatar" aria-hidden="true">{(channel.title || channel.username)[0].toUpperCase()}</span>
                <span className="channel-copy"><strong>{channel.title || channel.username}</strong><span>@{channel.username}</span><span>{channel.subscribers == null ? '—' : number.format(channel.subscribers)} підписників · {channel.post_count} постів</span></span>
                <span className={`status-badge ${channel.status}`}>{statuses[channel.status]}</span>
              </button>
            </li>)}
          </ul>}
        </section>
        {selected && <section className="panel posts-panel" aria-labelledby="posts-title">
          <div className="panel-header"><h2 id="posts-title">Пости: {selected.title || selected.username}</h2><span className="panel-label">@{selected.username}</span></div>
          <div className="collection-info">
            <p>Зібрана остання сторінка прев’ю; це не повний архів.</p>
            {selected.last_attempt_at && <p>Остання спроба: {date(selected.last_attempt_at)}</p>}
            {selected.last_success_at && <p>Останній успіх: {date(selected.last_success_at)}{selected.stale ? ' · Дані застаріли' : ''}</p>}
          </div>
          {['pending', 'collecting'].includes(selected.status) && <div className="state" role="status"><span className="loading-dot" />{selected.status === 'pending' ? 'Перший збір очікується…' : 'Збираємо пости…'}</div>}
          {['unavailable', 'error'].includes(selected.status) && <div className="state" role="alert"><h3>{statuses[selected.status]}</h3><p>{selected.last_error}</p></div>}
          {selected.status === 'ready' && <>
            {posts.isPending && <div className="state" role="status">Завантажуємо пости…</div>}
            {posts.isError && <div className="state" role="alert"><p>{posts.error.message}</p><button onClick={() => void posts.refetch()}>Спробувати ще раз</button></div>}
            {posts.data?.items.length === 0 && <div className="state"><h3>У прев’ю поки немає постів</h3><p>Канал доступний, збір завершено успішно.</p></div>}
            {posts.data?.items.map(post => <article className="post" key={post.message_id}>
              <div className="post-heading"><time dateTime={post.published_at}>{date(post.published_at)}</time><span>#{post.message_id}</span></div>
              <p className="post-text">{post.text || 'Пост містить медіа без тексту.'}</p>
              <div className="post-metrics"><span>Перегляди: {post.views === null ? '—' : number.format(post.views)}</span><span>Реакції: {post.reactions === null ? '—' : Object.entries(post.reactions).map(([emoji, count]) => `${emoji === 'paid' ? '⭐' : emoji.startsWith('custom:') ? `Emoji ${emoji.slice(7)}` : emoji}: ${number.format(count)}`).join(' · ')}</span></div>
              <a className="post-original" href={post.original_url} target="_blank" rel="noopener noreferrer">Оригінал у Telegram ↗</a>
            </article>)}
          </>}
        </section>}
      </main>
      <footer>Channel Radar <span>Дивіться ширше. Помічайте зміни.</span></footer>
    </div>
  );
}
