export type Channel = {
  id: number; username: string; title: string | null;
  status: 'pending' | 'collecting' | 'ready' | 'unavailable' | 'error';
  subscribers: number | null; post_count: number;
  last_attempt_at: string | null; last_success_at: string | null;
  last_error: string | null; stale: boolean;
  coverage_from: string | null; coverage_to: string | null;
};

export type Post = {
  channel_id: number; message_id: number; published_at: string; text: string;
  original_url: string; views: number | null; reactions: Record<string, number> | null;
  observed_at: string | null;
};

export async function getChannels(): Promise<Channel[]> {
  const response = await fetch('/api/channels');
  if (!response.ok) throw new Error('Не вдалося завантажити канали');
  return response.json();
}

export async function addChannel(username: string): Promise<Channel> {
  const response = await fetch('/api/channels', {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username }),
  });
  if (!response.ok) throw new Error(response.status === 422
    ? 'Введіть username: до 32 літер, цифр або _. URL не підтримується.'
    : 'Не вдалося додати канал. Повторіть спробу.');
  return response.json();
}

export async function getPosts(channelId: number): Promise<{ items: Post[]; next_cursor: number | null }> {
  const response = await fetch(`/api/channels/${channelId}/posts`);
  if (!response.ok) throw new Error('Не вдалося завантажити пости');
  return response.json();
}
