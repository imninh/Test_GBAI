/** Lớp gọi API. Mọi lỗi đều được quy về `ApiError` có `message_vi` và `code`
 *  để màn hình nào cũng hiện được câu tiếng Việt dễ hiểu kèm mã tra log.
 */

import type {
  AgentRunDetail,
  Classification,
  EvalSummary,
  OpsMetrics,
  Overview,
  Permissions,
  PickupRequest,
  PickupRoute,
  PrivacyReport,
  User,
  WasteCategory,
} from "./types";

/** Địa chỉ backend, **đã cắt dấu `/` thừa ở cuối**.
 *
 * Người điền biến môi trường trên Vercel gần như luôn dán kèm dấu `/` cuối, và
 * chuỗi nối thẳng khi đó sinh ra `https://host//api/v1/auth/me` — Starlette coi
 * đó là đường dẫn khác nên trả 404 cho **toàn bộ** API, kể cả lệnh khôi phục
 * phiên lúc mở app. `redirect_slashes` của FastAPI chỉ lo dấu `/` thừa ở cuối
 * đường dẫn, không lo dấu thừa ở đầu. Chuẩn hoá ngay tại nguồn thì lần sau ai
 * dán kiểu gì cũng không hỏng.
 */
export const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/+$/, "");
const TOKEN_KEY = "greenbin_token";

export class ApiError extends Error {
  code: string;
  status: number;

  constructor(messageVi: string, code: string, status: number) {
    super(messageVi);
    this.code = code;
    this.status = status;
  }
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null) {
  if (typeof window === "undefined") return;
  if (token) window.localStorage.setItem(TOKEN_KEY, token);
  else window.localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init.body && !(init.body instanceof FormData)) headers.set("Content-Type", "application/json");

  let response: Response;
  try {
    response = await fetch(`${API_URL}/api/v1${path}`, { ...init, headers });
  } catch {
    // Hầm để xe và khu thùng rác sóng rất yếu — đây là bối cảnh sử dụng thật.
    throw new ApiError("Không kết nối được tới máy chủ. Thử lại khi có mạng nhé.", "NET-503", 0);
  }

  if (!response.ok) {
    let code = `HTTP-${response.status}`;
    let message = "Có lỗi xảy ra, bạn thử lại giúp mình nhé.";
    try {
      const body = await response.json();
      if (body?.error) {
        code = body.error.code ?? code;
        message = body.error.message_vi ?? message;
      }
    } catch {
      /* giữ nguyên câu mặc định */
    }
    throw new ApiError(message, code, response.status);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

/** Đường dẫn ảnh — luôn qua endpoint có kiểm quyền, kèm token trong query
 *  chỉ khi thẻ `<img>` không gửi được header. */
export function mediaUrl(mediaId: number): string {
  return `${API_URL}/api/v1/media/${mediaId}`;
}

export const api = {
  // --- Auth ---
  login: (email: string, password: string) =>
    request<{ token: string; user: User; permissions: Permissions }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  me: () => request<{ user: User; permissions: Permissions }>("/auth/me"),
  demoAccounts: () =>
    request<{
      password: string;
      accounts: { email: string; full_name: string; role: string; unit: string; description: string }[];
      notice: string;
    }>("/auth/demo-accounts"),

  // --- Phân loại ---
  classifyText: (textQuery: string, buildingId?: number | null) =>
    request<Classification>("/classify/text", {
      method: "POST",
      body: JSON.stringify({ text_query: textQuery, building_id: buildingId ?? null }),
    }),
  classifyImage: (file: File, buildingId?: number | null) => {
    const form = new FormData();
    form.append("image", file);
    if (buildingId) form.append("building_id", String(buildingId));
    return request<Classification>("/classify", { method: "POST", body: form });
  },
  classifications: (params: Record<string, string | number | boolean> = {}) =>
    request<{ items: Classification[]; total: number }>(`/classifications?${new URLSearchParams(
      Object.entries(params).map(([k, v]) => [k, String(v)]),
    )}`),
  classification: (id: number) => request<Classification>(`/classifications/${id}`),
  feedback: (id: number, isCorrect: boolean, suggested = "") =>
    request<{ ok: boolean }>(`/classifications/${id}/feedback`, {
      method: "POST",
      body: JSON.stringify({ is_correct: isCorrect, suggested_category_code: suggested }),
    }),
  verifyQueue: () =>
    request<{ items: Classification[]; total: number; hard_cases: { pair: string; note: string }[] }>("/verify-queue"),
  verifyLabel: (id: number, categoryCode: string, replyText = "") =>
    request<Classification>(`/classifications/${id}/verify`, {
      method: "POST",
      body: JSON.stringify({ category_code: categoryCode, reply_text: replyText }),
    }),

  // --- Ảnh ---
  privacy: (mediaId: number) => request<PrivacyReport>(`/media/${mediaId}/privacy`),
  deleteMedia: (mediaId: number) => request<{ ok: boolean }>(`/media/${mediaId}`, { method: "DELETE" }),

  // --- Danh mục ---
  categories: () => request<{ items: WasteCategory[] }>("/categories"),
  buildings: () => request<{ items: { id: number; code: string; name: string }[] }>("/buildings"),
  schedule: (buildingId: number) =>
    request<{
      building: { id: number; code: string; name: string };
      items: {
        category_code: string;
        category_name: string;
        bin_color: string;
        icon: string;
        weekdays: number[];
        weekdays_vi: string[];
        window: string;
        location: string;
      }[];
    }>(`/buildings/${buildingId}/schedule`),
  knowledge: (params: Record<string, string | number> = {}) =>
    request<{ items: { id: number; title: string; doc_type: string; chunk_count: number; needs_verification: boolean }[] }>(
      `/knowledge?${new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)]))}`,
    ),
  chunk: (id: number) =>
    request<{ id: number; content: string; section: string; needs_verification: boolean; doc: { title: string; source: string } | null }>(
      `/knowledge/chunks/${id}`,
    ),
  enums: () =>
    request<{
      pickup_reject_reasons: { code: string; label_vi: string }[];
      stop_issues: { code: string; label_vi: string }[];
      known_limitations: string[];
      weekdays_vi: string[];
    }>("/meta/enums"),

  // --- Thu gom ---
  createPickup: (payload: Record<string, unknown>) =>
    request<PickupRequest>("/pickups", { method: "POST", body: JSON.stringify(payload) }),
  pickups: (params: Record<string, string | number> = {}) =>
    request<{ items: PickupRequest[]; total: number; reject_reasons: { code: string; label_vi: string }[] }>(
      `/pickups?${new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)]))}`,
    ),
  pickup: (id: number) => request<PickupRequest>(`/pickups/${id}`),
  reviewPickup: (id: number, payload: Record<string, unknown>) =>
    request<PickupRequest>(`/pickups/${id}/review`, { method: "POST", body: JSON.stringify(payload) }),
  cancelPickup: (id: number) => request<PickupRequest>(`/pickups/${id}`, { method: "DELETE" }),

  // --- Tuyến ---
  proposeRoute: (serviceDate: string, window: string) =>
    request<PickupRoute>("/routes/propose", {
      method: "POST",
      body: JSON.stringify({ service_date: serviceDate, window }),
    }),
  routes: (params: Record<string, string> = {}) =>
    request<{ items: PickupRoute[] }>(`/routes?${new URLSearchParams(params)}`),
  route: (id: number) => request<PickupRoute>(`/routes/${id}`),
  reviewRoute: (id: number, payload: Record<string, unknown>) =>
    request<PickupRoute>(`/routes/${id}/review`, { method: "POST", body: JSON.stringify(payload) }),
  completeStop: (routeId: number, stopId: number, payload: Record<string, unknown> = {}) =>
    request<PickupRoute>(`/routes/${routeId}/stops/${stopId}/done`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  // --- Vận hành ---
  overview: () => request<Overview>("/overview"),
  opsMetrics: () => request<OpsMetrics>("/ops/metrics"),
  evalSummary: () => request<EvalSummary>("/eval/summary"),
  runs: () => request<{ items: { id: number; kind: string; status: string; duration_ms: number; total_cost_usd: number; started_at: string }[] }>("/runs"),
  run: (id: number) => request<AgentRunDetail>(`/runs/${id}`),
  notifications: () =>
    request<{ items: { id: number; title: string; body: string; created_at: string }[]; unread: number }>("/notifications"),
};
