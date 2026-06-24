import type { StreamEvent } from "./types";

// FastAPI /query/stream은 POST + text/event-stream이라 EventSource(GET 전용)를 못 쓴다.
// fetch 스트림을 직접 읽어 `data: {json}\n\n` 프레임을 파싱한다.
export async function streamQuery(
  apiBase: string,
  query: string,
  onEvent: (event: StreamEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(`${apiBase.replace(/\/$/, "")}/query/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
    signal,
  });
  if (!res.ok || !res.body) {
    throw new Error(`백엔드 응답 오류 (${res.status})`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let sep: number;
    while ((sep = buffer.indexOf("\n\n")) >= 0) {
      const frame = buffer.slice(0, sep);
      buffer = buffer.slice(sep + 2);
      const dataLine = frame.split("\n").find((l) => l.startsWith("data:"));
      if (dataLine) onEvent(JSON.parse(dataLine.slice(5).trim()) as StreamEvent);
    }
  }
}
