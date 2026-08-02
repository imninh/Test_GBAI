"use client";

/** Khung thiết bị: điện thoại cho cư dân + đội vệ sinh, cửa sổ trình duyệt cho
 *  console ban quản lý. Đây là hai "bộ mặt" của sản phẩm — cùng bảng màu, cùng
 *  bộ chữ, nhưng mật độ thông tin và bối cảnh sử dụng khác hẳn nhau.
 */

import * as React from "react";

import { IconQuayLai } from "@/lib/icons";
import { cn } from "@/lib/utils";

export function PhoneFrame({
  children,
  bg = "#f4f1ea",
  statusDark = false,
  tabBar,
}: {
  children: React.ReactNode;
  bg?: string;
  statusDark?: boolean;
  tabBar?: React.ReactNode;
}) {
  return (
    <div className="relative h-[820px] w-[392px] max-w-full rounded-[56px] bg-[#0c0f0c] p-3 shadow-[0_30px_70px_-20px_rgba(15,30,18,.5),0_0_0_2px_rgba(255,255,255,.05)_inset]">
      <div className="relative h-full w-full overflow-hidden rounded-[45px]" style={{ background: bg }}>
        <StatusBar dark={statusDark} />
        <div className="gb-scroll absolute inset-0 overflow-y-auto overflow-x-hidden">{children}</div>
        {tabBar}
        <div
          className="absolute bottom-2 left-1/2 z-50 h-[5px] w-[130px] -translate-x-1/2 rounded-full"
          style={{ background: statusDark ? "rgba(255,255,255,.3)" : "rgba(20,40,25,.25)" }}
        />
      </div>
    </div>
  );
}

function StatusBar({ dark }: { dark: boolean }) {
  return (
    <div
      className="pointer-events-none absolute inset-x-0 top-0 z-40 flex h-12 items-end justify-between px-[30px] pb-2"
      style={{ color: dark ? "#fff" : "#16211a" }}
    >
      <span className="text-[15px] font-bold">9:41</span>
      <span className="flex items-center gap-1.5">
        <svg width="18" height="12" viewBox="0 0 18 12" aria-hidden>
          <g fill="currentColor">
            <rect x="0" y="7" width="3" height="5" rx="1" />
            <rect x="5" y="4" width="3" height="8" rx="1" />
            <rect x="10" y="1.5" width="3" height="10.5" rx="1" />
            <rect x="15" y="0" width="3" height="12" rx="1" opacity=".4" />
          </g>
        </svg>
        <svg width="26" height="13" viewBox="0 0 26 13" aria-hidden>
          <rect x="0.5" y="0.5" width="21" height="12" rx="3.5" fill="none" stroke="currentColor" opacity=".5" />
          <rect x="2.2" y="2.2" width="17" height="8.6" rx="2" fill="currentColor" />
          <rect x="23" y="4" width="2" height="5" rx="1" fill="currentColor" opacity=".5" />
        </svg>
      </span>
    </div>
  );
}

export interface TabItem {
  key: string;
  label: string;
  icon: React.ReactNode;
  badge?: number;
}

export function TabBar({
  items,
  active,
  onChange,
  accent = "#2fae66",
}: {
  items: TabItem[];
  active: string;
  onChange: (key: string) => void;
  accent?: string;
}) {
  return (
    <div className="absolute inset-x-0 bottom-0 z-30 flex h-[86px] items-start border-t border-[rgba(20,40,25,.06)] bg-white/95 px-3 pt-3 backdrop-blur">
      {items.map((item) => {
        const isActive = item.key === active;
        return (
          <button
            key={item.key}
            onClick={() => onChange(item.key)}
            className="relative flex flex-1 cursor-pointer flex-col items-center gap-1.5 bg-transparent"
            style={{ color: isActive ? accent : "#a8b0a7" }}
            aria-current={isActive ? "page" : undefined}
          >
            {item.icon}
            {item.badge ? (
              <span className="absolute -top-1 right-5 flex h-4 min-w-4 items-center justify-center rounded-lg bg-hazard px-1 text-[10px] font-extrabold text-white">
                {item.badge}
              </span>
            ) : null}
            <span className="text-[11px] font-bold">{item.label}</span>
          </button>
        );
      })}
    </div>
  );
}

export function BrowserFrame({ children, url = "console.greenbin.vn" }: { children: React.ReactNode; url?: string }) {
  return (
    <div className="w-full max-w-[1220px] rounded-2xl bg-[#0c0f0c] p-3 shadow-[0_30px_70px_-25px_rgba(15,30,18,.5)]">
      <div className="flex items-center gap-2 px-2.5 pb-3 pt-1.5">
        <span className="h-3 w-3 rounded-full bg-[#ff5f57]" />
        <span className="h-3 w-3 rounded-full bg-[#febc2e]" />
        <span className="h-3 w-3 rounded-full bg-[#28c840]" />
        <span className="ml-3 text-xs font-semibold text-muted">{url}</span>
      </div>
      <div className="flex h-[720px] flex-col overflow-hidden rounded-lg bg-console-bg">{children}</div>
    </div>
  );
}

export function ScreenHeader({
  title,
  onBack,
  right,
  tone = "muted",
}: {
  title: string;
  onBack?: () => void;
  right?: React.ReactNode;
  tone?: "muted" | "hazard";
}) {
  return (
    <div className="flex items-center gap-2.5 px-[18px] pb-3 pt-1.5">
      {onBack && (
        <button
          onClick={onBack}
          aria-label="Quay lại"
          className="flex h-[38px] w-[38px] cursor-pointer items-center justify-center rounded-full bg-white text-ink shadow-[0_2px_8px_rgba(20,40,25,.08)]"
        >
          <IconQuayLai className="h-5 w-5" />
        </button>
      )}
      <span className={cn("text-[15px] font-bold", tone === "hazard" ? "text-[#a04b26]" : "text-muted-2")}>{title}</span>
      <span className="flex-1" />
      {right}
    </div>
  );
}
