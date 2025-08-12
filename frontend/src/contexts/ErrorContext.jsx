import React, { createContext, useContext, useState, useCallback } from "react";
import ErrorPopup from "../components/common/ErrorPopup"; // you’ll create this component

const ErrorPopupContext = createContext();

export const useErrorPopup = () => useContext(ErrorPopupContext);

export const ErrorPopupProvider = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState("");

  const showError = useCallback((msg) => {
    setMessage(msg);
    setIsOpen(true);
  }, []);

  const closeError = useCallback(() => {
    setIsOpen(false);
    setMessage("");
  }, []);

  return (
    <ErrorPopupContext.Provider value={{ showError }}>
      {children}
      <ErrorPopup isOpen={isOpen} onClose={closeError} message={message} />
    </ErrorPopupContext.Provider>
  );
};
