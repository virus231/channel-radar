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
