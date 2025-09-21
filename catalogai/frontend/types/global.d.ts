/// <reference types="react" />
/// <reference types="react-dom" />

declare namespace React {
  type ReactNode = any;
  interface HTMLAttributes<T> {
    className?: string;
    [key: string]: any;
  }
}

declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}

declare module 'react' {
  export function useState<T>(initialState: T | (() => T)): [T, (value: T | ((prev: T) => T)) => void];
  export function useCallback<T extends (...args: any[]) => any>(callback: T, deps: any[]): T;
  export function useRef<T>(initialValue: T): { current: T };
  export interface HTMLAttributes<T> {
    className?: string;
    [key: string]: any;
  }
  export type ReactNode = any;
}

declare module 'next' {
  export interface Metadata {
    title?: string;
    description?: string;
    [key: string]: any;
  }
}

declare module 'next/font/google' {
  export function Inter(options: any): any;
}

declare module 'next/navigation' {
  export function usePathname(): string;
}

declare module 'next/link' {
  const Link: any;
  export default Link;
}

declare module 'axios' {
  const axios: any;
  export default axios;
  export interface AxiosInstance {
    [key: string]: any;
  }
  export interface AxiosResponse<T = any> {
    data: T;
    status: number;
    statusText: string;
    headers: any;
    config: any;
  }
}

declare module 'lucide-react' {
  export const Sparkles: any;
  export const Shield: any;
  export const Zap: any;
  export const Eye: any;
  export const Palette: any;
  export const Layers: any;
  export const Target: any;
  export const Lightbulb: any;
  export const Upload: any;
  export const X: any;
  export const Image: any;
  export const FileImage: any;
  export const AlertTriangle: any;
  export const Search: any;
  export const BarChart3: any;
  export const Settings: any;
}

declare global {
  namespace NodeJS {
    interface ProcessEnv {
      [key: string]: string | undefined;
      NEXT_PUBLIC_API_BASE?: string;
      NODE_ENV?: 'development' | 'production' | 'test';
    }
    interface Process {
      env: ProcessEnv;
    }
  }
  
  var process: NodeJS.Process;
}