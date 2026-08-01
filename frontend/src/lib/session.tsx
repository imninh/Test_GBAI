"use client";

import * as React from "react";

import { api, ApiError, setToken } from "./api";
import type { Permissions, User } from "./types";

interface SessionValue {
  user: User | null;
  permissions: Permissions;
  loading: boolean;
  error: string;
  dangNhap: (email: string, password: string) => Promise<User>;
  dangXuat: () => void;
  /** Vai trò hiện tại có quyền này không. Không có quyền thì UI hiện mờ kèm
   *  tooltip giải thích, **không ẩn hẳn** — để ranh giới phân quyền nhìn thấy được. */
  duocPhep: (permission: string) => boolean;
  lyDoCam: (permission: string) => string;
}

const SessionContext = React.createContext<SessionValue | null>(null);

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = React.useState<User | null>(null);
  const [permissions, setPermissions] = React.useState<Permissions>({});
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState("");

  React.useEffect(() => {
    let huy = false;
    api
      .me()
      .then((data) => {
        if (huy) return;
        setUser(data.user);
        setPermissions(data.permissions);
      })
      .catch(() => {
        /* chưa đăng nhập là trạng thái bình thường, không phải lỗi */
      })
      .finally(() => !huy && setLoading(false));
    return () => {
      huy = true;
    };
  }, []);

  const dangNhap = React.useCallback(async (email: string, password: string) => {
    setError("");
    try {
      const data = await api.login(email, password);
      setToken(data.token);
      setUser(data.user);
      setPermissions(data.permissions);
      return data.user;
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Không đăng nhập được.";
      setError(message);
      throw err;
    }
  }, []);

  const dangXuat = React.useCallback(() => {
    setToken(null);
    setUser(null);
    setPermissions({});
  }, []);

  const value: SessionValue = {
    user,
    permissions,
    loading,
    error,
    dangNhap,
    dangXuat,
    duocPhep: (permission) => permissions[permission]?.allowed ?? false,
    lyDoCam: (permission) => permissions[permission]?.reason ?? "Vai trò của bạn không có quyền này",
  };

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession(): SessionValue {
  const context = React.useContext(SessionContext);
  if (!context) throw new Error("useSession phải nằm trong SessionProvider");
  return context;
}
