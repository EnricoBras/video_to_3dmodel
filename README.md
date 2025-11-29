# 📘 INSTALLAZIONE E GUIDA – Ricostruzione 3D con COLMAP (Windows)

##  Requisiti minimi hardware

- CPU: **AMD Ryzen 5 / Intel i5 o superiore**
- GPU: **NVIDIA RTX consigliata (supporto CUDA)**
- RAM: **16 GB minimi, 32 GB consigliati**
- Spazio su disco: **~10 GB** liberi (tra video, immagini e output)
- Sistema operativo: **Windows 10 / 11 (64 bit)**

---

##Software necessario

Tutto quello che serve verrà installato automaticamente tramite uno script.  
Ma se vuoi farlo manualmente, ecco cosa serve:

| Componente | Descrizione | Installazione manuale |
|-------------|-------------|------------------------|
| **Python 3.10+** | Esegue lo script principale | [python.org/downloads](https://www.python.org/downloads/) |
| **COLMAP** | Software di Structure-from-Motion (SfM/MVS) | [github.com/colmap/colmap/releases](https://github.com/colmap/colmap/releases) |
| **FFmpeg** | Usato per estrarre i frame da video | [www.gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/) |
| **Git (facoltativo)** | Per scaricare e aggiornare il progetto da GitHub | [git-scm.com/downloads](https://git-scm.com/downloads) |

---



## installazione manuale 

---INSTALLAZIONE DI PYTHON---
1 Scarica Python 3.10 o superiore da python.org/downloads

2 (IMPORTANTE) Durante l’installazione, spuntare l’opzione “Add Python to PATH”.

3 Dopo l’installazione, verifica aprendo PowerShell e digitando: python --version

4 Se mostra qualcosa tipo Python 3.12.3, è installato correttamente.



--INSTALLAZIONE DI FFMPEG--
1 Vai su https://www.gyan.dev/ffmpeg/builds/

2 Scarica il file ffmpeg-release-essentials.zip.

3 Estrai il contenuto in una cartella apposita

4 vai in "proprietà del sistema" --> "variabili d'ambiente" --> "path": Questa è la variabile che utilizza python e tutti i suoi programmi esterni. 

5 apri il path, premi su nuovo, facendo questo aggiungi un nuovo percorso a quello che python può utilizzare. 

6 prendi il percorso della cartella ffmpeg. Attenzione, non la cartella in se, ma bensì la sua cartella "bin". Il percorso è più o meno simile a C:utente/desktop/ffmpeg/bin

7 salva il tutto

8 se vuoi verificare che si sia installato tutto per bene fai Verifica aprendo PowerShell:  ffmpeg -version



--INSTALLAZIONE DI COLMAP-- 

1 Vai su https://github.com/colmap/colmap/releases


2 Scarica la release Windows (colmap-x.x-windows-no-cuda.zip o colmap-x.x-windows-cuda.zip).  
ATTENZIONE: 
colmap funziona meglio con GPU con cuda cores, come ad esempio le rtx nvidia, il che andrebbe utilizzato colmap-x.x-windows-cuda.zip

Altrimenti, si può procedere con colmap-x.x-windows-no-cuda.zip



3 Estrai la cartella, per esempio in: C:\tools\colmap\


4 Aggiungi al PATH di sistema come fatto con il ffmpeg in precedenza. C:\tools\colmap\bin\


5 Verifica nella shell con : colmap -h
Se mostra l’help, COLMAP è pronto.





##Struttura del progetto

```
📁 progetto-ricostruzione3D/
 ├─ reconstruct_3d_colmap.py
 ├─ INSTALLAZIONE_E_GUIDA.txt
 ├─ .gitignore
 ├─ README.md
 └─ tools/
```

---

##  Utilizzo

### 🔹 Ricostruzione da video

```powershell
.\.venv\Scripts\python.exe .\reconstruct_3d_colmap.py --video "sostituisci con il percorso al file video" --output "percorso cartella output" --reset --fps 3 --threads 12 --gpu 0 --pm_max_size 2000
```

### 🔹 Ricostruzione da immagini

```powershell
.\.venv\Scripts\python.exe .\reconstruct_3d_colmap.py --images ".\input\images" --output ".\output" --reset --threads 12 --gpu 0 --pm_max_size 2000
```

---


## Monitoraggio avanzamento

Durante la fase PatchMatch, vedrai qualcosa come:

```
🧩 PatchMatch: 34/96 (35%)
```

Significa che ha elaborato 34 immagini su 96 totali.

---

##Risultati finali

```
dense/0/
 ├─ images/
 ├─ stereo/depth_maps/
 ├─ fused.ply
 └─ meshed-delaunay.ply
```

Apri `.ply` con **MeshLab**, **Blender** o **CloudCompare**.

--ESECUZIONE CON PYCHARM--



1 Aprire il progetto in PyCharm

- Apri PyCharm

- Clicca su File → Open

- Seleziona la cartella del progetto e premi OK




2 Configura l’interprete Python

- Vai su File → Settings → Project → Python Interpreter

- In alto a destra, clicca sull’icona dell'ingranaggio → Add Interpreter

- Seleziona Existing environment

Naviga fino a:

progetto-ricostruzione3D\.venv\Scripts\python.exe


(è l’ambiente virtuale creato dal setup)

✅ PyCharm userà automaticamente i pacchetti installati in .venv.



3 Creare una configurazione di esecuzione

- In alto a destra clicca su Add Configuration → + → Python

- Imposta i parametri:

- Script path:

- reconstruct_3d_colmap.py


Parameters:
Esempio per un video:

--video ".\input\video.mp4" --output ".\output" --reset --fps 3 --threads 12 --gpu 0 --pm_max_size 2000


Oppure per immagini:

--images ".\input\images" --output ".\output" --reset --threads 12 --gpu 0


Python interpreter:
Seleziona .venv\Scripts\python.exe

Working directory:
La root del progetto (es. C:\Users\<Nome>\Desktop\progetto-ricostruzione3D)

Clicca su Apply → OK

--Avvio--

Premi (Run) in alto a destra.
Vedrai l’output direttamente nella console integrata di PyCharm, con i log di FFmpeg e COLMAP.





## Risoluzione problemi

| Errore | Causa | Soluzione |
|---------|--------|-----------|
| colmap non riconosciuto | PATH non configurato | Rilancia `setup_windows.ps1` |
| ffmpeg non riconosciuto | Non nel PATH | Verifica `tools/ffmpeg/bin/` |
| rigs/cameras not found | workspace errato | Usa `dense/0` |
| CUDA error | Driver GPU vecchi | Aggiorna driver NVIDIA |
| Crash improvviso | RAM insufficiente | Riduci `--pm_max_size` o `--fps` |
