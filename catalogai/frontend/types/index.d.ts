// Global type declarations for CatalogAI Frontend

declare global {
  namespace React {
    type ReactNode = any;
    type ReactElement = any;
    type ComponentType<P = {}> = any;
    type FC<P = {}> = any;
    
    interface HTMLAttributes<T> {
      className?: string;
      style?: any;
      onClick?: () => void;
      onMouseEnter?: () => void;
      onMouseLeave?: () => void;
      [key: string]: any;
    }

    interface DragEvent<T = Element> {
      preventDefault(): void;
      stopPropagation(): void;
      dataTransfer: {
        files: FileList;
      };
    }

    interface ChangeEvent<T = Element> {
      preventDefault(): void;
      target: T & {
        files: FileList | null;
        value: string;
      };
    }

    interface MouseEvent<T = Element> {
      preventDefault(): void;
      stopPropagation(): void;
    }
  }

  namespace JSX {
    interface IntrinsicElements {
      [elemName: string]: any;
    }
  }

  // Node.js globals
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

  // Array extensions for older TypeScript targets
  interface Array<T> {
    includes(searchElement: T, fromIndex?: number): boolean;
    find(predicate: (value: T, index: number, obj: T[]) => boolean, thisArg?: any): T | undefined;
    filter(callbackfn: (value: T, index: number, array: T[]) => boolean, thisArg?: any): T[];
  }
}

export {};