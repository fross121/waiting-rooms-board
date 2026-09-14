// Shared, live-saved boards through Firebase Firestore. Does nothing until
// firebase-config.js fills in window.FIREBASE_CONFIG; the page then keeps
// boards in this browser instead.
(() => {
  const cfg = window.FIREBASE_CONFIG;
  if (!cfg || !cfg.projectId) return;
  const SDK = 'https://www.gstatic.com/firebasejs/10.14.1/';
  const load = src => new Promise((ok, bad) => { const s = document.createElement('script'); s.src = src; s.onload = ok; s.onerror = () => bad(new Error('could not load ' + src)); document.head.appendChild(s); });
  window.BOARD_STORE_FACTORY = async () => {
    await load(SDK + 'firebase-app-compat.js');
    await load(SDK + 'firebase-firestore-compat.js');
    const app = firebase.initializeApp(cfg);
    const db = firebase.firestore(app);
    const boards = () => db.collection('boards');
    let leaseTimer = 0;
    const LEASE_MS = 60000;
    // one editor at a time: a lock on the board itself, taken in a
    // transaction so two people cannot both win it
    async function acquire(id, holder) {
      const ref = boards().doc(id);
      return db.runTransaction(async tx => {
        const snap = await tx.get(ref);
        const now = Date.now();
        const lock = snap.exists ? (snap.data().lock || null) : null;
        if (lock && lock.holder !== holder && Number(lock.until) > now) return false;
        if (snap.exists) tx.update(ref, {lock: {holder, until: now + LEASE_MS}});
        return true;
      });
    }
    return {
      cloud: true, restoreId: null,
      list(onChange, onError) {
        boards().onSnapshot(snap => onChange(snap.docs.map(d => ({id: d.id, data: d.data(), pending: d.metadata.hasPendingWrites}))),
          e => onError && onError({code: e.code || 'unavailable', message: e.message}));
      },
      async load(id) { const s = await boards().doc(id).get(); return s.exists ? s.data() : null; },
      async save(id, doc) {
        // keep whatever lock the board carries; the doc itself never writes one
        const ref = boards().doc(id);
        const cur = await ref.get();
        const lock = cur.exists && cur.data().lock ? {lock: cur.data().lock} : {};
        await ref.set(Object.assign({}, doc, lock));
      },
      async remove(id) { await boards().doc(id).delete(); },
      async lease(id, holder, onLost) {
        if (!(await acquire(id, holder))) return false;
        clearInterval(leaseTimer);
        leaseTimer = setInterval(async () => { try { if (!(await acquire(id, holder)) && onLost) onLost(); } catch (e) {} }, 25000);
        return true;
      },
      release() { clearInterval(leaseTimer); leaseTimer = 0; },
      async download(filename, text) {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(new Blob([text], {type: 'application/json'})); a.download = filename;
        document.body.appendChild(a); a.click(); a.remove();
        setTimeout(() => URL.revokeObjectURL(a.href), 2000);
        return 'downloading ' + filename + ' - drop it into boards/';
      },
    };
  };
})();
