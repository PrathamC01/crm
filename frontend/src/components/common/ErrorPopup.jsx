import React, { useEffect, useState } from "react";
import Modal from "./Modal"; // path to your Modal component

const ErrorPopup = ({
  isOpen,
  onClose,
  title = "Error",
  message,
  autoClose = true,
  delay = 3000,
}) => {
  const [fadeOut, setFadeOut] = useState(false);

  useEffect(() => {
    if (isOpen && autoClose) {
      const fadeTimer = setTimeout(() => setFadeOut(true), delay - 300); // start fade 300ms before close
      const closeTimer = setTimeout(() => {
        setFadeOut(false);
        onClose();
      }, delay);

      return () => {
        clearTimeout(fadeTimer);
        clearTimeout(closeTimer);
      };
    }
  }, [isOpen, autoClose, delay, onClose]);

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="small"
      showCloseButton={true}
    >
      <div
        className={`transition-opacity duration-300 ${
          fadeOut ? "opacity-0" : "opacity-100"
        }`}
      >
        <div className="text-red-600 font-medium">{message}</div>
        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-400"
          >
            Close
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default ErrorPopup;
