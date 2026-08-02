"use client";

/** Quyền riêng tư · Lịch thu gom · Yêu cầu của tôi · Tôi. */

import * as React from "react";

import { CaiAppCard } from "@/components/pwa/cai-app";
import { Button, Card, EmptyState, Skeleton } from "@/components/ui/primitives";
import { ScreenHeader } from "@/components/ui/shell";
import { api, mediaUrl } from "@/lib/api";
import { dungLuong, kg, ngayVn, TRANG_THAI_YEU_CAU } from "@/lib/format";
import {
  IconChoDuyet,
  IconDuyet,
  IconGapLoi,
  IconKhoa,
  IconLichThuGom,
  IconMamXanh,
  IconMonDo,
  IconNguoiDung,
  IconTiepTuc,
  IconToaNha,
  IconTuChoi,
  IconTuXoa,
  IconXeThuGom,
} from "@/lib/icons";
import type { PickupRequest, PrivacyReport, User } from "@/lib/types";

export function PrivacyScreen({ mediaId, onBack }: { mediaId: number; onBack: () => void }) {
  const [bao, setBao] = React.useState<PrivacyReport | null>(null);
  const [daXoa, setDaXoa] = React.useState(false);

  React.useEffect(() => {
    api.privacy(mediaId).then(setBao).catch(() => setBao(null));
  }, [mediaId]);

  return (
    <div className="min-h-full bg-cream pb-10 pt-11">
      <ScreenHeader title="Ảnh của bạn được xử lý thế nào" onBack={onBack} />
      <div className="px-4">
        <h1 className="mb-3.5 mt-1.5 font-[family-name:var(--font-display)] text-2xl font-bold leading-tight">
          Mình lo quyền riêng tư
          <br />
          trước khi ảnh tới model
        </h1>

        {!bao ? (
          <Skeleton className="h-64 w-full" />
        ) : (
          <>
            <div className="mb-4 flex gap-2.5">
              <div className="flex-1">
                <div className="mb-1.5 text-[11px] font-bold text-muted">Ảnh gốc (chỉ ban quản lý mở được)</div>
                <div className="flex aspect-[3/4] items-center justify-center rounded-2xl bg-[repeating-linear-gradient(135deg,#d8ded2,#d8ded2_8px,#cfd6c8_8px,#cfd6c8_16px)] font-mono text-[10px] font-semibold text-[#5a6b5f]">
                  {bao.has_original ? "đã khoá" : "không lưu"}
                </div>
              </div>
              <div className="flex-1">
                <div className="mb-1.5 text-[11px] font-bold text-leaf">Đã gửi cho AI</div>
                <div className="relative aspect-[3/4] overflow-hidden rounded-2xl bg-[repeating-linear-gradient(135deg,#dfeadf,#dfeadf_8px,#d5e2d5_8px,#d5e2d5_16px)]">
                  {!daXoa && (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={mediaUrl(bao.media_id)} alt="Ảnh đã xử lý" className="h-full w-full object-cover" />
                  )}
                </div>
              </div>
            </div>

            <Card className="overflow-hidden p-0">
              <div className="flex border-b border-line px-4 py-3 text-xs font-extrabold text-muted">
                <span className="flex-[1.4]">Thông tin</span>
                <span className="flex-1">Ảnh gốc</span>
                <span className="flex-1 text-right">Đã gửi đi</span>
              </div>
              {bao.removed_fields.map((truong) => (
                <div key={truong.field} className="flex items-center border-b border-[#f2ede2] px-4 py-2.5 text-[13px] font-semibold">
                  <span className="flex-[1.4] text-ink-soft">{truong.label_vi}</span>
                  <span className="flex-1 truncate text-muted-2">{truong.value_before}</span>
                  <span className="flex flex-1 items-center justify-end gap-1.5 font-extrabold text-hazard-dark">
                    <IconTuChoi className="h-3.5 w-3.5" />
                    đã xoá
                  </span>
                </div>
              ))}
              <div className="flex items-center border-b border-[#f2ede2] px-4 py-2.5 text-[13px] font-semibold">
                <span className="flex-[1.4] text-ink-soft">Khuôn mặt</span>
                <span className="flex-1 text-muted-2">{bao.faces_blurred} khuôn mặt</span>
                <span className="flex flex-1 items-center justify-end gap-1.5 font-extrabold text-leaf-dark">
                  {bao.faces_blurred > 0 ? (
                    <>
                      <IconDuyet className="h-3.5 w-3.5" />
                      đã làm mờ
                    </>
                  ) : (
                    "không có"
                  )}
                </span>
              </div>
              <div className="flex items-center px-4 py-2.5 text-[13px] font-semibold">
                <span className="flex-[1.4] text-ink-soft">Kích thước</span>
                <span className="flex-1 text-muted-2">
                  {bao.original_size.width}×{bao.original_size.height} ({dungLuong(bao.original_size.bytes)})
                </span>
                <span className="flex-1 text-right font-extrabold text-leaf-dark">
                  {bao.processed_size.width}×{bao.processed_size.height} ({dungLuong(bao.processed_size.bytes)})
                </span>
              </div>
            </Card>

            <div className="mx-0.5 my-3.5 flex items-center gap-2 text-xs font-bold text-muted">
              <IconTuXoa className="h-4 w-4 flex-none" />
              Ảnh này sẽ tự động xoá {bao.expires_at ? `sau ${ngayVn(bao.expires_at)}` : "theo hạn lưu trữ"}.
            </div>
            <Button
              block
              variant="danger"
              disabled={daXoa}
              onClick={() => api.deleteMedia(bao.media_id).then(() => setDaXoa(true))}
            >
              {daXoa ? "Đã xoá khỏi hệ thống" : "Xoá ngay"}
            </Button>
          </>
        )}
      </div>
    </div>
  );
}

export function ScheduleScreen({ buildingId, buildingName }: { buildingId: number | null; buildingName: string }) {
  const [lich, setLich] = React.useState<Awaited<ReturnType<typeof api.schedule>> | null>(null);
  const [loi, setLoi] = React.useState("");

  React.useEffect(() => {
    if (!buildingId) return;
    api
      .schedule(buildingId)
      .then(setLich)
      .catch((e) => setLoi(e.message));
  }, [buildingId]);

  const thu = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"];

  return (
    <div className="min-h-full bg-cream px-[18px] pb-[108px] pt-[54px]">
      <h1 className="m-0 mb-1 font-[family-name:var(--font-display)] text-[28px] font-bold">Lịch thu gom</h1>
      <p className="m-0 mb-4 text-[13px] font-semibold text-muted">{buildingName} · xem được cả khi không có mạng</p>

      {!buildingId ? (
        <EmptyState icon={IconToaNha} title="Tài khoản chưa gắn với toà nào" hint="Liên hệ ban quản lý để gắn căn hộ." />
      ) : loi ? (
        <EmptyState icon={IconLichThuGom} title="Chưa tải được lịch" hint={loi} />
      ) : !lich ? (
        <Skeleton className="h-52 w-full" />
      ) : (
        <>
          <Card className="gb-hscroll mb-4 p-3">
            <div className="grid min-w-[340px] gap-1.5" style={{ gridTemplateColumns: "auto repeat(7, 1fr)" }}>
              <span />
              {thu.map((t) => (
                <span key={t} className="text-center text-[11px] font-extrabold text-muted">
                  {t}
                </span>
              ))}
              {lich.items.map((row) => (
                <React.Fragment key={row.category_code}>
                  <span className="flex items-center gap-1.5 whitespace-nowrap text-xs font-bold" style={{ color: row.bin_color }}>
                    <span className="h-2.5 w-2.5 rounded-[3px]" style={{ background: row.bin_color }} />
                    {row.category_name}
                  </span>
                  {[0, 1, 2, 3, 4, 5, 6].map((d) => (
                    <span
                      key={d}
                      className="h-[26px] rounded-md"
                      style={{ background: row.weekdays.includes(d) ? row.bin_color : "#f1efe8" }}
                      title={row.weekdays.includes(d) ? `${row.window} · ${row.location}` : "không thu gom"}
                    />
                  ))}
                </React.Fragment>
              ))}
            </div>
          </Card>

          <div className="mx-0.5 mb-2 mt-4 text-[13px] font-bold text-muted">Điểm tập kết trong toà</div>
          <Card className="p-4">
            {lich.items.map((row) => (
              <div key={row.category_code} className="flex justify-between border-b border-[#f2ede2] py-2 text-sm font-bold last:border-0">
                <span>{row.location}</span>
                <span className="font-semibold text-muted">
                  {row.category_name} · {row.window}
                </span>
              </div>
            ))}
          </Card>
        </>
      )}
    </div>
  );
}

export function RequestsScreen({ onOpen }: { onOpen: (id: number) => void }) {
  const [items, setItems] = React.useState<PickupRequest[] | null>(null);

  React.useEffect(() => {
    api.pickups().then((d) => setItems(d.items)).catch(() => setItems([]));
  }, []);

  return (
    <div className="min-h-full bg-cream px-[18px] pb-[108px] pt-[54px]">
      <h1 className="m-0 mb-4 font-[family-name:var(--font-display)] text-[28px] font-bold">Yêu cầu của tôi</h1>
      {items === null ? (
        <Skeleton className="h-24 w-full" />
      ) : items.length === 0 ? (
        <EmptyState icon={IconMonDo} title="Chưa có yêu cầu nào" hint="Chụp món rác đầu tiên để bắt đầu nhé." />
      ) : (
        items.map((yc) => {
          const tt = TRANG_THAI_YEU_CAU[yc.status];
          return (
            <Card key={yc.id} onClick={() => onOpen(yc.id)} className="mb-3 cursor-pointer p-4">
              <div className="mb-2 flex items-center justify-between">
                <span className="text-sm font-extrabold text-bulky">#PR-{String(yc.id).padStart(4, "0")}</span>
                <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-extrabold ${tt.className}`}>
                  <tt.icon className="h-3.5 w-3.5" />
                  {tt.label}
                </span>
              </div>
              <div className="mb-1 text-[15px] font-bold">{yc.items.map((i) => i.name).join(", ")}</div>
              <div className="text-[13px] font-semibold text-muted">
                {kg(yc.weight_max_kg)} · mong muốn {ngayVn(yc.preferred_date)}
                {yc.route ? ` · đi cùng ${Math.max(0, yc.route.stop_count - 1)} hộ khác` : ""}
              </div>
            </Card>
          );
        })
      )}
    </div>
  );
}

export function RequestDetailScreen({ id, onBack }: { id: number; onBack: () => void }) {
  const [yc, setYc] = React.useState<PickupRequest | null>(null);
  const [loi, setLoi] = React.useState("");

  const tai = React.useCallback(() => {
    api.pickup(id).then(setYc).catch((e) => setLoi(e.message));
  }, [id]);
  React.useEffect(tai, [tai]);

  if (loi) return <EmptyState icon={IconGapLoi} title="Không mở được yêu cầu" hint={loi} />;
  if (!yc) return <Skeleton className="m-4 h-64" />;

  const tt = TRANG_THAI_YEU_CAU[yc.status];

  return (
    <div className="min-h-full bg-cream pb-10 pt-11">
      <ScreenHeader title={`#PR-${String(yc.id).padStart(4, "0")}`} onBack={onBack} />
      <div className="px-[18px]">
        <div className="mb-3.5 flex items-center justify-between">
          <h1 className="m-0 font-[family-name:var(--font-display)] text-[22px] font-bold">
            {yc.items.map((i) => i.name).join(", ")}
          </h1>
          <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-extrabold ${tt.className}`}>
            <tt.icon className="h-3.5 w-3.5" />
            {tt.label}
          </span>
        </div>

        <Card className="p-4">
          {(yc.timeline ?? []).map((moc, i) => (
            <div key={i} className="flex items-start gap-3 pb-4 last:pb-0">
              <span className="flex h-6 w-6 flex-none items-center justify-center rounded-full bg-leaf text-white">
                <IconDuyet className="h-3.5 w-3.5" strokeWidth={3} />
              </span>
              <div className="flex-1">
                <div className="text-xs font-extrabold text-muted">{new Date(moc.at).toLocaleString("vi-VN")}</div>
                <div className="text-sm font-bold leading-snug">{moc.label_vi}</div>
              </div>
            </div>
          ))}
          {yc.status === "pending" && (
            <div className="flex items-start gap-3">
              <span className="flex h-6 w-6 flex-none items-center justify-center rounded-full bg-amber-line text-amber">
                <IconChoDuyet className="h-3.5 w-3.5" />
              </span>
              <div className="text-sm font-bold text-amber">Chờ ban quản lý duyệt</div>
            </div>
          )}
        </Card>

        {yc.route && (
          <div className="mt-3 flex gap-2.5 rounded-2xl bg-leaf-soft p-4 text-[13px] font-bold leading-relaxed text-leaf-dark">
            <IconXeThuGom className="h-4 w-4 flex-none" />
            Yêu cầu của bạn đi cùng chuyến với {Math.max(0, yc.route.stop_count - 1)} hộ khác trong toà — giảm{" "}
            {yc.route.saved_trips} chuyến xe.
          </div>
        )}

        {yc.reject_reason && (
          <div className="mt-3 rounded-2xl border border-[#f6cdb8] bg-hazard-soft p-4 text-[13px] font-bold text-hazard-dark">
            Bị từ chối: {yc.reject_reason}
            {yc.review_note ? ` — ${yc.review_note}` : ""}
          </div>
        )}

        {!["scheduled", "done", "cancelled"].includes(yc.status) && (
          <Button
            block
            variant="danger"
            className="mt-3.5"
            onClick={() => api.cancelPickup(yc.id).then(tai).catch((e) => setLoi(e.message))}
          >
            Huỷ yêu cầu
          </Button>
        )}
      </div>
    </div>
  );
}

export function MeScreen({ user, onPrivacy, onLogout }: { user: User; onPrivacy: () => void; onLogout: () => void }) {
  return (
    <div className="min-h-full bg-cream px-[18px] pb-[108px] pt-[54px]">
      <div className="mb-5 flex items-center gap-3.5">
        <div className="flex h-[60px] w-[60px] items-center justify-center rounded-[20px] bg-leaf-soft text-leaf-dark">
          <IconNguoiDung className="h-7 w-7" strokeWidth={1.8} />
        </div>
        <div>
          <div className="font-[family-name:var(--font-display)] text-xl font-bold">{user.full_name}</div>
          <div className="text-[13px] font-semibold text-muted">
            {user.unit ? `Căn ${user.unit} · ` : ""}
            {user.building || "Chưa gắn toà"}
          </div>
        </div>
      </div>

      <Card className="mb-3.5 overflow-hidden p-0">
        <button onClick={onPrivacy} className="flex w-full cursor-pointer items-center gap-3 border-b border-[#f2ede2] px-4 py-4 text-left">
          <IconKhoa className="h-[18px] w-[18px] text-muted" />
          <span className="flex-1 text-sm font-bold">Ảnh của tôi được xử lý thế nào</span>
          <IconTiepTuc className="h-[18px] w-[18px] text-[#c3cbc2]" />
        </button>
        <div className="flex items-center gap-3 px-4 py-4">
          <IconMamXanh className="h-[18px] w-[18px] text-leaf" />
          <span className="flex-1 text-sm font-bold">Điểm xanh</span>
          <span className="text-sm font-extrabold text-leaf-dark">{user.green_points}</span>
        </div>
      </Card>

      <CaiAppCard />

      <div className="mb-3.5 rounded-2xl bg-[#eef1ec] p-4">
        <div className="mb-2 text-xs font-bold text-muted">QUYỀN CỦA CƯ DÂN</div>
        <div className="flex flex-col gap-1 text-[13px] font-semibold leading-relaxed text-[#5a6b5f]">
          <span className="flex items-start gap-1.5">
            <IconDuyet className="mt-0.5 h-3.5 w-3.5 flex-none text-leaf" />
            Hỏi phân loại · đăng ký thu gom
          </span>
          <span className="flex items-start gap-1.5">
            <IconDuyet className="mt-0.5 h-3.5 w-3.5 flex-none text-leaf" />
            Xem yêu cầu của chính mình
          </span>
          <span className="flex items-start gap-1.5 text-[#b0b8ae]">
            <IconTuChoi className="mt-0.5 h-3.5 w-3.5 flex-none" />
            Duyệt yêu cầu · xem ảnh cư dân khác · trang vận hành
          </span>
        </div>
      </div>

      <Button block variant="danger" onClick={onLogout}>
        Đăng xuất
      </Button>
    </div>
  );
}
