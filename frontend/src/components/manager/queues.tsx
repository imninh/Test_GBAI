"use client";

/** Ba hàng đợi HITL của ban quản lý.
 *
 * Nguyên tắc chung cho cả ba: **hàng đợi phải nói vì sao mục này rơi vào đây.**
 * Một hàng đợi duyệt mà không nói lý do là hàng đợi vô nghĩa.
 */

import * as React from "react";

import { Button, Card, Chip, EmptyState, ErrorState, Skeleton } from "@/components/ui/primitives";
import { api } from "@/lib/api";
import { doTinCay, kg, ngayGioVn, ngayVn, soVn } from "@/lib/format";
import {
  IconAi,
  IconCaKho,
  IconCanhBao,
  IconChucMung,
  IconDuyet,
  IconHoanTac,
  IconLamLai,
  IconNhomRac,
  IconSua,
  IconTuChoi,
  IconXeThuGom,
  IconXongHet,
} from "@/lib/icons";
import type { Classification, PickupRequest, PickupRoute, WasteCategory } from "@/lib/types";

export function PickupQueue() {
  const [ds, setDs] = React.useState<PickupRequest[] | null>(null);
  const [lyDoTuChoi, setLyDoTuChoi] = React.useState<{ code: string; label_vi: string }[]>([]);
  const [dangChon, setDangChon] = React.useState<PickupRequest | null>(null);
  const [moTuChoi, setMoTuChoi] = React.useState(false);
  const [loi, setLoi] = React.useState("");

  const tai = React.useCallback(async () => {
    try {
      const d = await api.pickups({ status: "pending" });
      setDs(d.items);
      setLyDoTuChoi(d.reject_reasons);
      if (d.items.length) setDangChon(await api.pickup(d.items[0].id));
      else setDangChon(null);
    } catch (e) {
      setLoi(e instanceof Error ? e.message : "Lỗi tải hàng đợi");
    }
  }, []);

  React.useEffect(() => {
    tai();
  }, [tai]);

  async function duyet(action: string, reason = "") {
    if (!dangChon) return;
    await api.reviewPickup(dangChon.id, { action, reason });
    setMoTuChoi(false);
    tai();
  }

  if (loi) return <ErrorState message={loi} onRetry={tai} />;
  if (ds === null) return <Skeleton className="h-96 w-full" />;

  return (
    <>
      <div className="mb-4 flex items-center gap-2.5">
        <div className="font-[family-name:var(--font-display)] text-[22px] font-bold">Duyệt yêu cầu thu gom</div>
        <span className="rounded-lg border border-line-3 bg-console-bg px-2.5 py-1 text-xs font-bold text-muted">
          HITL #1 · AI đề xuất, người chốt
        </span>
      </div>

      {ds.length === 0 ? (
        <EmptyState icon={IconChucMung} title="Chưa có yêu cầu nào cần duyệt hôm nay" />
      ) : (
        <div className="grid items-start gap-4" style={{ gridTemplateColumns: "300px 1fr" }}>
          <div>
            <div className="mb-2.5 text-xs font-extrabold text-muted">CHỜ DUYỆT ({ds.length})</div>
            {ds.map((yc) => (
              <button
                key={yc.id}
                onClick={() => api.pickup(yc.id).then(setDangChon)}
                className="mb-2.5 w-full cursor-pointer rounded-2xl bg-white p-3.5 text-left"
                style={{ border: dangChon?.id === yc.id ? "2px solid #2fae66" : "1px solid #eceae3" }}
              >
                <div className="mb-1 flex justify-between">
                  <span className="text-[13px] font-extrabold text-bulky">#PR-{String(yc.id).padStart(4, "0")}</span>
                  <span className="rounded-md bg-amber-soft px-2 py-0.5 text-[11px] font-extrabold text-amber">
                    {kg(yc.weight_max_kg)}
                  </span>
                </div>
                <div className="text-[13px] font-bold">
                  {yc.unit} · {yc.resident?.full_name}
                </div>
                <div className="mt-1 text-[11px] font-semibold text-muted">mong muốn {ngayVn(yc.preferred_date)}</div>
              </button>
            ))}
          </div>

          {dangChon && (
            <Card className="overflow-hidden p-0">
              <div className="border-b border-[#f2ede2] px-5 py-4">
                <div className="mb-1 flex items-center gap-2.5">
                  <span className="rounded-md bg-amber-soft px-2.5 py-1 text-xs font-extrabold text-amber">CHỜ DUYỆT</span>
                  <span className="text-[15px] font-extrabold text-bulky">#PR-{String(dangChon.id).padStart(4, "0")}</span>
                </div>
                <div className="text-[13px] font-semibold text-muted">
                  {dangChon.resident?.full_name} · Căn {dangChon.unit} · gửi {ngayGioVn(dangChon.created_at)}
                </div>
              </div>

              <div className="px-5 py-4">
                <div className="mb-3.5 rounded-xl bg-console-bg p-3.5">
                  <div className="mb-2.5 text-[13px] font-bold">Vì sao yêu cầu này cần duyệt</div>
                  {dangChon.threshold_hit.map((t) => (
                    <div key={t.rule} className="flex justify-between py-1 text-[13px] font-bold">
                      <span className="text-muted-2">{t.label_vi}</span>
                      <span>
                        {t.value}{" "}
                        <span className="font-semibold text-muted">
                          {t.threshold ? `(ngưỡng ${t.threshold})` : "(luôn cần duyệt)"}
                        </span>{" "}
                        <span className="inline-flex items-center gap-1 text-hazard-dark">
                          <IconCanhBao className="h-3.5 w-3.5" />
                          vượt
                        </span>
                      </span>
                    </div>
                  ))}
                  <div className="flex justify-between py-1 text-[13px] font-bold">
                    <span className="text-muted-2">Khoảng khối lượng ước tính</span>
                    <span>
                      {dangChon.weight_min_kg}–{dangChon.weight_max_kg} kg
                    </span>
                  </div>
                </div>

                <div className="mb-3.5 grid grid-cols-4 gap-2">
                  {dangChon.items.map((m, i) => (
                    <div key={i}>
                      <div className="mb-1 aspect-square rounded-xl bg-[repeating-linear-gradient(135deg,#ece7f6,#ece7f6_6px,#e3daf3_6px,#e3daf3_12px)]" />
                      <div className="text-[10px] font-bold">
                        {m.name}
                        {m.qty > 1 ? ` ×${m.qty}` : ""}
                      </div>
                    </div>
                  ))}
                </div>

                {dangChon.resident_history && (
                  <div className="mb-3.5 rounded-xl border border-[#e6ece6] bg-[#f7f9f7] px-3.5 py-3 text-xs font-semibold leading-loose text-ink-soft">
                    Cư dân này: {dangChon.resident_history.so_yeu_cau_truoc} yêu cầu trước,{" "}
                    {dangChon.resident_history.so_lan_hoan_thanh} lần hoàn thành, {dangChon.resident_history.so_lan_huy} lần huỷ
                    <br />
                    Toà {dangChon.building_code}: {dangChon.building_context?.so_yeu_cau} yêu cầu, tổng{" "}
                    {kg(dangChon.building_context?.tong_khoi_luong_kg ?? 0)}
                    <br />
                    Ngày {ngayVn(dangChon.preferred_date)}: {dangChon.capacity_context?.so_yeu_cau_cung_ngay} yêu cầu khác
                    cùng ngày · tải trọng xe {kg(dangChon.capacity_context?.tai_trong_xe_kg ?? 0)}
                  </div>
                )}

                {dangChon.agent_suggestion && (
                  <div className="rounded-xl border-[1.5px] border-dashed border-[#cbb8ee] bg-[#faf8fe] p-3.5">
                    <div className="mb-1.5 flex items-center gap-1.5 text-[11px] font-extrabold text-bulky">
                      <IconAi className="h-3.5 w-3.5" />
                      {dangChon.agent_suggestion.label_vi}
                    </div>
                    <div className="text-[13px] font-semibold leading-relaxed text-ink-soft">
                      {dangChon.agent_suggestion.text_vi}
                    </div>
                  </div>
                )}
              </div>

              <div className="flex flex-wrap items-center gap-2.5 border-t border-[#f2ede2] bg-cream-soft px-5 py-3.5">
                <Button variant="leaf" onClick={() => duyet("approve")}>
                  <IconDuyet className="h-4 w-4" />
                  Duyệt
                </Button>
                <span className="flex-1" />
                <Button variant="danger" onClick={() => setMoTuChoi((v) => !v)}>
                  <IconTuChoi className="h-4 w-4" />
                  Từ chối
                </Button>
              </div>

              {moTuChoi && (
                <div className="border-t border-[#f2ede2] px-5 py-3.5">
                  <div className="mb-2 text-[13px] font-bold">
                    Chọn lý do từ chối — bắt buộc chọn từ danh sách để dữ liệu chảy vào tập cải tiến
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {lyDoTuChoi.map((r) => (
                      <Button key={r.code} size="sm" variant="outline" onClick={() => duyet("reject", r.code)}>
                        {r.label_vi}
                      </Button>
                    ))}
                  </div>
                </div>
              )}
            </Card>
          )}
        </div>
      )}
    </>
  );
}

export function VerifyQueue() {
  const [du, setDu] = React.useState<Awaited<ReturnType<typeof api.verifyQueue>> | null>(null);
  const [danhMuc, setDanhMuc] = React.useState<WasteCategory[]>([]);
  const [dangMo, setDangMo] = React.useState<number | null>(null);
  const [loi, setLoi] = React.useState("");

  const tai = React.useCallback(() => {
    api.verifyQueue().then(setDu).catch((e) => setLoi(e.message));
  }, []);
  React.useEffect(() => {
    tai();
    api.categories().then((d) => setDanhMuc(d.items)).catch(() => setDanhMuc([]));
  }, [tai]);

  if (loi) return <ErrorState message={loi} onRetry={tai} />;
  if (!du) return <Skeleton className="h-96 w-full" />;

  return (
    <>
      <div className="font-[family-name:var(--font-display)] text-[22px] font-bold">Xác nhận nhãn nghi ngờ</div>
      <div className="mb-4 text-sm font-semibold text-muted">
        {du.total} ca hệ thống chưa chắc hoặc cư dân báo sai · HITL #2
      </div>

      {du.hard_cases?.length ? (
        <div className="mb-4 rounded-2xl border border-amber-line bg-amber-soft px-4 py-3.5">
          <div className="mb-2 flex items-center gap-1.5 text-[11px] font-extrabold text-amber">
            <IconCaKho className="h-3.5 w-3.5" />
            CA KHÓ HAY BỊ NHẦM (từ eval)
          </div>
          <div className="flex flex-wrap gap-2 text-xs font-bold text-[#7a5c14]">
            {du.hard_cases.map((c) => (
              <span key={c.pair} className="rounded-lg bg-white px-2.5 py-1.5" title={c.note}>
                {c.pair}
              </span>
            ))}
          </div>
        </div>
      ) : null}

      {du.items.length === 0 ? (
        <EmptyState icon={IconXongHet} title="Hàng đợi trống" hint="Không có ca nào đang chờ người xác nhận." />
      ) : (
        <div className="grid grid-cols-2 gap-3.5">
          {du.items.map((ca: Classification) => (
            <Card key={ca.classification_id} className="p-4">
              <div className="mb-2 text-sm font-extrabold">
                AI đoán: {ca.guess?.item_name || ca.item_name || ca.text_query || "không rõ"} · {doTinCay(ca.confidence)}
              </div>
              <Chip tone="hazard" className="text-[11px]">
                Dưới ngưỡng {doTinCay(ca.min_confidence)}
              </Chip>
              <div className="my-2 text-[11px] font-semibold text-muted">Lý do từ chối: {ca.refusal_label_vi}</div>
              {dangMo === ca.classification_id ? (
                <div className="flex flex-wrap gap-1.5">
                  {danhMuc.map((dm) => (
                    <Button
                      key={dm.code}
                      size="sm"
                      variant="outline"
                      onClick={async () => {
                        await api.verifyLabel(ca.classification_id, dm.code);
                        setDangMo(null);
                        tai();
                      }}
                    >
                      <IconNhomRac code={dm.code} className="h-3.5 w-3.5" />
                      {dm.name}
                    </Button>
                  ))}
                </div>
              ) : (
                <Button size="sm" onClick={() => setDangMo(ca.classification_id)}>
                  Chọn nhãn đúng & trả lời
                </Button>
              )}
            </Card>
          ))}
        </div>
      )}
    </>
  );
}

export function RouteApproval() {
  const [ds, setDs] = React.useState<PickupRoute[] | null>(null);
  const [tuyen, setTuyen] = React.useState<PickupRoute | null>(null);
  const [boBot, setBoBot] = React.useState<number[]>([]);
  const [loi, setLoi] = React.useState("");
  const [thongBao, setThongBao] = React.useState("");

  const tai = React.useCallback(async () => {
    try {
      const d = await api.routes({ status: "proposed" });
      setDs(d.items);
      if (d.items.length) setTuyen(await api.route(d.items[0].id));
      else setTuyen(null);
    } catch (e) {
      setLoi(e instanceof Error ? e.message : "Lỗi tải tuyến");
    }
  }, []);
  React.useEffect(() => {
    tai();
  }, [tai]);

  async function duyet(action: string) {
    if (!tuyen) return;
    const ketQua = await api.reviewRoute(tuyen.id, {
      action,
      removed_stops: boBot.length ? boBot : undefined,
    });
    setThongBao(ketQua.message_vi ?? "");
    setBoBot([]);
    tai();
  }

  if (loi) return <ErrorState message={loi} onRetry={tai} />;
  if (ds === null) return <Skeleton className="h-96 w-full" />;

  return (
    <>
      <div className="mb-3.5 font-[family-name:var(--font-display)] text-[22px] font-bold">Duyệt tuyến gộp</div>
      {thongBao && <div className="mb-3 rounded-xl bg-leaf-soft px-4 py-3 text-sm font-bold text-leaf-dark">{thongBao}</div>}

      {!tuyen ? (
        <EmptyState
          icon={IconXeThuGom}
          title="Chưa có tuyến nào chờ duyệt"
          hint="Agent sẽ đề xuất tuyến khi có đủ yêu cầu đã duyệt cùng ngày và cùng khung giờ."
        />
      ) : (
        <>
          <div className="mb-4 flex items-center gap-4 rounded-2xl bg-[linear-gradient(150deg,#16211a,#1c3326)] px-5 py-4 text-white">
            <span className="rounded-lg bg-amber-line px-2.5 py-1 text-[11px] font-extrabold text-[#5a4410]">
              AI ĐỀ XUẤT — CHỜ DUYỆT
            </span>
            <div className="flex-1">
              <div className="font-[family-name:var(--font-display)] text-[17px] font-bold">
                Chuyến {tuyen.window} · {ngayVn(tuyen.service_date)}
              </div>
              <div className="text-xs font-semibold text-[#9fb3a6]">
                {tuyen.stop_count} điểm dừng · {kg(tuyen.total_weight_kg)} · ~{soVn(tuyen.est_distance_km, 1)} km
                {tuyen.team ? ` · ${tuyen.team.full_name}` : ""}
              </div>
            </div>
          </div>

          <div className="grid items-start gap-4" style={{ gridTemplateColumns: "1fr 1fr" }}>
            <Card className="p-4">
              <div className="mb-2.5 text-[13px] font-bold text-muted">Điểm dừng</div>
              {(tuyen.stops ?? []).map((s) => {
                const daBo = boBot.includes(s.request_id);
                return (
                  <div
                    key={s.stop_id}
                    className="mb-2 flex items-center gap-3 rounded-xl border border-line bg-cream-soft px-3 py-2.5"
                    style={{ opacity: daBo ? 0.4 : 1 }}
                  >
                    <span className="flex h-[26px] w-[26px] items-center justify-center rounded-lg bg-ink text-xs font-extrabold text-white">
                      {s.seq}
                    </span>
                    <div className="flex-1">
                      <div className="text-[13px] font-extrabold">{s.unit}</div>
                      <div className="text-[11px] font-semibold text-muted">{s.items.map((i) => i.name).join(", ")}</div>
                    </div>
                    <span className="text-[13px] font-extrabold text-recycle">{kg(s.weight_max_kg)}</span>
                    <button
                      onClick={() => setBoBot((cu) => (daBo ? cu.filter((x) => x !== s.request_id) : [...cu, s.request_id]))}
                      className="cursor-pointer text-muted"
                      title={daBo ? "Giữ lại điểm này" : "Bỏ khỏi tuyến"}
                      aria-label={daBo ? `Giữ lại điểm ${s.unit}` : `Bỏ điểm ${s.unit} khỏi tuyến`}
                    >
                      {daBo ? <IconHoanTac className="h-4 w-4" /> : <IconTuChoi className="h-4 w-4" />}
                    </button>
                  </div>
                );
              })}
            </Card>

            <div>
              <div className="mb-3.5 rounded-2xl border-[1.5px] border-dashed border-[#cbb8ee] bg-[#faf8fe] p-4">
                <div className="mb-2.5 flex items-center gap-1.5 text-[11px] font-extrabold text-bulky">
                  <IconAi className="h-3.5 w-3.5" />
                  AI GIẢI THÍCH — VÌ SAO GỘP THẾ NÀY
                </div>
                <div className="text-xs font-semibold leading-loose text-ink-soft">
                  Tiêu chí gộp:
                  <br />
                  {tuyen.reasoning?.criteria.map((c) => (
                    <React.Fragment key={c}>
                      • {c}
                      <br />
                    </React.Fragment>
                  ))}
                  {tuyen.reasoning?.excluded.slice(0, 3).map((e) => (
                    <React.Fragment key={e.request_id}>
                      • KHÔNG gộp #{e.request_id} ({e.unit}) vì {e.ly_do}
                      <br />
                    </React.Fragment>
                  ))}
                </div>
                <div className="mt-3 rounded-xl bg-leaf-soft px-3 py-2.5 text-[13px] font-bold text-leaf-dark">
                  So với đi lẻ: {tuyen.stop_count} chuyến → 1 chuyến · ~{soVn(tuyen.reasoning?.baseline_km ?? 0, 1)} km
                  → ~{soVn(tuyen.est_distance_km, 1)} km{" "}
                  <b>
                    (giảm{" "}
                    {tuyen.reasoning?.baseline_km
                      ? Math.round((tuyen.reasoning.saved_km / tuyen.reasoning.baseline_km) * 100)
                      : 0}
                    %)
                  </b>
                </div>
                {tuyen.reasoning?.note && (
                  <div className="mt-2 text-[11px] font-semibold text-muted">{tuyen.reasoning.note}</div>
                )}
              </div>

              <Card className="p-4">
                <div className="mb-2.5 text-xs font-bold text-muted">Sơ đồ tuyến</div>
                <svg viewBox="0 0 260 90" className="w-full">
                  <path
                    d={(tuyen.stops ?? [])
                      .map((_, i, arr) => {
                        const x = 20 + (i * 220) / Math.max(1, arr.length - 1);
                        const y = i % 2 === 0 ? 70 : 30;
                        return `${i === 0 ? "M" : "L"}${x} ${y}`;
                      })
                      .join(" ")}
                    fill="none"
                    stroke="#2fae66"
                    strokeWidth="2.5"
                    strokeDasharray="4 4"
                  />
                  {(tuyen.stops ?? []).map((s, i, arr) => {
                    const x = 20 + (i * 220) / Math.max(1, arr.length - 1);
                    const y = i % 2 === 0 ? 70 : 30;
                    return (
                      <g key={s.stop_id}>
                        <circle cx={x} cy={y} r="11" fill="#16211a" />
                        <text x={x} y={y + 4} fill="#fff" textAnchor="middle" fontSize="10" fontWeight="800">
                          {s.seq}
                        </text>
                      </g>
                    );
                  })}
                </svg>
              </Card>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap gap-2.5">
            <Button variant="leaf" onClick={() => duyet("approve")} disabled={boBot.length > 0}>
              <IconDuyet className="h-4 w-4" />
              Duyệt tuyến
            </Button>
            <Button variant="outline" disabled={boBot.length === 0} onClick={() => duyet("approve_with_changes")}>
              <IconSua className="h-4 w-4" />
              Sửa rồi duyệt ({boBot.length} điểm bị bỏ)
            </Button>
            <Button variant="outline" onClick={() => duyet("regenerate")}>
              <IconLamLai className="h-4 w-4" />
              Đề xuất lại
            </Button>
            <span className="flex-1" />
            <Button variant="danger" onClick={() => duyet("cancel")}>
              Huỷ tuyến
            </Button>
          </div>
        </>
      )}
    </>
  );
}
