import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { App } from './App';

function renderOverview() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={client}><App /></QueryClientProvider>);
}

describe('channel overview', () => {
  it('shows loading while the API is pending', () => {
    vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {})));
    renderOverview();
    expect(screen.getByRole('status')).toHaveTextContent('Завантажуємо канали');
  });

  it('shows the empty dashboard after reading the API', async () => {
    const fetch = vi.fn().mockResolvedValue(new Response('[]'));
    vi.stubGlobal('fetch', fetch);
    renderOverview();
    expect(await screen.findByText('Поки що немає каналів')).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith('/api/channels');
  });

  it('shows saved channels', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify([
      { id: 1, username: 'example_channel', title: 'Приклад' },
    ]))));
    renderOverview();
    expect(await screen.findByText('Приклад')).toBeInTheDocument();
    expect(screen.getByText('@example_channel')).toBeInTheDocument();
  });

  it('lets the user retry an API error', async () => {
    const fetch = vi.fn()
      .mockResolvedValueOnce(new Response('', { status: 503 }))
      .mockResolvedValueOnce(new Response('[]'));
    vi.stubGlobal('fetch', fetch);
    renderOverview();
    expect(await screen.findByRole('alert')).toHaveTextContent('Не вдалося завантажити канали');
    fireEvent.click(screen.getByRole('button', { name: 'Спробувати ще раз' }));
    expect(await screen.findByText('Поки що немає каналів')).toBeInTheDocument();
  });
});

it('adds a channel, polls collection and renders saved text safely', async () => {
  const channel = { id: 1, username: 'example_channel', title: 'Приклад', status: 'pending', subscribers: null, post_count: 0, last_attempt_at: null, last_success_at: null, last_error: null, stale: true, coverage_from: null, coverage_to: null };
  let added = false;
  let reads = 0;
  vi.stubGlobal('fetch', vi.fn(async (url, options) => {
    if (options?.method === 'POST') {
      added = true;
      return new Response(JSON.stringify(channel), { status: 202 });
    }
    if (url === '/api/channels') {
      if (!added) return new Response('[]');
      reads++;
      return new Response(JSON.stringify([{ ...channel, status: reads > 1 ? 'ready' : 'collecting', post_count: reads > 1 ? 1 : 0, subscribers: 1200 }]));
    }
    return new Response(JSON.stringify({ items: [{ channel_id: 1, message_id: 12, text: '<img src=x onerror=alert(1)>\nЗбережений пост', published_at: '2026-10-08T10:00:00Z', original_url: 'https://t.me/example_channel/12', views: null, reactions: null, observed_at: '2026-10-08T12:00:00Z' }], next_cursor: null }));
  }));
  renderOverview();
  await screen.findByText('Поки що немає каналів');
  fireEvent.change(screen.getByRole('textbox', { name: 'Username каналу' }), { target: { value: '@example_channel' } });
  fireEvent.click(screen.getByRole('button', { name: 'Додати канал' }));
  expect(await screen.findByText('Збираємо пости…')).toBeInTheDocument();
  expect(await screen.findByText(/Збережений пост/, {}, { timeout: 4000 })).toBeInTheDocument();
  expect(screen.queryByRole('img')).not.toBeInTheDocument();
  expect(screen.getByRole('link', { name: /^Оригінал у Telegram/ })).toHaveAttribute('href', 'https://t.me/example_channel/12');
});

it('shows a validation error and allows correcting the username', async () => {
  vi.stubGlobal('fetch', vi.fn(async (_url, options) => options?.method === 'POST'
    ? new Response('', { status: 422 }) : new Response('[]')));
  renderOverview();
  await screen.findByText('Поки що немає каналів');
  fireEvent.change(screen.getByLabelText('Username каналу'), { target: { value: 'https://example.com' } });
  fireEvent.click(screen.getByRole('button', { name: 'Додати канал' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('URL не підтримується');
  expect(screen.getByLabelText('Username каналу')).toHaveValue('https://example.com');
});

it.each(['unavailable', 'error', 'ready'] as const)('shows %s and does not duplicate an existing channel', async (status) => {
  const channel = { id: 1, username: 'example_channel', title: 'Приклад', status, subscribers: null, post_count: 0, last_attempt_at: '2026-10-08T12:00:00Z', last_success_at: status === 'ready' ? '2026-10-08T12:00:00Z' : null, last_error: status === 'ready' ? null : 'Публічне прев’ю недоступне.', stale: status !== 'ready', coverage_from: null, coverage_to: null };
  vi.stubGlobal('fetch', vi.fn(async (url, options) => {
    if (options?.method === 'POST') return new Response(JSON.stringify(channel));
    if (url === '/api/channels') return new Response(JSON.stringify([channel]));
    return new Response(JSON.stringify({ items: [], next_cursor: null }));
  }));
  renderOverview();
  await screen.findByText('Приклад');
  fireEvent.change(screen.getByLabelText('Username каналу'), { target: { value: '@example_channel' } });
  fireEvent.click(screen.getByRole('button', { name: 'Додати канал' }));
  await screen.findByRole('heading', { name: 'Пости: Приклад' });
  expect(screen.getAllByRole('listitem')).toHaveLength(1);
  if (status === 'ready') expect(await screen.findByText('У прев’ю поки немає постів')).toBeInTheDocument();
  else expect(await screen.findByRole('alert')).toHaveTextContent('Публічне прев’ю недоступне.');
});
