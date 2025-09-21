// Environment and global declarations

declare namespace NodeJS {
  interface ProcessEnv {
    readonly NODE_ENV: 'development' | 'production' | 'test';
    readonly NEXT_PUBLIC_API_BASE?: string;
    readonly PORT?: string;
    readonly HOSTNAME?: string;
    [key: string]: string | undefined;
  }
}

// Extend global process
declare var process: {
  env: NodeJS.ProcessEnv;
  cwd(): string;
  platform: string;
  version: string;
};

// Browser globals
declare var window: Window & typeof globalThis;
declare var document: Document;
declare var navigator: Navigator;
declare var location: Location;

// File API
declare var File: {
  prototype: File;
  new(fileBits: BlobPart[], fileName: string, options?: FilePropertyBag): File;
};

declare var FileList: {
  prototype: FileList;
  new(): FileList;
};

declare var FormData: {
  prototype: FormData;
  new(form?: HTMLFormElement): FormData;
};