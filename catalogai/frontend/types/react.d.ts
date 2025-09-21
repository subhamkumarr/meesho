declare module 'react' {
  export = React;
  export as namespace React;

  namespace React {
    type ReactNode = any;
    type ReactElement = any;
    type ComponentType<P = {}> = any;
    type FC<P = {}> = any;
    type HTMLAttributes<T> = any;
    type CSSProperties = any;

    function useState<S>(initialState: S | (() => S)): [S, (value: S | ((prevState: S) => S)) => void];
    function useEffect(effect: () => void | (() => void), deps?: any[]): void;
    function useCallback<T extends (...args: any[]) => any>(callback: T, deps: any[]): T;
    function useMemo<T>(factory: () => T, deps: any[]): T;
    function useRef<T>(initialValue: T): { current: T };
    function useContext<T>(context: any): T;
    function useReducer<R extends any>(reducer: R, initialState: any): [any, any];

    interface DragEvent<T = Element> {
      preventDefault(): void;
      dataTransfer: {
        files: FileList;
      };
    }

    interface ChangeEvent<T = Element> {
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
}