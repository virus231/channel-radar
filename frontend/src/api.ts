export type Channel = { id: number; username: string; title: string | null };

export async function getChannels(): Promise<Channel[]> {
  const response = await fetch('/api/channels');
  if (!response.ok) throw new Error('Не вдалося завантажити канали');
  return response.json();
}
