/* ConceptCheckmate — frontend controller */

const topicSelect   = document.getElementById('topicSelect');
const customBox      = document.getElementById('customTopicBox');
const customTitle     = document.getElementById('customTitle');
const customIdeal     = document.getElementById('customIdeal');
const transcriptBox  = document.getElementById('transcript');
const micBtn         = document.getElementById('micBtn');
const micLabel       = document.getElementById('micLabel');
const recIndicator   = document.getElementById('recIndicator');
const analyzeBtn     = document.getElementById('analyzeBtn');
const errorMsg       = document.getElementById('errorMsg');
const emptyState     = document.getElementById('emptyState');
const reportBody     = document.getElementById('reportBody');
const engineLabel    = document.getElementById('engineLabel');
const downloadBtn    = document.getElementById('downloadBtn');

let lastResult = null;

/* ---------------- Engine status ---------------- */
fetch('/api/health').then(r => r.json()).then(d => {
  engineLabel.textContent = d.engine_mode === 'sentence-transformers'
    ? 'Semantic engine: Sentence-Transformers (MiniLM)'
    : 'Semantic engine: TF-IDF + Cosine Similarity';
}).catch(() => { engineLabel.textContent = 'engine offline'; });

/* ---------------- Load topics ---------------- */
fetch('/api/topics').then(r => r.json()).then(topics => {
  topics.forEach(t => {
    const opt = document.createElement('option');
    opt.value = t.id; opt.textContent = t.title;
    topicSelect.appendChild(opt);
  });
  const customOpt = document.createElement('option');
  customOpt.value = '__custom__'; customOpt.textContent = '+ Custom topic (type your own)';
  topicSelect.appendChild(customOpt);
});

topicSelect.addEventListener('change', () => {
  customBox.classList.toggle('hidden', topicSelect.value !== '__custom__');
});

/* ---------------- Speech Recognition ---------------- */
let recognition = null;
let isRecording = false;

const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognitionAPI) {
  recognition = new SpeechRecognitionAPI();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = 'en-US';

  let finalTranscript = transcriptBox.value || '';

  recognition.onresult = (event) => {
    let interim = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const chunk = event.results[i][0].transcript;
      if (event.results[i].isFinal) finalTranscript += chunk + ' ';
      else interim += chunk;
    }
    transcriptBox.value = (finalTranscript + interim).trim();
  };

  recognition.onerror = (e) => {
    showError('Speech recognition error: ' + e.error + '. You can type your explanation instead.');
    stopRecording();
  };

  recognition.onend = () => { if (isRecording) recognition.start(); /* keep listening until user stops */ };

  micBtn.addEventListener('click', () => {
    if (!isRecording) {
      finalTranscript = transcriptBox.value ? transcriptBox.value + ' ' : '';
      startRecording();
    } else {
      stopRecording();
    }
  });
} else {
  micLabel.textContent = 'Voice input unsupported — type instead';
  micBtn.disabled = true;
}

function startRecording() {
  isRecording = true;
  recognition.start();
  micBtn.classList.add('active');
  micLabel.textContent = 'Stop';
  recIndicator.classList.remove('hidden');
}

function stopRecording() {
  isRecording = false;
  try { recognition.stop(); } catch (e) {}
  micBtn.classList.remove('active');
  micLabel.textContent = 'Start speaking';
  recIndicator.classList.add('hidden');
}

/* ---------------- Analyze ---------------- */
analyzeBtn.addEventListener('click', async () => {
  hideError();
  const transcript = transcriptBox.value.trim();
  if (!transcript) { showError('Please speak or type an explanation first.'); return; }

  const payload = { transcript };
  if (topicSelect.value === '__custom__') {
    if (!customIdeal.value.trim()) { showError('Please provide a model/ideal answer for the custom topic.'); return; }
    payload.custom_title = customTitle.value.trim();
    payload.custom_ideal_answer = customIdeal.value.trim();
  } else if (topicSelect.value) {
    payload.topic_id = topicSelect.value;
  } else {
    showError('Please select a topic.'); return;
  }

  setLoading(true);
  try {
    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) { showError(data.error || 'Analysis failed.'); return; }
    lastResult = data;
    renderReport(data);
  } catch (e) {
    showError('Could not reach the analysis server. Is app.py running?');
  } finally {
    setLoading(false);
  }
});

function setLoading(loading) {
  analyzeBtn.disabled = loading;
  analyzeBtn.firstChild.textContent = loading ? 'Analyzing… ' : 'Analyze Understanding';
}

function showError(msg) { errorMsg.textContent = msg; errorMsg.classList.remove('hidden'); }
function hideError() { errorMsg.classList.add('hidden'); }

/* ---------------- Render ---------------- */
function renderReport(data) {
  emptyState.classList.add('hidden');
  reportBody.classList.remove('hidden');

  document.getElementById('scoreNum').textContent = data.score;
  document.getElementById('bandTag').textContent = data.band;
  document.getElementById('topicTitleOut').textContent = data.topic_title;
  document.getElementById('simPct').textContent = data.overall_similarity + '%';
  document.getElementById('sentCount').textContent = data.student_sentence_count;

  const arc = document.getElementById('gaugeArc');
  const circumference = 220;
  const offset = circumference - (circumference * data.score / 100);
  const color = data.score >= 85 ? 'var(--teal)' : data.score >= 40 ? 'var(--gold)' : 'var(--clay)';
  requestAnimationFrame(() => {
    arc.style.stroke = color;
    arc.style.strokeDashoffset = offset;
  });

  renderChipList('matchedList', data.matched_concepts, 'matched', c =>
    `<div class="chip matched"><b>${c.label}</b><small>confidence ${Math.round(c.confidence*100)}%</small></div>`);
  renderChipList('partialList', data.partial_concepts, 'partial', c =>
    `<div class="chip partial"><b>${c.label}</b><small>confidence ${Math.round(c.confidence*100)}%</small></div>`);
  renderChipList('missingList', data.missing_concepts, 'missing', c =>
    `<div class="chip missing"><b>${c.label}</b></div>`);

  const miscBox = document.getElementById('misconceptionBox');
  const miscList = document.getElementById('misconceptionList');
  miscList.innerHTML = '';
  if (data.misconceptions && data.misconceptions.length) {
    miscBox.classList.remove('hidden');
    data.misconceptions.forEach(m => {
      const li = document.createElement('li'); li.textContent = m; miscList.appendChild(li);
    });
  } else {
    miscBox.classList.add('hidden');
  }

  document.getElementById('feedbackText').textContent = data.feedback;
  reportBody.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function renderChipList(elId, items, cls, renderFn) {
  const el = document.getElementById(elId);
  el.innerHTML = '';
  if (!items || !items.length) {
    el.innerHTML = `<div class="chip-empty">None</div>`;
    return;
  }
  items.forEach(item => { el.insertAdjacentHTML('beforeend', renderFn(item)); });
}

/* ---------------- Download report ---------------- */
downloadBtn.addEventListener('click', () => {
  if (!lastResult) return;
  const d = lastResult;
  const lines = [
    `ConceptCheckmate — Assessment Report`,
    `Topic: ${d.topic_title}`,
    `Score: ${d.score}/100  (${d.band})`,
    `Overall semantic similarity: ${d.overall_similarity}%`,
    ``,
    `Concepts covered: ${d.matched_concepts.map(c=>c.label).join(', ') || 'None'}`,
    `Partially explained: ${d.partial_concepts.map(c=>c.label).join(', ') || 'None'}`,
    `Missing concepts: ${d.missing_concepts.map(c=>c.label).join(', ') || 'None'}`,
    ``,
    `Misconceptions:`,
    ...(d.misconceptions.length ? d.misconceptions.map(m => ' - ' + m) : [' None']),
    ``,
    `Feedback:`,
    d.feedback
  ];
  const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = `concept-report-${Date.now()}.txt`;
  a.click();
  URL.revokeObjectURL(url);
});
