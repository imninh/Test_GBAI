"use client";

/** Console ban quản lý — desktop.
 *
 * Nhóm "CẦN DUYỆT" đặt trên cùng và có badge số: đó là công việc hàng ngày của
 * BQL, và là nơi HITL thể hiện ra. Mục nào vai trò hiện tại không có quyền thì
 * **hiện mờ kèm tooltip giải thích**, không ẩn hẳn.
 */

import * as React from "react";

import { AgentRunScreen, OpsScreen, OverviewScreen, QualityScreen } from "@/components/manager/insights";
import { PickupQueue, RouteApproval, VerifyQueue } from "@/components/manager/queues";
import { BrowserFrame } from "@/components/ui/shell";
import { api } from "@/lib/api";
import { IconKhoa } from "@/lib/icons";
import { useSession } from "@/lib/session";

type Nav = "overview" | "pickup" | "verify" | "route" | "runs" | "ops" | "quality";

const MUC: { key: Nav; label: string; permission: string; group?: "queue" | "insight" }[] = [
  { key: "overview", label: "Tổng quan", permission: "view_ops" },
  { key: "pickup", label: "Thu gom", permission: "review_pickup", group: "queue" },
  { key: "verify", label: "Nhãn nghi ngờ", permission: "verify_label", group: "queue" },
  { key: "route", label: "Tuyến gộp", permission: "review_route", group: "queue" },
  { key: "runs", label: "Agent run", permission: "view_runs", group: "insight" },
  { key: "ops", label: "Vận hành", permission: "view_ops", group: "insight" },
  { key: "quality", label: "Chất lượng AI", permission: "view_eval", group: "insight" },
];

export function ManagerConsole() {
  const { user, dangXuat, duocPhep, lyDoCam } = useSession();
  const [nav, setNav] = React.useState<Nav>("overview");
  const [dem, setDem] = React.useState({ pickup: 0, labels: 0, routes: 0 });

  React.useEffect(() => {
    api
      .overview()
      .then((d) => setDem({ pickup: d.queues.pickup, labels: d.queues.labels, routes: d.queues.routes }))
      .catch(() => setDem({ pickup: 0, labels: 0, routes: 0 }));
  }, [nav]);

  const badge: Record<string, number> = { pickup: dem.pickup, verify: dem.labels, route: dem.routes };

  return (
    <BrowserFrame>
      <div className="flex h-14 flex-none items-center gap-3.5 border-b border-line-3 bg-white px-5">
        <span className="font-[family-name:var(--font-display)] text-base font-bold tracking-tight">
          GreenBin<span className="text-leaf"> AI</span>
        </span>
        <span className="rounded-lg border border-line-3 bg-console-bg px-3 py-1.5 text-[13px] font-bold">
          Toà: {user?.building || "Tất cả"}
        </span>
        <span className="flex-1" />
        <span className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-bulky-soft text-[13px] font-extrabold text-bulky">
            {user?.full_name
              ?.split(" ")
              .slice(-2)
              .map((w) => w[0])
              .join("") ?? "BQ"}
          </span>
          <span>
            <span className="block text-[13px] font-bold leading-tight">{user?.full_name}</span>
            <span className="text-[11px] font-semibold text-muted">Ban quản lý</span>
          </span>
        </span>
        <button onClick={dangXuat} className="cursor-pointer text-[13px] font-bold text-hazard-dark">
          Đăng xuất
        </button>
      </div>

      <div className="flex flex-1 overflow-hidden">
        <div className="w-[230px] flex-none overflow-y-auto border-r border-line-3 bg-cream-soft p-3">
          {MUC.filter((m) => !m.group).map((m) => (
            <NavButton key={m.key} muc={m} nav={nav} setNav={setNav} allowed={duocPhep(m.permission)} reason={lyDoCam(m.permission)} />
          ))}

          <div className="px-3 pb-1.5 pt-3.5 text-[10px] font-extrabold tracking-widest text-[#a0a89f]">CẦN DUYỆT</div>
          {MUC.filter((m) => m.group === "queue").map((m) => (
            <NavButton
              key={m.key}
              muc={m}
              nav={nav}
              setNav={setNav}
              allowed={duocPhep(m.permission)}
              reason={lyDoCam(m.permission)}
              badge={badge[m.key]}
            />
          ))}

          <div className="mx-2 my-3 h-px bg-line-3" />
          {MUC.filter((m) => m.group === "insight").map((m) => (
            <NavButton key={m.key} muc={m} nav={nav} setNav={setNav} allowed={duocPhep(m.permission)} reason={lyDoCam(m.permission)} />
          ))}
        </div>

        <div className="gb-scroll flex-1 overflow-y-auto px-8 py-6">
          {nav === "overview" && <OverviewScreen onGoto={(n) => setNav(n as Nav)} />}
          {nav === "pickup" && <PickupQueue />}
          {nav === "verify" && <VerifyQueue />}
          {nav === "route" && <RouteApproval />}
          {nav === "runs" && <AgentRunScreen />}
          {nav === "ops" && <OpsScreen />}
          {nav === "quality" && <QualityScreen />}
        </div>
      </div>
    </BrowserFrame>
  );
}

function NavButton({
  muc,
  nav,
  setNav,
  allowed,
  reason,
  badge,
}: {
  muc: { key: Nav; label: string };
  nav: Nav;
  setNav: (n: Nav) => void;
  allowed: boolean;
  reason: string;
  badge?: number;
}) {
  const dangChon = nav === muc.key;
  return (
    <button
      onClick={() => allowed && setNav(muc.key)}
      disabled={!allowed}
      title={allowed ? undefined : reason}
      className="mb-0.5 flex w-full items-center rounded-xl px-3 py-2.5 text-left text-[13px] font-bold"
      style={{
        background: dangChon ? "#16211a" : "transparent",
        color: !allowed ? "#b8beb6" : dangChon ? "#fff" : "#3a453d",
        cursor: allowed ? "pointer" : "not-allowed",
      }}
    >
      {muc.label}
      <span className="flex-1" />
      {!allowed && <IconKhoa className="h-3.5 w-3.5" />}
      {allowed && badge ? (
        <span className="rounded-md bg-hazard px-2 py-0.5 text-[11px] font-extrabold text-white">{badge}</span>
      ) : null}
    </button>
  );
}
