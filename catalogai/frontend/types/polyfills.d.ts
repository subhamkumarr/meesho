// Polyfills for older TypeScript targets

// Array.prototype.includes polyfill
declare global {
  interface Array<T> {
    includes(searchElement: T, fromIndex?: number): boolean;
  }
  
  interface ReadonlyArray<T> {
    includes(searchElement: T, fromIndex?: number): boolean;
  }
}

// String.prototype.includes polyfill
declare global {
  interface String {
    includes(searchString: string, position?: number): boolean;
  }
}

// Object.assign polyfill
declare global {
  interface ObjectConstructor {
    assign<T, U>(target: T, source: U): T & U;
    assign<T, U, V>(target: T, source1: U, source2: V): T & U & V;
    assign<T, U, V, W>(target: T, source1: U, source2: V, source3: W): T & U & V & W;
    assign(target: object, ...sources: any[]): any;
  }
}

export {};