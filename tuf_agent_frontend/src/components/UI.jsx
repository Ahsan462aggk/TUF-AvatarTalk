 import { useRef } from "react";
 import { useChat } from "../hooks/useChat";

 export const UI = ({ hidden, ...props }) => {
  const input = useRef();
  const { chat, loading, cameraZoomed, setCameraZoomed, message, startVoice, stopVoice, voiceRecording } = useChat();

  const sendMessage = () => {
    const text = input.current.value;
    if (!loading && !message) {
      chat(text);
      input.current.value = "";
    }
  };
  if (hidden) {
    return null;
  }

  return (
    <>
      <div className="fixed top-0 left-0 right-0 bottom-0 z-10 flex justify-between p-4 flex-col pointer-events-none">
        <div className="w-full flex flex-col items-end justify-center gap-4">
          <button
            onClick={() => setCameraZoomed(!cameraZoomed)}
            className="pointer-events-auto bg-pink-500 hover:bg-pink-600 text-white p-4 rounded-md"
          >
            {cameraZoomed ? (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                className="w-6 h-6"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607zM13.5 10.5h-6"
                />
              </svg>
            ) : (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                className="w-6 h-6"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607zM10.5 7.5v6m3-3h-6"
                />
              </svg>
            )}
          </button>
        </div>
        <div className="flex flex-col items-center justify-center gap-2 pointer-events-auto max-w-screen-sm w-full mx-auto mb-6">
          <button
            disabled={loading}
            onMouseDown={() => startVoice()}
            onTouchStart={() => startVoice()}
            onMouseUp={() => stopVoice()}
            onMouseLeave={() => stopVoice()}
            onTouchEnd={() => stopVoice()}
            aria-label={voiceRecording ? "Release to send" : "Hold to talk"}
            className={`pointer-events-auto rounded-full text-white shadow-lg shadow-fuchsia-500/30 transition-all duration-200 
              bg-gradient-to-r from-pink-500 to-fuchsia-600 hover:from-pink-600 hover:to-fuchsia-700 
              ${voiceRecording ? "ring-4 ring-fuchsia-400/50 scale-105" : "ring-0"} 
              ${loading ? "cursor-not-allowed opacity-30" : ""}
              p-5 md:p-6`}
            title={voiceRecording ? "Release to send" : "Hold to talk"}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className={`w-7 h-7 md:w-8 md:h-8 ${voiceRecording ? "animate-pulse" : ""}`}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 18.75a6.75 6.75 0 006.75-6.75m-13.5 0a6.75 6.75 0 006.75 6.75m0 0v3.75m-3.75-3.75h7.5m-3.75-15a3 3 0 00-3 3v3a3 3 0 106 0v-3a3 3 0 00-3-3z"
              />
            </svg>
          </button>
          <div className="text-white/80 text-sm select-none">
            {voiceRecording ? "Release to send" : "Hold to talk"}
          </div>
        </div>
      </div>
    </>
  );
};
