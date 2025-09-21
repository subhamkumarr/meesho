// Node.js type declarations

declare namespace NodeJS {
  interface ProcessEnv {
    [key: string]: string | undefined;
    NEXT_PUBLIC_API_BASE?: string;
    NODE_ENV?: 'development' | 'production' | 'test';
  }

  interface Process {
    env: ProcessEnv;
    cwd(): string;
    platform: string;
    version: string;
  }
}

declare var process: NodeJS.Process;

// Global Node.js types
declare module 'process' {
  const process: NodeJS.Process;
  export = process;
}

// File and Buffer types
declare class Buffer {
  static from(data: any): Buffer;
  toString(encoding?: string): string;
}

declare var global: any;