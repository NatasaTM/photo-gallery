📸 FotoGalerija

---

**Instalacija i pokretanje**

1️⃣ **Kloniranje projekta sa GitHub-a:**

- Prvo, instaliraj [Git](https://git-scm.com/) ako ga nemaš.
- Otvori **Command Prompt** ili **PowerShell** na željenoj lokaciji i pokreni:
  
  ```
  git clone https://github.com/tvoj-nalog/naziv-repozitorijuma.git
  ```
  (Zameni adresu odgovarajućim URL-om tvog repozitorijuma)

2️⃣ **Instaliraj Python 3.10+** (ako već nije instaliran):
- [Preuzmi Python ovde](https://www.python.org/downloads/windows/), obavezno čekiraj "Add Python to PATH" tokom instalacije.

3️⃣ **Pokreni start_setup.bat**
- Duplo klikni na `start_setup.bat` fajl.
- Ovo automatski kreira virtuelno okruženje i instalira potrebne biblioteke.

4️⃣ **Kreiranje .exe fajla za produkciju**
- Fajl `FotoGalerija.exe` se obično već nalazi u folderu `dist`, spreman za korišćenje.
- Ako trebaš da napraviš nov `.exe` (npr. posle izmene koda):
  - Pokreni u terminalu (sa aktiviranim venv-om):
    ```
    pip install pyinstaller
    pyinstaller FotoGalerija.spec
    ```
  - Gotov izvršni fajl nalazićeš u folderu `dist/` pod imenom `FotoGalerija.exe`.

5️⃣ **Pokretanje galerije**
- Duplo klikni na `start_fotke.bat`.
- Aplikacija će se pokrenuti i automatski otvoriti lokalnu adresu u tvom browseru (npr. `http://localhost:5000`).
- Vidjećeš i LAN adresu (za pristup sa drugih uređaja u mreži).

6️⃣ **Zaustavljanje galerije**
- Da zaustaviš aplikaciju, duplo klikni na `stop_fotke.bat`.

7️⃣ **Dodavanje slika**
- Slike se organizuju u podfoldere (npr. prema satnici) unutar glavnog foldera sa slikama koji odabereš pri prvom pokretanju.

---

🛈 Ako koristiš više tableta u mreži, otvori adresu sa LAN-a na svakom uređaju: `http://[IP_laptopa]:5000`

---

**Sažetak fajlova:**
- `start_fotke.bat` — pokreće FotoGaleriju kao .exe i prikazuje adresu.
- `stop_fotke.bat` — gasi FotoGalerija.exe proces.
- `start_setup.bat` — kreira venv i instalira dependency-je.
- `start_dev.bat` i `start_prod.bat` — startuju razvojni/produkcijski mod iz izvornog koda (koristi ih developer).

---

# English Instructions

---

**Installation and Usage**

1️⃣ **Clone the project from GitHub:**
- First, install [Git](https://git-scm.com/) if you don't have it.
- Open **Command Prompt** or **PowerShell** where you want the project and run:

  ```
  git clone https://github.com/your-username/your-repository.git
  ```
  (Replace the URL with your repository)

2️⃣ **Install Python 3.10+** (if not already installed):
- [Download Python here](https://www.python.org/downloads/windows/) and be sure to check "Add Python to PATH" during installation.

3️⃣ **Run start_setup.bat**
- Double-click the `start_setup.bat` file.
- This will automatically create a virtual environment and install all needed libraries.

4️⃣ **Create the .exe file for production**
- The file `FotoGalerija.exe` is typically already present in the `dist` folder and ready to use.
- If you need to generate a new `.exe` (e.g., after changing the code):
  - In a terminal with the venv activated, run:
    ```
    pip install pyinstaller
    pyinstaller FotoGalerija.spec
    ```
  - The final executable is in the `dist/` folder (named `FotoGalerija.exe`).

5️⃣ **Run the gallery**
- Double-click `start_fotke.bat`.
- The app will start and automatically open the local address in your browser (e.g., `http://localhost:5000`).
- You will also see the LAN address (for access from other devices on the network).

6️⃣ **Stop the gallery**
- To stop the app, double-click `stop_fotke.bat`.

7️⃣ **Adding images**
- Organize images inside subfolders (e.g., by time slot) within the main image folder you select when first starting the app.

---

🛈 If you use more tablets/devices on your local network, open the LAN address on each device: `http://[YOUR_LAPTOP_IP]:5000`

---

**File summary:**
- `start_fotke.bat` — starts FotoGalerija as an .exe and shows the web address.
- `stop_fotke.bat` — stops the FotoGalerija.exe process.
- `start_setup.bat` — creates a venv and installs dependencies.
- `start_dev.bat` & `start_prod.bat` — start development/production mode from source (for developers).
