const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const statusEl = document.getElementById("status");
const logEl = document.getElementById("log");
const vizEl = document.getElementById("viz");

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let listening = false;
let isAwake = false;
let speaking = false;
function setViz(state){ if(!vizEl) return; vizEl.className = "viz " + (state || ""); }

function addLog(sender, text) {
  const div = document.createElement("div");
  div.className = "msg " + (sender === "Max" ? "max" : "user");
  div.textContent = (sender === "Max" ? "Max: " : "You: ") + text;
  logEl.appendChild(div);
  logEl.scrollTop = logEl.scrollHeight;
}

function speak(text, onDone) {
  const cleaned = text.replace(/[^\w\s,?.!':-]/g, "").trim();
  const utter = new SpeechSynthesisUtterance(cleaned);
  utter.rate = 1.0;
  utter.pitch = 1.0;
  const voices = window.speechSynthesis.getVoices();
  if (voices && voices.length) {
    const preferred = voices.find(v => /en/i.test(v.lang) && /female/i.test(v.name)) || voices[0];
    utter.voice = preferred;
  }
  if (recognition) {
    try { recognition.stop(); } catch {}
  }
  speaking = true;
  statusEl.textContent = "Speaking...";
  setViz("speaking");
  window.speechSynthesis.cancel();
  utter.onend = () => {
    speaking = false;
    statusEl.textContent = isAwake ? "Listening..." : "Idle";
    setViz(isAwake ? "listening" : "");
    if (typeof onDone === "function") onDone();
    if (listening && recognition) {
      try { recognition.start(); } catch {}
    }
  };
  window.speechSynthesis.speak(utter);
}

async function sendToBackend(text) {
  try {
    const res = await fetch("/api/assist", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    const data = await res.json();
    const reply = (data && data.reply) ? data.reply : "";
    addLog("Max", reply);
    speak(reply, () => {
      isAwake = false;
    });
  } catch (e) {
    addLog("Max", "Network error.");
    speak("Network error.", () => {
      isAwake = false;
    });
  }
}

function initRecognition() {
  if (!SpeechRecognition) {
    statusEl.textContent = "SpeechRecognition not supported.";
    return;
  }
  recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.continuous = true;
  recognition.interimResults = false;

  recognition.onstart = () => {
    statusEl.textContent = "Listening...";
    setViz(isAwake ? "listening" : "");
  };
  recognition.onend = () => {
    statusEl.textContent = "Idle";
    setViz("");
    if (listening) recognition.start();
  };
  recognition.onerror = () => {
    statusEl.textContent = "Error";
  };
  recognition.onresult = (event) => {
    const res = event.results[event.results.length - 1];
    if (res && res.isFinal) {
      if (speaking) return;
      let text = res[0].transcript.trim().toLowerCase();
      if (!isAwake) {
        if (text.includes("hey max")) {
          isAwake = true;
          addLog("You", text);
          addLog("Max", "Yeah?");
          speak("Yeah?", () => {
            statusEl.textContent = "Listening...";
            setViz("listening");
          });
        }
        return;
      }
      // Remove wake word if included
      text = text.replace("hey max", "").trim();
      if (!text) return;
      addLog("You", text);
      statusEl.textContent = "Thinking...";
      sendToBackend(text);
    }
  };
}

startBtn.onclick = () => {
  if (!recognition) initRecognition();
  if (recognition && !listening) {
    listening = true;
    recognition.start();
    statusEl.textContent = isAwake ? "Listening..." : "Say 'Hey Max'...";
    setViz(isAwake ? "listening" : "");
  }
};

stopBtn.onclick = () => {
  listening = false;
  if (recognition) recognition.stop();
  statusEl.textContent = "Idle";
  window.speechSynthesis.cancel();
  isAwake = false;
  setViz("");
};

window.addEventListener("load", () => {
  window.speechSynthesis.onvoiceschanged = () => {};
  setViz("");
});
