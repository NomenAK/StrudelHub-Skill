// Browser-side verifier for the pinned StrudelHub recorder. No session API calls.
async ({code, begin, cycles, loop, render, ranges, labels, tours, tourLen}) => {
  const expected = 'https://unpkg.com/@strudel/repl@1.3.0';
  if (![...document.scripts].some(script => script.src === expected)) {
    throw new Error('Recorder runtime changed: expected @strudel/repl@1.3.0');
  }
  const editor = document.getElementById('rec-editor').editor;
  const pattern = await editor.repl.evaluate(code, false);
  if (editor.repl.state.evalError) throw editor.repl.state.evalError;
  if (editor.repl.state.started) {
    editor.repl.stop();
    throw new Error('Track started the scheduler during verification');
  }
  const cps = editor.repl.scheduler.cps;
  if (!(cps > 0 && Number.isFinite(cps))) throw new Error('Invalid cycle rate');
  const events = pattern.queryArc(begin, begin + cycles, {_cps: cps})
    .filter(event => event.hasOnset());
  const failures = new Set();
  const sounds = new Set();
  const soundName = value => value.bank ? `${value.bank}_${value.s || 'triangle'}` : (value.s || 'triangle');
  const labelOf = value => (value.label === undefined || value.label === null) ? '' : String(value.label);
  const labelCounts = rows => {
    const counts = {};
    for (const event of rows) {
      const key = labelOf(event.value);
      counts[key] = (counts[key] || 0) + 1;
    }
    return Object.fromEntries(Object.entries(counts).sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0));
  };
  // gm_* soundfonts and note-keyed (pitched) sample maps such as VCSL / piano.
  const isPitched = name => {
    if (name.startsWith('gm_')) return true;
    const sound = getSound(name);
    const samples = sound && sound.data && sound.data.samples;
    return !!samples && typeof samples === 'object' && !Array.isArray(samples);
  };
  function inspect(eventsToCheck, soundSet = sounds) {
    for (const event of eventsToCheck) {
      const value = event.value;
      // MIDI/OSC output is outside this audio verifier's contract.
      if (value.midichan !== undefined || value.osc !== undefined) {
        failures.add('External MIDI/OSC output is not supported by this verifier');
      }
      const name = soundName(value);
      soundSet.add(name);
      const sound = getSound(name);
      if (!sound) {
        failures.add(`Unknown sound: ${name}`);
        continue;
      }
      const index = Number(value.n ?? 0);
      if (sound.data.type === 'soundfont' &&
          (!Number.isInteger(index) || index < 0 || index >= sound.data.fonts.length)) {
        failures.add(`Invalid soundfont index: ${name}:${index}`);
      }
    }
  }
  inspect(events);
  const result = {
    runtime: '@strudel/repl@1.3.0', started: false,
    range: [begin, begin + cycles], cps, events: events.length,
    sounds: [], errors: [],
    limits: ['Only queried onsets checked; registry checks do not fetch audio assets or prove soundfont pitch coverage.']
  };
  const signature = (rows, offset) => rows.map(event => {
    const value = event.value;
    return JSON.stringify([
      Number((Number(event.whole.begin) - offset).toFixed(8)),
      Number((Number(event.whole.end) - Number(event.whole.begin)).toFixed(8)),
      value.note ?? null, value.s ?? 'triangle', value.bank ?? null,
      value.n ?? null, value.label ?? null, value.orbit ?? null
    ]);
  }).sort();
  if (loop !== null) {
    const next = pattern.queryArc(begin + loop, begin + loop + cycles, {_cps: cps})
      .filter(event => event.hasOnset());
    inspect(next);
    result.loop = {offset: loop, matches: JSON.stringify(signature(events, begin)) ===
      JSON.stringify(signature(next, begin + loop))};
    if (!result.loop.matches) failures.add('Loop note/rhythm/instrument signatures differ');
    result.limits.push('Loop comparison excludes dynamics/effects; intentional randomness can differ.');
  }
  if (ranges) {
    // badNotes: one entry per offending event, any sound (synths too). Judged on the original note value:
    // a number < 20 (typically `@.5` -> 0.5 / -11.5), null, NaN/Infinity, a non-number/non-string, or a string
    // that is neither numeric nor a note name. Valid names such as "c0" are fine whatever their MIDI value.
    // ranges: min/max MIDI per gm_* / pitched-sample sound over the valid notes only.
    const table = {};
    const badNotes = [];
    let badCount = 0;
    const BAD_CAP = 200;
    for (const event of events) {
      const value = event.value;
      const note = value.note;
      if (note === undefined) continue;
      const name = soundName(value);
      let midi = NaN, reason = null;
      if (typeof note === 'number') {
        if (!Number.isFinite(note)) reason = 'non-finite number';
        else if (note < 20) reason = 'number < 20';
        else midi = note;
      } else if (typeof note === 'string') {
        const text = note.trim();
        if (/^-?\d+(\.\d+)?$/.test(text)) {
          midi = Number(text);
          if (midi < 20) reason = 'numeric string < 20';
        } else {
          try { midi = noteToMidi(text); } catch { midi = NaN; }
          if (!Number.isFinite(midi)) reason = 'unparseable note name';
        }
      } else {
        reason = note === null ? 'null note' : `note of type ${typeof note}`;
      }
      if (reason) {
        badCount++;
        if (badNotes.length < BAD_CAP) {
          const shown = typeof note === 'string' ? note
            : (typeof note === 'number' && Number.isFinite(note)) ? note : String(note);
          badNotes.push({sound: name, note: shown, reason, label: labelOf(value),
            begin: Number(event.whole.begin)});
        }
        continue;
      }
      if (!isPitched(name)) continue;
      const row = table[name] || (table[name] = {min: midi, max: midi, events: 0});
      row.min = Math.min(row.min, midi);
      row.max = Math.max(row.max, midi);
      row.events++;
    }
    result.ranges = Object.fromEntries(Object.entries(table).sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0));
    result.badNotes = badNotes;
    if (badCount) failures.add(`${badCount} event(s) with a bad note value (number < 20 or non-numeric); see badNotes`);
    if (badCount > BAD_CAP) result.limits.push(`badNotes lists the first ${BAD_CAP} of ${badCount} offending events.`);
    result.limits.push('Ranges cover gm_* and note-keyed sample sounds in the queried window; they show requested MIDI notes, not available sample/soundfont coverage.');
  }
  if (labels) {
    result.labels = labelCounts(events);
  }
  if (tours !== null) {
    // Per tour k (base = k*tourLen): early, late and final windows, then cycle 0 against cycle tours*tourLen.
    const windows = [];
    for (let k = 0; k < tours; k++) {
      const base = k * tourLen;
      for (const [a, b] of [[2, 4], [tourLen - 15, tourLen - 13], [tourLen - 4, tourLen]]) {
        const rows = pattern.queryArc(base + a, base + b, {_cps: cps}).filter(event => event.hasOnset());
        const set = new Set();
        inspect(rows, set);
        windows.push({tour: k, range: [base + a, base + b], events: rows.length,
          sounds: [...set].sort(), labels: labelCounts(rows)});
      }
    }
    const total = tours * tourLen;
    const first = pattern.queryArc(0, 1, {_cps: cps}).filter(event => event.hasOnset());
    const last = pattern.queryArc(total, total + 1, {_cps: cps}).filter(event => event.hasOnset());
    const matches = JSON.stringify(signature(first, 0)) === JSON.stringify(signature(last, total));
    result.tours = {count: tours, tourLen, windows,
      loop: {cycle: 0, against: total, events: [first.length, last.length], matches}};
    if (!matches) failures.add(`Tour loop: cycle 0 differs from cycle ${total}`);
    result.limits.push('Tour loop compares note/s/bank/n/label/orbit signatures of cycle 0 and the cycle after the last tour, not dynamics/effects.');
  }
  if (render && !failures.size) {
    // Strudel's renderer exports a WAV by clicking an anchor. Suppress that download;
    // inspect the returned AudioBuffer instead. Rendering never reaches speakers.
    const originalRender = OfflineAudioContext.prototype.startRendering;
    const originalClick = HTMLAnchorElement.prototype.click;
    let metrics = null;
    OfflineAudioContext.prototype.startRendering = async function () {
      const buffer = await originalRender.call(this);
      if (this === getAudioContext()) {
        let peak = 0, energy = 0;
        for (let channel = 0; channel < buffer.numberOfChannels; channel++) {
          for (const sample of buffer.getChannelData(channel)) {
            peak = Math.max(peak, Math.abs(sample));
            energy += sample * sample;
          }
        }
        metrics = {seconds: buffer.duration, peak,
          rms: Math.sqrt(energy / (buffer.length * buffer.numberOfChannels))};
      }
      return buffer;
    };
    HTMLAnchorElement.prototype.click = function () {
      if (!this.download) return originalClick.call(this);
    };
    try {
      await renderPatternAudio(pattern, cps, begin, begin + cycles, 22050, 64, false, 'verify-track');
      if (!metrics) throw new Error('Renderer returned no measured audio buffer');
      result.render = metrics;
      if (!Number.isFinite(metrics.peak) || !Number.isFinite(metrics.rms)) failures.add('Nonfinite audio samples');
      if (metrics.peak >= 1) failures.add('Rendered peak reaches or exceeds full scale');
    } finally {
      OfflineAudioContext.prototype.startRendering = originalRender;
      HTMLAnchorElement.prototype.click = originalClick;
    }
    result.limits.push('Render covers the selected window only, without earlier effect tails; it does not judge musical quality.');
  }
  result.sounds = [...sounds].sort();
  result.errors = [...failures];
  return result;
}
