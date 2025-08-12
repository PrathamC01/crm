// errorHandler.js
let errorCallback = null;

export function registerErrorHandler(callback) {
    errorCallback = callback;
}

export function showGlobalError(message) {
    if (errorCallback) {
        errorCallback(message);
    }
}