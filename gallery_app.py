from flask import (
    Flask,
    render_template_string,
    send_from_directory,
    jsonify,
    make_response,
    Response,
    stream_with_context,
)
import os
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import threading, queue, time

# ---- watchdog za praćenje fajl sistema ----
# pip install watchdog
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

app = Flask(__name__)
# Izbegni default Flask keširanje statike (za svaki slučaj)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

# ==========================
#  POSTAVKE – FOLDER SA SLIKAMA
# ==========================

import tkinter as tk
from tkinter import filedialog
import os, sys

GALLERY_FOLDER = os.environ.get("GALLERY_FOLDER")

if not GALLERY_FOLDER:
    import tkinter as tk
    from tkinter import filedialog, messagebox
    import webbrowser

    root = tk.Tk()
    root.withdraw()
    while True:
        folder = filedialog.askdirectory(title="Izaberite folder sa slikama")
        if folder:
            GALLERY_FOLDER = folder
            break
        else:
            if not messagebox.askretrycancel(
                "Odabir foldera", "Niste izabrali folder. Pokušajte ponovo?"
            ):
                import sys

                sys.exit("Zatvoreno - nije izabran folder.")
    root.destroy()
    webbrowser.open("http://localhost:5000")

os.makedirs(GALLERY_FOLDER, exist_ok=True)


# 🔹 Dozvoljene ekstenzije
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}

print(f"📁 Aktivni folder za slike: {GALLERY_FOLDER}")


# ==========================
#   GLOBALNI KEŠ I SINHRONIZACIJA
# ==========================
gallery_index = {}  # {folderName: [{name, url, mtime}, ...], ...}
gallery_version = 0  # Monotono raste kad se nešto promeni
listeners = set()  # skup queue.Queue() objekata, po jedan za svakog klijenta
lock = threading.Lock()  # štiti gallery_index i gallery_version

# ==========================
#   HTML (ugrađen u aplikaciju)
# ==========================
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="sr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>📸 Foto Galerija</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      background: #0f0f0f; color: #fff; padding: 20px;
    }
    .header {
      text-align: center; padding: 30px 20px;
      background: linear-gradient(135deg,#667eea 0%,#764ba2 100%);
      border-radius: 15px; margin-bottom: 30px;
    }
    .header h1 { font-size: clamp(26px, 5vw, 48px); margin-bottom: 10px; }
    .header p { font-size: 18px; opacity: 0.9; }

    .folder-nav {
      display: flex; gap: 15px; flex-wrap: wrap;
      justify-content: center; margin-bottom: 30px;
      padding: 20px; background: #1a1a1a; border-radius: 10px;
    }
    .folder-btn {
      padding: 12px 24px; background: #2a2a2a;
      border: 2px solid #3a3a3a; color: #fff; border-radius: 8px;
      cursor: pointer; font-size: 16px; font-weight: 500;
      transition: all .3s ease;
    }
    .folder-btn:hover {
      background: #3a3a3a; border-color: #667eea;
      transform: translateY(-2px);
    }
    .folder-btn.active {
      background: linear-gradient(135deg,#667eea 0%,#764ba2 100%);
      border-color: #667eea;
    }

    .gallery-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
      gap: 20px; padding: 20px;
    }
    @media (max-width: 768px) {
      .gallery-grid { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 15px; padding: 10px; }
    }

    .image-card {
      position: relative; aspect-ratio: 1;
      border-radius: 10px; overflow: hidden;
      background: #1a1a1a; cursor: pointer;
      transition: transform .3s ease, box-shadow .3s ease;
    }
    .image-card:hover {
      transform: scale(1.05);
      box-shadow: 0 10px 30px rgba(102,126,234,.3);
    }
    .image-card img { width: 100%; height: 100%; object-fit: cover; }
    .image-name {
      position: absolute; bottom: 0; left: 0; right: 0;
      padding: 10px; background: linear-gradient(to top, rgba(0,0,0,.9), transparent);
      font-size: 14px; opacity: 0; transition: opacity .3s ease;
    }
    .image-card:hover .image-name { opacity: 1; }

    .lightbox {
      display: none; position: fixed; inset: 0;
      background: rgba(0,0,0,.95); z-index: 1000;
      justify-content: center; align-items: center;
    }
    .lightbox.active { display: flex; }
    .lightbox img {
      max-width: 90%; max-height: 90vh;
      object-fit: contain; border-radius: 10px;
    }
    .lightbox-close, .lightbox-nav {
      position: absolute; color: #fff; cursor: pointer;
      background: rgba(255,255,255,.1);
      border-radius: 50%; display: flex; align-items: center;
      justify-content: center; transition: all .3s ease;
      user-select: none;
    }
    .lightbox-close:hover, .lightbox-nav:hover {
      background: rgba(255,255,255,.2);
    }
    .lightbox-close {
      top: 30px; right: 30px; width: 50px; height: 50px;
      font-size: 36px;
    }
    .lightbox-prev, .lightbox-next {
      top: 50%; transform: translateY(-50%);
      width: 60px; height: 60px; font-size: 50px;
    }
    .lightbox-prev { left: 30px; }
    .lightbox-next { right: 30px; }
    .empty-state {
      text-align: center; padding: 60px 20px; color: #888;
    }
    .loading {
      text-align: center; padding: 40px; color: #667eea;
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>📸 Foto Galerija</h1>
    <p>Plesno takmičenje – Izaberite svoje fotografije</p>
  </div>

  <div class="folder-nav" id="folderNav">
    <div class="loading">Učitavanje foldera...</div>
  </div>

  <div class="gallery-grid" id="gallery">
    <div class="loading">Učitavanje slika...</div>
  </div>

  <div class="lightbox" id="lightbox">
    <div class="lightbox-close" onclick="closeLightbox()">×</div>
    <div class="lightbox-nav lightbox-prev" onclick="navigateLightbox(-1)">‹</div>
    <img id="lightboxImg" src="" alt="">
    <div class="lightbox-nav lightbox-next" onclick="navigateLightbox(1)">›</div>
  </div>

  <script>
    window.__initialVersion = {{ initial_version|tojson }};
    let galleryData = {};
    let currentFolder = null;
    let currentImages = [];
    let currentImageIndex = 0;
    let currentVersion = 0;
    const LAST_FOLDER_KEY = "gallery:lastFolder";

    async function init() {
      try {
        const response = await fetch(`/api/gallery?_=${Date.now()}`, { cache: "no-store" });
        galleryData = await response.json();
        currentVersion = window.__initialVersion || 0;
        const folders = Object.keys(galleryData).sort();
        if (folders.length === 0) {
          document.getElementById("folderNav").innerHTML = '<div class="empty-state"><h2>Nema foldera sa slikama</h2></div>';
          document.getElementById("gallery").innerHTML = '<div class="empty-state"><h2>Dodajte slike u foldere</h2></div>';
          connectStream(); return;
        }
        const saved = localStorage.getItem(LAST_FOLDER_KEY);
        currentFolder = (saved && folders.includes(saved)) ? saved : folders[0];
        renderFolderNav(); loadFolder(currentFolder); connectStream();
      } catch (err) {
        console.error("Greška pri init:", err);
        document.getElementById("gallery").innerHTML = '<div class="empty-state"><h2>Greška pri učitavanju slika</h2></div>';
        connectStream();
      }
    }

    function renderFolderNav() {
      const nav = document.getElementById("folderNav");
      nav.innerHTML = "";
      Object.keys(galleryData).sort().forEach((folder) => {
        const btn = document.createElement("button");
        btn.className = "folder-btn";
        btn.textContent = folder;
        btn.onclick = () => loadFolder(folder);
        if (folder === currentFolder) btn.classList.add("active");
        nav.appendChild(btn);
      });
    }

    function loadFolder(folder) {
      currentFolder = folder;
      localStorage.setItem(LAST_FOLDER_KEY, folder);
      currentImages = galleryData[folder] || [];
      renderGallery(); renderFolderNav();
    }

    function renderGallery() {
      const gallery = document.getElementById("gallery");
      gallery.innerHTML = "";
      if (!currentImages || currentImages.length === 0) {
        gallery.innerHTML = '<div class="empty-state"><h2>Nema slika u ovom folderu</h2></div>';
        return;
      }
      currentImages.forEach((img, index) => gallery.appendChild(createCard(img, index)));
    }

    function createCard(img, index) {
      const card = document.createElement("div");
      card.className = "image-card";
      card.onclick = () => openLightbox(index);
      card.innerHTML = `<img src="${img.url}" alt="${img.name}" loading="lazy">
                        <div class="image-name">${img.name}</div>`;
      return card;
    }

    function openLightbox(index) {
      currentImageIndex = index;
      document.getElementById("lightboxImg").src = currentImages[index].url;
      document.getElementById("lightbox").classList.add("active");
    }
    function closeLightbox() { document.getElementById("lightbox").classList.remove("active"); }
    function navigateLightbox(dir) {
      currentImageIndex = (currentImageIndex + dir + currentImages.length) % currentImages.length;
      document.getElementById("lightboxImg").src = currentImages[currentImageIndex].url;
    }

    async function refreshGallery() {
  try {
    const response = await fetch(`/api/gallery?_=${Date.now()}`, { cache: "no-store" });
    const fresh = await response.json();
    const freshFolders = Object.keys(fresh).sort();
    const oldFolders = Object.keys(galleryData).sort();

    const foldersChanged = JSON.stringify(freshFolders) !== JSON.stringify(oldFolders);

    // ✅ Ako nema foldera, ažuriraj i izađi
    if (freshFolders.length === 0) {
      galleryData = fresh;  // ✅ Ažuriraj prvo!
      if (foldersChanged) {
        document.getElementById("folderNav").innerHTML = 
          '<div class="empty-state"><h2>Nema foldera sa slikama</h2></div>';
      }
      document.getElementById("gallery").innerHTML =
        '<div class="empty-state"><h2>Dodajte slike u foldere</h2></div>';
      currentFolder = null;
      return;
    }

    // ✅ KLJUČNA IZMENA: Ažuriraj galleryData ODMAH nakon što dobiješ fresh podatke
    const prevList = galleryData[currentFolder] || [];
    galleryData = fresh;  // ⭐ Pomeri OVDE, pre renderFolderNav()

    // ✅ Ako currentFolder ne postoji (startup ili obrisan), postavi prvi dostupan
    if (!currentFolder || !freshFolders.includes(currentFolder)) {
      const saved = localStorage.getItem(LAST_FOLDER_KEY);
      currentFolder = (saved && freshFolders.includes(saved)) ? saved : freshFolders[0];
      localStorage.setItem(LAST_FOLDER_KEY, currentFolder);
    }

    // ✅ Osvežava navigaciju ako su se folderi promenili
    if (foldersChanged) {
      renderFolderNav();  // Sada koristi NOVI galleryData!
    }

    // Uporedi slike unutar aktivnog foldera
    const freshList = galleryData[currentFolder] || [];
    freshList.sort((a,b)=>a.name.localeCompare(b.name,undefined,{numeric:true,sensitivity:'base'}));

    const prevKeys = new Set(prevList.map(x => `${x.name}:${x.mtime}`));
    const newItems = freshList.filter(x => !prevKeys.has(`${x.name}:${x.mtime}`));

    const galleryEl = document.getElementById("gallery");
    
    if (prevList.length === 0 && freshList.length > 0) {
      // Prvi put: renderuj sve
      galleryEl.innerHTML = "";
      freshList.forEach((img, idx) => galleryEl.appendChild(createCard(img, idx)));
      currentImages = freshList.slice();
    } else if (newItems.length > 0) {
      // Dodaj nove slike samo na kraj
      const startIndex = prevList.length;
      newItems.forEach((img, i) => {
        const idx = startIndex + i;
        galleryEl.appendChild(createCard(img, idx));
      });
      currentImages = prevList.concat(newItems);
    } else if (freshList.length === 0) {
      // Folder je ispražnjen
      galleryEl.innerHTML = '<div class="empty-state"><h2>Nema slika u ovom folderu</h2></div>';
      currentImages = [];
    }

  } catch (e) {
    console.warn("Refresh greška:", e);
  }
}


    function connectStream() {
      try {
        const es = new EventSource('/api/stream');
        es.addEventListener('version', ev => {
          const v = parseInt(ev.data, 10);
          if (!isNaN(v) && v > currentVersion) { currentVersion = v; refreshGallery(); }
        });
        es.addEventListener('ping', ()=>{});
        es.onerror = ()=>{ try{es.close();}catch(e){}; setTimeout(connectStream, 2000); };
      } catch(e){ setTimeout(connectStream,4000); }
    }

    init();
  </script>
</body>
</html>"""


# ==========================
#   POMOĆNE FUNKCIJE
# ==========================
def scan_gallery_folder():
    """Skenira gallery folder i vraća strukturu foldera i slika (abecedno po imenu)."""
    gallery_path = Path(GALLERY_FOLDER)
    if not gallery_path.exists():
        return {}

    result = {}
    for folder in sorted(gallery_path.iterdir()):
        if folder.is_dir():
            images = []
            # sortiraj po nazivu fajla (abecedno)
            for file in sorted(folder.iterdir(), key=lambda f: f.name.lower()):
                if file.suffix.lower() in ALLOWED_EXTENSIONS and file.is_file():
                    mtime = int(file.stat().st_mtime)
                    images.append(
                        {
                            "name": file.name,
                            # cache-bust po mtime -> kad se doda/zameni fajl, URL se menja
                            "url": f"/images/{folder.name}/{file.name}?v={mtime}",
                            "mtime": mtime,
                        }
                    )
            if images:
                result[folder.name] = images
    return result


def rebuild_index_and_bump():
    """Ponovo izgradi keš i podignu verziju; poziva se nakon FS promene."""
    global gallery_index, gallery_version
    with lock:
        gallery_index = scan_gallery_folder()
        gallery_version += 1
        v = gallery_version
    for q in list(listeners):
        try:
            q.put_nowait(v)
        except Exception:
            pass


# ==========================
#   WATCHDOG
# ==========================
class FSHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        # Debounce: grupiši rafale izmene u jednu verziju
        def _do():
            time.sleep(0.3)
            rebuild_index_and_bump()

        threading.Thread(target=_do, daemon=True).start()


def start_watcher():
    handler = FSHandler()
    # 1) probaj brži, nativni Windows watcher
    try:
        observer = Observer()
        observer.schedule(handler, GALLERY_FOLDER, recursive=True)
        observer.daemon = True
        observer.start()
        print(f"[watcher] Native Observer started on {GALLERY_FOLDER}")
        return observer
    except Exception as e:
        print(f"[watcher][WARN] Native Observer failed: {e}")
        # 2) fallback: portable polling watcher (radi svuda; malo veći I/O)
        observer = PollingObserver(timeout=1.0)
        observer.schedule(handler, GALLERY_FOLDER, recursive=True)
        observer.daemon = True
        observer.start()
        print(f"[watcher] PollingObserver started on {GALLERY_FOLDER}")
        return observer


# ==========================
#   ROUTES
# ==========================
@app.route("/")
def index():
    with lock:
        iv = gallery_version
    return render_template_string(HTML_TEMPLATE, initial_version=iv)


@app.route("/api/gallery")
def api_gallery():
    with lock:
        data = dict(gallery_index)  # plitka kopija je dovoljna
        v = gallery_version
    resp = make_response(jsonify(data))
    # anti-cache za JSON (uvek sveže)
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    resp.headers["ETag"] = f'W/"{v}"'
    return resp


@app.route("/api/stream")
def api_stream():
    """SSE stream: šalje 'version' event kad se desi promena, plus keepalive ping."""
    q = queue.Queue()
    listeners.add(q)

    @stream_with_context
    def gen():
        with lock:
            v = gallery_version
        yield f"event: version\ndata: {v}\n\n"
        try:
            while True:
                try:
                    v2 = q.get(timeout=30)
                    yield f"event: version\ndata: {v2}\n\n"
                except queue.Empty:
                    yield "event: ping\ndata: keepalive\n\n"
        finally:
            listeners.discard(q)

    return Response(
        gen(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/images/<folder>/<filename>")
def serve_image(folder, filename):
    """Servira slike – efikasno keširanje, URL menjaš po mtime (?v=...)."""
    folder_path = os.path.join(GALLERY_FOLDER, folder)
    resp = send_from_directory(folder_path, filename)
    resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return resp


# ==========================
#   FACTORY ZA WSGI SERVER (PRODUCTION)
# ==========================
def create_app():
    """Factory koju zove WSGI server (Waitress)."""
    if not getattr(app, "_booted", False):
        with lock:
            global gallery_index
            gallery_index = scan_gallery_folder()
        try:
            start_watcher()
        except Exception as e:
            print(f"[WARN] Watcher nije pokrenut: {e}")
        app._booted = True
    return app


# ==========================
#   DEV STARTER
# ==========================
if __name__ == "__main__":
    if not os.path.exists(GALLERY_FOLDER):
        print(
            f"\n⚠️  UPOZORENJE: Folder '{GALLERY_FOLDER}' ne postoji! Kreiraj ga ili promeni GALLERY_FOLDER u kodu.\n"
        )
    with lock:
        gallery_index = scan_gallery_folder()
    observer = start_watcher()
    print("\n🚀 DEV server pokrenut")
    print("🌐 http://localhost:5000")
    print("📱 LAN: http://[IP_LAPTOPA]:5000   (npr. http://192.168.0.12:5000)\n")
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
