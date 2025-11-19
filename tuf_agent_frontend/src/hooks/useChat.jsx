import { createContext, useContext, useEffect, useRef, useState } from "react";

const backendUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const wsRef = useRef(null);
  const recRef = useRef(null);
  const streamRef = useRef(null);
  const hasFirstChunkRef = useRef(false);
  const pendingEndRef = useRef(false);
  const pendingEndTimerRef = useRef(null);
  const [voiceRecording, setVoiceRecording] = useState(false);
  const estimateLipsyncFromBlob = async (blob) => {
    try {
      const arrayBuffer = await blob.arrayBuffer();
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      const audioCtx = new AudioCtx();
      const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);
      const channel = audioBuffer.getChannelData(0);
      const sampleRate = audioBuffer.sampleRate;
      const frameSec = 0.06; // 60ms analysis window
      const hopSec = 0.03; // 30ms hop
      const frameSize = Math.max(1, Math.floor(sampleRate * frameSec));
      const hopSize = Math.max(1, Math.floor(sampleRate * hopSec));
      const mouthCues = [];
      const rmsAt = (start, end) => {
        let sum = 0;
        for (let i = start; i < end; i++) {
          const v = channel[i] || 0;
          sum += v * v;
        }
        const n = Math.max(1, end - start);
        return Math.sqrt(sum / n);
      };
      let lastViseme = null;
      let lastStart = 0;
      for (let i = 0; i < channel.length; i += hopSize) {
        const startIdx = i;
        const endIdx = Math.min(i + frameSize, channel.length);
        const r = rmsAt(startIdx, endIdx);
        // Map RMS to coarse visemes (A,C,E,F,X) expected by Avatar mapping
        let viseme = "X"; // closed/default
        if (r > 0.12) viseme = "A"; // wide open
        else if (r > 0.08) viseme = "F"; // rounded
        else if (r > 0.05) viseme = "E"; // mid
        else if (r > 0.02) viseme = "C"; // slight open
        const t = startIdx / sampleRate;
        if (lastViseme === null) {
          lastViseme = viseme;
          lastStart = t;
        } else if (viseme !== lastViseme) {
          mouthCues.push({ start: lastStart, end: t, value: lastViseme });
          lastViseme = viseme;
          lastStart = t;
        }
      }
      // close the last segment
      const duration = channel.length / sampleRate;
      if (lastViseme !== null) {
        mouthCues.push({ start: lastStart, end: duration, value: lastViseme });
      }
      // Filter very short cues (<40ms)
      const filtered = mouthCues.filter((c) => c.end - c.start > 0.04);
      try { audioCtx.close(); } catch {}
      return { mouthCues: filtered };
    } catch {
      return null;
    }
  };
  const stopTracks = () => {
    try {
      const s = streamRef.current;
      if (s) {
        s.getTracks().forEach((t) => {
          try { t.stop(); } catch {}
        });
      }
    } catch {}
    streamRef.current = null;
  };
  const chat = async (message) => {
    try {
      setLoading(true);
      const res = await fetch(
        `${backendUrl}/ask?question=${encodeURIComponent(message)}`,
        {
          method: "GET",
          headers: {
            Accept: "audio/wav",
          },
        }
      );
      if (!res.ok) {
        setLoading(false);
        return;
      }
      const contentType = res.headers.get("content-type") || "audio/wav";
      const blob = await res.blob();
      const dataUrl = URL.createObjectURL(blob);
      const lipsync = await estimateLipsyncFromBlob(blob);
      const resp = [
        {
          dataUrl,
          mime: contentType.split(";")[0],
          lipsync,
          animation: "Idle",
          facialExpression: "default",
        },
      ];
      setMessages((messages) => [...messages, ...resp]);
    } catch (e) {
    } finally {
      setLoading(false);
    }
  };
  const startVoice = async () => {
    console.log("startVoice called", { loading, voiceRecording });
    if (loading || voiceRecording) {
      console.log("startVoice early return", { loading, voiceRecording });
      return;
    }
    try {
      // 1) Ask for mic permission immediately (better UX; shows prompt right away)
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.error("getUserMedia not supported in this browser");
        return;
      }
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      // 2) Validate MediaRecorder and MIME
      if (typeof window.MediaRecorder === "undefined") {
        console.error("MediaRecorder not supported (consider a WAV/MP4 POST fallback)");
        stopTracks();
        return;
      }
      const mimeType = "audio/webm;codecs=opus";
      if (MediaRecorder.isTypeSupported && !MediaRecorder.isTypeSupported(mimeType)) {
        console.error(`MIME not supported: ${mimeType}`);
        stopTracks();
        return;
      }

      // 3) Open WebSocket after we have permission
      const wsBase = backendUrl.replace(/^http/, "ws");
      const ws = new WebSocket(`${wsBase}/ws/ask`);
      ws.binaryType = "arraybuffer";
      wsRef.current = ws;
      ws.onopen = async () => {
        try {
          ws.send("mime:audio/webm");
          const rec = new MediaRecorder(stream, { mimeType });
          recRef.current = rec;
          hasFirstChunkRef.current = false;
          pendingEndRef.current = false;
          try { clearTimeout(pendingEndTimerRef.current); } catch {}
          rec.ondataavailable = async (e) => {
            try {
              if (e.data && e.data.size > 0) {
                ws.send(await e.data.arrayBuffer());
                hasFirstChunkRef.current = true;
                if (pendingEndRef.current && ws && ws.readyState === WebSocket.OPEN) {
                  try { ws.send("end"); } catch {}
                  pendingEndRef.current = false;
                  try { clearTimeout(pendingEndTimerRef.current); } catch {}
                  setLoading(true);
                }
              }
            } catch {}
          };
          rec.start(250);
          setVoiceRecording(true);
        } catch (err) {
          try { ws.close(); } catch {}
          wsRef.current = null;
          stopTracks();
          setVoiceRecording(false);
        }
      };
      ws.onmessage = async (e) => {
        if (typeof e.data === "string") {
          return;
        }
        try {
          const blob = new Blob([e.data], { type: "audio/wav" });
          const dataUrl = URL.createObjectURL(blob);
          const lipsync = await estimateLipsyncFromBlob(blob);
          const resp = [
            {
              dataUrl,
              mime: "audio/wav",
              lipsync,
              animation: "Idle",
              facialExpression: "default",
            },
          ];
          setMessages((messages) => [...messages, ...resp]);
        } catch {}
      };
      ws.onclose = () => {
        setVoiceRecording(false);
        setLoading(false);
        stopTracks();
        recRef.current = null;
        wsRef.current = null;
      };
      ws.onerror = () => {
        try { ws.close(); } catch {}
      };
    } catch (err) {
      console.error("startVoice error", err);
    }
  };
  const stopVoice = () => {
    try {
      const rec = recRef.current;
      const ws = wsRef.current;
      if (rec && rec.state !== "inactive") {
        try { rec.stop(); } catch {}
      }
      if (ws && ws.readyState === WebSocket.OPEN) {
        if (hasFirstChunkRef.current) {
          try { ws.send("end"); } catch {}
          setLoading(true);
        } else {
          pendingEndRef.current = true;
          try { clearTimeout(pendingEndTimerRef.current); } catch {}
          pendingEndTimerRef.current = setTimeout(() => {
            try {
              const w = wsRef.current;
              if (w && w.readyState === WebSocket.OPEN) {
                w.send("end");
                setLoading(true);
              }
            } catch {}
          }, 750);
        }
      }
    } catch {}
  };
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState();
  const [loading, setLoading] = useState(false);
  const [cameraZoomed, setCameraZoomed] = useState(true);
  const onMessagePlayed = () => {
    setMessages((messages) => messages.slice(1));
  };

  useEffect(() => {
    if (messages.length > 0) {
      setMessage(messages[0]);
    } else {
      setMessage(null);
    }
  }, [messages]);

  return (
    <ChatContext.Provider
      value={{
        chat,
        startVoice,
        stopVoice,
        message,
        onMessagePlayed,
        loading,
        voiceRecording,
        cameraZoomed,
        setCameraZoomed,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
};
